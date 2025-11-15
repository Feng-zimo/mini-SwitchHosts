#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt All-in-One GitHub & Replit Hosts Manager v3.0
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
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QTextEdit, QPushButton, QLabel,
                            QMessageBox, QFileDialog, QSplitter, QProgressBar,
                            QComboBox, QStatusBar, QGroupBox, QTabWidget)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QTextCursor, QAction, QIcon


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
        import re
        ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        return re.match(ip_pattern, ip_str) is not None

    def apply_hosts(self):
        """Apply rules to system hosts file"""
        if not self.data:
            error_msg = "No rules to apply" if self.language == 'en' else "没有规则可应用"
            self.result_signal.emit({'success': False, 'error': error_msg})
            return

        try:
            self.log_signal.emit("🛡️ Checking administrator privileges..." if self.language == 'en' else "🛡️ 检查管理员权限...")
            
            if not is_admin():
                error_msg = "Administrator privileges required" if self.language == 'en' else "需要管理员权限"
                self.result_signal.emit({'success': False, 'error': error_msg})
                return

            hosts_path = self.get_hosts_path()
            self.log_signal.emit(f"📂 Hosts file path: {hosts_path}" if self.language == 'en' else f"📂 Hosts文件路径: {hosts_path}")

            # Create backup first
            self.create_backup_internal(hosts_path)
            
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
            target_name = "GitHub & Replit" if self.language == 'en' else "GitHub和Replit"
            new_lines.append("")
            new_lines.append(section_start_marker)
            new_lines.append(f"# {target_name} Hosts Rules")
            new_lines.append(f"# Updated: {timestamp}")
            new_lines.append(self.data)
            new_lines.append(section_end_marker)
            new_lines.append("")
            
            # Write back to hosts file
            with open(hosts_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write('\n'.join(new_lines))
            
            success_msg = "Rules applied successfully" if self.language == 'en' else "规则应用成功"
            self.result_signal.emit({'success': True, 'message': success_msg})
            
        except PermissionError as e:
            error_msg = f"Permission denied: {str(e)}. Please run as administrator." if self.language == 'en' else f"权限被拒绝: {str(e)}。请以管理员身份运行。"
            self.result_signal.emit({'success': False, 'error': error_msg})
        except Exception as e:
            error_msg = f"Apply failed: {str(e)}" if self.language == 'en' else f"应用失败: {str(e)}"
            self.result_signal.emit({'success': False, 'error': error_msg})

    def get_hosts_path(self):
        """Get hosts file path based on OS"""
        system = platform.system().lower()
        if system == 'windows':
            return r"C:\Windows\System32\drivers\etc\hosts"
        else:
            return "/etc/hosts"

    def create_backup(self):
        """Create backup of current hosts file"""
        try:
            hosts_path = self.get_hosts_path()
            self.create_backup_internal(hosts_path)
            backup_msg = "Backup created successfully" if self.language == 'en' else "备份创建成功"
            self.result_signal.emit({'success': True, 'message': backup_msg})
        except Exception as e:
            error_msg = f"Backup failed: {str(e)}" if self.language == 'en' else f"备份失败: {str(e)}"
            self.result_signal.emit({'success': False, 'error': error_msg})

    def create_backup_internal(self, hosts_path):
        """Internal method to create backup"""
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
        
        backup_created_msg = f"Backup created: {backup_path}" if self.language == 'en' else f"已创建备份: {backup_path}"
        self.log_signal.emit(backup_created_msg)

    def restore_backup(self):
        """Restore hosts file from backup"""
        try:
            self.log_signal.emit("🛡️ Checking administrator privileges..." if self.language == 'en' else "🛡️ 检查管理员权限...")
            
            if not is_admin():
                error_msg = "Administrator privileges required" if self.language == 'en' else "需要管理员权限"
                self.result_signal.emit({'success': False, 'error': error_msg})
                return

            # Let user select backup file
            backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
            
            if self.language == 'en':
                backup_file, _ = QFileDialog.getOpenFileName(
                    None, 'Select Backup File', backup_dir, 'Text Files (*.txt);;All Files (*)')
            else:
                backup_file, _ = QFileDialog.getOpenFileName(
                    None, '选择备份文件', backup_dir, '文本文件 (*.txt);;所有文件 (*)')
            
            if not backup_file:
                cancel_msg = "Operation cancelled" if self.language == 'en' else "操作已取消"
                self.result_signal.emit({'success': False, 'error': cancel_msg})
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

            success_msg = "Backup restored successfully" if self.language == 'en' else "备份恢复成功"
            self.result_signal.emit({'success': True, 'message': success_msg})
        except PermissionError as e:
            error_msg = f"Permission denied: {str(e)}. Please run as administrator." if self.language == 'en' else f"权限被拒绝: {str(e)}。请以管理员身份运行。"
            self.result_signal.emit({'success': False, 'error': error_msg})
        except Exception as e:
            error_msg = f"Restore failed: {str(e)}" if self.language == 'en' else f"恢复失败: {str(e)}"
            self.result_signal.emit({'success': False, 'error': error_msg})

    def incremental_update(self):
        """Perform incremental update"""
        # Placeholder for incremental update functionality
        pass

    def check_for_updates(self):
        """Check for program updates"""
        # Placeholder for update check functionality
        pass


class EnhancedHostsManager(QMainWindow):
    """Enhanced main window with modern UI"""

    def __init__(self):
        super().__init__()
        self.current_rules = ""
        self.current_target = "github"  # Default target
        self.language = get_system_language()  # Auto-detect system language
        self.init_ui()
        self.check_admin_status()
        self.setup_auto_update_check()

    def init_ui(self):
        """Initialize user interface with modern design"""
        window_title = "GitHub & Replit Hosts Manager v3.0 (PyQt Edition)" if self.language == 'en' else "GitHub & Replit Hosts 管理工具 v3.0 (PyQt版)"
        self.setWindowTitle(window_title)
        self.setGeometry(300, 200, 1000, 750)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Title
        title_label = QLabel("GitHub & Replit Hosts One-Click Management Tool" if self.language == 'en' else "GitHub & Replit Hosts 一键管理工具")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("margin: 15px;")
        layout.addWidget(title_label)

        # Top panel with target selection and admin status
        top_panel = QGroupBox()
        top_layout = QHBoxLayout(top_panel)
        
        # Target selection
        target_label = QLabel("Select target:" if self.language == 'en' else "选择目标:")
        self.target_combo = QComboBox()
        self.target_combo.addItem("GitHub", "github")
        self.target_combo.addItem("Replit", "replit")
        self.target_combo.currentTextChanged.connect(self.on_target_changed)
        self.target_combo.setMinimumWidth(150)
        
        # Language selection
        lang_label = QLabel("Language:" if self.language == 'en' else "语言:")
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("English", "en")
        self.lang_combo.addItem("中文", "zh")
        self.lang_combo.setCurrentIndex(0 if self.language == 'en' else 1)
        self.lang_combo.currentIndexChanged.connect(self.on_language_changed)
        self.lang_combo.setMinimumWidth(100)
        
        top_layout.addWidget(target_label)
        top_layout.addWidget(self.target_combo)
        top_layout.addSpacing(20)
        top_layout.addWidget(lang_label)
        top_layout.addWidget(self.lang_combo)
        top_layout.addStretch()
        
        layout.addWidget(top_panel)

        # Administrator status indicator
        self.admin_label = QLabel()
        self.admin_label.setAlignment(Qt.AlignCenter)
        self.admin_label.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(self.admin_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Tab widget for different views
        self.tab_widget = QTabWidget()
        
        # Main tab
        main_tab = QWidget()
        main_layout = QVBoxLayout(main_tab)
        
        # Horizontal layout for buttons
        button_layout = QHBoxLayout()

        # Function buttons with enhanced styling
        self.btn_download = QPushButton("🔄 Update Rules" if self.language == 'en' else "🔄 更新规则")
        self.btn_apply = QPushButton("💾 Apply Rules" if self.language == 'en' else "💾 应用规则")
        self.btn_backup = QPushButton("📦 Create Backup" if self.language == 'en' else "📦 创建备份")
        self.btn_restore = QPushButton("⏪ Restore Backup" if self.language == 'en' else "⏪ 恢复备份")

        self.btn_download.clicked.connect(self.download_rules)
        self.btn_apply.clicked.connect(self.apply_rules)
        self.btn_backup.clicked.connect(self.create_backup)
        self.btn_restore.clicked.connect(self.restore_backup)

        button_layout.addWidget(self.btn_download)
        button_layout.addWidget(self.btn_apply)
        button_layout.addWidget(self.btn_backup)
        button_layout.addWidget(self.btn_restore)

        main_layout.addLayout(button_layout)

        # Splitter for rules display and logs
        splitter = QSplitter(Qt.Vertical)

        # Rules display area
        rules_widget = QWidget()
        rules_layout = QVBoxLayout(rules_widget)
        rules_label = QLabel("Rules Display/Edit Area:" if self.language == 'en' else "规则显示/编辑区域:")
        rules_layout.addWidget(rules_label)

        self.rules_edit = QTextEdit()
        self.rules_edit.setPlaceholderText("Rules will be displayed here..." if self.language == 'en' else "规则将在此处显示...")
        rules_layout.addWidget(self.rules_edit)

        # Log display area
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        log_label = QLabel("Operation Log:" if self.language == 'en' else "操作日志:")
        log_layout.addWidget(log_label)

        self.log_edit = QTextEdit()
        self.log_edit.setPlaceholderText("Operation logs will be displayed here..." if self.language == 'en' else "操作日志将在此处显示...")
        self.log_edit.setMaximumHeight(200)
        self.log_edit.setReadOnly(True)
        log_layout.addWidget(self.log_edit)

        splitter.addWidget(rules_widget)
        splitter.addWidget(log_widget)
        splitter.setSizes([500, 200])

        main_layout.addWidget(splitter)
        self.tab_widget.addTab(main_tab, "Main" if self.language == 'en' else "主页")

        # Settings tab
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        settings_label = QLabel("Settings will be available in future versions" if self.language == 'en' else "设置功能将在未来版本中提供")
        settings_label.setAlignment(Qt.AlignCenter)
        settings_layout.addWidget(settings_label)
        self.tab_widget.addTab(settings_tab, "Settings" if self.language == 'en' else "设置")

        layout.addWidget(self.tab_widget)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready" if self.language == 'en' else "就绪")

        # Menu bar
        self.create_menu()

        # Log startup message
        self.log("🚀 GitHub & Replit Hosts Manager PyQt Edition started" if self.language == 'en' else "🚀 GitHub & Replit Hosts 管理工具 PyQt 版已启动")

    def create_menu(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File' if self.language == 'en' else '文件')
        
        exit_action = QAction('Exit' if self.language == 'en' else '退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help' if self.language == 'en' else '帮助')
        
        about_action = QAction('About' if self.language == 'en' else '关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def on_target_changed(self, text):
        """Handle target type change"""
        self.current_target = self.target_combo.currentData()
        target_name = "GitHub" if self.current_target == "github" else "Replit"
        msg = f"🎯 Switched to {target_name} mode" if self.language == 'en' else f"🎯 已切换到 {target_name} 模式"
        self.log(msg)
        status_msg = f"Current target: {target_name}" if self.language == 'en' else f"当前目标: {target_name}"
        self.status_bar.showMessage(status_msg)

    def on_language_changed(self, index):
        """Handle language change"""
        selected_lang = self.lang_combo.currentData()
        if selected_lang != self.language:
            self.language = selected_lang
            self.update_ui_language()

    def update_ui_language(self):
        """Update UI text based on selected language"""
        # Update window title
        window_title = "GitHub & Replit Hosts Manager v3.0 (PyQt Edition)" if self.language == 'en' else "GitHub & Replit Hosts 管理工具 v3.0 (PyQt版)"
        self.setWindowTitle(window_title)
        
        # Update labels and buttons
        target_label = "Select target:" if self.language == 'en' else "选择目标:"
        lang_label = "Language:" if self.language == 'en' else "语言:"
        
        # Update combo box texts
        self.target_combo.setItemText(0, "GitHub")
        self.target_combo.setItemText(1, "Replit")
        
        # Update button texts
        self.btn_download.setText("🔄 Update Rules" if self.language == 'en' else "🔄 更新规则")
        self.btn_apply.setText("💾 Apply Rules" if self.language == 'en' else "💾 应用规则")
        self.btn_backup.setText("📦 Create Backup" if self.language == 'en' else "📦 创建备份")
        self.btn_restore.setText("⏪ Restore Backup" if self.language == 'en' else "⏪ 恢复备份")
        
        # Update tab texts
        self.tab_widget.setTabText(0, "Main" if self.language == 'en' else "主页")
        self.tab_widget.setTabText(1, "Settings" if self.language == 'en' else "设置")
        
        # Update placeholders
        self.rules_edit.setPlaceholderText("Rules will be displayed here..." if self.language == 'en' else "规则将在此处显示...")
        self.log_edit.setPlaceholderText("Operation logs will be displayed here..." if self.language == 'en' else "操作日志将在此处显示...")
        
        # Update status bar
        self.status_bar.showMessage("Ready" if self.language == 'en' else "就绪")
        
        # Log language change
        lang_msg = "Language switched to English" if self.language == 'en' else "语言已切换为中文"
        self.log(lang_msg)

    def check_admin_status(self):
        """Check and display administrator status"""
        if is_admin():
            status_msg = "✅ Running with administrator privileges" if self.language == 'en' else "✅ 当前以管理员权限运行"
            self.admin_label.setText(status_msg)
            self.admin_label.setStyleSheet("color: green; font-weight: bold; padding: 5px;")
        else:
            status_msg = "⚠️ Not running with administrator privileges (some functions may be limited)" if self.language == 'en' else "⚠️ 当前未以管理员权限运行（部分功能可能受限）"
            self.admin_label.setText(status_msg)
            self.admin_label.setStyleSheet("color: orange; font-weight: bold; padding: 5px;")

    def log(self, message):
        """Add log message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_edit.append(formatted_message)
        self.log_edit.moveCursor(QTextCursor.End)
        QApplication.processEvents()  # Ensure UI updates

    def set_buttons_enabled(self, enabled):
        """Enable/disable all buttons"""
        self.btn_download.setEnabled(enabled)
        self.btn_apply.setEnabled(enabled)
        self.btn_backup.setEnabled(enabled)
        self.btn_restore.setEnabled(enabled)

    def download_rules(self):
        """Download latest rules"""
        target_name = "GitHub" if self.current_target == "github" else "Replit"
        msg = f"Starting to download latest {target_name} hosts rules..." if self.language == 'en' else f"开始下载最新 {target_name} hosts 规则..."
        self.log(msg)
        self.set_buttons_enabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.thread = EnhancedHostsManagerThread('download', target_type=self.current_target, language=self.language)
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
            self.log(result.get('message', 'Download completed' if self.language == 'en' else '下载完成'))
            QMessageBox.information(self, 'Success' if self.language == 'en' else '成功', 
                                  result.get('message', 'Rules updated successfully' if self.language == 'en' else '规则更新成功'))
        else:
            self.log(f"❌ {result.get('error', 'Download failed' if self.language == 'en' else '下载失败')}")
            QMessageBox.critical(self, 'Error' if self.language == 'en' else '错误', 
                               result.get('error', 'Download failed' if self.language == 'en' else '下载失败'))

    def apply_rules(self):
        """Apply rules to system hosts file"""
        # Check admin privileges first
        if not is_admin():
            msg = "This operation requires administrator privileges. Restart as administrator?" if self.language == 'en' else "此操作需要管理员权限。是否以管理员身份重新启动？"
            reply = QMessageBox.question(self, 'Administrator Privileges Required' if self.language == 'en' else '需要管理员权限', 
                                       msg, QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                run_as_admin()
                sys.exit(0)
            return

        target_name = "GitHub" if self.current_target == "github" else "Replit"
        confirm_msg = f"This will modify the system hosts file to optimize {target_name} access. Continue?" if self.language == 'en' else f"这将修改系统 hosts 文件以优化 {target_name} 访问。继续吗？"
        reply = QMessageBox.question(self, 'Confirm' if self.language == 'en' else '确认',
                                   confirm_msg, QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            msg = f"Starting to apply {target_name} rules to system hosts file..." if self.language == 'en' else f"开始应用 {target_name} 规则到系统 hosts 文件..."
            self.log(msg)
            self.set_buttons_enabled(False)

            self.current_rules = self.rules_edit.toPlainText()
            self.thread = EnhancedHostsManagerThread('apply', self.current_rules, self.current_target, self.language)
            self.thread.log_signal.connect(self.log)
            self.thread.result_signal.connect(self.on_apply_result)
            self.thread.finished.connect(self.on_thread_finished)
            self.thread.start()

    def on_apply_result(self, result):
        """Handle apply result"""
        if result['success']:
            target_name = "GitHub" if self.current_target == "github" else "Replit"
            success_msg = f"✅ {target_name} rules applied successfully!" if self.language == 'en' else f"✅ {target_name} 规则应用成功！"
            self.log(success_msg)
            dns_msg = "💡 Suggest flushing DNS cache: ipconfig /flushdns (Windows)" if self.language == 'en' else "💡 建议刷新DNS缓存: ipconfig /flushdns (Windows)"
            self.log(dns_msg)
            QMessageBox.information(self, 'Success' if self.language == 'en' else '成功',
                                  'Rules applied successfully! Please flush DNS cache for changes to take effect.' if self.language == 'en' else '规则应用成功！请刷新DNS缓存使更改生效。')
            self.status_bar.showMessage("Rules applied successfully" if self.language == 'en' else "规则应用成功")
        else:
            error_msg = f"❌ Apply failed: {result.get('error', 'Unknown error' if self.language == 'en' else '未知错误')}"
            self.log(error_msg)
            QMessageBox.critical(self, 'Error' if self.language == 'en' else '错误',
                               f"Apply failed: {result.get('error', 'Unknown error' if self.language == 'en' else '未知错误')}")

    def create_backup(self):
        """Create backup of current hosts file"""
        self.log("Starting to create backup of current hosts file..." if self.language == 'en' else "开始创建当前 hosts 文件的备份...")
        self.set_buttons_enabled(False)

        self.thread = EnhancedHostsManagerThread('backup', language=self.language)
        self.thread.log_signal.connect(self.log)
        self.thread.result_signal.connect(self.on_backup_result)
        self.thread.finished.connect(self.on_thread_finished)
        self.thread.start()

    def on_backup_result(self, result):
        """Handle backup result"""
        if result['success']:
            self.log("✅ Backup created successfully!" if self.language == 'en' else "✅ 备份创建成功！")
            QMessageBox.information(self, 'Success' if self.language == 'en' else '成功',
                                  'Backup created successfully!' if self.language == 'en' else '备份创建成功！')
            self.status_bar.showMessage("Backup created successfully" if self.language == 'en' else "备份创建成功")
        else:
            error_msg = f"❌ Backup failed: {result.get('error', 'Unknown error' if self.language == 'en' else '未知错误')}"
            self.log(error_msg)
            QMessageBox.critical(self, 'Error' if self.language == 'en' else '错误',
                               f"Backup failed: {result.get('error', 'Unknown error' if self.language == 'en' else '未知错误')}")

    def restore_backup(self):
        """Restore hosts file from backup"""
        # Check admin privileges first
        if not is_admin():
            msg = "This operation requires administrator privileges. Restart as administrator?" if self.language == 'en' else "此操作需要管理员权限。是否以管理员身份重新启动？"
            reply = QMessageBox.question(self, 'Administrator Privileges Required' if self.language == 'en' else '需要管理员权限', 
                                       msg, QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                run_as_admin()
                sys.exit(0)
            return

        confirm_msg = "This will restore the hosts file from a backup. Continue?" if self.language == 'en' else "这将从备份恢复 hosts 文件。继续吗？"
        reply = QMessageBox.question(self, 'Confirm' if self.language == 'en' else '确认',
                                   confirm_msg, QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.log("Starting to restore hosts file from backup..." if self.language == 'en' else "开始从备份恢复 hosts 文件...")
            self.set_buttons_enabled(False)

            self.thread = EnhancedHostsManagerThread('restore', language=self.language)
            self.thread.log_signal.connect(self.log)
            self.thread.result_signal.connect(self.on_restore_result)
            self.thread.finished.connect(self.on_thread_finished)
            self.thread.start()

    def on_restore_result(self, result):
        """Handle restore result"""
        if result['success']:
            self.log("✅ Backup restored successfully!" if self.language == 'en' else "✅ 备份恢复成功！")
            QMessageBox.information(self, 'Success' if self.language == 'en' else '成功',
                                  'Backup restored successfully!' if self.language == 'en' else '备份恢复成功！')
            self.status_bar.showMessage("Backup restored successfully" if self.language == 'en' else "备份恢复成功")
        else:
            error_msg = f"❌ Restore failed: {result.get('error', 'Unknown error' if self.language == 'en' else '未知错误')}"
            self.log(error_msg)
            QMessageBox.critical(self, 'Error' if self.language == 'en' else '错误',
                               f"Restore failed: {result.get('error', 'Unknown error' if self.language == 'en' else '未知错误')}")

    def on_thread_finished(self):
        """Clean up when thread finishes"""
        self.set_buttons_enabled(True)
        self.progress_bar.setVisible(False)

    def setup_auto_update_check(self):
        """Set up automatic update check"""
        # Placeholder for future update check functionality
        pass

    def show_about(self):
        """Show about dialog"""
        if self.language == 'en':
            about_text = """
            <h2>mini-SwitchHosts v3.0 PyQt Edition</h2>
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
                <li>PyQt-based interface for better performance</li>
            </ul>
            <p>© 2025 mini-SwitchHosts Project</p>
            """
        else:
            about_text = """
            <h2>mini-SwitchHosts v3.0 PyQt版</h2>
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
                <li>基于PyQt的界面，性能更好</li>
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
    """Main function"""
    try:
        # Check for administrator privileges, request elevation if not admin
        if not is_admin():
            print("Requesting administrator privileges..." if get_system_language() == 'en' else "请求管理员权限...")
            run_as_admin()
            return 0

        app = QApplication(sys.argv)

        # Set application style
        app.setStyle('Fusion')

        # Create and show window
        window = EnhancedHostsManager()
        window.show()

        return app.exec_()

    except Exception as e:
        print(f"Application error: {e}" if get_system_language() == 'en' else f"应用程序错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())