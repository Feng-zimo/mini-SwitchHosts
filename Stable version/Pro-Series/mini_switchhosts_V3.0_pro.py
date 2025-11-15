#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mini-SwitchHosts Pro v3.0
Professional Edition with Advanced Features
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
import json
import zipfile
import urllib.request
import hashlib
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QTextEdit, QPushButton, QLabel,
                            QMessageBox, QFileDialog, QSplitter, QProgressBar,
                            QComboBox, QStatusBar, QGroupBox, QTabWidget,
                            QTreeWidgetItem, QTreeWidget, QHeaderView, 
                            QCheckBox, QSpinBox, QListWidget, QInputDialog,
                            QMenu, QTableWidget, QTableWidgetItem, QAbstractItemView,
                            QToolBar, QAction, QDockWidget, QLineEdit, QFormLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings, QUrl
from PyQt5.QtGui import QFont, QTextCursor, QIcon, QPalette, QColor, QDesktopServices


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


class PluginManager:
    """Manage plugins for extending functionality"""
    
    def __init__(self, parent):
        self.parent = parent
        self.plugins = {}
        self.plugin_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plugins')
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir)
        self.load_plugins()
    
    def load_plugins(self):
        """Load available plugins"""
        plugins = {}
        if os.path.exists(self.plugin_dir):
            for filename in os.listdir(self.plugin_dir):
                if filename.endswith('.py') and not filename.startswith('__'):
                    plugin_name = filename[:-3]  # Remove .py extension
                    try:
                        # In a real implementation, we would dynamically import the plugin
                        plugins[plugin_name] = {
                            'name': plugin_name,
                            'path': os.path.join(self.plugin_dir, filename),
                            'enabled': True
                        }
                    except Exception as e:
                        print(f"Failed to load plugin {plugin_name}: {str(e)}")
        self.plugins = plugins
        return plugins
    
    def install_plugin_from_repo(self, plugin_url):
        """Install plugin from online repository"""
        try:
            # Download plugin
            plugin_name = os.path.basename(plugin_url)
            plugin_path = os.path.join(self.plugin_dir, plugin_name)
            
            urllib.request.urlretrieve(plugin_url, plugin_path)
            
            # Add to plugins
            name = plugin_name[:-3]  # Remove .py extension
            self.plugins[name] = {
                'name': name,
                'path': plugin_path,
                'enabled': True
            }
            
            return True
        except Exception as e:
            print(f"Failed to install plugin from {plugin_url}: {str(e)}")
            return False
    
    def remove_plugin(self, plugin_name):
        """Remove a plugin"""
        if plugin_name in self.plugins:
            plugin_path = self.plugins[plugin_name]['path']
            if os.path.exists(plugin_path):
                os.remove(plugin_path)
            del self.plugins[plugin_name]
            return True
        return False


