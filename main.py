# Project Name : LogHarvesterWeapon 
#----------------------------------------------------------------------------------------------------------
import paramiko
import os
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, scrolledtext

# SSH connection details for Kali Linux VM
hostname = '192.168.238.128'  
port = 22  
username = 'gany'  
password = 'gany'  

# Define the log files you want to collect
log_files = [
    "/var/log/syslog",
    "/var/log/auth.log",
    "/var/log/dpkg.log",
     "/var/log/alternatives.log ",
    "/var/log/boot.log",
     "/var/log/fontconfig.log",
    "/var/log/vmware-network.1.log ",
    "/var/log/vmware-network.log",
     "/var/log/alternatives.log ",
    "/var/log/alternatives.log.1"
]

# Define the base output directory on Windows
output_base_dir = r"D:\Projects\Log_Collection_Weapon\output"

# Function to create a date and time-based folder
def create_datetime_folder(base_dir):
    # Generate a folder name based on the current date and time
    folder_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder_path = os.path.join(base_dir, folder_name)
    
    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created folder: {folder_path}")
    
    return folder_path

# Function to collect logs via SSH
def collect_logs_ssh(hostname, port, username, password, log_files, output_base_dir):
    try:
        # Establish SSH connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, port, username, password)
        print("Connected to Kali Linux VM via SSH.")

        # Open SFTP session
        sftp = ssh.open_sftp()

        # Create a date and time-based folder for this log collection
        output_dir = create_datetime_folder(output_base_dir)

        for log_file in log_files:
            try:
                # Create a timestamped filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                log_name = os.path.basename(log_file)
                output_file = os.path.join(output_dir, f"{log_name}_{timestamp}.log")

                # Debug: Print the log file path
                print(f"Attempting to collect: {log_file}")

                # Download the log file from Kali Linux to Windows
                sftp.get(log_file, output_file)
                print(f"Collected: {log_file} -> {output_file}")

                # Debug: Verify the downloaded file is not empty
                if os.path.getsize(output_file) == 0:
                    print(f"Warning: {output_file} is empty!")
                else:
                    print(f"Success: {output_file} contains data.")

            except FileNotFoundError:
                print(f"Log file not found on Kali Linux: {log_file}")
            except Exception as e:
                print(f"Error collecting {log_file}: {e}")

        # Close SFTP and SSH connections
        sftp.close()
        ssh.close()
        print("Disconnected from Kali Linux VM.")

    except Exception as e:
        print(f"SSH connection failed: {e}")


# Function to load and display logs in the GUI
def load_logs(log_text, status_label, output_dir):
    # Clear the text widget
    log_text.delete(1.0, tk.END)

    # Open a file dialog to select a log file
    file_path = filedialog.askopenfilename(
        initialdir=output_dir,
        title="Select Log File",
        filetypes=(("Log Files", "*.log"), ("All Files", "*.*"))
    )

    if file_path:
        try:
            # Read the selected log file
            with open(file_path, "r") as file:
                logs = file.read()
                # Display the logs in the text widget
                log_text.insert(tk.END, logs)
                status_label.config(text=f"Loaded: {os.path.basename(file_path)}")
        except Exception as e:
            status_label.config(text=f"Error reading file: {e}")

# Function to create the GUI
def create_gui(output_dir):
    # Create the main window
    root = tk.Tk()
    root.title("Log Viewer")
    root.geometry("800x600")

    # Create a scrolled text widget to display logs
    log_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=30)
    log_text.pack(padx=10, pady=10)

    # Create a button to load logs
    load_button = tk.Button(
        root,
        text="Load Logs",
        command=lambda: load_logs(log_text, status_label, output_dir)
    )
    load_button.pack(pady=10)

    # Create a status label
    status_label = tk.Label(root, text="Select a log file to view", fg="blue")
    status_label.pack()

    # Run the application
    root.mainloop()

# Main function 
if __name__ == "__main__":
    # Collect the logs
    collect_logs_ssh(hostname, port, username, password, log_files, output_base_dir)
    create_gui(output_base_dir)
    print("Log collection and display complete.")