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

def add_timestamp_to_prompt():
    """Ask the user if they want to add a timestamp to the command prompt and update ~/.bashrc."""
    if get_user_confirmation("Would you like to add a timestamp to your command prompt?"):
        print("[*] Adding timestamp to the command prompt...")
        try:
            bashrc_path = os.path.expanduser("~/.bashrc")
            with open(bashrc_path, "a") as file:
                # Add a timestamp to the PS1 variable
                file.write('\n# Add timestamp to the command prompt\n')
                file.write('export PS1="\\[\\e[32m\\]\\D{%Y-%m-%d %H:%M:%S} \\[\\e[0m\\]\\u@\\h:\\w\\$ "\n')
            print("[+] Timestamp added to the command prompt. Please restart your terminal or run 'source ~/.bashrc' to apply changes.")
        except Exception as e:
            print(f"[!] An error occurred while modifying ~/.bashrc: {e}")
    else:
        print("[*] Skipping adding a timestamp to the command prompt.")

def modify_text_editor_config():
    """Modify the text editor configuration in ~/.zshrc file."""
    if get_user_confirmation("Do you want to modify the text editor configuration?"):
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

def prompt_installation(task, command, sudo_prefix):
    """Prompt user for Yes/No confirmation before running an installation."""
    if get_user_confirmation(f"Do you want to {task}?"):
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
    if get_user_confirmation("Do you want to update and upgrade the system?"):
        # Update and upgrade the system
        run_command(f"{sudo_prefix} apt update", "Updating package list")
        run_command(f"{sudo_prefix} apt upgrade -y", "Upgrading installed packages")
    else:
        print("[*] Skipping system update and upgrade.")

    # Prompt for each tool installation
    prompt_installation("install Terminator", "apt install -y terminator", sudo_prefix)

    # Modify text editor configuration
    modify_text_editor_config()

    # Add timestamp to the command prompt
    add_timestamp_to_prompt()

    prompt_installation("install dependencies for AutoRecon", "apt install -y python3-pip python3-venv seclists curl", sudo_prefix)
    prompt_installation("install AutoRecon by Tiberius", "pip3 install git+https://github.com/Tib3rius/AutoRecon.git", sudo_prefix)
    prompt_installation("install bpytop and its dependencies", "apt install -y bpytop", sudo_prefix)

    print("[*] All tasks completed successfully!")

if __name__ == "__main__":
    main()
