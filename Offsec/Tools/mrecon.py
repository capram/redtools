import nmap
import os
import getpass
import subprocess

def request_sudo_privileges():
    print("This script requires sudo privileges to run.")
    sudo_password = getpass.getpass(prompt="Enter your sudo password: ")
    return sudo_password

def check_sudo_privileges(sudo_password):
    try:
        # Test sudo privileges with a harmless command
        result = subprocess.run(
            ['sudo', '-S', 'echo', 'Sudo access granted'],
            input=f"{sudo_password}\n",
            text=True,
            capture_output=True,
            check=True
        )
        print(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print("Invalid sudo password or sudo privileges are not configured.")
        exit(1)

def ask_user(prompt):
    while True:
        response = input(f"{prompt} (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

def run_gobuster(target_ip, port):
    wordlist_path = "/usr/share/wordlists/dirb/common.txt"
    if not os.path.exists(wordlist_path):
        print(f"Wordlist not found at {wordlist_path}. Please ensure it exists.")
        return

    # Construct the URL based on the port
    url = f"http://{target_ip}" if port == 80 else f"https://{target_ip}"
    print(f"Running Gobuster on {url} with wordlist {wordlist_path}...")
    try:
        subprocess.run(
            ['gobuster', 'dir', '-u', url, '-w', wordlist_path, '-t', '10'],
            check=True
        )
    except FileNotFoundError:
        print("Gobuster is not installed. Please install it and try again.")
    except subprocess.CalledProcessError as e:
        print(f"Gobuster scan failed: {e}")

def scan_open_ports(target_ip, sudo_password):
    # Create an Nmap PortScanner object
    nm = nmap.PortScanner()

    if ask_user(f"Do you want to scan target {target_ip} for open TCP ports?"):
        print(f"Scanning target: {target_ip} for open TCP ports...")
        nm.scan(hosts=target_ip, arguments=f'-p- -T4 --open -Pn', sudo=True)

        # Check if the target is up
        if target_ip not in nm.all_hosts():
            print(f"Target {target_ip} is not reachable or no open ports found.")
            return

        # Get the list of open TCP ports
        open_ports = nm[target_ip]['tcp'].keys()
        print(f"Open TCP ports found: {list(open_ports)}")

        for port in open_ports:
            if ask_user(f"Do you want to perform a detailed scan for port {port}?"):
                print(f"Performing detailed scan for port {port}...")
                detailed_scan = nm.scan(hosts=target_ip, arguments=f'-p {port} -sV -sC -Pn', sudo=True)

                # Save the detailed scan results to a text file
                output_file = f"port_{port}_details.txt"
                with open(output_file, 'w') as file:
                    file.write(f"Detailed Scan for Port {port}:\n")
                    file.write(str(detailed_scan) + '\n')

                if port in [80, 443] and ask_user(f"Port {port} is open. Do you want to use Gobuster for directory scanning?"):
                    run_gobuster(target_ip, port)

                if ask_user(f"Do you want to perform an NSE vuln script scan for port {port}?"):
                    print(f"Performing NSE vuln script scan for port {port}...")
                    vuln_scan = nm.scan(hosts=target_ip, arguments=f'-p {port} --script vuln -Pn', sudo=True)

                    # Append the NSE vuln script scan results to the same text file
                    with open(output_file, 'a') as file:
                        file.write(f"\nNSE Vuln Script Scan for Port {port}:\n")
                        file.write(str(vuln_scan) + '\n')

                    print(f"Details for port {port} (including NSE vuln scan) saved to {output_file}")
                else:
                    print(f"Skipped NSE vuln script scan for port {port}.")
            else:
                print(f"Skipped detailed scan for port {port}.")
    else:
        print(f"Skipped scanning target {target_ip} for open TCP ports.")

if __name__ == "__main__":
    # Ask for the target machine's IP address
    target_ip = input("Enter the target machine IP address: ")

    # Request sudo privileges
    sudo_password = request_sudo_privileges()
    check_sudo_privileges(sudo_password)

    # Scan for open ports and perform detailed + NSE vuln scans
    scan_open_ports(target_ip, sudo_password)
