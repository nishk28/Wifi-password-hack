#!/bin/bash

# Wi-Fi Assessment Tool Installation Script

echo "Wi-Fi Assessment Tool Installation"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}[-] This script must be run as root${NC}" 
   echo "Please run with sudo: sudo ./install.sh"
   exit 1
fi

# Update package list
echo -e "${YELLOW}[*] Updating package list...${NC}"
apt update

# Install main dependencies
echo -e "${YELLOW}[*] Installing required packages...${NC}"

# Core tools
PACKAGES=(
    "aircrack-ng"
    "wireless-tools"
    "iw"
    "rfkill"
)

INSTALLED=0
FAILED=0

for package in "${PACKAGES[@]}"; do
    if dpkg -l | grep -q "^ii  $package "; then
        echo -e "${GREEN}[+] Already installed: $package${NC}"
        ((INSTALLED++))
    else
        echo -e "${YELLOW}[*] Installing $package...${NC}"
        if apt install -y "$package"; then
            echo -e "${GREEN}[+] Successfully installed: $package${NC}"
            ((INSTALLED++))
        else
            echo -e "${RED}[-] Failed to install: $package${NC}"
            ((FAILED++))
        fi
    fi
done

# Check for wordlists
echo -e "${YELLOW}[*] Checking wordlists...${NC}"
WORDLIST_DIR="/usr/share/wordlists"

if [ ! -d "$WORDLIST_DIR" ]; then
    mkdir -p "$WORDLIST_DIR"
fi

ROCKYOU_PATH="$WORDLIST_DIR/rockyou.txt"
if [ ! -f "$ROCKYOU_PATH" ] && [ -f "$ROCKYOU_PATH.gz" ]; then
    echo -e "${YELLOW}[*] Extracting rockyou wordlist...${NC}"
    gunzip "$ROCKYOU_PATH.gz"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[+] Rockyou wordlist extracted${NC}"
    else
        echo -e "${RED}[-] Failed to extract rockyou wordlist${NC}"
    fi
elif [ ! -f "$ROCKYOU_PATH" ] && [ ! -f "$ROCKYOU_PATH.gz" ]; then
    echo -e "${YELLOW}[*] Installing seclists for additional wordlists...${NC}"
    apt install -y seclists
fi

# Make main script executable
chmod +x ../wifi_assessment.py

echo ""
echo "Installation Summary:"
echo "===================="
echo -e "${GREEN}[+] Installed packages: $INSTALLED${NC}"
echo -e "${RED}[-] Failed packages: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}[+] Installation completed successfully!${NC}"
    echo ""
    echo "Usage:"
    echo "  cd .."
    echo "  sudo python3 wifi_assessment.py"
    echo ""
    echo "Note: This tool is for authorized security testing only."
else
    echo -e "${RED}[-] Some packages failed to install${NC}"
fi
