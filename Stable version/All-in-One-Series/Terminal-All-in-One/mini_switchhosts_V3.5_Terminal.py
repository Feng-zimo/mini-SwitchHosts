#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mini-SwitchHosts CLI v3.5
Command-line version for GitHub & Replit Hosts management
Supports Windows, Linux, and macOS
"""

import sys
import os
import requests
import shutil
import tempfile
import argparse
import platform
import ctypes
from datetime import datetime
import re


def is_admin():
    """Check if the program has administrator privileges"""
    try:
        if platform.system().lower() == 'windows':
            return ctypes.windll.shell32.IsUserAnAdmin()
        else:
            return os.geteuid() == 0
    except:
        return False


def get_hosts_path():
    """Get hosts file path based on OS"""
    system = platform.system().lower()
    if system == 'windows':
        return r"C:\Windows\System32\drivers\etc\hosts"
    else:
        return "/etc/hosts"


def create_backup():
    """Create backup of current hosts file"""
    try:
        hosts_path = get_hosts_path()
        
        # Create backup directory if not exists
        backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"hosts_backup_{timestamp}.txt"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Copy hosts file to backup location
        shutil.copy2(hosts_path, backup_path)
        
        print(f"✅ Backup created: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Backup failed: {str(e)}")
        return None


def download_rules(target='github'):
    """Download hosts rules from network sources"""
    print(f"📡 Connecting to servers for {target} rules...")
    
    if target == 'github':
        sources = [
            "https://gitee.com/ineo6/hosts/raw/master/hosts",
            "https://raw.hellogithub.com/hosts",
            "https://cdn.jsdelivr.net/gh/ineo6/hosts/hosts"
        ]
    else:  # replit
        sources = [
            "https://raw.githubusercontent.com/techsharing/toolbox/main/hosts/replit-hosts",
            "https://gitee.com/techsharing/toolbox/raw/main/hosts/replit-hosts",
            "https://cdn.jsdelivr.net/gh/techsharing/toolbox/hosts/replit-hosts"
        ]

    # Try each source
    for i, source in enumerate(sources):
        try:
            print(f"🔄 Trying to download from {source.split('//')[1].split('/')[0]}...")
            response = requests.get(source, timeout=15)
            if response.status_code == 200:
                print("✅ Download successful, parsing rules...")
                
                if target == 'github':
                    rules = extract_github_rules(response.text)
                else:
                    rules = extract_replit_rules(response.text)
                
                if rules and not rules.startswith("# Not found"):
                    print(f"✅ Successfully parsed {target} rules")
                    return rules
                else:
                    print("⚠️  Downloaded rules are empty, trying next source...")
                
        except requests.exceptions.Timeout:
            print(f"⚠️  {source} connection timed out")
            continue
        except requests.exceptions.ConnectionError:
            print(f"⚠️  {source} connection error")
            continue
        except Exception as e:
            print(f"⚠️  {source} failed: {str(e)}")
            continue

    print("❌ All sources failed")
    return None


def extract_github_rules(content):
    """Extract GitHub related rules"""
    github_rules = []
    lines = content.split('\n')

    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            if any(domain in line for domain in [
                'github.com', 'github.global.ssl.fastly.net',
                'assets-cdn.github.com', 'github.githubassets.com',
                'codeload.github.com', 'api.github.com',
                'raw.githubusercontent.com', 'user-images.githubusercontent.com',
                'favicons.githubusercontent.com', 'camo.githubusercontent.com',
                'gist.github.com', 'gist.githubusercontent.com'
            ]):
                github_rules.append(line)

    return '\n'.join(github_rules) if github_rules else "# GitHub related rules not found"


def extract_replit_rules(content):
    """Extract Replit related rules"""
    replit_rules = []
    lines = content.split('\n')

    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            if any(domain in line for domain in [
                'replit.com', 'repl.co', 'repl.it',
                'cdn.replit.com', 'static.replit.com',
                'sp.replit.com', 'replit.app',
                'firewalledreplit.com', 'ide.replit.com',
                'docs.replit.com', 'api.replit.com',
                'eval.replit.com', 'widgets.replit.com'
            ]):
                replit_rules.append(line)

    return '\n'.join(replit_rules) if replit_rules else "# Replit related rules not found"


def is_valid_ip(ip_str):
    """Check if string is a valid IP address"""
    ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    return re.match(ip_pattern, ip_str) is not None


def apply_rules(rules, target='github'):
    """Apply rules to system hosts file"""
    if not rules:
        print("❌ No rules to apply")
        return False

    try:
        print("🛡️  Checking administrator privileges...")
        
        if not is_admin():
            print("❌ Administrator privileges required")
            return False

        hosts_path = get_hosts_path()
        print(f"📂 Hosts file path: {hosts_path}")

        # Create backup first
        create_backup()
        
        # Read current hosts file
        with open(hosts_path, 'r', encoding='utf-8') as f:
            current_content = f.read()

        # Process content
        section_start_marker = "# === GitHub & Replit Hosts Rules Start ==="
        section_end_marker = "# === GitHub & Replit Hosts Rules End ==="
        
        # Remove existing section if present
        lines = current_content.split('\n')
        new_lines = []
        in_target_section = False
        
        for line in lines:
            stripped = line.strip()
            
            # Detect section start
            if stripped.startswith(section_start_marker):
                in_target_section = True
                continue
            
            # Detect section end
            if stripped.startswith(section_end_marker):
                in_target_section = False
                continue
            
            # Skip lines in target section
            if in_target_section:
                continue
            
            # Add line if not in target section
            new_lines.append(line)
        
        # Add new rules section
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        target_name = "GitHub & Replit"
        new_lines.append("")
        new_lines.append(section_start_marker)
        new_lines.append(f"# {target_name} Hosts Rules")
        new_lines.append(f"# Updated: {timestamp}")
        new_lines.append(rules)
        new_lines.append(section_end_marker)
        new_lines.append("")
        
        # Write back to hosts file
        with open(hosts_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(new_lines))
        
        print("✅ Rules applied successfully")
        return True
        
    except PermissionError as e:
        print(f"❌ Permission denied: {str(e)}. Please run as administrator.")
        return False
    except Exception as e:
        print(f"❌ Apply failed: {str(e)}")
        return False


def restore_backup(backup_file=None):
    """Restore hosts file from backup"""
    try:
        print("🛡️  Checking administrator privileges...")
        
        if not is_admin():
            print("❌ Administrator privileges required")
            return False

        if not backup_file:
            # List available backups
            backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
            if not os.path.exists(backup_dir):
                print("❌ No backups directory found")
                return False
            
            backups = [f for f in os.listdir(backup_dir) if f.startswith('hosts_backup_') and f.endswith('.txt')]
            if not backups:
                print("❌ No backup files found")
                return False
            
            # Sort by timestamp (newest first)
            backups.sort(reverse=True)
            backup_file = os.path.join(backup_dir, backups[0])
            print(f"📂 Using latest backup: {backup_file}")
        
        if not os.path.exists(backup_file):
            print(f"❌ Backup file not found: {backup_file}")
            return False

        hosts_path = get_hosts_path()
        
        # Use temporary file for safe restore
        temp_dir = tempfile.gettempdir()
        temp_hosts = os.path.join(temp_dir, 'hosts_restore_temp')

        shutil.copy2(backup_file, temp_hosts)
        shutil.copy2(temp_hosts, hosts_path)

        # Clean up temporary file
        if os.path.exists(temp_hosts):
            os.remove(temp_hosts)

        print("✅ Backup restored successfully")
        return True
    except PermissionError as e:
        print(f"❌ Permission denied: {str(e)}. Please run as administrator.")
        return False
    except Exception as e:
        print(f"❌ Restore failed: {str(e)}")
        return False


def list_backups():
    """List available backup files"""
    backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
    if not os.path.exists(backup_dir):
        print("❌ No backups directory found")
        return
    
    backups = [f for f in os.listdir(backup_dir) if f.startswith('hosts_backup_') and f.endswith('.txt')]
    if not backups:
        print("❌ No backup files found")
        return
    
    # Sort by timestamp (newest first)
    backups.sort(reverse=True)
    
    print("Available backups:")
    for i, backup in enumerate(backups):
        print(f"  {i+1}. {backup}")


def show_version():
    """Show version information"""
    print("mini-SwitchHosts CLI v3.5")
    print("GitHub & Replit Hosts Manager (Command-Line Edition)")
    print("Supports Windows, Linux, and macOS")
    print("© 2025 mini-SwitchHosts Project")


def show_help():
    """Show help information"""
    print("mini-SwitchHosts CLI v3.5")
    print("Usage: python mini_switchhosts_V3.5_cli.py [OPTIONS]")
    print("")
    print("Options:")
    print("  -h, --help               Show this help message and exit")
    print("  -v, --version            Show version information")
    print("  -t TARGET, --target TARGET")
    print("                           Target service: github (default) or replit")
    print("  -d, --download           Download latest rules")
    print("  -a, --apply              Apply downloaded rules to hosts file")
    print("  -b, --backup             Create backup of current hosts file")
    print("  -r, --restore [FILE]     Restore hosts file from backup")
    print("  -l, --list-backups       List available backup files")
    print("  --rules RULES_FILE       Use rules from file instead of downloading")
    print("")
    print("Examples:")
    print("  python mini_switchhosts_V3.5_cli.py -d -t github")
    print("    Download latest GitHub rules")
    print("  python mini_switchhosts_V3.5_cli.py -d -a -t replit")
    print("    Download and apply latest Replit rules")
    print("  python mini_switchhosts_V3.5_cli.py -b")
    print("    Create backup of current hosts file")
    print("  python mini_switchhosts_V3.5_cli.py -r")
    print("    Restore hosts file from latest backup")
    print("  python mini_switchhosts_V3.5_cli.py -r backups/hosts_backup_20251201_120000.txt")
    print("    Restore hosts file from specific backup")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="mini-SwitchHosts CLI - Command-line tool for managing GitHub & Replit hosts rules",
        add_help=False
    )
    
    parser.add_argument('-h', '--help', action='store_true', help='Show help message')
    parser.add_argument('-v', '--version', action='store_true', help='Show version information')
    parser.add_argument('-t', '--target', choices=['github', 'replit'], default='github', 
                       help='Target service: github (default) or replit')
    parser.add_argument('-d', '--download', action='store_true', help='Download latest rules')
    parser.add_argument('-a', '--apply', action='store_true', help='Apply downloaded rules to hosts file')
    parser.add_argument('-b', '--backup', action='store_true', help='Create backup of current hosts file')
    parser.add_argument('-r', '--restore', nargs='?', const=True, default=False, 
                       help='Restore hosts file from backup')
    parser.add_argument('-l', '--list-backups', action='store_true', help='List available backup files')
    parser.add_argument('--rules', help='Use rules from file instead of downloading')
    
    args = parser.parse_args()
    
    # Handle help and version first
    if args.help:
        show_help()
        return 0
    
    if args.version:
        show_version()
        return 0
    
    if args.list_backups:
        list_backups()
        return 0
    
    # Check if any action is specified
    if not (args.download or args.apply or args.backup or args.restore):
        print("❌ No action specified. Use -h for help.")
        return 1
    
    # Handle backup
    if args.backup:
        create_backup()
    
    # Handle restore
    if args.restore:
        if args.restore is True:  # No file specified, use latest
            restore_backup()
        else:  # Specific file specified
            restore_backup(args.restore)
    
    # Handle download and apply
    rules = None
    if args.download or args.rules:
        if args.rules:
            # Read rules from file
            try:
                with open(args.rules, 'r', encoding='utf-8') as f:
                    rules = f.read()
                print(f"📂 Rules loaded from file: {args.rules}")
            except Exception as e:
                print(f"❌ Failed to read rules from file: {str(e)}")
                return 1
        else:
            # Download rules
            rules = download_rules(args.target)
            if not rules:
                return 1
    
    if args.apply:
        if not rules:
            print("❌ No rules to apply. Please download rules first or specify a rules file.")
            return 1
        if not apply_rules(rules, args.target):
            return 1
    
    print("✅ Operation completed successfully")
    return 0


if __name__ == "__main__":
    # Check for administrator privileges for operations that need it
    if len(sys.argv) > 1 and not is_admin():
        operations_requiring_admin = ['-a', '--apply', '-b', '--backup', '-r', '--restore']
        if any(op in sys.argv for op in operations_requiring_admin):
            print("❌ This operation requires administrator privileges.")
            if platform.system().lower() == 'windows':
                print("   Please run as administrator.")
            else:
                print("   Please run with sudo.")
            sys.exit(1)
    
    sys.exit(main())