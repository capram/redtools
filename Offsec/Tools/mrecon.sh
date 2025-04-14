#!/bin/bash

# Function to prompt the user for input
function prompt() {
    local message=$1
    while true; do
        read -p "$message (y/n): " response
        case "$response" in
            [Yy]* ) return 0 ;;  # Yes
            [Nn]* ) return 1 ;;  # No
            * ) echo "Please answer y or n." ;;
        esac
    done
}

# Function to check if a command exists
function check_command() {
    local cmd=$1
    if ! command -v "$cmd" &> /dev/null; then
        echo "Error: $cmd is not installed. Please install it and try again."
        exit 1
    fi
}

# Check for required commands
check_command nmap
check_command gobuster

# Ask for the target IP address
read -p "Enter the target machine IP address: " TARGET_IP

# Scan for open TCP ports
if prompt "Do you want to scan target $TARGET_IP for open TCP ports?"; then
    echo "Scanning target: $TARGET_IP for open TCP ports..."
    NMAP_OUTPUT=$(nmap -p- -T4 --open -Pn "$TARGET_IP")
    echo "$NMAP_OUTPUT"

    # Extract open ports from the Nmap output
    OPEN_PORTS=$(echo "$NMAP_OUTPUT" | grep -oP '^\s*\d+/tcp' | cut -d '/' -f 1)
    if [ -z "$OPEN_PORTS" ]; then
        echo "No open ports found on $TARGET_IP."
        exit 0
    fi

    echo "Open TCP ports found: $OPEN_PORTS"

    # Loop through each open port
    for PORT in $OPEN_PORTS; do
        if prompt "Do you want to perform a detailed scan for port $PORT?"; then
            echo "Performing detailed scan for port $PORT..."
            DETAILED_SCAN=$(nmap -p "$PORT" -sV -sC -Pn "$TARGET_IP")
            echo "$DETAILED_SCAN" | sudo tee "port_${PORT}_details.txt" > /dev/null
            echo "Detailed scan for port $PORT saved to port_${PORT}_details.txt"

            # Check if port 80 or 443 is open for Gobuster
            if [[ "$PORT" == "80" || "$PORT" == "443" ]]; then
                if prompt "Port $PORT is open. Do you want to use Gobuster for directory scanning?"; then
                    WORDLIST="/usr/share/wordlists/dirb/common.txt"
                    if [ ! -f "$WORDLIST" ]; then
                        echo "Wordlist not found at $WORDLIST. Skipping Gobuster scan."
                    else
                        URL="http://$TARGET_IP"
                        [ "$PORT" == "443" ] && URL="https://$TARGET_IP"
                        GOBUSTER_OUTPUT="port_${PORT}_gobuster.txt"
                        echo "Running Gobuster on $URL with wordlist $WORDLIST..."
                        gobuster dir -u "$URL" -w "$WORDLIST" -t 10 | sudo tee "$GOBUSTER_OUTPUT" > /dev/null
                        echo "Gobuster results for port $PORT saved to $GOBUSTER_OUTPUT"
                    fi
                fi

                # Perform Webserver Fingerprinting
                if prompt "Port $PORT is open. Do you want to perform Webserver Fingerprinting using Nmap's http-enum script?"; then
                    echo "Performing Webserver Fingerprinting for port $PORT..."
                    FINGERPRINT_SCAN=$(nmap -p "$PORT" --script=http-enum -Pn "$TARGET_IP")
                    echo "$FINGERPRINT_SCAN" | sudo tee "port_${PORT}_webfingerprint.txt" > /dev/null
                    echo "Webserver Fingerprinting results for port $PORT saved to port_${PORT}_webfingerprint.txt"
                fi
            fi

            # Perform NSE vuln script scan
            if prompt "Do you want to perform an NSE vuln script scan for port $PORT?"; then
                echo "Performing NSE vuln script scan for port $PORT..."
                VULN_SCAN=$(nmap -p "$PORT" --script vuln -Pn "$TARGET_IP")
                echo "$VULN_SCAN" | sudo tee -a "port_${PORT}_details.txt" > /dev/null
                echo "NSE vuln script scan for port $PORT appended to port_${PORT}_details.txt"
            fi
        else
            echo "Skipped detailed scan for port $PORT."
        fi
    done
else
    echo "Skipped scanning target $TARGET_IP for open TCP ports."
fi
