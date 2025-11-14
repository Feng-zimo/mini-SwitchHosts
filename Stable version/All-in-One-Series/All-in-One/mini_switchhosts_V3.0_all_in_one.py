#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PySide6 All-in-One GitHub & Replit Hosts Manager v3.0
Function: Update, backup, and restore GitHub and Replit related hosts rules
Supports Windows, Linux, and macOS with multilingual interface
"""

import sys
import os
import requests
import shutil
import ctypes
import tempfile
import threading
import platform
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QTextEdit, QPushButton, QLabel,
                               QMessageBox, QFileDialog, QSplitter, QProgressBar,
                               QComboBox, QStatusBar, QGroupBox, QTabWidget)
from PySide6.QtCore import Qt, QThread, Signal as pyqtSignal, QTimer
from PySide6.QtGui import QFont, QTextCursor, QAction, QIcon


def is_admin():
    """Check if the program has administrator privileges"""
    try:
        if platform.system().lower() == 'windows':
            return ctypes.windll.shell32.IsUserAnAdmin()
        else:
            return os.geteuid() == 0
    except:
        return False


def run_as_admin():
    """Run the program with administrator privileges"""
    if not is_admin():
        if platform.system().lower() == 'windows':
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        else:
            # For Linux/macOS, suggest using sudo
            QMessageBox.critical(None, 'Administrator Privileges Required',
                               'This program requires administrator privileges. Please run with sudo.')
        return False
    return True


def get_system_language():
    """Get system default language"""
    import locale
    try:
        lang, _ = locale.getdefaultlocale()
        if lang:
            return lang.split('_')[0].lower()
    except:
        pass
    return 'en'


class EnhancedHostsManagerThread(QThread):
    """Enhanced background thread with concurrent processing"""
    log_signal = pyqtSignal(str)
    result_signal = pyqtSignal(dict)
    progress_signal = pyqtSignal(int)

    def __init__(self, task_type, data=None, target_type='github', language='en'):
        super().__init__()
        self.task_type = task_type  # 'download', 'apply', 'backup', 'restore', 'incremental'
        self.data = data
        self.target_type = target_type
        self.language = language

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
            self.log_signal.emit(f"❌ Error: {str(e)}" if self.language == 'en' else f"❌ 错误: {str(e)}")

    def download_hosts_enhanced(self):
        """Enhanced download with smart filtering and concurrent requests"""
        msg = "📡 Connecting to servers with enhanced protocol..." if self.language == 'en' else "📡 使用增强协议连接服务器..."
        self.log_signal.emit(msg)
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
                host = source.split('//')[1].split('/')[0]
                msg = f"🔄 Fetching from {host}..." if self.language == 'en' else f"🔄 正在从 {host} 获取..."
                self.log_signal.emit(msg)
                response = requests.get(source, timeout=15)
                if response.status_code == 200:
                    results[index] = response.text
            except Exception as e:
                msg = f"⚠️  {source} failed: {str(e)}" if self.language == 'en' else f"⚠️  {source} 失败: {str(e)}"
                self.log_signal.emit(msg)

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
            source_msg = "Source" if self.language == 'en' else "来源"
            success_msg = "✅ Enhanced download completed successfully" if self.language == 'en' else "✅ 增强版下载成功完成"
            self.result_signal.emit({'success': True, 'rules': rules, 'source': sources[0], 'message': f"{success_msg}\n{source_msg}: {sources[0]}"})
        else:
            error_msg = "All sources failed" if self.language == 'en' else "所有源都尝试失败"
            self.result_signal.emit({'success': False, 'error': error_msg})

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

        not_found_msg = "# GitHub related rules not found" if self.language == 'en' else "# 未找到GitHub相关规则"
        return '\n'.join(github_rules) if github_rules else not_found_msg

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

        not_found_msg = "# Replit related rules not found" if self.language == 'en' else "# 未找到Replit相关规则"
        return '\n'.join(replit_rules) if replit_rules else not_found_msg

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
        msg = "🔄 Performing incremental update..." if self.language == 'en' else "🔄 执行增量更新..."
        self.log_signal.emit(msg)
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
                detect_msg = "🔍 Changes detected, applying update..." if self.language == 'en' else "🔍 检测到变更，正在应用更新..."
                self.log_signal.emit(detect_msg)
                self.apply_hosts()
            else:
                up_to_date_msg = "✅ No changes detected, hosts file is up to date" if self.language == 'en' else "✅ 未检测到变更，hosts文件已为最新"
                self.log_signal.emit(up_to_date_msg)
            
            self.result_signal.emit({'success': True})
        except Exception as e:
            fail_msg = f"❌ Incremental update failed: {str(e)}" if self.language == 'en' else f"❌ 增量更新失败: {str(e)}"
            self.log_signal.emit(fail_msg)
            self.result_signal.emit({'success': False, 'error': str(e)})

    def get_hosts_path(self):
        """Get system hosts file path"""
        system = platform.system().lower()
        if system == 'windows':
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
            backup_msg = f"✅ Backup created: {backup_path}" if self.language == 'en' else f"✅ 备份已创建: {backup_path}"
            self.log_signal.emit(backup_msg)
            return True
        except Exception as e:
            fail_msg = f"❌ Backup failed: {str(e)}" if self.language == 'en' else f"❌ 备份失败: {str(e)}"
            self.log_signal.emit(fail_msg)
            return False

    def restore_backup(self):
        """Restore hosts file from backup"""
        restore_msg = "🔄 Restoring from backup..." if self.language == 'en' else "🔄 从备份恢复..."
        self.log_signal.emit(restore_msg)
        try:
            # Get backup directory
            backup_dir = os.path.join(os.path.expanduser('~'), 'HostsBackups')
            
            if not os.path.exists(backup_dir):
                not_found_msg = "❌ Backup directory not found" if self.language == 'en' else "❌ 未找到备份目录"
                self.log_signal.emit(not_found_msg)
                self.result_signal.emit({'success': False, 'error': 'Backup directory not found' if self.language == 'en' else '未找到备份目录'})
                return
            
            # List all backup files
            backups = [f for f in os.listdir(backup_dir) if f.startswith('hosts_backup_')]
            if not backups:
                no_backup_msg = "❌ No backup files found" if self.language == 'en' else "❌ 未找到备份文件"
                self.log_signal.emit(no_backup_msg)
                self.result_signal.emit({'success': False, 'error': 'No backup files found' if self.language == 'en' else '未找到备份文件'})
                return
            
            # Sort by timestamp to get the latest
            backups.sort(reverse=True)
            latest_backup = backups[0]
            backup_path = os.path.join(backup_dir, latest_backup)
            
            # Restore the backup
            hosts_path = self.get_hosts_path()
            shutil.copy(backup_path, hosts_path)
            
            success_msg = f"✅ Backup restored successfully from {latest_backup}" if self.language == 'en' else f"✅ 成功从 {latest_backup} 恢复备份"
            self.log_signal.emit(success_msg)
            self.result_signal.emit({'success': True})
        except Exception as e:
            fail_msg = f"❌ Restore failed: {str(e)}" if self.language == 'en' else f"❌ 恢复失败: {str(e)}"
            self.log_signal.emit(fail_msg)
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

        admin_msg = "🛡️ Checking administrator privileges..." if self.language == 'en' else "🛡️ 检查管理员权限..."
        self.log_signal.emit(admin_msg)
        if not is_admin():
            error_msg = "Administrator privileges required, please run the program as administrator" if self.language == 'en' else "需要管理员权限，请以管理员身份运行程序"
            self.result_signal.emit({'success': False, 'error': error_msg})
            return

        # Backup current hosts
        backup_msg = "📦 Creating backup..." if self.language == 'en' else "📦 创建备份..."
        self.log_signal.emit(backup_msg)
        if not self.create_backup():
            fail_msg = "Backup failed" if self.language == 'en' else "备份失败"
            self.result_signal.emit({'success': False, 'error': fail_msg})
            return

        try:
            reading_msg = "📖 Reading existing hosts file..." if self.language == 'en' else "📖 读取现有hosts文件..."
            self.log_signal.emit(reading_msg)
            # Read existing hosts, remove old rules
            with open(hosts_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Clean up old rules
            cleaning_msg = "🧹 Cleaning up old rules..." if self.language == 'en' else "🧹 清理旧规则..."
            self.log_signal.emit(cleaning_msg)
            cleaned_content = self.clean_old_rules(content, target_type)

            # Build new content
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            section_name = "GitHub" if target_type == "github" else "Replit"
            
            new_content = cleaned_content.rstrip() + f'\n\n# {section_name} Hosts Start - Updated at {timestamp}\n'
            new_content += new_rules
            new_content += f'\n# {section_name} Hosts End\n'

            # Use temporary file for safe writing
            writing_msg = "💾 Writing new hosts file..." if self.language == 'en' else "💾 写入新hosts文件..."
            self.log_signal.emit(writing_msg)
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
            perm_msg = f"Permission denied: {str(e)}. Please make sure to run the program as administrator." if self.language == 'en' else f"权限拒绝: {str(e)}。请确保以管理员身份运行程序。"
            self.result_signal.emit({'success': False, 'error': perm_msg})
        except Exception as e:
            write_msg = f"Write failed: {str(e)}" if self.language == 'en' else f"写入失败: {str(e)}"
            self.result_signal.emit({'success': False, 'error': write_msg})

    def check_for_updates(self):
        """Check for updates from GitHub"""
        connecting_msg = "📡 Connecting to GitHub..." if self.language == 'en' else "📡 正在连接GitHub..."
        self.log_signal.emit(connecting_msg)
        try:
            # In a real implementation, this would check GitHub for the latest release
            # For now, we'll simulate the check
            import time
            time.sleep(2)  # Simulate network delay
            
            # For demonstration purposes, we'll return a fixed version
            # In a real implementation, this would fetch from GitHub API
            self.result_signal.emit({
                'success': True, 
                'latest_version': '3.0 All-in-One'  # Current version
            })
        except Exception as e:
            fail_msg = f"⚠️  Update check failed: {str(e)}" if self.language == 'en' else f"⚠️  更新检查失败: {str(e)}"
            self.log_signal.emit(fail_msg)
            self.result_signal.emit({'success': False, 'error': str(e)})


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.language = get_system_language()  # Auto-detect system language
        self.init_ui()
        self.download_rules = ""
        self.current_target = 'github'

    def init_ui(self):
        """Initialize user interface with modern design"""
        title = "mini-SwitchHosts v3.0 All-in-One - Enhanced Edition" if self.language == 'en' else "mini-SwitchHosts v3.0 一体化增强版"
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 900, 700)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create menu bar
        self.create_menu()
        
        # Create target selection group
        target_group_text = "Target Selection" if self.language == 'en' else "目标选择"
        target_group = QGroupBox(target_group_text)
        target_layout = QHBoxLayout()
        self.target_combo = QComboBox()
        github_text = "GitHub"
        replit_text = "Replit"
        self.target_combo.addItems([github_text, replit_text])
        self.target_combo.currentTextChanged.connect(self.on_target_changed)
        select_target_text = "Select Target:" if self.language == 'en' else "选择目标:"
        target_layout.addWidget(QLabel(select_target_text))
        target_layout.addWidget(self.target_combo)
        target_group.setLayout(target_layout)
        main_layout.addWidget(target_group)
        
        # Create buttons with enhanced layout
        button_layout = QHBoxLayout()
        
        download_text = "📥 Download Rules" if self.language == 'en' else "📥 下载规则"
        self.download_btn = QPushButton(download_text)
        self.download_btn.clicked.connect(self.download_rules_func)
        self.download_btn.setStyleSheet("QPushButton { font-weight: bold; padding: 10px; }")
        
        apply_text = "✅ Apply Rules" if self.language == 'en' else "✅ 应用规则"
        self.apply_btn = QPushButton(apply_text)
        self.apply_btn.clicked.connect(self.apply_rules_func)
        self.apply_btn.setStyleSheet("QPushButton { font-weight: bold; padding: 10px; }")
        
        backup_text = "📦 Create Backup" if self.language == 'en' else "📦 创建备份"
        self.backup_btn = QPushButton(backup_text)
        self.backup_btn.clicked.connect(self.create_backup_func)
        
        restore_text = "🔄 Restore Backup" if self.language == 'en' else "🔄 恢复备份"
        self.restore_btn = QPushButton(restore_text)
        self.restore_btn.clicked.connect(self.restore_backup_func)
        
        update_text = "🔍 Check for Updates" if self.language == 'en' else "🔍 检查更新"
        self.update_btn = QPushButton(update_text)
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
        status_text = "Ready - mini-SwitchHosts v3.0 All-in-One Enhanced Edition" if self.language == 'en' else "就绪 - mini-SwitchHosts v3.0 一体化增强版"
        self.status_bar.showMessage(status_text)
        
        # Initialize worker thread
        self.worker_thread = None
        
        # Log startup message
        start_msg = "🚀 mini-SwitchHosts v3.0 All-in-One started" if self.language == 'en' else "🚀 mini-SwitchHosts v3.0 一体化版本已启动"
        self.log_message(start_msg)

    def create_menu(self):
        """Create application menu"""
        menubar = self.menuBar()
        
        # File menu
        file_text = "File" if self.language == 'en' else "文件"
        file_menu = menubar.addMenu(file_text)
        
        exit_text = "Exit" if self.language == 'en' else "退出"
        exit_action = QAction(exit_text, self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Language menu
        lang_text = "Language" if self.language == 'en' else "语言"
        lang_menu = menubar.addMenu(lang_text)
        
        en_action = QAction("English", self)
        en_action.triggered.connect(lambda: self.change_language('en'))
        lang_menu.addAction(en_action)
        
        zh_action = QAction("中文", self)
        zh_action.triggered.connect(lambda: self.change_language('zh'))
        lang_menu.addAction(zh_action)
        
        # Help menu
        help_text = "Help" if self.language == 'en' else "帮助"
        help_menu = menubar.addMenu(help_text)
        
        about_text = "About" if self.language == 'en' else "关于"
        about_action = QAction(about_text, self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def change_language(self, lang):
        """Change application language"""
        self.language = lang
        self.init_ui()

    def on_target_changed(self, text):
        """Handle target selection change"""
        self.current_target = text.lower()
        target_msg = f"Target changed to: {text}" if self.language == 'en' else f"目标已更改为: {text}"
        self.log_message(target_msg)

    def download_rules_func(self):
        """Download rules from network sources"""
        download_msg = "Starting enhanced rules download..." if self.language == 'en' else "开始增强版规则下载..."
        self.log_message(download_msg)
        self.download_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        
        target_type = self.current_target
        self.worker_thread = EnhancedHostsManagerThread('download', target_type=target_type, language=self.language)
        self.worker_thread.log_signal.connect(self.log_message)
        self.worker_thread.result_signal.connect(self.on_download_complete)
        self.worker_thread.progress_signal.connect(self.progress_bar.setValue)
        self.worker_thread.finished.connect(self.on_worker_finished)
        self.worker_thread.start()

    def on_download_complete(self, result):
        """Handle download completion"""
        if result.get('success'):
            self.download_rules = result.get('rules', '')
            message = result.get('message', '')
            if message:
                self.log_message(message)
            else:
                success_msg = "✅ Enhanced download completed successfully" if self.language == 'en' else "✅ 增强版下载成功完成"
                source_msg = result.get('source', 'Unknown')
                source_text = "Source" if self.language == 'en' else "来源"
                self.log_message(f"{success_msg}\n{source_text}: {source_msg}")
            
            # Show preview of rules
            preview_text = "--- Preview of downloaded rules ---" if self.language == 'en' else "--- 下载规则预览 ---"
            self.log_message(preview_text)
            rules_preview = '\n'.join(self.download_rules.split('\n')[:10])  # Show first 10 lines
            self.log_message(rules_preview)
            if len(self.download_rules.split('\n')) > 10:
                self.log_message("...")
            end_preview_text = "--- End of preview ---" if self.language == 'en' else "--- 预览结束 ---"
            self.log_message(end_preview_text)
        else:
            fail_text = "❌ Download failed" if self.language == 'en' else "❌ 下载失败"
            error_msg = result.get('error', 'Unknown error')
            self.log_message(f"{fail_text}: {error_msg}")

    def apply_rules_func(self):
        """Apply downloaded rules to hosts file"""
        if not self.download_rules:
            no_rules_text = "⚠️  No rules to apply. Please download rules first." if self.language == 'en' else "⚠️  没有可应用的规则。请先下载规则。"
            self.log_message(no_rules_text)
            return
            
        applying_text = "Applying enhanced rules..." if self.language == 'en' else "正在应用增强版规则..."
        self.log_message(applying_text)
        self.apply_btn.setEnabled(False)
        
        target_type = self.current_target
        self.worker_thread = EnhancedHostsManagerThread('apply', self.download_rules, target_type, self.language)
        self.worker_thread.log_signal.connect(self.log_message)
        self.worker_thread.result_signal.connect(self.on_apply_complete)
        self.worker_thread.progress_signal.connect(self.progress_bar.setValue)
        self.worker_thread.finished.connect(self.on_worker_finished)
        self.worker_thread.start()

    def on_apply_complete(self, result):
        """Handle apply completion"""
        if result.get('success'):
            success_text = "✅ Rules applied successfully!" if self.language == 'en' else "✅ 规则应用成功!"
            self.log_message(success_text)
            title = "Success" if self.language == 'en' else "成功"
            message = "Hosts rules have been applied successfully!" if self.language == 'en' else "Hosts规则已成功应用!"
            QMessageBox.information(self, title, message)
        else:
            fail_text = "❌ Failed to apply rules" if self.language == 'en' else "❌ 规则应用失败"
            error_msg = result.get('error', 'Unknown error')
            self.log_message(f"{fail_text}: {error_msg}")
            title = "Error" if self.language == 'en' else "错误"
            QMessageBox.critical(self, title, f"{fail_text}:\n{error_msg}")

    def create_backup_func(self):
        """Create backup of current hosts file"""
        backup_text = "Creating backup..." if self.language == 'en' else "正在创建备份..."
        self.log_message(backup_text)
        self.backup_btn.setEnabled(False)
        
        self.worker_thread = EnhancedHostsManagerThread('backup', language=self.language)
        self.worker_thread.log_signal.connect(self.log_message)
        self.worker_thread.result_signal.connect(self.on_backup_complete)
        self.worker_thread.progress_signal.connect(self.progress_bar.setValue)
        self.worker_thread.finished.connect(self.on_worker_finished)
        self.worker_thread.start()

    def on_backup_complete(self, result):
        """Handle backup completion"""
        if result.get('success'):
            success_text = "✅ Backup created successfully!" if self.language == 'en' else "✅ 备份创建成功!"
            self.log_message(success_text)
        else:
            fail_text = "❌ Backup failed" if self.language == 'en' else "❌ 备份失败"
            error_msg = result.get('error', 'Unknown error')
            self.log_message(f"{fail_text}: {error_msg}")

    def restore_backup_func(self):
        """Restore hosts file from backup"""
        restore_text = "Restoring backup..." if self.language == 'en' else "正在恢复备份..."
        self.log_message(restore_text)
        self.restore_btn.setEnabled(False)
        
        confirm_title = "Confirm Restore" if self.language == 'en' else "确认恢复"
        confirm_msg = "Are you sure you want to restore from backup?\nThis will replace your current hosts file." if self.language == 'en' else "确定要从备份恢复吗?\n这将替换您当前的hosts文件。"
        reply = QMessageBox.question(self, confirm_title, confirm_msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.worker_thread = EnhancedHostsManagerThread('restore', language=self.language)
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
            success_text = "✅ Backup restored successfully!" if self.language == 'en' else "✅ 备份恢复成功!"
            self.log_message(success_text)
            title = "Success" if self.language == 'en' else "成功"
            message = "Hosts file has been restored from backup!" if self.language == 'en' else "Hosts文件已从备份恢复!"
            QMessageBox.information(self, title, message)
        else:
            fail_text = "❌ Failed to restore backup" if self.language == 'en' else "❌ 备份恢复失败"
            error_msg = result.get('error', 'Unknown error')
            self.log_message(f"{fail_text}: {error_msg}")
            title = "Error" if self.language == 'en' else "错误"
            QMessageBox.critical(self, title, f"{fail_text}:\n{error_msg}")

    def check_for_updates(self):
        """Check for updates from GitHub"""
        update_text = "🔍 Checking for updates..." if self.language == 'en' else "🔍 正在检查更新..."
        self.log_message(update_text)
        self.update_btn.setEnabled(False)
        
        self.worker_thread = EnhancedHostsManagerThread('update_check', language=self.language)
        self.worker_thread.log_signal.connect(self.log_message)
        self.worker_thread.result_signal.connect(self.on_update_check_complete)
        self.worker_thread.finished.connect(self.on_worker_finished)
        self.worker_thread.start()

    def on_update_check_complete(self, result):
        """Handle update check completion"""
        if result.get('success'):
            latest_version = result.get('latest_version', 'Unknown')
            current_version = "3.0 All-in-One"
            
            if latest_version != current_version:
                new_ver_text = f"🎉 New version available: {latest_version}" if self.language == 'en' else f"🎉 发现新版本: {latest_version}"
                self.log_message(new_ver_text)
                visit_text = "Please visit GitHub to download the latest version" if self.language == 'en' else "请访问GitHub下载最新版本"
                self.log_message(visit_text)
                title = "Update Available" if self.language == 'en' else "发现更新"
                message = f"New version {latest_version} is available!\nPlease visit GitHub to download." if self.language == 'en' else f"新版本 {latest_version} 已发布!\n请访问GitHub下载最新版本。"
                QMessageBox.information(self, title, message)
            else:
                up_to_date_text = "✅ You are using the latest version" if self.language == 'en' else "✅ 您使用的是最新版本"
                self.log_message(up_to_date_text)
                title = "Up to Date" if self.language == 'en' else "已是最新"
                message = "You are using the latest version!" if self.language == 'en' else "您使用的是最新版本!"
                QMessageBox.information(self, title, message)
        else:
            fail_text = "❌ Update check failed" if self.language == 'en' else "❌ 更新检查失败"
            error_msg = result.get('error', 'Unknown error')
            self.log_message(f"{fail_text}: {error_msg}")
            title = "Error" if self.language == 'en' else "错误"
            QMessageBox.critical(self, title, f"{fail_text}:\n{error_msg}")

    def on_worker_finished(self):
        """Handle worker thread completion"""
        self.download_btn.setEnabled(True)
        self.apply_btn.setEnabled(True)
        self.backup_btn.setEnabled(True)
        self.restore_btn.setEnabled(True)
        self.update_btn.setEnabled(True)
        status_text = "Operation completed - mini-SwitchHosts v3.0 All-in-One" if self.language == 'en' else "操作完成 - mini-SwitchHosts v3.0 一体化"
        self.status_bar.showMessage(status_text)

    def log_message(self, message):
        """Add message to log display"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_message = f"[{timestamp}] {message}"
        self.log_display.append(formatted_message)
        self.log_display.moveCursor(QTextCursor.End)
        QApplication.processEvents()  # Ensure UI updates

    def show_about(self):
        """Show about dialog"""
        if self.language == 'en':
            about_text = """
            <h2>mini-SwitchHosts v3.0 All-in-One</h2>
            <p><b>Enhanced Edition with Improved Features</b></p>
            <p>Enhanced IP resolution, smart filtering, and incremental updates</p>
            <p><b>Key Improvements:</b></p>
            <ul>
                <li>Enhanced IP parsing algorithm for better accuracy</li>
                <li>Smart rule filtering to remove invalid entries</li>
                <li>Incremental update mechanism for efficiency</li>
                <li>Modern UI with real-time status monitoring</li>
                <li>Concurrent processing for faster downloads</li>
                <li>Multi-language support (English and Chinese)</li>
                <li>Cross-platform compatibility (Windows, Linux, macOS)</li>
            </ul>
            <p>© 2025 mini-SwitchHosts Project</p>
            """
        else:
            about_text = """
            <h2>mini-SwitchHosts v3.0 一体化版本</h2>
            <p><b>增强版，包含改进功能</b></p>
            <p>增强的IP解析、智能过滤和增量更新</p>
            <p><b>主要改进:</b></p>
            <ul>
                <li>增强的IP解析算法，提高准确性</li>
                <li>智能规则过滤，去除无效条目</li>
                <li>增量更新机制，提高效率</li>
                <li>现代化UI，支持实时状态监控</li>
                <li>并发处理，加快下载速度</li>
                <li>多语言支持（英文和中文）</li>
                <li>跨平台兼容性（Windows、Linux、macOS）</li>
            </ul>
            <p>© 2025 mini-SwitchHosts 项目</p>
            """
        title = "About mini-SwitchHosts" if self.language == 'en' else "关于 mini-SwitchHosts"
        QMessageBox.about(self, title, about_text)

    def closeEvent(self, event):
        """Handle application close event"""
        confirm_title = "Confirm Exit" if self.language == 'en' else "确认退出"
        confirm_msg = "Are you sure you want to exit?\nUnsaved changes may be lost." if self.language == 'en' else "确定要退出吗?\n未保存的更改可能会丢失。"
        reply = QMessageBox.question(self, confirm_title, confirm_msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


def main():
    app = QApplication(sys.argv)
    
    # Set application information
    app.setApplicationName("mini-SwitchHosts")
    app.setApplicationVersion("3.0 All-in-One")
    
    # Check for administrator privileges
    if not is_admin():
        if platform.system().lower() == 'windows':
            reply = QMessageBox.question(None, 'Administrator Privileges Required' if get_system_language() == 'en' else '需要管理员权限',
                                       'This program requires administrator privileges to modify the hosts file.\n\nWould you like to restart as administrator?' if get_system_language() == 'en' else '此程序需要管理员权限来修改hosts文件。\n\n是否要以管理员身份重新启动?',
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            
            if reply == QMessageBox.Yes:
                if not run_as_admin():
                    QMessageBox.critical(None, 'Error' if get_system_language() == 'en' else '错误', 
                                       'Failed to obtain administrator privileges.' if get_system_language() == 'en' else '无法获取管理员权限。')
                    sys.exit(1)
            else:
                sys.exit(0)
        else:
            # For Linux/macOS, just show a message
            QMessageBox.critical(None, 'Administrator Privileges Required' if get_system_language() == 'en' else '需要管理员权限',
                               'This program requires administrator privileges. Please run with sudo.' if get_system_language() == 'en' else '此程序需要管理员权限。请使用sudo运行。')
            sys.exit(1)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()