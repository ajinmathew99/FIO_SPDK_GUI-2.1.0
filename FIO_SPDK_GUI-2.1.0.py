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


# Create the main window
root = tk.Tk()
root.title("FIO_SPDK-2.1.0")

window_width = 600
window_height = 400
root.geometry(f"{window_width}x{window_height}")
root.resizable(False, False)
root.withdraw()  # Hide the main window initially

# Styling
font_style = ("Arial", 12)
label_color = "#333333"
entry_color = "#666666"
button_color = "#009900"

# Add padding between walls and lines
label_pad_y = 10
entry_pad_y = 5
button_pad_y = 20
left_padding = 40
top_padding = 40

# Create the login frame
login_window = tk.Tk()
login_window.title("Login")

login_window_width = 450
login_window_height = 350
login_window.geometry(f"{login_window_width}x{login_window_height}")
login_window.resizable(False, False)

ssh_host_label = tk.Label(login_window, text="SSH Host:", font=font_style, fg=label_color, anchor='w')
ssh_host_label.grid(row=0, column=0, pady=(top_padding, label_pad_y), padx=left_padding, sticky='w')
ssh_host_entry = tk.Entry(login_window, font=font_style, fg=entry_color)
ssh_host_entry.grid(row=0, column=1, pady=(top_padding, entry_pad_y), padx=5, sticky='w')

ssh_username_label = tk.Label(login_window, text="Username:", font=font_style, fg=label_color, anchor='w')
ssh_username_label.grid(row=1, column=0, pady=(top_padding, label_pad_y), padx=left_padding, sticky='w')
ssh_username_entry = tk.Entry(login_window, font=font_style, fg=entry_color)
ssh_username_entry.grid(row=1, column=1, pady=(top_padding, entry_pad_y), padx=5, sticky='w')

ssh_password_label = tk.Label(login_window, text="Password:", font=font_style, fg=label_color, anchor='w')
ssh_password_label.grid(row=2, column=0, pady=(top_padding, label_pad_y), padx=left_padding, sticky='w')
ssh_password_entry = tk.Entry(login_window, font=font_style, fg=entry_color, show="*")  # Show asterisks for password
ssh_password_entry.grid(row=2, column=1, pady=(top_padding, entry_pad_y), padx=5, sticky='w')

login_button = tk.Button(login_window, text="Login", font=font_style, bg=button_color, command=connect_to_server)
login_button.grid(row=3, column=1, pady=(top_padding, entry_pad_y), padx=5, sticky='w')

spdkpath_label = tk.Label(root, text="Path to SPDK", font=font_style, fg=label_color, anchor='w')
spdkpath_label.grid(row=0, column=0, pady=(top_padding, label_pad_y), padx=left_padding, sticky='w')
spdkpath_entry = tk.Entry(root, font=font_style, fg=entry_color)
spdkpath_entry.grid(row=0, column=1, pady=(top_padding, entry_pad_y), padx=5, sticky='w')

traddr0_label = tk.Label(root, text="PCI address of Disk", font=font_style, fg=label_color, anchor='w')
traddr0_label.grid(row=1, column=0, pady=label_pad_y, padx=left_padding, sticky='w')
traddr0_entry = tk.Entry(root, font=font_style, fg=entry_color)
traddr0_entry.grid(row=1, column=1, pady=entry_pad_y, padx=5, sticky='w')

size_label = tk.Label(root, text="Size", font=font_style, fg=label_color, anchor='w')
size_label.grid(row=2, column=0, pady=label_pad_y, padx=left_padding, sticky='w')
size_entry = tk.Entry(root, font=font_style, fg=entry_color)
size_entry.grid(row=2, column=1, pady=entry_pad_y, padx=5, sticky='w')

rw_options = ["read", "write", "randread", "randwrite"]

rw_label = tk.Label(root, text="Specify Read/Write command", font=font_style, fg=label_color, anchor='w')
rw_label.grid(row=3, column=0, pady=label_pad_y, padx=left_padding, sticky='w')

rw_combobox = Combobox(root, values=rw_options, font=font_style, state="readonly")
rw_combobox.grid(row=3, column=1, pady=entry_pad_y, padx=5, sticky='w')
rw_combobox.set(rw_options[0])

bs_label = tk.Label(root, text="Block size", font=font_style, fg=label_color, anchor='w')
bs_label.grid(row=5, column=0, pady=label_pad_y, padx=left_padding, sticky='w')
bs_entry = tk.Entry(root, font=font_style, fg=entry_color)
bs_entry.grid(row=5, column=1, pady=entry_pad_y, padx=5, sticky='w')

iodepth_label = tk.Label(root, text="IO depth", font=font_style, fg=label_color, anchor='w')
iodepth_label.grid(row=6, column=0, pady=label_pad_y, padx=left_padding, sticky='w')
iodepth_entry = tk.Entry(root, font=font_style, fg=entry_color)
iodepth_entry.grid(row=6, column=1, pady=entry_pad_y, padx=5, sticky='w')

run_button = tk.Button(root, text="Run FIO", font=font_style, bg=button_color, command=run_fio_command_on_remote)
run_button.grid(row=7, column=0, columnspan=2, pady=button_pad_y)

result_label = tk.Label(root, text="", font=font_style, fg="black")
result_label.grid(row=8, column=0, columnspan=2, pady=label_pad_y)

login_window.mainloop()
root.mainloop()

