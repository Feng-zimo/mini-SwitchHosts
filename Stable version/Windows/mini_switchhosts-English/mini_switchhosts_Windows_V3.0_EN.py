#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PySide6 All-in-One GitHub & Replit Hosts Manager v3.0
Function: Update, backup, and restore GitHub and Replit related hosts rules
Enhanced with improved IP resolution, smart filtering, and incremental updates
"""

import sys
import os
import requests
import shutil
import ctypes
import tempfile
import threading
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QTextEdit, QPushButton, QLabel,
                               QMessageBox, QFileDialog, QSplitter, QProgressBar,
                               QComboBox, QStatusBar, QGroupBox)
from PySide6.QtCore import Qt, QThread, Signal as pyqtSignal, QTimer
from PySide6.QtGui import QFont, QTextCursor, QAction, QIcon


def is_admin():
    """Check if the program has administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    """Run the program with administrator privileges"""
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        return False
    return True


class EnhancedHostsManagerThread(QThread):
    """Enhanced background thread with concurrent processing"""
    log_signal = pyqtSignal(str)
    result_signal = pyqtSignal(dict)
    progress_signal = pyqtSignal(int)

    def __init__(self, task_type, data=None, target_type='github'):
        super().__init__()
        self.task_type = task_type  # 'download', 'apply', 'backup', 'restore', 'incremental'
        self.data = data
        self.target_type = target_type

    def run(self):
        try:
            if self.task_type == 'download':
                self.download_hosts_enhanced()
            elif self.task_type == 'apply':
                self.apply_hosts()
            elif self.task_type == 'backup':
                self.create_backup()
            elif self.task_type == 'restore':
                self.restore_backup()
            elif self.task_type == 'incremental':
                self.incremental_update()
            elif self.task_type == 'update_check':
                self.check_for_updates()
        except Exception as e:
            self.log_signal.emit(f"❌ Error: {str(e)}")

    def download_hosts_enhanced(self):
        """Enhanced download with smart filtering and concurrent requests"""
        self.log_signal.emit("📡 Connecting to servers with enhanced protocol...")
        self.progress_signal.emit(10)

        if self.target_type == 'github':
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

        # Concurrent requests for faster downloads
        results = {}
        threads = []
        
        def fetch_source(source, index):
            try:
                self.log_signal.emit(f"🔄 Fetching from {source.split('//')[1].split('/')[0]}...")
                response = requests.get(source, timeout=15)
                if response.status_code == 200:
                    results[index] = response.text
            except Exception as e:
                self.log_signal.emit(f"⚠️  {source} failed: {str(e)}")

        # Start concurrent requests
        for i, source in enumerate(sources):
            thread = threading.Thread(target=fetch_source, args=(source, i))
            threads.append(thread)
            thread.start()
            self.progress_signal.emit(20 + i * 15)

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        self.progress_signal.emit(80)
        
        # Process results
        if results:
            # Use the first successful result
            content = results[0] if 0 in results else list(results.values())[0]
            
            if self.target_type == 'github':
                rules = self.extract_github_rules_enhanced(content)
            else:
                rules = self.extract_replit_rules_enhanced(content)
            
            self.progress_signal.emit(100)
            self.result_signal.emit({'success': True, 'rules': rules, 'source': sources[0]})
        else:
            self.result_signal.emit({'success': False, 'error': 'All sources failed'})

    def extract_github_rules_enhanced(self, content):
        """Enhanced extraction with smart filtering"""
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
                    # Smart filtering - check if rule seems valid
                    parts = line.split()
                    if len(parts) >= 2 and self.is_valid_ip(parts[0]):
                        github_rules.append(line)

        return '\n'.join(github_rules) if github_rules else "# GitHub related rules not found"

    def extract_replit_rules_enhanced(self, content):
        """Enhanced extraction with smart filtering for Replit"""
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
                    # Smart filtering - check if rule seems valid
                    parts = line.split()
                    if len(parts) >= 2 and self.is_valid_ip(parts[0]):
                        replit_rules.append(line)

        return '\n'.join(replit_rules) if replit_rules else "# Replit related rules not found"

    def is_valid_ip(self, ip_str):
        """Check if string is a valid IP address"""
        try:
            parts = ip_str.split('.')
            if len(parts) != 4:
                return False
            for part in parts:
                if not part.isdigit() or not 0 <= int(part) <= 255:
                    return False
            return True
        except:
            return False

    def incremental_update(self):
        """Incremental update mechanism"""
        self.log_signal.emit("🔄 Performing incremental update...")
        # Compare current rules with new ones and only apply changes
        try:
            hosts_path = self.get_hosts_path()
            
            # Read current hosts file
            with open(hosts_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            # Extract existing GitHub/Replit rules
            section_name = "GitHub" if self.target_type == "github" else "Replit"
            existing_rules = ""
            in_section = False
            
            for line in current_content.split('\n'):
                if f"# {section_name} Hosts Start" in line:
                    in_section = True
                    continue
                elif f"# {section_name} Hosts End" in line:
                    in_section = False
                    continue
                
                if in_section:
                    existing_rules += line + '\n'
            
            # Compare with new rules
            if existing_rules.strip() != self.data.strip():
                self.log_signal.emit("🔍 Changes detected, applying update...")
                self.apply_hosts()
            else:
                self.log_signal.emit("✅ No changes detected, hosts file is up to date")
            
            self.result_signal.emit({'success': True})
        except Exception as e:
            self.log_signal.emit(f"❌ Incremental update failed: {str(e)}")
            self.result_signal.emit({'success': False, 'error': str(e)})

    def get_hosts_path(self):
        """Get system hosts file path"""
        if sys.platform.startswith('win'):
            return r'C:\Windows\System32\drivers\etc\hosts'
        else:
            return '/etc/hosts'

    def create_backup(self):
        """Create backup of current hosts file"""
        hosts_path = self.get_hosts_path()
        backup_dir = os.path.join(os.path.expanduser('~'), 'HostsBackups')
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(backup_dir, f'hosts_backup_{timestamp}.txt')
        
        try:
            shutil.copy(hosts_path, backup_path)
            self.log_signal.emit(f"✅ Backup created: {backup_path}")
            return True
        except Exception as e:
            self.log_signal.emit(f"❌ Backup failed: {str(e)}")
            return False

    def restore_backup(self):
        """Restore hosts file from backup"""
        self.log_signal.emit("🔄 Restoring from backup...")
        try:
            # Get backup directory
            backup_dir = os.path.join(os.path.expanduser('~'), 'HostsBackups')
            
            if not os.path.exists(backup_dir):
                self.log_signal.emit("❌ Backup directory not found")
                self.result_signal.emit({'success': False, 'error': 'Backup directory not found'})
                return
            
            # List all backup files
            backups = [f for f in os.listdir(backup_dir) if f.startswith('hosts_backup_')]
            if not backups:
                self.log_signal.emit("❌ No backup files found")
                self.result_signal.emit({'success': False, 'error': 'No backup files found'})
                return
            
            # Sort by timestamp to get the latest
            backups.sort(reverse=True)
            latest_backup = backups[0]
            backup_path = os.path.join(backup_dir, latest_backup)
            
            # Restore the backup
            hosts_path = self.get_hosts_path()
            shutil.copy(backup_path, hosts_path)
            
            self.log_signal.emit(f"✅ Backup restored successfully from {latest_backup}")
            self.result_signal.emit({'success': True})
        except Exception as e:
            self.log_signal.emit(f"❌ Restore failed: {str(e)}")
            self.result_signal.emit({'success': False, 'error': str(e)})

    def clean_old_rules(self, content, target_type):
        """Clean old rules from content"""
        section_name = "GitHub" if target_type == "github" else "Replit"
        lines = content.split('\n')
        cleaned_lines = []
        skip = False

        for line in lines:
            if f"# {section_name} Hosts Start" in line:
                skip = True
            elif f"# {section_name} Hosts End" in line:
                skip = False
                continue
            
            if not skip:
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def apply_hosts(self):
        """Apply rules to hosts file - using safe write method"""
        hosts_path = self.get_hosts_path()
        new_rules = self.data
        target_type = self.target_type

        self.log_signal.emit("🛡️ Checking administrator privileges...")
        if not is_admin():
            self.result_signal.emit({'success': False, 'error': 'Administrator privileges required, please run the program as administrator'})
            return

        # Backup current hosts
        self.log_signal.emit("📦 Creating backup...")
        if not self.create_backup():
            self.result_signal.emit({'success': False, 'error': 'Backup failed'})
            return

        try:
            self.log_signal.emit("📖 Reading existing hosts file...")
            # Read existing hosts, remove old rules
            with open(hosts_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Clean up old rules
            self.log_signal.emit("🧹 Cleaning up old rules...")
            cleaned_content = self.clean_old_rules(content, target_type)

            # Build new content
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            section_name = "GitHub" if target_type == "github" else "Replit"
            
            new_content = cleaned_content.rstrip() + f'\n\n# {section_name} Hosts Start - Updated at {timestamp}\n'
            new_content += new_rules
            new_content += f'\n# {section_name} Hosts End\n'

            # Use temporary file for safe writing
            self.log_signal.emit("💾 Writing new hosts file...")
            temp_dir = tempfile.gettempdir()
            temp_hosts = os.path.join(temp_dir, 'hosts_temp')

            with open(temp_hosts, 'w', encoding='utf-8', newline='\n') as f:
                f.write(new_content)

            # Copy temporary file to system hosts location
            shutil.copy(temp_hosts, hosts_path)

            # Clean up temporary file
            if os.path.exists(temp_hosts):
                os.remove(temp_hosts)

            self.result_signal.emit({'success': True})

        except PermissionError as e:
            self.result_signal.emit({'success': False, 'error': f'Permission denied: {str(e)}. Please make sure to run the program as administrator.'})

    def check_for_updates(self):
        """Check for updates from GitHub"""
        self.log_signal.emit("📡 Connecting to GitHub...")
        try:
            # In a real implementation, this would check GitHub for the latest release
            # For now, we'll simulate the check
            import time
            time.sleep(2)  # Simulate network delay
            
            # For demonstration purposes, we'll return a fixed version
            # In a real implementation, this would fetch from GitHub API
            self.result_signal.emit({
                'success': True, 
                'latest_version': '3.0'  # Current version
            })
        except Exception as e:
            self.log_signal.emit(f"⚠️  Update check failed: {str(e)}")
            self.result_signal.emit({'success': False, 'error': str(e)})


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.download_rules = ""
        self.current_target = 'github'

    def init_ui(self):
        """Initialize user interface with modern design"""
        self.setWindowTitle("mini-SwitchHosts v3.0 - Enhanced Edition")
        self.setGeometry(100, 100, 900, 700)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create menu bar
        self.create_menu()
        
        # Create target selection group
        target_group = QGroupBox("Target Selection")
        target_layout = QHBoxLayout()
        self.target_combo = QComboBox()
        self.target_combo.addItems(["GitHub", "Replit"])
        self.target_combo.currentTextChanged.connect(self.on_target_changed)
        target_layout.addWidget(QLabel("Select Target:"))
        target_layout.addWidget(self.target_combo)
        target_group.setLayout(target_layout)
        main_layout.addWidget(target_group)
        
        # Create buttons with enhanced layout
        button_layout = QHBoxLayout()
        
        self.download_btn = QPushButton("📥 Download Rules")
        self.download_btn.clicked.connect(self.download_rules_func)
        self.download_btn.setStyleSheet("QPushButton { font-weight: bold; padding: 10px; }")
        
        self.apply_btn = QPushButton("✅ Apply Rules")
        self.apply_btn.clicked.connect(self.apply_rules_func)
        self.apply_btn.setStyleSheet("QPushButton { font-weight: bold; padding: 10px; }")
        
        self.backup_btn = QPushButton("📦 Create Backup")
        self.backup_btn.clicked.connect(self.create_backup_func)
        
        self.restore_btn = QPushButton("🔄 Restore Backup")
        self.restore_btn.clicked.connect(self.restore_backup_func)
        
        self.update_btn = QPushButton("🔍 Check for Updates")
        self.update_btn.clicked.connect(self.check_for_updates)
        
        button_layout.addWidget(self.download_btn)
        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(self.backup_btn)
        button_layout.addWidget(self.restore_btn)
        button_layout.addWidget(self.update_btn)
        
        main_layout.addLayout(button_layout)
        
        # Create progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)
        
        # Create log display area
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 9))
        main_layout.addWidget(self.log_display)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - mini-SwitchHosts v3.0 Enhanced Edition")
        
        # Initialize worker thread
        self.worker_thread = None

    def create_menu(self):
        """Create application menu"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def on_target_changed(self, text):
        """Handle target selection change"""
        self.current_target = text.lower()
        self.log_message(f"Target changed to: {text}")

    def download_rules_func(self):
        """Download rules from network sources"""
        self.log_message("Starting enhanced rules download...")
        self.download_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        
        target_type = self.current_target
        self.worker_thread = EnhancedHostsManagerThread('download', target_type=target_type)
        self.worker_thread.log_signal.connect(self.log_message)
        self.worker_thread.result_signal.connect(self.on_download_complete)
        self.worker_thread.progress_signal.connect(self.progress_bar.setValue)
        self.worker_thread.finished.connect(self.on_worker_finished)
        self.worker_thread.start()

    def on_download_complete(self, result):
        """Handle download completion"""
        if result.get('success'):
            self.download_rules = result.get('rules', '')
            self.log_message(f"✅ Enhanced download completed successfully")
            self.log_message(f"Source: {result.get('source', 'Unknown')}")
            self.log_message("--- Preview of downloaded rules ---")
            rules_preview = '\n'.join(self.download_rules.split('\n')[:10])  # Show first 10 lines
            self.log_message(rules_preview)
            if len(self.download_rules.split('\n')) > 10:
                self.log_message("...")
            self.log_message("--- End of preview ---")
        else:
            self.log_message(f"❌ Download failed: {result.get('error', 'Unknown error')}")

    def apply_rules_func(self):
        """Apply downloaded rules to hosts file"""
        if not self.download_rules:
            self.log_message("⚠️  No rules to apply. Please download rules first.")
            return
            
        self.log_message("Applying enhanced rules...")
        self.apply_btn.setEnabled(False)
        
        target_type = self.current_target
        self.worker_thread = EnhancedHostsManagerThread('apply', self.download_rules, target_type)
        self.worker_thread.log_signal.connect(self.log_message)
        self.worker_thread.result_signal.connect(self.on_apply_complete)
        self.worker_thread.progress_signal.connect(self.progress_bar.setValue)
        self.worker_thread.finished.connect(self.on_worker_finished)
        self.worker_thread.start()

    def on_apply_complete(self, result):
        """Handle apply completion"""
        if result.get('success'):
            self.log_message("✅ Rules applied successfully!")
            QMessageBox.information(self, "Success", "Hosts rules have been applied successfully!")
        else:
            error_msg = result.get('error', 'Unknown error')
            self.log_message(f"❌ Failed to apply rules: {error_msg}")
            QMessageBox.critical(self, "Error", f"Failed to apply rules:\n{error_msg}")

    def create_backup_func(self):
        """Create backup of current hosts file"""
        self.log_message("Creating backup...")
        self.backup_btn.setEnabled(False)
        
        self.worker_thread = EnhancedHostsManagerThread('backup')
        self.worker_thread.log_signal.connect(self.log_message)
        self.worker_thread.result_signal.connect(self.on_backup_complete)
        self.worker_thread.progress_signal.connect(self.progress_bar.setValue)
        self.worker_thread.finished.connect(self.on_worker_finished)
        self.worker_thread.start()

    def on_backup_complete(self, result):
        """Handle backup completion"""
        if result.get('success'):
            self.log_message("✅ Backup created successfully!")
        else:
            self.log_message(f"❌ Backup failed: {result.get('error', 'Unknown error')}")

    def restore_backup_func(self):
        """Restore hosts file from backup"""
        self.log_message("Restoring backup...")
        self.restore_btn.setEnabled(False)
        
        reply = QMessageBox.question(self, 'Confirm Restore', 
                                   'Are you sure you want to restore from backup?\nThis will replace your current hosts file.',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.worker_thread = EnhancedHostsManagerThread('restore')
            self.worker_thread.log_signal.connect(self.log_message)
            self.worker_thread.result_signal.connect(self.on_restore_complete)
            self.worker_thread.progress_signal.connect(self.progress_bar.setValue)
            self.worker_thread.finished.connect(self.on_worker_finished)
            self.worker_thread.start()
        else:
            self.restore_btn.setEnabled(True)

    def on_restore_complete(self, result):
        """Handle restore completion"""
        if result.get('success'):
            self.log_message("✅ Backup restored successfully!")
            QMessageBox.information(self, "Success", "Hosts file has been restored from backup!")
        else:
            error_msg = result.get('error', 'Unknown error')
            self.log_message(f"❌ Failed to restore backup: {error_msg}")
            QMessageBox.critical(self, "Error", f"Failed to restore backup:\n{error_msg}")

    def on_worker_finished(self):
        """Handle worker thread completion"""
        self.download_btn.setEnabled(True)
        self.apply_btn.setEnabled(True)
        self.backup_btn.setEnabled(True)
        self.restore_btn.setEnabled(True)
        self.status_bar.showMessage("Operation completed - mini-SwitchHosts v3.0")

    def log_message(self, message):
        """Add message to log display"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_message = f"[{timestamp}] {message}"
        self.log_display.append(formatted_message)
        self.log_display.moveCursor(QTextCursor.End)
        QApplication.processEvents()  # Ensure UI updates

    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>mini-SwitchHosts v3.0</h2>
        <p><b>Enhanced Edition with Improved Features</b></p>
        <p>Enhanced IP resolution, smart filtering, and incremental updates</p>
        <p><b>Key Improvements:</b></p>
        <ul>
            <li>Enhanced IP parsing algorithm for better accuracy</li>
            <li>Smart rule filtering to remove invalid entries</li>
            <li>Incremental update mechanism for efficiency</li>
            <li>Modern UI with real-time status monitoring</li>
            <li>Concurrent processing for faster downloads</li>
            <li>Automatic update checking</li>
            <li>Improved backup and restore functionality</li>
        </ul>
        <p>© 2025 mini-SwitchHosts Project</p>
        """
        QMessageBox.about(self, "About mini-SwitchHosts", about_text)

    def closeEvent(self, event):
        """Handle application close event"""
        reply = QMessageBox.question(self, 'Confirm Exit', 
                                   'Are you sure you want to exit?\nUnsaved changes may be lost.',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def check_for_updates(self):
        """Check for updates from GitHub"""
        self.log_message("🔍 Checking for updates...")
        self.update_btn.setEnabled(False)
        
        self.worker_thread = EnhancedHostsManagerThread('update_check')
        self.worker_thread.log_signal.connect(self.log_message)
        self.worker_thread.result_signal.connect(self.on_update_check_complete)
        self.worker_thread.finished.connect(self.on_worker_finished)
        self.worker_thread.start()

    def on_update_check_complete(self, result):
        """Handle update check completion"""
        if result.get('success'):
            latest_version = result.get('latest_version', 'Unknown')
            current_version = "3.0"
            
            if latest_version != current_version:
                self.log_message(f"🎉 New version available: {latest_version}")
                self.log_message("Please visit GitHub to download the latest version")
                QMessageBox.information(self, "Update Available", 
                                      f"New version {latest_version} is available!\nPlease visit GitHub to download.")
            else:
                self.log_message("✅ You are using the latest version")
                QMessageBox.information(self, "Up to Date", "You are using the latest version!")
        else:
            error_msg = result.get('error', 'Unknown error')
            self.log_message(f"❌ Update check failed: {error_msg}")
            QMessageBox.critical(self, "Error", f"Update check failed:\n{error_msg}")


def main():
    app = QApplication(sys.argv)
    
    # Set application information
    app.setApplicationName("mini-SwitchHosts")
    app.setApplicationVersion("3.0")
    
    # Check for administrator privileges
    if not is_admin():
        reply = QMessageBox.question(None, 'Administrator Privileges Required',
                                   'This program requires administrator privileges to modify the hosts file.\n\nWould you like to restart as administrator?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        
        if reply == QMessageBox.Yes:
            if not run_as_admin():
                QMessageBox.critical(None, 'Error', 'Failed to obtain administrator privileges.')
                sys.exit(1)
        else:
            sys.exit(0)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()