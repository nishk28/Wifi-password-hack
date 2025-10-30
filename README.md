# Wi-Fi Network Assessment Tool

A comprehensive Python-based automation tool for conducting authorized Wi-Fi security assessments using the aircrack-ng suite. This tool streamlines the process of network discovery, handshake capture, and password cracking for educational and authorized penetration testing purposes.

## ⚠️ LEGAL DISCLAIMER

**THIS TOOL IS FOR AUTHORIZED SECURITY TESTING PURPOSES ONLY.** 

Unauthorized access to computer networks is illegal and unethical. You must only use this tool on networks you own or have explicit written permission to test. The authors assume no liability for misuse of this software.

## Features

- **Automated Network Discovery**: Scan and display all available Wi-Fi networks in your vicinity
- **Handshake Capture**: Automatically capture WPA/WPA2 handshakes using deauthentication techniques
- **Password Cracking**: Integrated wordlist-based password recovery
- **User-Friendly Interface**: Interactive command-line interface with real-time feedback
- **Cross-Platform Compatibility**: Works on Kali Linux, Parrot Security OS, Ubuntu, and other Linux distributions
- **Verbose Logging**: Detailed progress reporting for educational purposes
- **Automatic Cleanup**: Properly restores network interfaces after assessment

## Prerequisites

### Hardware Requirements
- Wireless network adapter that supports monitor mode and packet injection
- Most modern USB Wi-Fi adapters work well (recommended: Alfa AWUS036 series)

### Software Requirements
- Linux operating system (Kali, Parrot, Ubuntu, etc.)
- Administrative privileges (root/sudo access)
- Python 3.6 or higher

## Installation

### Option 1: Automatic Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/nishk28/wifi-password-hack.git
cd wifi-password-hack/scripts/

# Run the installation script
sudo ./install.sh
```

### Option 2: Manual Installation

```bash
# Update package list
sudo apt update

# Install required packages
sudo apt install aircrack-ng wireless-tools iw rfkill

# Install wordlists (optional but recommended)
sudo apt install seclists

# Extract rockyou wordlist if compressed
sudo gunzip /usr/share/wordlists/rockyou.txt.gz

# Make the main script executable
chmod +x wifi_assessment.py
```

## Usage

### Basic Usage

```bash
# Run the tool with root privileges
sudo python3 wifi_assessment.py
```

### Command Line Options

```bash
# Basic assessment
sudo python3 wifi_assessment.py

# Verbose mode with detailed output
sudo python3 wifi_assessment.py -v

# Show version information
sudo python3 wifi_assessment.py --version
```

### Step-by-Step Process

When you run the tool, it will guide you through:

1. **Dependency Check**: Verify all required tools are installed
2. **Interface Detection**: Automatically detect your wireless adapter
3. **Monitor Mode Setup**: Configure your adapter for packet capture
4. **Network Scanning**: Discover all available Wi-Fi networks
5. **Target Selection**: Choose a specific network to assess
6. **Handshake Capture**: Monitor and capture authentication packets
7. **Password Cracking**: Attempt to recover password using wordlists

## How It Works

### Technical Process

1. **Network Discovery**:
   - Uses `airodump-ng` to scan for networks
   - Displays network names, BSSIDs, channels, and encryption types

2. **Handshake Capture**:
   - Monitors network traffic on target channel
   - Sends deauthentication packets to force client reconnection
   - Captures the 4-way WPA handshake during client authentication

3. **Password Recovery**:
   - Attempts dictionary attacks using provided wordlists
   - Compares captured handshake with password candidates

## Understanding Results

### Successful Password Recovery

If the tool successfully recovers a password, you'll see:
```
==================================================
PASSWORD CRACKED SUCCESSFULLY!
==================================================
Network: Target_Network
BSSID:   12:34:56:78:90:AB
Password: password123
==================================================
```

### Failed Attempts

If no password is recovered, this could mean:
- The password is not in your wordlist
- No valid handshake was captured
- The network uses strong, complex security

## Common Issues and Troubleshooting

### No Networks Found
- Ensure your wireless adapter supports monitor mode
- Check if you're close enough to access points
- Verify drivers are properly installed

### Handshake Not Captured
- Target networks may have no active clients
- Try longer capture durations
- Ensure proper deauthentication settings

## Legal and Ethical Guidelines

### ✅ Permitted Usage
- Testing your own home/office networks
- Authorized penetration testing with written permission
- Educational purposes in controlled environments

### ❌ Prohibited Usage
- Accessing networks without explicit permission
- Commercial exploitation without authorization
- Any activity that violates local laws

### Responsible Disclosure
- Report vulnerabilities to network owners
- Follow ethical hacking principles
- Respect privacy and data protection laws

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
- Commit your changes (`git commit -m 'Add amazing feature'`)
- Push to the branch (`git push origin feature/amazing-feature`)
- Open a Pull Request

### Development Setup
```bash
# Clone your fork
git clone https://github.com/nishk28/wifi-password-hack.git
cd wifi-password-hack

# Create virtual environment (optional)
python3 -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt
```

## Support

- **Issues**: [GitHub Issues](https://github.com/nishk28/wifi-password-hack/issues)
- **Documentation**: [Wiki](https://github.com/nishk28/wifi-password-hack/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/nishk28/wifi-password-hack/discussions)

## Limitations

- Effectiveness depends on password complexity and wordlist quality
- May not work against WPA3 or enterprise networks
- Requires compatible hardware and proper configuration
- Time-intensive for strong passwords

## Frequently Asked Questions

**Q: Why can't I capture any handshakes?**
A: This could be due to no active clients, weak signal, or hardware limitations.

**Q: How long does the process take?**
A: Typically 5-15 minutes for scanning and capture, plus cracking time depending on wordlist size.

**Q: Is this tool guaranteed to work?**
A: No. Success depends on multiple factors including network conditions and password strength.

## Security Considerations

- This tool should only be used in controlled, authorized environments
- Always obtain proper permissions before testing
- Follow responsible disclosure practices
- Respect privacy and data protection regulations
