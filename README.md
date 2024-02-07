# FIO_SPDK_GUI-2.1.0
Revised GUI for Performing FIO Benchmarking using SPDK as IO Engine in a Remote Server via SSH
        
## Features
- You can run FIO benchmarking using SPDK as IO Engine in a remote server via SSH.
- Login to a remote server via SSH and .
- Specify the SPDK path, PCI address of the disk, size, read/write command, block size, and IO depth.
- The GUI shows a progress bar while the FIO command is running.
- The output of the FIO command is saved to a text file.

## Prerequisites
- Python 3.6 or later
- SSH client
- SPDK installed with FIO on the remote server
  - You can refer to the following link for installing SPDK with FIO:
```
https://github.com/ajin412/FIO_SPDK_GUI-2.1.0/blob/main/SPDK_Installation.md
```

- SPDK NVMe driver binded with all the NVMe drives that we need to benchmark on the remote server.

## Usage
1. Open the FIO_SPDK_GUI-2.1.0.py file in a Python IDE.
2. Run the program by typing `python FIO_SPDK_GUI-2.1.0.py` in the terminal.
3. Enter the SSH host, username, and password in the login window.
4. Specify the SPDK path, PCI address of the disk, size, read/write command, block size, and IO depth in the main window.
5. Click the "Run FIO" button to start the FIO benchmarking.
6. The output of the FIO command will be displayed in the result label.
7. The output of the FIO command will also be saved to a text file.

## Troubleshooting
If you encounter any issues, please check the following:
- Make sure that the SSH host, username, and password are correct.
- Make sure that the SPDK path is correct.
- Make sure that the PCI address of the disk is correct.
- Make sure that the size, read/write command, block size, and IO depth are valid.
- Make sure that the FIO got installed on the remote server.
- Make sure that the SPDK NVMe driver is binded with all the NVMe drives that we need to benchmark on the remote server.
- You can manually bind the SPDK NVMe driver with the NVMe drives by doing the following:
  - Go to the SPDK directory via terminal.
  - Run the following command:
  
```
sudo ./spdk/scripts/setup.sh
```

## Contributing
If you would like to contribute to this project, please fork the repository and submit a pull request.
