import os
import subprocess

def run_command(command, description):
    """Run a shell command and print its status."""
    print(f"[*] {description}...")
    result = subprocess.run(command, shell=True)
    if result.returncode == 0:
        print(f"[+] {description} - Completed successfully")
    else:
        print(f"[!] {description} - Failed")
        exit(1)

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
        print("[!] Failed to start VPN connection")
        exit(1)

def main():
    print("[*] This script requires sudo privileges.")
    sudo_password = input("Enter your sudo password: ")
    sudo_prefix = f"echo {sudo_password} | sudo -S"

    # Update and upgrade the system
    run_command(f"{sudo_prefix} apt update", "Updating package list")
    run_command(f"{sudo_prefix} apt upgrade -y", "Upgrading installed packages")

    # Install Terminator
    run_command(f"{sudo_prefix} apt install -y terminator", "Installing Terminator")

    # Install Sublime Text Editor
    run_command(f"{sudo_prefix} apt install -y sublime-text", "Installing Sublime Text Editor")

    # Install AutoRecon and its dependencies
    run_command(f"{sudo_prefix} apt install -y python3-pip python3-venv seclists curl", "Installing dependencies for AutoRecon")
    run_command(f"{sudo_prefix} pip3 install git+https://github.com/Tib3rius/AutoRecon.git", "Installing AutoRecon by Tiberius")

    # Install bpytop and its dependencies
    run_command(f"{sudo_prefix} apt install -y bpytop", "Installing bpytop and its dependencies")

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
