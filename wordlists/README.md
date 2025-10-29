# Wordlists Directory

This directory is intended for storing wordlists used in Wi-Fi password cracking.

## Default Wordlists Location

Most Linux distributions store default wordlists in:
`/usr/share/wordlists/`

Common wordlists include:
- `rockyou.txt` - Popular password list (~14 million passwords)
- `/usr/share/seclists/Passwords/` - Various specialized lists

## Important Notes

1. **Legal Usage**: Wordlists should only be used for authorized security testing
2. **Storage Requirements**: Large wordlists can consume significant disk space
3. **Effectiveness**: Larger wordlists increase cracking possibilities but require more processing

## Getting Started

To install common wordlists:

```bash
# Install seclists (contains many useful wordlists)
sudo apt install seclists

# Extract rockyou if compressed
sudo gunzip /usr/share/wordlists/rockyou.txt.gz
