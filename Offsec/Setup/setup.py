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

def modify_text_editor_config():
    """Modify the text editor configuration in ~/.zshrc file."""
    choice = input("Do you want to modify the text editor configuration? (yes/no): ").strip().lower()
    if choice == "yes":
        print("[*] Modifying ~/.zshrc...")
        try:
            with open(os.path.expanduser("~/.zshrc"), "r") as file:
                lines = file.readlines()

            # Modify specific lines
            if len(lines) > 119:  # Ensure the file has enough lines
                lines[118] = lines[118].replace("twoline", "oneline")  # Line 119 in 0-based index
                lines[119] = lines[119].replace("yes", "no")  # Line 120 in 0-based index

                # Write changes back to the file
                with open(os.path.expanduser("~/.zshrc"), "w") as file:
                    file.writelines(lines)

                print("[+] ~/.zshrc modified successfully. Changes saved.")
            else:
                print("[!] ~/.zshrc does not have enough lines to modify. Skipping.")
        except Exception as e:
            print(f"[!] An error occurred while modifying ~/.zshrc: {e}")
    else:
        print("[*] Skipping text editor modification.")

def download_vpn_config(vpn_url, config_path):
    """Download the VPN configuration file."""
    print(f"[*] Downloading VPN configuration from {vpn_url}...")
    result = subprocess.run(f"wget -O {config_path} {vpn_url}", shell=True)
    if result.returncode == 0:
        print("[+] VPN configuration downloaded successfully")
    else:
        print("[!] Failed to download VPN configuration")
        exit(1)

def start_vpn(config_path):
    """Start the VPN using the OpenVPN configuration file."""
    print("[*] Starting VPN connection...")
    result = subprocess.run(f"sudo openvpn {config_path}", shell=True)
    if result.returncode == 0:
        print("[+] VPN connection started successfully")
    else:
        print(f"[!] Failed to start VPN connection")
        exit(1)

def prompt_installation(task, command, sudo_prefix):
    """Prompt user for Yes/No confirmation before running an installation."""
    choice = input(f"Do you want to {task}? (yes/no): ").strip().lower()
    if choice == 'yes':
        success = run_command(f"{sudo_prefix} {command}", task)
        if not success:
            print(f"[*] Moving to the next task after failure in: {task}")
    else:
        print(f"[*] Skipping {task}.")

def main():
    print("[*] This script requires sudo privileges.")
    sudo_password = input("Enter your sudo password: ")
    sudo_prefix = f"echo {sudo_password} | sudo -S"

    # Ask user for confirmation before updating and upgrading
    update_upgrade_choice = input("Do you want to update and upgrade the system? (yes/no): ").strip().lower()
    if update_upgrade_choice == 'yes':
        # Update and upgrade the system
        run_command(f"{sudo_prefix} apt update", "Updating package list")
        run_command(f"{sudo_prefix} apt upgrade -y", "Upgrading installed packages")
    else:
        print("[*] Skipping system update and upgrade.")

    # Prompt for each tool installation
    prompt_installation("install Terminator", "apt install -y terminator", sudo_prefix)

    # Modify text editor configuration
    modify_text_editor_config()

    prompt_installation("install dependencies for AutoRecon", "apt install -y python3-pip python3-venv seclists curl", sudo_prefix)
    prompt_installation("install AutoRecon by Tiberius", "pip3 install git+https://github.com/Tib3rius/AutoRecon.git", sudo_prefix)
    prompt_installation("install bpytop and its dependencies", "apt install -y bpytop", sudo_prefix)

    # Download VPN configuration
    vpn_url = "https://vpn.offsec.com/config.ovpn"  # Replace with the actual URL from Offsec
    config_path = "/etc/openvpn/offsec.ovpn"
    download_vpn_config(vpn_url, config_path)

    # Ask user if they want to start the VPN
    start_vpn_choice = input("Do you want to start the VPN now? (yes/no): ").strip().lower()
    if start_vpn_choice == 'yes':
        start_vpn(config_path)

    print("[*] All tasks completed successfully!")

if __name__ == "__main__":
    main()
