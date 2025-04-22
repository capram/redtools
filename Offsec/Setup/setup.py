import os
import subprocess

def run_command(command, description):
    """Run a shell command and print its status."""
    print(f"[*] {description}...")
    result = subprocess.run(command, shell=True)
    if result.returncode == 0:
        print(f"[+] {description} - Completed successfully")
        return True
    else:
        print(f"[!] {description} - Failed")
        return False

def get_user_confirmation(prompt_message):
    """Get a normalized Yes/No confirmation from the user."""
    while True:
        choice = input(prompt_message + " (yes/no): ").strip().lower()
        if choice in ['y', 'yes']:
            return True
        elif choice in ['n', 'no']:
            return False
        else:
            print("[!] Invalid input. Please enter 'yes', 'no', 'y', or 'n'.")

def add_timestamp_to_prompt_system_wide():
    """Ask the user if they want to add a timestamp to the command prompt for all users and modify /etc/bash.bashrc."""
    if get_user_confirmation("Would you like to add a timestamp to the command prompt for all users (including sudo)?"):
        print("[*] Replacing PS1 variable to include timestamp in /etc/bash.bashrc...")
        try:
            bashrc_path = "/etc/bash.bashrc"

            # Read the existing contents of /etc/bash.bashrc
            with open(bashrc_path, "r") as file:
                lines = file.readlines()

            # Remove any existing PS1 definition
            lines = [line for line in lines if not line.strip().startswith("PS1=")]

            # Add the new PS1 definition with timestamp
            lines.append('# Set PS1 to include timestamp for all users\n')
            lines.append('export PS1="\\[\\e[32m\\]\\D{%Y-%m-%d %H:%M:%S} \\[\\e[0m\\]\\u@\\h:\\w\\$ "\n')

            # Write the updated lines back to the file
            with open(bashrc_path, "w") as file:
                file.writelines(lines)

            print("[+] PS1 variable replaced successfully in /etc/bash.bashrc. Please restart your terminal or run 'source /etc/bash.bashrc' to apply changes.")
        except PermissionError:
            print("[!] Permission denied. Please run this script with superuser privileges (e.g., sudo).")
        except Exception as e:
            print(f"[!] An error occurred while modifying /etc/bash.bashrc: {e}")
    else:
        print("[*] Skipping adding a timestamp to the command prompt

