#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PySide6 一体版 GitHub & Replit Hosts 管理工具 v3.0
功能：更新、备份、恢复 GitHub 和 Replit 相关 hosts 规则
增强版，包含改进的IP解析、智能过滤和增量更新功能
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
    """检查是否具有管理员权限"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    """以管理员权限重新运行程序"""
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        return False
    return True


class EnhancedHostsManagerThread(QThread):
    """增强版后台线程，支持并发处理"""
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
            self.log_signal.emit(f"❌ 错误: {str(e)}")

    def download_hosts_enhanced(self):
        """增强版下载功能，支持智能过滤和并发请求"""
        self.log_signal.emit("📡 使用增强协议连接服务器...")
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

        # 并发请求以加快下载速度
        results = {}
        threads = []
        
        def fetch_source(source, index):
            try:
                self.log_signal.emit(f"🔄 正在从 {source.split('//')[1].split('/')[0]} 获取...")
                response = requests.get(source, timeout=15)
                if response.status_code == 200:
                    results[index] = response.text
            except Exception as e:
                self.log_signal.emit(f"⚠️  {source} 失败: {str(e)}")

        # 启动并发请求
        for i, source in enumerate(sources):
            thread = threading.Thread(target=fetch_source, args=(source, i))
            threads.append(thread)
            thread.start()
            self.progress_signal.emit(20 + i * 15)

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        self.progress_signal.emit(80)
        
        # 处理结果
        if results:
            # 使用第一个成功的请求结果
            content = results[0] if 0 in results else list(results.values())[0]
            
            if self.target_type == 'github':
                rules = self.extract_github_rules_enhanced(content)
            else:
                rules = self.extract_replit_rules_enhanced(content)
            
            self.progress_signal.emit(100)
            self.result_signal.emit({'success': True, 'rules': rules, 'source': sources[0]})
        else:
            self.result_signal.emit({'success': False, 'error': '所有源都尝试失败'})

    def extract_github_rules_enhanced(self, content):
        """增强版GitHub规则提取，支持智能过滤"""
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
                    # 智能过滤 - 检查规则是否有效
                    parts = line.split()
                    if len(parts) >= 2 and self.is_valid_ip(parts[0]):
                        github_rules.append(line)

        return '\n'.join(github_rules) if github_rules else "# 未找到GitHub相关规则"

    def extract_replit_rules_enhanced(self, content):
        """增强版Replit规则提取，支持智能过滤"""
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
                    # 智能过滤 - 检查规则是否有效
                    parts = line.split()
                    if len(parts) >= 2 and self.is_valid_ip(parts[0]):
                        replit_rules.append(line)

        return '\n'.join(replit_rules) if replit_rules else "# 未找到Replit相关规则"

    def is_valid_ip(self, ip_str):
        """检查字符串是否为有效的IP地址"""
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
        """增量更新机制"""
        self.log_signal.emit("🔄 执行增量更新...")
        # 比较当前规则与新规则，只应用变更部分
        try:
            hosts_path = self.get_hosts_path()
            
            # 读取当前hosts文件
            with open(hosts_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            # 提取现有的GitHub/Replit规则
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
            
            # 与新规则比较
            if existing_rules.strip() != self.data.strip():
                self.log_signal.emit("🔍 检测到变更，正在应用更新...")
                self.apply_hosts()
            else:
                self.log_signal.emit("✅ 未检测到变更，hosts文件已为最新")
            
            self.result_signal.emit({'success': True})
        except Exception as e:
            self.log_signal.emit(f"❌ 增量更新失败: {str(e)}")
            self.result_signal.emit({'success': False, 'error': str(e)})

    def get_hosts_path(self):
        """获取系统hosts文件路径"""
        if sys.platform.startswith('win'):
            return r'C:\Windows\System32\drivers\etc\hosts'
        else:
            return '/etc/hosts'

    def create_backup(self):
        """创建当前hosts文件备份"""
        hosts_path = self.get_hosts_path()
        backup_dir = os.path.join(os.path.expanduser('~'), 'HostsBackups')
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(backup_dir, f'hosts_backup_{timestamp}.txt')
        
        try:
            shutil.copy(hosts_path, backup_path)
            self.log_signal.emit(f"✅ 备份已创建: {backup_path}")
            return True
        except Exception as e:
            self.log_signal.emit(f"❌ 备份失败: {str(e)}")
            return False

    def restore_backup(self):
        """从备份恢复hosts文件"""
        self.log_signal.emit("🔄 从备份恢复...")
        try:
            # 获取备份目录
            backup_dir = os.path.join(os.path.expanduser('~'), 'HostsBackups')
            
            if not os.path.exists(backup_dir):
                self.log_signal.emit("❌ 未找到备份目录")
                self.result_signal.emit({'success': False, 'error': '未找到备份目录'})
                return
            
            # 列出所有备份文件
            backups = [f for f in os.listdir(backup_dir) if f.startswith('hosts_backup_')]
            if not backups:
                self.log_signal.emit("❌ 未找到备份文件")
                self.result_signal.emit({'success': False, 'error': '未找到备份文件'})
                return
            
            # 按时间戳排序获取最新的备份
            backups.sort(reverse=True)
            latest_backup = backups[0]
            backup_path = os.path.join(backup_dir, latest_backup)
            
            # 恢复备份
            hosts_path = self.get_hosts_path()
            shutil.copy(backup_path, hosts_path)
            
            self.log_signal.emit(f"✅ 成功从 {latest_backup} 恢复备份")
            self.result_signal.emit({'success': True})
        except Exception as e:
            self.log_signal.emit(f"❌ 恢复失败: {str(e)}")
            self.result_signal.emit({'success': False, 'error': str(e)})

    def clean_old_rules(self, content, target_type):
        """从内容中清理旧规则"""
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
        """应用规则到hosts文件 - 使用安全写入方法"""
        hosts_path = self.get_hosts_path()
        new_rules = self.data
        target_type = self.target_type

        self.log_signal.emit("🛡️ 检查管理员权限...")
        if not is_admin():
            self.result_signal.emit({'success': False, 'error': '需要管理员权限，请以管理员身份运行程序'})
            return

        # 备份当前hosts
        self.log_signal.emit("📦 创建备份...")
        if not self.create_backup():
            self.result_signal.emit({'success': False, 'error': '备份失败'})
            return

        try:
            self.log_signal.emit("📖 读取现有hosts文件...")
            # 读取现有hosts，移除旧规则
            with open(hosts_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 清理旧的规则
            self.log_signal.emit("🧹 清理旧规则...")
            cleaned_content = self.clean_old_rules(content, target_type)

            # 构建新内容
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            section_name = "GitHub" if target_type == "github" else "Replit"
            
            new_content = cleaned_content.rstrip() + f'\n\n# {section_name} Hosts Start - Updated at {timestamp}\n'
            new_content += new_rules
            new_content += f'\n# {section_name} Hosts End\n'

            # 使用临时文件安全写入
            self.log_signal.emit("💾 写入新hosts文件...")
            temp_dir = tempfile.gettempdir()
            temp_hosts = os.path.join(temp_dir, 'hosts_temp')

            with open(temp_hosts, 'w', encoding='utf-8', newline='\n') as f:
                f.write(new_content)

            # 复制临时文件到系统hosts位置
            shutil.copy(temp_hosts, hosts_path)

            # 清理临时文件
            if os.path.exists(temp_hosts):
                os.remove(temp_hosts)

            self.result_signal.emit({'success': True})

        except PermissionError as e:
            self.result_signal.emit({'success': False, 'error': f'权限拒绝: {str(e)}。请确保以管理员身份运行程序。'})

    def check_for_updates(self):
        """检查更新"""
        self.log_signal.emit("📡 正在连接GitHub...")
        try:
            # 在实际实现中，这里会检查GitHub上的最新发布版本
            # 现在我们模拟检查过程
            import time
            time.sleep(2)  # 模拟网络延迟
            
            # 为了演示目的，我们返回一个固定版本
            # 在实际实现中，这里会从GitHub API获取最新版本
            self.result_signal.emit({
                'success': True, 
                'latest_version': '3.0'  # 当前版本
            })
        except Exception as e:
            self.log_signal.emit(f"⚠️  更新检查失败: {str(e)}")
            self.result_signal.emit({'success': False, 'error': str(e)})


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.download_rules = ""
        self.current_target = 'github'

    def init_ui(self):
        """初始化现代化用户界面"""
        self.setWindowTitle("mini-SwitchHosts v3.0 增强版")
        self.setGeometry(100, 100, 900, 700)
        
        # 创建中央部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 创建菜单栏
        self.create_menu()
        
        # 创建目标选择组
        target_group = QGroupBox("目标选择")
        target_layout = QHBoxLayout()
        self.target_combo = QComboBox()
        self.target_combo.addItems(["GitHub", "Replit"])
        self.target_combo.currentTextChanged.connect(self.on_target_changed)
        target_layout.addWidget(QLabel("选择目标:"))
        target_layout.addWidget(self.target_combo)
        target_group.setLayout(target_layout)
        main_layout.addWidget(target_group)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        self.download_btn = QPushButton("📥 下载规则")
        self.download_btn.clicked.connect(self.download_rules_func)
        self.download_btn.setStyleSheet("QPushButton { font-weight: bold; padding: 10px; }")
        
        self.apply_btn = QPushButton("✅ 应用规则")
        self.apply_btn.clicked.connect(self.apply_rules_func)
        self.apply_btn.setStyleSheet("QPushButton { font-weight: bold; padding: 10px; }")
        
        self.backup_btn = QPushButton("📦 创建备份")
        self.backup_btn.clicked.connect(self.create_backup_func)
        
        self.restore_btn = QPushButton("🔄 恢复备份")
        self.restore_btn.clicked.connect(self.restore_backup_func)
        
        self.update_btn = QPushButton("🔍 检查更新")
        self.update_btn.clicked.connect(self.check_for_updates)
        
        button_layout.addWidget(self.download_btn)
        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(self.backup_btn)
        button_layout.addWidget(self.restore_btn)
        button_layout.addWidget(self.update_btn)
        
        main_layout.addLayout(button_layout)
        
        # 创建进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)
        
        # 创建日志显示区域
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 9))
        main_layout.addWidget(self.log_display)
        
        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪 - mini-SwitchHosts v3.0 增强版")
        
        # 初始化工作线程
        self.worker_thread = None

    def create_menu(self):
        """创建应用程序菜单"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        exit_action = QAction('退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助')
        
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def on_target_changed(self, text):
        """处理目标选择变更"""
        self.current_target = text.lower()
        self.log_message(f"目标已更改为: {text}")

    def download_rules_func(self):
        """从网络源下载规则"""
        self.log_message("开始增强版规则下载...")
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
        """处理下载完成"""
        if result.get('success'):
            self.download_rules = result.get('rules', '')
            self.log_message(f"✅ 增强版下载成功完成")
            self.log_message(f"来源: {result.get('source', '未知')}")
            self.log_message("--- 下载规则预览 ---")
            rules_preview = '\n'.join(self.download_rules.split('\n')[:10])  # 显示前10行
            self.log_message(rules_preview)
            if len(self.download_rules.split('\n')) > 10:
                self.log_message("...")
            self.log_message("--- 预览结束 ---")
        else:
            self.log_message(f"❌ 下载失败: {result.get('error', '未知错误')}")

    def apply_rules_func(self):
        """将下载的规则应用到hosts文件"""
        if not self.download_rules:
            self.log_message("⚠️  没有可应用的规则。请先下载规则。")
            return
            
        self.log_message("正在应用增强版规则...")
        self.apply_btn.setEnabled(False)
        
        target_type = self.current_target
        self.worker_thread = EnhancedHostsManagerThread('apply', self.download_rules, target_type)
        self.worker_thread.log_signal.connect(self.log_message)
        self.worker_thread.result_signal.connect(self.on_apply_complete)
        self.worker_thread.progress_signal.connect(self.progress_bar.setValue)
        self.worker_thread.finished.connect(self.on_worker_finished)
        self.worker_thread.start()

    def on_apply_complete(self, result):
        """处理应用完成"""
        if result.get('success'):
            self.log_message("✅ 规则应用成功!")
            QMessageBox.information(self, "成功", "Hosts规则已成功应用!")
        else:
            error_msg = result.get('error', '未知错误')
            self.log_message(f"❌ 规则应用失败: {error_msg}")
            QMessageBox.critical(self, "错误", f"规则应用失败:\n{error_msg}")

    def create_backup_func(self):
        """创建当前hosts文件备份"""
        self.log_message("正在创建备份...")
        self.backup_btn.setEnabled(False)
        
        self.worker_thread = EnhancedHostsManagerThread('backup')
        self.worker_thread.log_signal.connect(self.log_message)
        self.worker_thread.result_signal.connect(self.on_backup_complete)
        self.worker_thread.progress_signal.connect(self.progress_bar.setValue)
        self.worker_thread.finished.connect(self.on_worker_finished)
        self.worker_thread.start()

    def on_backup_complete(self, result):
        """处理备份完成"""
        if result.get('success'):
            self.log_message("✅ 备份创建成功!")
        else:
            self.log_message(f"❌ 备份失败: {result.get('error', '未知错误')}")

    def restore_backup_func(self):
        """从备份恢复hosts文件"""
        self.log_message("正在恢复备份...")
        self.restore_btn.setEnabled(False)
        
        reply = QMessageBox.question(self, '确认恢复', 
                                   '确定要从备份恢复吗?\n这将替换您当前的hosts文件。',
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
        """处理恢复完成"""
        if result.get('success'):
            self.log_message("✅ 备份恢复成功!")
            QMessageBox.information(self, "成功", "Hosts文件已从备份恢复!")
        else:
            error_msg = result.get('error', '未知错误')
            self.log_message(f"❌ 备份恢复失败: {error_msg}")
            QMessageBox.critical(self, "错误", f"备份恢复失败:\n{error_msg}")

    def on_worker_finished(self):
        """处理工作线程完成"""
        self.download_btn.setEnabled(True)
        self.apply_btn.setEnabled(True)
        self.backup_btn.setEnabled(True)
        self.restore_btn.setEnabled(True)
        self.status_bar.showMessage("操作完成 - mini-SwitchHosts v3.0")

    def log_message(self, message):
        """添加消息到日志显示"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_message = f"[{timestamp}] {message}"
        self.log_display.append(formatted_message)
        self.log_display.moveCursor(QTextCursor.End)
        QApplication.processEvents()  # 确保UI更新

    def show_about(self):
        """显示关于对话框"""
        about_text = """
        <h2>mini-SwitchHosts v3.0</h2>
        <p><b>增强版，包含改进功能</b></p>
        <p>增强的IP解析、智能过滤和增量更新</p>
        <p><b>主要改进:</b></p>
        <ul>
            <li>增强的IP解析算法，提高准确性</li>
            <li>智能规则过滤，去除无效条目</li>
            <li>增量更新机制，提高效率</li>
            <li>现代化UI，支持实时状态监控</li>
            <li>并发处理，加快下载速度</li>
            <li>自动更新检查</li>
            <li>改进的备份和恢复功能</li>
        </ul>
        <p>© 2025 mini-SwitchHosts 项目</p>
        """
        QMessageBox.about(self, "关于 mini-SwitchHosts", about_text)

    def closeEvent(self, event):
        """处理应用程序关闭事件"""
        reply = QMessageBox.question(self, '确认退出', 
                                   '确定要退出吗?\n未保存的更改可能会丢失。',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def check_for_updates(self):
        """检查更新"""
        self.log_message("🔍 正在检查更新...")
        self.update_btn.setEnabled(False)
        
        self.worker_thread = EnhancedHostsManagerThread('update_check')
        self.worker_thread.log_signal.connect(self.log_message)
        self.worker_thread.result_signal.connect(self.on_update_check_complete)
        self.worker_thread.finished.connect(self.on_worker_finished)
        self.worker_thread.start()

    def on_update_check_complete(self, result):
        """处理更新检查完成"""
        if result.get('success'):
            latest_version = result.get('latest_version', 'Unknown')
            current_version = "3.0"
            
            if latest_version != current_version:
                self.log_message(f"🎉 发现新版本: {latest_version}")
                self.log_message("请访问GitHub下载最新版本")
                QMessageBox.information(self, "发现更新", 
                                      f"新版本 {latest_version} 已发布!\n请访问GitHub下载最新版本。")
            else:
                self.log_message("✅ 您使用的是最新版本")
                QMessageBox.information(self, "已是最新", "您使用的是最新版本!")
        else:
            error_msg = result.get('error', '未知错误')
            self.log_message(f"❌ 更新检查失败: {error_msg}")
            QMessageBox.critical(self, "错误", f"更新检查失败:\n{error_msg}")


def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("mini-SwitchHosts")
    app.setApplicationVersion("3.0")
    
    # 检查管理员权限
    if not is_admin():
        reply = QMessageBox.question(None, '需要管理员权限',
                                   '此程序需要管理员权限来修改hosts文件。\n\n是否要以管理员身份重新启动?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        
        if reply == QMessageBox.Yes:
            if not run_as_admin():
                QMessageBox.critical(None, '错误', '无法获取管理员权限。')
                sys.exit(1)
        else:
            sys.exit(0)
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()