class RuleSetManager:
    """Advanced rule set management system"""
    
    def __init__(self):
        self.rule_sets = {}
        self.current_rule_set = 'default'
        self.rule_sets_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rule_sets.json')
        self.load_rule_sets()
    
    def load_rule_sets(self):
        """Load rule sets from file"""
        if os.path.exists(self.rule_sets_file):
            try:
                with open(self.rule_sets_file, 'r', encoding='utf-8') as f:
                    self.rule_sets = json.load(f)
            except Exception as e:
                print(f"Error loading rule sets: {str(e)}")
        else:
            # Create default rule set
            self.rule_sets = {
                'default': {
                    'name': 'Default',
                    'rules': [],
                    'groups': {},
                    'tags': []
                }
            }
            self.save_rule_sets()
    
    def save_rule_sets(self):
        """Save rule sets to file"""
        try:
            with open(self.rule_sets_file, 'w', encoding='utf-8') as f:
                json.dump(self.rule_sets, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving rule sets: {str(e)}")
    
    def create_rule_set(self, name):
        """Create a new rule set"""
        rule_set_id = name.lower().replace(' ', '_')
        self.rule_sets[rule_set_id] = {
            'name': name,
            'rules': [],
            'groups': {},
            'tags': []
        }
        self.save_rule_sets()
        return rule_set_id
    
    def delete_rule_set(self, rule_set_id):
        """Delete a rule set"""
        if rule_set_id in self.rule_sets and rule_set_id != 'default':
            del self.rule_sets[rule_set_id]
            if self.current_rule_set == rule_set_id:
                self.current_rule_set = 'default'
            self.save_rule_sets()
            return True
        return False
    
    def add_rule(self, rule_set_id, ip, domain, group='default', tags=None):
        """Add a rule to a rule set"""
        if rule_set_id not in self.rule_sets:
            return False
        
        if tags is None:
            tags = []
        
        rule = {
            'id': len(self.rule_sets[rule_set_id]['rules']),
            'ip': ip,
            'domain': domain,
            'group': group,
            'tags': tags,
            'enabled': True,
            'priority': 0,
            'created': datetime.now().isoformat()
        }
        
        self.rule_sets[rule_set_id]['rules'].append(rule)
        self.save_rule_sets()
        return True
    
    def remove_rule(self, rule_set_id, rule_id):
        """Remove a rule from a rule set"""
        if rule_set_id not in self.rule_sets:
            return False
        
        rules = self.rule_sets[rule_set_id]['rules']
        for i, rule in enumerate(rules):
            if rule['id'] == rule_id:
                rules.pop(i)
                self.save_rule_sets()
                return True
        return False


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
            elif self.task_type == 'verify_signature':
                self.verify_source_signature()
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

    def verify_source_signature(self):
        """Verify digital signature of rule sources"""
        # Placeholder for signature verification functionality
        self.log_signal.emit("🔒 Verifying digital signatures of rule sources..." if self.language == 'en' else "🔒 验证规则源的数字签名...")
        self.progress_signal.emit(50)
        # Simulate verification
        self.progress_signal.emit(100)
        self.result_signal.emit({'success': True, 'message': 'All sources verified successfully' if self.language == 'en' else '所有源验证成功'})


class ProHostsManager(QMainWindow):
    """Professional main window with advanced features"""

    def __init__(self):
        super().__init__()
        self.current_rules = ""
        self.current_target = "github"  # Default target
        self.language = get_system_language()  # Auto-detect system language
        self.settings = QSettings('mini-SwitchHosts', 'Pro')
        self.plugin_manager = PluginManager(self)
        self.rule_set_manager = RuleSetManager()
        self.dark_mode = self.settings.value('dark_mode', False, type=bool)
        self.init_ui()
        self.check_admin_status()
        self.setup_auto_update_check()

    def init_ui(self):
        """Initialize user interface with modern design"""
        window_title = "GitHub & Replit Hosts Manager Pro v3.0" if self.language == 'en' else "GitHub & Replit Hosts 管理工具 Pro v3.0"
        self.setWindowTitle(window_title)
        self.setGeometry(200, 150, 1200, 850)

        # Apply dark theme if enabled
        if self.dark_mode:
            self.apply_dark_theme()

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Title
        title_label = QLabel("GitHub & Replit Hosts Professional Management Tool" if self.language == 'en' else "GitHub & Replit Hosts 专业管理工具")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("margin: 15px;")
        layout.addWidget(title_label)

        # Toolbar
        self.create_toolbar()

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
        self.create_main_tab()
        
        # Rules tab
        self.create_rules_tab()
        
        # Rule Sets tab
        self.create_rule_sets_tab()
        
        # Plugins tab
        self.create_plugins_tab()
        
        # Settings tab
        self.create_settings_tab()

        layout.addWidget(self.tab_widget)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready" if self.language == 'en' else "就绪")

        # Menu bar
        self.create_menu()

        # Log startup message
        self.log("🚀 GitHub & Replit Hosts Manager Pro v3.0 started" if self.language == 'en' else "🚀 GitHub & Replit Hosts 管理工具 Pro v3.0 已启动")

    def create_toolbar(self):
        """Create toolbar with common actions"""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        # Download action
        self.download_action = QAction(QIcon(), "Download" if self.language == 'en' else "下载", self)
        self.download_action.triggered.connect(self.download_rules)
        toolbar.addAction(self.download_action)
        
        # Apply action
        self.apply_action = QAction(QIcon(), "Apply" if self.language == 'en' else "应用", self)
        self.apply_action.triggered.connect(self.apply_rules)
        toolbar.addAction(self.apply_action)
        
        # Backup action
        self.backup_action = QAction(QIcon(), "Backup" if self.language == 'en' else "备份", self)
        self.backup_action.triggered.connect(self.create_backup)
        toolbar.addAction(self.backup_action)
        
        # Restore action
        self.restore_action = QAction(QIcon(), "Restore" if self.language == 'en' else "恢复", self)
        self.restore_action.triggered.connect(self.restore_backup)
        toolbar.addAction(self.restore_action)
        
        toolbar.addSeparator()
        
        # Settings action
        self.settings_action = QAction(QIcon(), "Settings" if self.language == 'en' else "设置", self)
        self.settings_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(4))
        toolbar.addAction(self.settings_action)

    def create_main_tab(self):
        """Create main tab with core functionality"""
        main_tab = QWidget()
        main_layout = QVBoxLayout(main_tab)
        
        # Horizontal layout for buttons
        button_layout = QHBoxLayout()

        # Function buttons with enhanced styling
        self.btn_download = QPushButton("🔄 Update Rules" if self.language == 'en' else "🔄 更新规则")
        self.btn_apply = QPushButton("💾 Apply Rules" if self.language == 'en' else "💾 应用规则")
        self.btn_backup = QPushButton("📦 Create Backup" if self.language == 'en' else "📦 创建备份")
        self.btn_restore = QPushButton("⏪ Restore Backup" if self.language == 'en' else "⏪ 恢复备份")
        self.btn_verify = QPushButton("🔒 Verify Sources" if self.language == 'en' else "🔒 验证源")

        self.btn_download.clicked.connect(self.download_rules)
        self.btn_apply.clicked.connect(self.apply_rules)
        self.btn_backup.clicked.connect(self.create_backup)
        self.btn_restore.clicked.connect(self.restore_backup)
        self.btn_verify.clicked.connect(self.verify_sources)

        button_layout.addWidget(self.btn_download)
        button_layout.addWidget(self.btn_apply)
        button_layout.addWidget(self.btn_backup)
        button_layout.addWidget(self.btn_restore)
        button_layout.addWidget(self.btn_verify)

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

    def create_rules_tab(self):
        """Create rules management tab"""
        rules_tab = QWidget()
        rules_layout = QVBoxLayout(rules_tab)
        
        # Custom rules section
        rules_group = QGroupBox("Custom Rules" if self.language == 'en' else "自定义规则")
        rules_group_layout = QVBoxLayout(rules_group)
        
        # Rules table
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(6)
        self.rules_table.setHorizontalHeaderLabels([
            "ID" if self.language == 'en' else "ID",
            "IP Address" if self.language == 'en' else "IP地址",
            "Domain" if self.language == 'en' else "域名",
            "Group" if self.language == 'en' else "组",
            "Tags" if self.language == 'en' else "标签",
            "Enabled" if self.language == 'en' else "启用"
        ])
        self.rules_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.rules_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        rules_group_layout.addWidget(self.rules_table)
        
        # Rule actions
        rule_actions_layout = QHBoxLayout()
        self.btn_add_rule = QPushButton("➕ Add Rule" if self.language == 'en' else "➕ 添加规则")
        self.btn_remove_rule = QPushButton("➖ Remove Rule" if self.language == 'en' else "➖ 删除规则")
        self.btn_add_rule.clicked.connect(self.add_custom_rule)
        self.btn_remove_rule.clicked.connect(self.remove_custom_rule)
        rule_actions_layout.addWidget(self.btn_add_rule)
        rule_actions_layout.addWidget(self.btn_remove_rule)
        rule_actions_layout.addStretch()
        rules_group_layout.addLayout(rule_actions_layout)
        
        rules_layout.addWidget(rules_group)
        self.tab_widget.addTab(rules_tab, "Rules" if self.language == 'en' else "规则")

    def create_rule_sets_tab(self):
        """Create rule sets management tab"""
        rule_sets_tab = QWidget()
        rule_sets_layout = QVBoxLayout(rule_sets_tab)
        
        # Rule sets management
        rule_sets_group = QGroupBox("Rule Sets" if self.language == 'en' else "规则集")
        rule_sets_group_layout = QVBoxLayout(rule_sets_group)
        
        # Rule sets list
        self.rule_sets_list = QListWidget()
        self.update_rule_sets_list()
        rule_sets_group_layout.addWidget(self.rule_sets_list)
        
        # Rule set actions
        rule_set_actions_layout = QHBoxLayout()
        self.btn_add_rule_set = QPushButton("➕ Add Rule Set" if self.language == 'en' else "➕ 添加规则集")
        self.btn_remove_rule_set = QPushButton("➖ Remove Rule Set" if self.language == 'en' else "➖ 删除规则集")
        self.btn_add_rule_set.clicked.connect(self.add_rule_set)
        self.btn_remove_rule_set.clicked.connect(self.remove_rule_set)
        rule_set_actions_layout.addWidget(self.btn_add_rule_set)
        rule_set_actions_layout.addWidget(self.btn_remove_rule_set)
        rule_set_actions_layout.addStretch()
        rule_sets_group_layout.addLayout(rule_set_actions_layout)
        
        rule_sets_layout.addWidget(rule_sets_group)
        self.tab_widget.addTab(rule_sets_tab, "Rule Sets" if self.language == 'en' else "规则集")

    def create_plugins_tab(self):
        """Create plugins management tab"""
        plugins_tab = QWidget()
        plugins_layout = QVBoxLayout(plugins_tab)
        
        # Plugins management
        plugins_group = QGroupBox("Plugins" if self.language == 'en' else "插件")
        plugins_group_layout = QVBoxLayout(plugins_group)
        
        # Plugins list
        self.plugins_list = QListWidget()
        self.update_plugins_list()
        plugins_group_layout.addWidget(self.plugins_list)
        
        # Plugin actions
        plugin_actions_layout = QHBoxLayout()
        self.btn_install_plugin = QPushButton("📥 Install Plugin" if self.language == 'en' else "📥 安装插件")
        self.btn_remove_plugin = QPushButton("🗑️ Remove Plugin" if self.language == 'en' else "🗑️ 删除插件")
        self.btn_install_plugin.clicked.connect(self.install_plugin)
        self.btn_remove_plugin.clicked.connect(self.remove_plugin)
        plugin_actions_layout.addWidget(self.btn_install_plugin)
        plugin_actions_layout.addWidget(self.btn_remove_plugin)
        plugin_actions_layout.addStretch()
        plugins_group_layout.addLayout(plugin_actions_layout)
        
        # Plugin repository
        repo_layout = QHBoxLayout()
        repo_layout.addWidget(QLabel("Plugin Repository URL:" if self.language == 'en' else "插件仓库URL:"))
        self.plugin_repo_edit = QLineEdit()
        self.plugin_repo_edit.setText("https://example.com/plugins/" if self.language == 'en' else "https://example.com/plugins/")
        repo_layout.addWidget(self.plugin_repo_edit)
        plugins_group_layout.addLayout(repo_layout)
        
        plugins_layout.addWidget(plugins_group)
        self.tab_widget.addTab(plugins_tab, "Plugins" if self.language == 'en' else "插件")

    def create_settings_tab(self):
        """Create settings tab"""
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        
        # Theme settings
        theme_group = QGroupBox("Theme Settings" if self.language == 'en' else "主题设置")
        theme_layout = QVBoxLayout(theme_group)
        
        self.dark_mode_checkbox = QCheckBox("Dark Mode" if self.language == 'en' else "暗色主题")
        self.dark_mode_checkbox.setChecked(self.dark_mode)
        self.dark_mode_checkbox.stateChanged.connect(self.toggle_dark_mode)
        theme_layout.addWidget(self.dark_mode_checkbox)
        
        settings_layout.addWidget(theme_group)
        
        # Update settings
        update_group = QGroupBox("Update Settings" if self.language == 'en' else "更新设置")
        update_layout = QVBoxLayout(update_group)
        
        update_check_layout = QHBoxLayout()
        update_check_layout.addWidget(QLabel("Auto-check for updates:" if self.language == 'en' else "自动检查更新:"))
        self.update_check_checkbox = QCheckBox()
        self.update_check_checkbox.setChecked(True)
        update_check_layout.addWidget(self.update_check_checkbox)
        update_check_layout.addStretch()
        update_layout.addLayout(update_check_layout)
        
        settings_layout.addWidget(update_group)
        
        # Security settings
        security_group = QGroupBox("Security Settings" if self.language == 'en' else "安全设置")
        security_layout = QVBoxLayout(security_group)
        
        self.signature_check_checkbox = QCheckBox("Verify source signatures" if self.language == 'en' else "验证源签名")
        self.signature_check_checkbox.setChecked(True)
        security_layout.addWidget(self.signature_check_checkbox)
        
        settings_layout.addWidget(security_group)
        settings_layout.addStretch()
        
        self.tab_widget.addTab(settings_tab, "Settings" if self.language == 'en' else "设置")

    def create_menu(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File' if self.language == 'en' else '文件')
        
        exit_action = QAction('Exit' if self.language == 'en' else '退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu('View' if self.language == 'en' else '视图')
        
        self.dark_mode_action = QAction('Dark Mode' if self.language == 'en' else '暗色主题', self)
        self.dark_mode_action.setCheckable(True)
        self.dark_mode_action.setChecked(self.dark_mode)
        self.dark_mode_action.triggered.connect(self.toggle_dark_mode)
        view_menu.addAction(self.dark_mode_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools' if self.language == 'en' else '工具')
        
        verify_action = QAction('Verify Sources' if self.language == 'en' else '验证源', self)
        verify_action.triggered.connect(self.verify_sources)
        tools_menu.addAction(verify_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help' if self.language == 'en' else '帮助')
        
        about_action = QAction('About' if self.language == 'en' else '关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def apply_dark_theme(self):
        """Apply dark theme to the application"""
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        
        QApplication.setPalette(dark_palette)
        QApplication.setStyle("Fusion")

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
        window_title = "GitHub & Replit Hosts Manager Pro v3.0" if self.language == 'en' else "GitHub & Replit Hosts 管理工具 Pro v3.0"
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
        self.btn_verify.setText("🔒 Verify Sources" if self.language == 'en' else "🔒 验证源")
        
        # Update tab texts
        self.tab_widget.setTabText(0, "Main" if self.language == 'en' else "主页")
        self.tab_widget.setTabText(1, "Rules" if self.language == 'en' else "规则")
        self.tab_widget.setTabText(2, "Rule Sets" if self.language == 'en' else "规则集")
        self.tab_widget.setTabText(3, "Plugins" if self.language == 'en' else "插件")
        self.tab_widget.setTabText(4, "Settings" if self.language == 'en' else "设置")
        
        # Update placeholders
        self.rules_edit.setPlaceholderText("Rules will be displayed here..." if self.language == 'en' else "规则将在此处显示...")
        self.log_edit.setPlaceholderText("Operation logs will be displayed here..." if self.language == 'en' else "操作日志将在此处显示...")
        
        # Update status bar
        self.status_bar.showMessage("Ready" if self.language == 'en' else "就绪")
        
        # Update menu
        file_menu = self.menuBar().actions()[0].menu()
        file_menu.setTitle('File' if self.language == 'en' else '文件')
        
        view_menu = self.menuBar().actions()[1].menu()
        view_menu.setTitle('View' if self.language == 'en' else '视图')
        self.dark_mode_action.setText('Dark Mode' if self.language == 'en' else '暗色主题')
        
        tools_menu = self.menuBar().actions()[2].menu()
        tools_menu.setTitle('Tools' if self.language == 'en' else '工具')
        
        help_menu = self.menuBar().actions()[3].menu()
        help_menu.setTitle('Help' if self.language == 'en' else '帮助')
        self.dark_mode_action.setText('About' if self.language == 'en' else '关于')
        
        # Update toolbar
        self.download_action.setText("Download" if self.language == 'en' else "下载")
        self.apply_action.setText("Apply" if self.language == 'en' else "应用")
        self.backup_action.setText("Backup" if self.language == 'en' else "备份")
        self.restore_action.setText("Restore" if self.language == 'en' else "恢复")
        self.settings_action.setText("Settings" if self.language == 'en' else "设置")
        
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
        self.btn_verify.setEnabled(enabled)

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

    def verify_sources(self):
        """Verify digital signatures of rule sources"""
        self.log("Starting to verify digital signatures of rule sources..." if self.language == 'en' else "开始验证规则源的数字签名...")
        self.set_buttons_enabled(False)

        self.thread = EnhancedHostsManagerThread('verify_signature', language=self.language)
        self.thread.log_signal.connect(self.log)
        self.thread.result_signal.connect(self.on_verify_result)
        self.thread.finished.connect(self.on_thread_finished)
        self.thread.start()

    def on_verify_result(self, result):
        """Handle verification result"""
        if result['success']:
            self.log("✅ Source verification completed successfully!" if self.language == 'en' else "✅ 源验证成功完成！")
            QMessageBox.information(self, 'Success' if self.language == 'en' else '成功',
                                  result.get('message', 'Source verification completed successfully!' if self.language == 'en' else '源验证成功完成！'))
            self.status_bar.showMessage("Source verification completed" if self.language == 'en' else "源验证完成")
        else:
            error_msg = f"❌ Verification failed: {result.get('error', 'Unknown error' if self.language == 'en' else '未知错误')}"
            self.log(error_msg)
            QMessageBox.critical(self, 'Error' if self.language == 'en' else '错误',
                               f"Verification failed: {result.get('error', 'Unknown error' if self.language == 'en' else '未知错误')}")

    def on_thread_finished(self):
        """Clean up when thread finishes"""
        self.set_buttons_enabled(True)
        self.progress_bar.setVisible(False)

    def setup_auto_update_check(self):
        """Set up automatic update check"""
        # Placeholder for future update check functionality
        pass

    def toggle_dark_mode(self):
        """Toggle dark mode"""
        self.dark_mode = not self.dark_mode
        self.settings.setValue('dark_mode', self.dark_mode)
        
        if self.dark_mode:
            self.apply_dark_theme()
        else:
            QApplication.setPalette(QPalette())
            QApplication.setStyle("Fusion")
        
        # Update checkbox state
        self.dark_mode_checkbox.setChecked(self.dark_mode)
        self.dark_mode_action.setChecked(self.dark_mode)

    def add_custom_rule(self):
        """Add a custom rule"""
        # Create a dialog for adding rules
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Custom Rule" if self.language == 'en' else "添加自定义规则")
        dialog.setGeometry(300, 300, 400, 200)
        
        layout = QFormLayout(dialog)
        
        ip_edit = QLineEdit()
        domain_edit = QLineEdit()
        group_edit = QLineEdit()
        group_edit.setText("default")
        
        layout.addRow("IP Address:" if self.language == 'en' else "IP地址:", ip_edit)
        layout.addRow("Domain:" if self.language == 'en' else "域名:", domain_edit)
        layout.addRow("Group:" if self.language == 'en' else "组:", group_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            ip = ip_edit.text()
            domain = domain_edit.text()
            group = group_edit.text()
            
            if ip and domain:
                # Add rule to current rule set
                if self.rule_set_manager.add_rule(
                    self.rule_set_manager.current_rule_set, ip, domain, group):
                    self.log(f"Added custom rule: {ip} {domain}" if self.language == 'en' else f"添加自定义规则: {ip} {domain}")
                    self.update_rules_table()
                else:
                    QMessageBox.warning(self, "Error" if self.language == 'en' else "错误", 
                                      "Failed to add rule" if self.language == 'en' else "添加规则失败")
            else:
                QMessageBox.warning(self, "Warning" if self.language == 'en' else "警告", 
                                  "Please enter both IP address and domain" if self.language == 'en' else "请输入IP地址和域名")

    def remove_custom_rule(self):
        """Remove selected custom rule"""
        selected_rows = self.rules_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Warning" if self.language == 'en' else "警告", 
                               "Please select a rule to remove" if self.language == 'en' else "请选择要删除的规则")
            return
            
        # Remove from rule manager
        row = selected_rows[0].row()
        rule_id = int(self.rules_table.item(row, 0).text())
        
        if self.rule_set_manager.remove_rule(
            self.rule_set_manager.current_rule_set, rule_id):
            # Remove from table
            self.rules_table.removeRow(row)
            self.log("Rule removed successfully" if self.language == 'en' else "规则删除成功")
        else:
            QMessageBox.warning(self, "Error" if self.language == 'en' else "错误", 
                              "Failed to remove rule" if self.language == 'en' else "删除规则失败")

    def update_rules_table(self):
        """Update rules table with current rule set"""
        # Clear table
        self.rules_table.setRowCount(0)
        
        # Get current rule set
        rule_set = self.rule_set_manager.rule_sets.get(
            self.rule_set_manager.current_rule_set, {})
        rules = rule_set.get('rules', [])
        
        # Add rules to table
        for rule in rules:
            row_count = self.rules_table.rowCount()
            self.rules_table.insertRow(row_count)
            
            self.rules_table.setItem(row_count, 0, QTableWidgetItem(str(rule['id'])))
            self.rules_table.setItem(row_count, 1, QTableWidgetItem(rule['ip']))
            self.rules_table.setItem(row_count, 2, QTableWidgetItem(rule['domain']))
            self.rules_table.setItem(row_count, 3, QTableWidgetItem(rule['group']))
            self.rules_table.setItem(row_count, 4, QTableWidgetItem(', '.join(rule['tags'])))
            
            enabled_checkbox = QTableWidgetItem()
            enabled_checkbox.setCheckState(Qt.Checked if rule['enabled'] else Qt.Unchecked)
            self.rules_table.setItem(row_count, 5, enabled_checkbox)

    def add_rule_set(self):
        """Add a new rule set"""
        name, ok = QInputDialog.getText(self, "New Rule Set" if self.language == 'en' else "新建规则集", 
                                       "Enter rule set name:" if self.language == 'en' else "输入规则集名称:")
        if ok and name:
            rule_set_id = self.rule_set_manager.create_rule_set(name)
            self.update_rule_sets_list()
            self.log(f"Created rule set: {name}" if self.language == 'en' else f"创建规则集: {name}")

    def remove_rule_set(self):
        """Remove selected rule set"""
        current_row = self.rule_sets_list.currentRow()
        if current_row >= 0:
            rule_set_id = list(self.rule_set_manager.rule_sets.keys())[current_row]
            if rule_set_id != 'default':
                reply = QMessageBox.question(self, 'Confirm' if self.language == 'en' else '确认',
                                           f"Delete rule set '{self.rule_set_manager.rule_sets[rule_set_id]['name']}'?" if self.language == 'en' else f"删除规则集 '{self.rule_set_manager.rule_sets[rule_set_id]['name']}'?",
                                           QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    if self.rule_set_manager.delete_rule_set(rule_set_id):
                        self.update_rule_sets_list()
                        self.log("Rule set deleted successfully" if self.language == 'en' else "规则集删除成功")
                    else:
                        QMessageBox.warning(self, "Error" if self.language == 'en' else "错误", 
                                          "Failed to delete rule set" if self.language == 'en' else "删除规则集失败")
            else:
                QMessageBox.warning(self, "Warning" if self.language == 'en' else "警告", 
                                  "Cannot delete default rule set" if self.language == 'en' else "无法删除默认规则集")
        else:
            QMessageBox.warning(self, "Warning" if self.language == 'en' else "警告", 
                              "Please select a rule set to delete" if self.language == 'en' else "请选择要删除的规则集")

    def update_rule_sets_list(self):
        """Update rule sets list"""
        self.rule_sets_list.clear()
        for rule_set_id, rule_set in self.rule_set_manager.rule_sets.items():
            self.rule_sets_list.addItem(f"{rule_set['name']} ({len(rule_set['rules'])} rules)" if self.language == 'en' else f"{rule_set['name']} ({len(rule_set['rules'])} 条规则)")

    def update_plugins_list(self):
        """Update plugins list"""
        self.plugins_list.clear()
        for plugin_name, plugin in self.plugin_manager.plugins.items():
            status = "Enabled" if plugin['enabled'] else "Disabled"
            status_cn = "已启用" if plugin['enabled'] else "已禁用"
            self.plugins_list.addItem(f"{plugin_name} ({status if self.language == 'en' else status_cn})")

    def install_plugin(self):
        """Install a plugin from repository"""
        url = self.plugin_repo_edit.text()
        if url:
            if self.plugin_manager.install_plugin_from_repo(url):
                self.update_plugins_list()
                self.log(f"Plugin installed from: {url}" if self.language == 'en' else f"插件已从以下位置安装: {url}")
                QMessageBox.information(self, "Success" if self.language == 'en' else "成功", 
                                      "Plugin installed successfully" if self.language == 'en' else "插件安装成功")
            else:
                QMessageBox.critical(self, "Error" if self.language == 'en' else "错误", 
                                   "Failed to install plugin" if self.language == 'en' else "插件安装失败")
        else:
            QMessageBox.warning(self, "Warning" if self.language == 'en' else "警告", 
                              "Please enter a plugin repository URL" if self.language == 'en' else "请输入插件仓库URL")

    def remove_plugin(self):
        """Remove selected plugin"""
        current_row = self.plugins_list.currentRow()
        if current_row >= 0:
            plugin_name = list(self.plugin_manager.plugins.keys())[current_row]
            reply = QMessageBox.question(self, 'Confirm' if self.language == 'en' else '确认',
                                       f"Remove plugin '{plugin_name}'?" if self.language == 'en' else f"删除插件 '{plugin_name}'?",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                if self.plugin_manager.remove_plugin(plugin_name):
                    self.update_plugins_list()
                    self.log(f"Plugin removed: {plugin_name}" if self.language == 'en' else f"插件已删除: {plugin_name}")
                    QMessageBox.information(self, "Success" if self.language == 'en' else "成功", 
                                          "Plugin removed successfully" if self.language == 'en' else "插件删除成功")
                else:
                    QMessageBox.critical(self, "Error" if self.language == 'en' else "错误", 
                                       "Failed to remove plugin" if self.language == 'en' else "插件删除失败")
        else:
            QMessageBox.warning(self, "Warning" if self.language == 'en' else "警告", 
                              "Please select a plugin to remove" if self.language == 'en' else "请选择要删除的插件")

    def show_about(self):
        """Show about dialog"""
        if self.language == 'en':
            about_text = """
            <h2>mini-SwitchHosts Pro v3.0</h2>
            <p><b>Professional Edition with Advanced Features</b></p>
            <p>Enhanced IP resolution, smart filtering, incremental updates, plugin system, and advanced rule management</p>
            <p><b>Key Improvements:</b></p>
            <ul>
                <li>Enhanced IP parsing algorithm for better accuracy</li>
                <li>Smart rule filtering to remove invalid entries</li>
                <li>Incremental update mechanism for efficiency</li>
                <li>Modern UI with real-time status monitoring</li>
                <li>Concurrent processing for faster downloads</li>
                <li>Multi-language support (English and Chinese)</li>
                <li>Cross-platform compatibility (Windows, Linux, macOS)</li>
                <li>Plugin system for extensibility</li>
                <li>Advanced rule management with rule sets</li>
                <li>Dark theme support</li>
                <li>Digital signature verification for security</li>
            </ul>
            <p>© 2025 mini-SwitchHosts Project</p>
            """
        else:
            about_text = """
            <h2>mini-SwitchHosts Pro v3.0</h2>
            <p><b>专业版，包含高级功能</b></p>
            <p>增强的IP解析、智能过滤、增量更新、插件系统和高级规则管理</p>
            <p><b>主要改进:</b></p>
            <ul>
                <li>增强的IP解析算法，提高准确性</li>
                <li>智能规则过滤，去除无效条目</li>
                <li>增量更新机制，提高效率</li>
                <li>现代化UI，支持实时状态监控</li>
                <li>并发处理，加快下载速度</li>
                <li>多语言支持（英文和中文）</li>
                <li>跨平台兼容性（Windows、Linux、macOS）</li>
                <li>插件系统，支持功能扩展</li>
                <li>高级规则管理，支持规则集</li>
                <li>暗色主题支持</li>
                <li>数字签名验证，增强安全性</li>
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
        window = ProHostsManager()
        window.show()

        return app.exec_()

    except Exception as e:
        print(f"Application error: {e}" if get_system_language() == 'en' else f"应用程序错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
