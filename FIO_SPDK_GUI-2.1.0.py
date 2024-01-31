import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar, Combobox
from paramiko import SSHClient, AutoAddPolicy

ssh_host = None
ssh_username = None
ssh_password = None
ssh = None  # To store the SSH connection

def connect_to_server():
    global ssh_host, ssh_username, ssh_password, ssh
    # Get user inputs from login GUI
    ssh_host = ssh_host_entry.get()
    ssh_username = ssh_username_entry.get()
    ssh_password = ssh_password_entry.get()

    try:
        # Establish SSH connection
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(ssh_host, username=ssh_username, password=ssh_password)
        login_window.iconify()  # Minimize the login window
        show_main_gui()
    except Exception as e:
        print(e)
        messagebox.showerror("Login Failed", "Invalid username or password")

def show_main_gui():
    # Show the main GUI
    root.deiconify()

def run_fio_command_on_remote():
    # Get user inputs from GUI
    traddr0 = traddr0_entry.get()
    size = size_entry.get()
    rw = rw_combobox.get()
    bs = bs_entry.get()
    iodepth = iodepth_entry.get()
    spdkpath = spdkpath_entry.get()

    # Validate inputs (you can add more validation if needed)
    if not all((spdkpath, traddr0, size, rw, bs, iodepth)):
        result_label.config(text="Please fill in all fields.", fg="red")
        return

    # Change to the spdk directory and execute setup.sh on the remote server
    spdk_directory = spdkpath_entry.get()
    setup_script = './scripts/setup.sh'

    try:
        # Execute setup.sh on the remote server
        stdin, stdout, stderr = ssh.exec_command(f'cd {spdk_directory} && {setup_script}')
        # You might want to check stdout and stderr for any output or errors
        print(stdout.read().decode('utf-8'))
        print(stderr.read().decode('utf-8'))

    except Exception as e:
        result_label.config(text=f"Error occurred during setup: {e}", fg="red")
        return

    # Run the fio command for each traddr value on the remote server
    for traddr in [traddr0]:
        # Construct the fio command
        fio_command = (
            f'LD_PRELOAD={spdk_directory}/build/fio/spdk_nvme '
            f'fio --filename="trtype=PCIe traddr={traddr} ns=1" '
            f'--name=fiotest --size={size} --rw={rw} --bs={bs} '
            f'--numjobs=1 --ioengine=spdk --iodepth={iodepth} --thread=1'
        )

        try:
            # Execute the fio command on the remote server
            stdin, stdout, stderr = ssh.exec_command(fio_command)
            # You might want to check stdout and stderr for any output or errors
            print(stdout.read().decode('utf-8'))
            print(stderr.read().decode('utf-8'))

            result_label.config(text="Fio Command executed successfully on the remote server.", fg="#006400")

        except Exception as e:
            result_label.config(text=f"Error occurred during fio execution on the remote server: {e}", fg="red")

    # Add the progress bar
    progress_bar = Progressbar(root, orient="horizontal", length=200, mode="indeterminate")
    progress_bar.grid(row=8, column=0, columnspan=2, pady=10)

    try:
        # Show the progress bar while the command is running
        progress_bar.start()

        # Execute the fio command
        subprocess.check_call(fio_command, cwd=spdk_directory, shell=True)
        
        # Stop the progress bar after the command is executed
        progress_bar.stop()

        output_file = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=rw, title="Save FIO Output")

        if output_file:
            result_label.config(text=f"Fio Command executed successfully.\nOutput saved to {output_file}.", fg="#006400")
        else:
            result_label.config(text="Fio Command executed successfully.", fg="#006400")

    except subprocess.CalledProcessError as e:
        progress_bar.stop()
        result_label.config(text=f"Error occurred during fio execution: {e}", fg="red")