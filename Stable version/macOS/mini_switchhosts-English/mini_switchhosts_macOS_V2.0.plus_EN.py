#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PySide6 All-in-One GitHub & Replit Hosts Manager
Function: Update, backup, and restore GitHub and Replit related hosts rules
"""

import sys
import os
import requests
import shutil
import subprocess
import tempfile
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QTextEdit, QPushButton, QLabel,
                               QMessageBox, QFileDialog, QSplitter, QProgressBar,
                               QComboBox)
from PySide6.QtCore import Qt, QThread, Signal as pyqtSignal
from PySide6.QtGui import QFont, QTextCursor


def is_admin():
    """Check if the program has root privileges"""
    try:
        return os.geteuid() == 0
    except:
        return False


def run_as_admin():
    """Run the program with root privileges"""
    if not is_admin():
        try:
            subprocess.Popen(['osascript', '-e', 
                             f'do shell script "{sys.executable} {" ".join(sys.argv)}" with administrator privileges'])
            return False
        except:
            return False
    return True


class HostsManagerThread(QThread):
    """Background thread to handle network requests and file operations"""
    log_signal = pyqtSignal(str)
    result_signal = pyqtSignal(dict)
    progress_signal = pyqtSignal(int)

    def __init__(self, task_type, data=None, target_type='github'):
        super().__init__()
        self.task_type = task_type  # 'download', 'apply', 'backup', 'restore'
        self.data = data
        self.target_type = target_type  # 'github' or 'replit'

    def run(self):
        try:
            if self.task_type == 'download':
                self.download_hosts()
            elif self.task_type == 'apply':
                self.apply_hosts()
            elif self.task_type == 'backup':
                self.create_backup()
            elif self.task_type == 'restore':
                self.restore_backup()
        except Exception as e:
            self.log_signal.emit(f"❌ Error: {str(e)}")

    def download_hosts(self):
        """Download hosts rules from network sources"""
        self.log_signal.emit("📡 Connecting to server...")
        self.progress_signal.emit(10)

        if self.target_type == 'github':
            sources = [
                "https://gitee.com/ineo6/hosts/raw/master/hosts",
                "https://raw.hellogithub.com/hosts",
                "https://cdn.jsdelivr.net/gh/ineo6/hosts/hosts",
                "https://gitlab.com/ineo6/hosts/-/raw/master/hosts"
            ]
        else:  # replit
            sources = [
                # Remove unreliable sources, add new reliable sources
                "https://cdn.jsdelivr.net/gh/techsharing/toolbox/hosts/replit-hosts",
                "https://gitee.com/techsharing/toolbox/raw/main/hosts/replit-hosts",
                "https://raw.githubusercontent.com/521xueweihan/GitHub520/main/hosts",  # This source also contains some replit rules
                "https://gitlab.com/techsharing/toolbox/-/raw/main/hosts/replit-hosts"
            ]

        for i, source in enumerate(sources):
            try:
                self.log_signal.emit(f"🔄 Trying to download from {source.split('//')[1].split('/')[0]}...")
                self.progress_signal.emit(20 + i * 15)

                response = requests.get(source, timeout=10)  # Shorten timeout
                if response.status_code == 200:
                    self.log_signal.emit("✅ Download successful, parsing rules...")
                    self.progress_signal.emit(80)

                    if self.target_type == 'github':
                        rules = self.extract_github_rules(response.text)
                    else:
                        rules = self.extract_replit_rules(response.text)
                
                    # Verify if rules are valid
                    if rules and not rules.startswith("# Not found"):
                        self.progress_signal.emit(100)
                        self.result_signal.emit({'success': True, 'rules': rules, 'source': source})
                        return
                    else:
                        self.log_signal.emit("️⚠ Downloaded rules are empty, trying next source...")
                    
            except requests.exceptions.Timeout:
                self.log_signal.emit(f"⚠️  {source} connection timed out")
                continue
            except requests.exceptions.ConnectionError:
                self.log_signal.emit(f"⚠️  {source} connection error")
                continue
            except Exception as e:
                self.log_signal.emit(f"⚠️  {source} failed: {str(e)}")
                continue

        self.result_signal.emit({'success': False, 'error': 'All sources failed, please check network connection'})

    def extract_github_rules(self, content):
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

    def extract_replit_rules(self, content):
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

    def parse_rules(self, rules_text):
        """Parse rules text, return domain to IP mapping"""
        domain_ip_map = {}
        lines = rules_text.split('\n')
        
        for line in lines:
            line = line.strip()
            # Skip empty lines and comment lines
            if not line or line.startswith('#'):
                continue
                
            # Split IP and domain
            parts = line.split()
            if len(parts) >= 2:
                ip = parts[0]
                domain = parts[1]
                domain_ip_map[domain] = ip
                
        return domain_ip_map

    def update_hosts_content(self, content, domain_ip_map):
        """Update hosts file content, replace existing GitHub related entries"""
        lines = content.split('\n')
        updated_lines = []
        in_github_section = False
        
        github_domains = [
            'alive.github.com', 'api.github.com', 'camo.githubusercontent.com',
            'central.github.com', 'codeload.github.com', 'collector.github.com',
            'favicons.githubusercontent.com', 'gist.github.com', 'github.com',
            'github.community', 'github.githubassets.com', 'github.global.ssl.fastly.net',
            'live.github.com', 'raw.githubusercontent.com', 'user-images.githubusercontent.com',
            'education.github.com', 'private-user-images.githubusercontent.com'
        ]
        
        i = 0
        while i < len(lines):
            line = lines[i]
            line_stripped = line.strip()
            
            # Check if entering GitHub rule section
            if line_stripped.startswith('# GitHub Hosts Start'):
                # Skip entire GitHub rule section
                while i < len(lines) and not lines[i].strip().startswith('# GitHub Hosts End'):
                    i += 1
                # Skip end marker line
                if i < len(lines):
                    i += 1
                continue
                
            # Skip empty lines and comment lines
            if not line_stripped or line_stripped.startswith('#'):
                updated_lines.append(line)
                i += 1
                continue
                
            # Split IP and domain
            parts = line.split()
            if len(parts) >= 2:
                domain = parts[1]
                # If it's a GitHub related domain, update to new IP
                if domain in github_domains and domain in domain_ip_map:
                    # Don't add this line, as all GitHub rules will be added uniformly at the end
                    pass
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)
                
            i += 1
                
        # Add GitHub rule section with latest rules
        if domain_ip_map:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            updated_lines.append("")
            updated_lines.append(f"# GitHub Hosts Start - Updated at {timestamp}")
            # Sort by domain name for neat output
            for domain in sorted(domain_ip_map.keys()):
                updated_lines.append(f"{domain_ip_map[domain]} {domain}")
            updated_lines.append("# GitHub Hosts End")
            
        return '\n'.join(updated_lines)

    def apply_hosts(self):
        """Apply rules to hosts file - using safe write method"""
        hosts_path = self.get_hosts_path()
        new_rules = self.data
        target_type = self.target_type

        self.log_signal.emit("🛡️ Checking root privileges...")
        if not is_admin():
            self.result_signal.emit({'success': False, 'error': 'Root privileges required, please run the program as root'})
            return

        # Backup current hosts
        self.log_signal.emit("📦 Creating backup...")
        if not self.create_backup():
            self.result_signal.emit({'success': False, 'error': 'Backup failed'})
            return

        try:
            self.log_signal.emit("📖 Reading existing hosts file...")
            # Read existing hosts
            with open(hosts_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse new rules
            self.log_signal.emit("🔍 Parsing new rules...")
            domain_ip_map = self.parse_rules(new_rules)

            # Update hosts content
            self.log_signal.emit("🔄 Updating GitHub related entries...")
            updated_content = self.update_hosts_content(content, domain_ip_map)

            # Use temporary file for safe writing
            self.log_signal.emit("💾 Writing updated hosts file...")
            temp_dir = tempfile.gettempdir()
            temp_hosts = os.path.join(temp_dir, 'hosts_temp')

            with open(temp_hosts, 'w', encoding='utf-8', newline='\n') as f:
                f.write(updated_content)

            # Copy temporary file to system hosts location
            shutil.copy(temp_hosts, hosts_path)

            # Clean up temporary file
            if os.path.exists(temp_hosts):
                os.remove(temp_hosts)

            self.result_signal.emit({'success': True})

        except PermissionError as e:
            self.result_signal.emit({'success': False, 'error': f'Permission denied: {str(e)}. Please make sure to run the program as root.'})
        except Exception as e:
            self.result_signal.emit({'success': False, 'error': f'Write failed: {str(e)}'})

    def clean_old_rules(self, content, target_type):
        """Clean up old rules"""
        lines = content.split('\n')
        cleaned_lines = []
        in_target_section = False
        section_start_marker = f"# {target_type.capitalize()} Hosts Start"
        section_end_marker = f"# {target_type.capitalize()} Hosts End"

        # Determine domains to clean based on target type
        if target_type == 'github':
            target_domains = [
                'github.com', 'github.global.ssl.fastly.net',
                'assets-cdn.github.com', 'github.githubassets.com',
                'codeload.github.com', 'api.github.com',
                'raw.githubusercontent.com', 'user-images.githubusercontent.com',
                'favicons.githubusercontent.com', 'camo.githubusercontent.com',
                'gist.github.com', 'gist.githubusercontent.com'
            ]
        else:  # replit
            target_domains = [
                'replit.com', 'repl.co', 'repl.it',
                'cdn.replit.com', 'static.replit.com',
                'sp.replit.com', 'replit.app',
                'firewalledreplit.com', 'ide.replit.com',
                'docs.replit.com', 'api.replit.com',
                'eval.replit.com', 'widgets.replit.com'
            ]

        for line in lines:
            stripped = line.strip()

            # Detect target rule section start
            if stripped.startswith(section_start_marker):
                in_target_section = True
                continue

            # Detect target rule section end
            if stripped.startswith(section_end_marker):
                in_target_section = False
                continue

            # If in target section, skip
            if in_target_section:
                continue

            # Clean up scattered target related rules
            if (not in_target_section and stripped and
                    not stripped.startswith('#') and
                    any(domain in stripped for domain in target_domains)):
                continue

            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def create_backup(self):
        """Create hosts backup"""
        try:
            hosts_path = self.get_hosts_path()
            backup_dir = os.path.join(os.path.dirname(__file__), 'hosts_backups')
            os.makedirs(backup_dir, exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(backup_dir, f'hosts_backup_{timestamp}')

            shutil.copy2(hosts_path, backup_path)
            self.log_signal.emit(f"✅ Backup created: {backup_path}")
            return True
        except Exception as e:
            self.log_signal.emit(f"❌ Backup failed: {str(e)}")
            return False

    def restore_backup(self):
        """Restore backup"""
        backup_file = self.data
        if not backup_file:
            self.result_signal.emit({'success': False, 'error': 'No backup file specified'})
            return

        try:
            self.log_signal.emit("🛡️ Checking root privileges...")
            if not is_admin():
                self.result_signal.emit({'success': False, 'error': 'Root privileges required, please run the program as root'})
                return

            hosts_path = self.get_hosts_path()

            # Use temporary file for safe restore
            temp_dir = tempfile.gettempdir()
            temp_hosts = os.path.join(temp_dir, 'hosts_restore_temp')

            shutil.copy2(backup_file, temp_hosts)
            shutil.copy2(temp_hosts, hosts_path)

            # Clean up temporary file
            if os.path.exists(temp_hosts):
                os.remove(temp_hosts)

            self.result_signal.emit({'success': True})
        except PermissionError as e:
            self.result_signal.emit({'success': False, 'error': f'Permission denied: {str(e)}. Please make sure to run the program as root.'})
        except Exception as e:
            self.result_signal.emit({'success': False, 'error': f'Restore failed: {str(e)}'})

    def get_hosts_path(self):
        """Get hosts file path"""
        return "/etc/hosts"


class HostsManager(QMainWindow):
    """Main window interface"""

    def __init__(self):
        super().__init__()
        self.current_rules = ""
        self.current_target = "github"  # Default target
        self.init_ui()
        self.check_admin_status()

    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("GitHub & Replit Hosts Manager (PySide6 All-in-One)")
        self.setGeometry(300, 200, 900, 700)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Title
        title_label = QLabel("GitHub & Replit Hosts One-Click Management Tool")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Target selection
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Select target:"))
        
        self.target_combo = QComboBox()
        self.target_combo.addItem("GitHub", "github")
        self.target_combo.addItem("Replit", "replit")
        self.target_combo.currentTextChanged.connect(self.on_target_changed)
        target_layout.addWidget(self.target_combo)
        
        target_layout.addStretch()
        layout.addLayout(target_layout)

        # Administrator status indicator
        self.admin_label = QLabel()
        self.admin_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.admin_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Horizontal layout for buttons
        button_layout = QHBoxLayout()

        # Function buttons
        self.btn_download = QPushButton("🔄 Update Rules")
        self.btn_apply = QPushButton("💾 Apply Rules")
        self.btn_backup = QPushButton("📦 Create Backup")
        self.btn_restore = QPushButton("⏪ Restore Backup")

        self.btn_download.clicked.connect(self.download_rules)
        self.btn_apply.clicked.connect(self.apply_rules)
        self.btn_backup.clicked.connect(self.create_backup)
        self.btn_restore.clicked.connect(self.restore_backup)

        button_layout.addWidget(self.btn_download)
        button_layout.addWidget(self.btn_apply)
        button_layout.addWidget(self.btn_backup)
        button_layout.addWidget(self.btn_restore)

        layout.addLayout(button_layout)

        # Splitter for rules display and logs
        splitter = QSplitter(Qt.Vertical)

        # Rules display area
        rules_widget = QWidget()
        rules_layout = QVBoxLayout(rules_widget)
        rules_layout.addWidget(QLabel("Rules Display/Edit Area:"))

        self.rules_edit = QTextEdit()
        self.rules_edit.setPlaceholderText("Rules will be displayed here...")
        rules_layout.addWidget(self.rules_edit)

        # Log display area
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        log_layout.addWidget(QLabel("Operation Log:"))

        self.log_edit = QTextEdit()
        self.log_edit.setPlaceholderText("Operation logs will be displayed here...")
        self.log_edit.setMaximumHeight(200)
        log_layout.addWidget(self.log_edit)

        splitter.addWidget(rules_widget)
        splitter.addWidget(log_widget)
        splitter.setSizes([500, 200])

        layout.addWidget(splitter, 1)

        # Status bar
        self.statusBar().showMessage("Ready")

        self.log("🚀 GitHub & Replit Hosts Manager started")

    def on_target_changed(self, text):
        """Target type changed"""
        self.current_target = self.target_combo.currentData()
        target_name = "GitHub" if self.current_target == "github" else "Replit"
        self.log(f"🎯 Switched to {target_name} mode")
        self.statusBar().showMessage(f"Current target: {target_name}")

    def check_admin_status(self):
        """Check and display administrator status"""
        if is_admin():
            self.admin_label.setText("✅ Currently running with root privileges")
            self.admin_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.admin_label.setText("⚠️ Not running with root privileges (some functions may be limited)")
            self.admin_label.setStyleSheet("color: orange; font-weight: bold;")

    def log(self, message):
        """Add log information"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_edit.append(f"[{timestamp}] {message}")
        self.log_edit.moveCursor(QTextCursor.End)

    def set_buttons_enabled(self, enabled):
        """Enable/disable all buttons"""
        self.btn_download.setEnabled(enabled)
        self.btn_apply.setEnabled(enabled)
        self.btn_backup.setEnabled(enabled)
        self.btn_restore.setEnabled(enabled)

    def download_rules(self):
        """Download latest rules"""
        target_name = "GitHub" if self.current_target == "github" else "Replit"
        self.log(f"Starting to download latest {target_name} hosts rules...")
        self.set_buttons_enabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.thread = HostsManagerThread('download', target_type=self.current_target)
        self.thread.log_signal.connect(self.log)
        self.thread.result_signal.connect(self.on_download_result)
        self.thread.progress_signal.connect(self.progress_bar.setValue)
        self.thread.finished.connect(self.on_thread_finished)
        self.thread.start()

    def on_download_result(self, result):
        """Handle download result"""
        if result['success']:
            self.current_rules = result['rules']
            self.rules_edit.setPlainText(self.current_rules)
            rule_count = len(self.current_rules.splitlines())
            target_name = "GitHub" if self.current_target == "github" else "Replit"
            self.log(f"✅ {target_name} rules successfully obtained, total {rule_count} entries")
            self.statusBar().showMessage(f"{target_name} rules downloaded successfully")
        else:
            self.log(f"❌ Rule acquisition failed: {result.get('error', 'Unknown error')}")
            self.statusBar().showMessage("Download failed")

    def apply_rules(self):
        """Apply rules to hosts file"""
        if not self.rules_edit.toPlainText().strip():
            QMessageBox.warning(self, "Warning", "No rules to apply")
            return

        # Check administrator privileges
        if not is_admin():
            target_name = "GitHub" if self.current_target == "github" else "Replit"
            reply = QMessageBox.question(self, "Root privileges required",
                                         f"Applying {target_name} rules requires root privileges. Restart the program as root now?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                run_as_admin()
                sys.exit(0)
            return

        target_name = "GitHub" if self.current_target == "github" else "Replit"
        reply = QMessageBox.question(self, "Confirm",
                                     f"This will modify the system hosts file to optimize {target_name} access. Continue?",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.log(f"Starting to apply {target_name} rules to system hosts file...")
            self.set_buttons_enabled(False)

            self.current_rules = self.rules_edit.toPlainText()
            self.thread = HostsManagerThread('apply', self.current_rules, self.current_target)
            self.thread.log_signal.connect(self.log)
            self.thread.result_signal.connect(self.on_apply_result)
            self.thread.finished.connect(self.on_thread_finished)
            self.thread.start()

    def on_apply_result(self, result):
        """Handle apply result"""
        if result['success']:
            target_name = "GitHub" if self.current_target == "github" else "Replit"
            self.log(f"✅ {target_name} rules applied successfully!")
            self.log("💡 Suggested to flush DNS cache: sudo dscacheutil -flushcache (macOS)")
            QMessageBox.information(self, "Success",
                                    f"{target_name} rules applied successfully!\n\nSuggested to run in terminal: sudo dscacheutil -flushcache to flush DNS cache")
            self.statusBar().showMessage(f"{target_name} rules applied successfully")
        else:
            self.log(f"❌ Rule application failed: {result.get('error', 'Unknown error')}")
            QMessageBox.critical(self, "Error", f"Application failed: {result.get('error', 'Unknown error')}")

    def create_backup(self):
        """Create backup"""
        self.log("Creating hosts file backup...")
        self.set_buttons_enabled(False)

        self.thread = HostsManagerThread('backup')
        self.thread.log_signal.connect(self.log)
        self.thread.result_signal.connect(self.on_backup_result)
        self.thread.finished.connect(self.on_thread_finished)
        self.thread.start()

    def on_backup_result(self, result):
        """Handle backup result"""
        self.statusBar().showMessage("Backup completed")

    def restore_backup(self):
        """Restore backup"""
        backup_dir = os.path.join(os.path.dirname(__file__), 'hosts_backups')
        if not os.path.exists(backup_dir):
            QMessageBox.information(self, "Information", "Backup directory not found")
            return

        # Check administrator privileges
        if not is_admin():
            reply = QMessageBox.question(self, "Root privileges required",
                                         "Restoring backup requires root privileges. Restart the program as root now?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                run_as_admin()
                sys.exit(0)
            return

        # Let user select backup file
        backup_file, _ = QFileDialog.getOpenFileName(
            self, "Select backup file", backup_dir, "Backup Files (hosts_backup_*)")

        if backup_file:
            self.log(f"Starting to restore hosts file from {backup_file}...")
            self.set_buttons_enabled(False)

            self.thread = HostsManagerThread('restore', backup_file)
            self.thread.log_signal.connect(self.log)
            self.thread.result_signal.connect(self.on_restore_result)
            self.thread.finished.connect(self.on_thread_finished)
            self.thread.start()

    def on_restore_result(self, result):
        """Handle restore result"""
        if result['success']:
            self.log("✅ Backup restored successfully!")
            QMessageBox.information(self, "Success", "Backup restored successfully!")
            self.statusBar().showMessage("Backup restored successfully")
        else:
            self.log(f"❌ Backup restore failed: {result.get('error', 'Unknown error')}")
            QMessageBox.critical(self, "Error", f"Restore failed: {result.get('error', 'Unknown error')}")

    def on_thread_finished(self):
        """Cleanup work when thread finishes"""
        self.set_buttons_enabled(True)
        self.progress_bar.setVisible(False)


def main():
    """Main function"""
    try:
        # Check root privileges, request elevation if not root
        if os.name != 'nt' and not is_admin():
            print("Requesting root privileges...")
            run_as_admin()
            return 0

        app = QApplication(sys.argv)

        # Set application style
        app.setStyle('Fusion')

        # Create and show window
        window = HostsManager()
        window.show()

        return app.exec()

    except Exception as e:
        print(f"Application error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())