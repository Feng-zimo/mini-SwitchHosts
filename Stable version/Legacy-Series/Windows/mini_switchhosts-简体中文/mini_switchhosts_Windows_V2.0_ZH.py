#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PySide6 一体版 GitHub & Replit Hosts 管理工具
功能：更新、备份、恢复 GitHub 和 Replit 相关 hosts 规则
"""

import sys
import os
import requests
import shutil
import ctypes
import tempfile
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QTextEdit, QPushButton, QLabel,
                               QMessageBox, QFileDialog, QSplitter, QProgressBar,
                               QComboBox)
from PySide6.QtCore import Qt, QThread, Signal as pyqtSignal
from PySide6.QtGui import QFont, QTextCursor


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


class HostsManagerThread(QThread):
    """后台线程处理网络请求和文件操作"""
    log_signal = pyqtSignal(str)
    result_signal = pyqtSignal(dict)
    progress_signal = pyqtSignal(int)

    def __init__(self, task_type, data=None, target_type='github'):
        super().__init__()
        self.task_type = task_type  # 'download', 'apply', 'backup', 'restore'
        self.data = data
        self.target_type = target_type  # 'github' 或 'replit'

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
            self.log_signal.emit(f"❌ 错误: {str(e)}")

    def download_hosts(self):
        """从网络源下载hosts规则"""
        self.log_signal.emit("📡 正在连接服务器...")
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

        for i, source in enumerate(sources):
            try:
                self.log_signal.emit(f"🔄 尝试从 {source.split('//')[1].split('/')[0]} 下载...")
                self.progress_signal.emit(20 + i * 20)

                response = requests.get(source, timeout=15)
                if response.status_code == 200:
                    self.log_signal.emit("✅ 下载成功，解析规则中...")
                    self.progress_signal.emit(80)

                    if self.target_type == 'github':
                        rules = self.extract_github_rules(response.text)
                    else:
                        rules = self.extract_replit_rules(response.text)
                    
                    self.progress_signal.emit(100)
                    self.result_signal.emit({'success': True, 'rules': rules, 'source': source})
                    return
            except Exception as e:
                self.log_signal.emit(f"⚠️  {source} 失败: {str(e)}")
                continue

        self.result_signal.emit({'success': False, 'error': '所有源都尝试失败'})

    def extract_github_rules(self, content):
        """提取GitHub相关规则"""
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

        return '\n'.join(github_rules) if github_rules else "# 未找到GitHub相关规则"

    def extract_replit_rules(self, content):
        """提取Replit相关规则"""
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

        return '\n'.join(replit_rules) if replit_rules else "# 未找到Replit相关规则"

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
        except Exception as e:
            self.result_signal.emit({'success': False, 'error': f'写入失败: {str(e)}'})

    def clean_old_rules(self, content, target_type):
        """清理旧的规则"""
        lines = content.split('\n')
        cleaned_lines = []
        in_target_section = False
        section_start = f"# {target_type.capitalize()} Hosts Start"
        section_end = f"# {target_type.capitalize()} Hosts End"

        # 根据目标类型确定要清理的域名
        if target_type == 'github':
            target_domains = ['github.com', 'github.global.ssl.fastly.net']
        else:  # replit
            target_domains = ['replit.com', 'repl.co', 'repl.it']

        for line in lines:
            stripped = line.strip()

            # 检测目标规则段开始
            if section_start in line:
                in_target_section = True
                continue

            # 检测目标规则段结束
            if section_end in line:
                in_target_section = False
                continue

            # 如果在目标段中，跳过
            if in_target_section:
                continue

            # 清理零散的目标相关规则
            if (not in_target_section and stripped and
                    not stripped.startswith('#') and
                    any(domain in stripped for domain in target_domains)):
                continue

            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def create_backup(self):
        """创建hosts备份"""
        try:
            hosts_path = self.get_hosts_path()
            backup_dir = os.path.join(os.path.dirname(__file__), 'hosts_backups')
            os.makedirs(backup_dir, exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(backup_dir, f'hosts_backup_{timestamp}')

            shutil.copy2(hosts_path, backup_path)
            self.log_signal.emit(f"✅ 备份已创建: {backup_path}")
            return True
        except Exception as e:
            self.log_signal.emit(f"❌ 备份失败: {str(e)}")
            return False

    def restore_backup(self):
        """恢复备份"""
        backup_file = self.data
        if not backup_file:
            self.result_signal.emit({'success': False, 'error': '未指定备份文件'})
            return

        try:
            self.log_signal.emit("🛡️ 检查管理员权限...")
            if not is_admin():
                self.result_signal.emit({'success': False, 'error': '需要管理员权限，请以管理员身份运行程序'})
                return

            hosts_path = self.get_hosts_path()

            # 使用临时文件安全恢复
            temp_dir = tempfile.gettempdir()
            temp_hosts = os.path.join(temp_dir, 'hosts_restore_temp')

            shutil.copy2(backup_file, temp_hosts)
            shutil.copy2(temp_hosts, hosts_path)

            # 清理临时文件
            if os.path.exists(temp_hosts):
                os.remove(temp_hosts)

            self.result_signal.emit({'success': True})
        except PermissionError as e:
            self.result_signal.emit({'success': False, 'error': f'权限拒绝: {str(e)}。请确保以管理员身份运行程序。'})
        except Exception as e:
            self.result_signal.emit({'success': False, 'error': f'恢复失败: {str(e)}'})

    def get_hosts_path(self):
        """获取hosts文件路径"""
        if os.name == 'nt':
            return r"C:\Windows\System32\drivers\etc\hosts"
        else:
            return "/etc/hosts"


class HostsManager(QMainWindow):
    """主窗口界面"""

    def __init__(self):
        super().__init__()
        self.current_rules = ""
        self.current_target = "github"  # 默认目标
        self.init_ui()
        self.check_admin_status()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("GitHub & Replit Hosts 管理工具 (PySide6 一体版)")
        self.setGeometry(300, 200, 900, 700)

        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 标题
        title_label = QLabel("GitHub & Replit Hosts 一键管理工具")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 目标选择
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("选择目标:"))
        
        self.target_combo = QComboBox()
        self.target_combo.addItem("GitHub", "github")
        self.target_combo.addItem("Replit", "replit")
        self.target_combo.currentTextChanged.connect(self.on_target_changed)
        target_layout.addWidget(self.target_combo)
        
        target_layout.addStretch()
        layout.addLayout(target_layout)

        # 管理员状态提示
        self.admin_label = QLabel()
        self.admin_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.admin_label)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # 水平布局用于按钮
        button_layout = QHBoxLayout()

        # 功能按钮
        self.btn_download = QPushButton("🔄 更新规则")
        self.btn_apply = QPushButton("💾 应用规则")
        self.btn_backup = QPushButton("📦 创建备份")
        self.btn_restore = QPushButton("⏪ 恢复备份")

        self.btn_download.clicked.connect(self.download_rules)
        self.btn_apply.clicked.connect(self.apply_rules)
        self.btn_backup.clicked.connect(self.create_backup)  # 连接到正确的方法
        self.btn_restore.clicked.connect(self.restore_backup)

        button_layout.addWidget(self.btn_download)
        button_layout.addWidget(self.btn_apply)
        button_layout.addWidget(self.btn_backup)
        button_layout.addWidget(self.btn_restore)

        layout.addLayout(button_layout)

        # 分割器用于规则显示和日志
        splitter = QSplitter(Qt.Vertical)

        # 规则显示区域
        rules_widget = QWidget()
        rules_layout = QVBoxLayout(rules_widget)
        rules_layout.addWidget(QLabel("规则显示/编辑区:"))

        self.rules_edit = QTextEdit()
        self.rules_edit.setPlaceholderText("规则将在这里显示...")
        rules_layout.addWidget(self.rules_edit)

        # 日志显示区域
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        log_layout.addWidget(QLabel("操作日志:"))

        self.log_edit = QTextEdit()
        self.log_edit.setPlaceholderText("操作日志将在这里显示...")
        self.log_edit.setMaximumHeight(200)
        log_layout.addWidget(self.log_edit)

        splitter.addWidget(rules_widget)
        splitter.addWidget(log_widget)
        splitter.setSizes([500, 200])

        layout.addWidget(splitter, 1)

        # 状态栏
        self.statusBar().showMessage("就绪")

        self.log("🚀 GitHub & Replit Hosts 管理工具已启动")

    def on_target_changed(self, text):
        """目标类型改变"""
        self.current_target = self.target_combo.currentData()
        target_name = "GitHub" if self.current_target == "github" else "Replit"
        self.log(f"🎯 已切换到 {target_name} 模式")
        self.statusBar().showMessage(f"当前目标: {target_name}")

    def check_admin_status(self):
        """检查并显示管理员状态"""
        if is_admin():
            self.admin_label.setText("✅ 当前以管理员权限运行")
            self.admin_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.admin_label.setText("⚠️ 当前未以管理员权限运行（部分功能可能受限）")
            self.admin_label.setStyleSheet("color: orange; font-weight: bold;")

    def log(self, message):
        """添加日志信息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_edit.append(f"[{timestamp}] {message}")
        self.log_edit.moveCursor(QTextCursor.End)

    def set_buttons_enabled(self, enabled):
        """启用/禁用所有按钮"""
        self.btn_download.setEnabled(enabled)
        self.btn_apply.setEnabled(enabled)
        self.btn_backup.setEnabled(enabled)
        self.btn_restore.setEnabled(enabled)

    def download_rules(self):
        """下载最新规则"""
        target_name = "GitHub" if self.current_target == "github" else "Replit"
        self.log(f"开始下载最新 {target_name} hosts 规则...")
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
        """下载结果处理"""
        if result['success']:
            self.current_rules = result['rules']
            self.rules_edit.setPlainText(self.current_rules)
            rule_count = len(self.current_rules.splitlines())
            target_name = "GitHub" if self.current_target == "github" else "Replit"
            self.log(f"✅ {target_name} 规则获取成功，共 {rule_count} 条")
            self.statusBar().showMessage(f"{target_name} 规则下载成功")
        else:
            self.log(f"❌ 规则获取失败: {result.get('error', '未知错误')}")
            self.statusBar().showMessage("下载失败")

    def apply_rules(self):
        """应用规则到hosts文件"""
        if not self.rules_edit.toPlainText().strip():
            QMessageBox.warning(self, "警告", "没有可应用的规则")
            return

        # 检查管理员权限
        if not is_admin():
            target_name = "GitHub" if self.current_target == "github" else "Replit"
            reply = QMessageBox.question(self, "需要管理员权限",
                                         f"应用{target_name}规则需要管理员权限。是否立即以管理员身份重新启动程序？",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                run_as_admin()
                sys.exit(0)
            return

        target_name = "GitHub" if self.current_target == "github" else "Replit"
        reply = QMessageBox.question(self, "确认",
                                     f"这将修改系统 hosts 文件以优化 {target_name} 访问。继续吗？",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.log(f"开始应用 {target_name} 规则到系统 hosts 文件...")
            self.set_buttons_enabled(False)

            self.current_rules = self.rules_edit.toPlainText()
            self.thread = HostsManagerThread('apply', self.current_rules, self.current_target)
            self.thread.log_signal.connect(self.log)
            self.thread.result_signal.connect(self.on_apply_result)
            self.thread.finished.connect(self.on_thread_finished)
            self.thread.start()

    def on_apply_result(self, result):
        """应用结果处理"""
        if result['success']:
            target_name = "GitHub" if self.current_target == "github" else "Replit"
            self.log(f"✅ {target_name} 规则应用成功！")
            self.log("💡 建议刷新DNS缓存: ipconfig /flushdns (Windows)")
            QMessageBox.information(self, "成功",
                                    f"{target_name} 规则应用成功！\n\n建议在命令提示符中运行: ipconfig /flushdns 来刷新DNS缓存")
            self.statusBar().showMessage(f"{target_name} 规则应用成功")
        else:
            self.log(f"❌ 规则应用失败: {result.get('error', '未知错误')}")
            QMessageBox.critical(self, "错误", f"应用失败: {result.get('error', '未知错误')}")

    def create_backup(self):
        """创建hosts备份 - 改进版本，允许用户选择备份位置"""
        try:
            # 让用户选择备份位置
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            default_backup_name = f'hosts_backup_{timestamp}'
            
            backup_file, _ = QFileDialog.getSaveFileName(
                self, 
                "选择备份文件保存位置", 
                default_backup_name,
                "All Files (*)"
            )
            
            if not backup_file:
                self.log("❌ 备份已取消")
                return

            self.log("📦 创建 hosts 文件备份...")
            self.set_buttons_enabled(False)

            # 启动线程进行备份
            self.thread = HostsManagerThread('backup')
            self.thread.log_signal.connect(self.log)
            self.thread.result_signal.connect(self.on_backup_result)
            self.thread.finished.connect(self.on_thread_finished)
            self.thread.start()

        except Exception as e:
            self.log(f"❌ 备份失败: {str(e)}")

    def on_backup_result(self, result):
        """备份结果处理"""
        self.statusBar().showMessage("备份完成")

    def restore_backup(self):
        """恢复备份"""
        # 让用户选择备份文件
        backup_file, _ = QFileDialog.getOpenFileName(
            self, "选择备份文件", "", "Backup Files (hosts_backup_*)")

        if backup_file:
            self.log(f"开始从 {backup_file} 恢复 hosts 文件...")
            self.set_buttons_enabled(False)

            self.thread = HostsManagerThread('restore', backup_file)
            self.thread.log_signal.connect(self.log)
            self.thread.result_signal.connect(self.on_restore_result)
            self.thread.finished.connect(self.on_thread_finished)
            self.thread.start()

    def on_restore_result(self, result):
        """恢复结果处理"""
        if result['success']:
            self.log("✅ 备份恢复成功！")
            QMessageBox.information(self, "成功", "备份恢复成功！")
            self.statusBar().showMessage("备份恢复成功")
        else:
            self.log(f"❌ 备份恢复失败: {result.get('error', '未知错误')}")
            QMessageBox.critical(self, "错误", f"恢复失败: {result.get('error', '未知错误')}")

    def on_thread_finished(self):
        """线程完成时的清理工作"""
        self.set_buttons_enabled(True)
        self.progress_bar.setVisible(False)


def main():
    """主函数"""
    try:
        # 检查管理员权限，如果不是管理员则请求提升
        if os.name == 'nt' and not is_admin():
            print("请求管理员权限...")
            run_as_admin()
            return 0

        app = QApplication(sys.argv)

        # 设置应用样式
        app.setStyle('Fusion')

        # 创建并显示窗口
        window = HostsManager()
        window.show()

        return app.exec()

    except Exception as e:
        print(f"应用程序错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
