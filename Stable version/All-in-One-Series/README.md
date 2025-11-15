,# All-in-One 一体化版本说明

![Logo](../../../logo/logo.png)

此目录包含 mini-SwitchHosts 的 All-in-One 一体化版本，支持所有主流操作系统和多语言界面。

## 目录结构

### [All-in-One](All-in-One)
基于 PySide6 框架的 All-in-One 版本

### [PyQt-All-in-one-Series](PyQt-All-in-one-Series)
基于 PyQt 框架的 All-in-One 版本

### [Terminal-All-in-One](Terminal-All-in-One)
命令行版本，适用于服务器环境或自动化脚本使用

## 版本历史

### v3.5 版本 (最新)
- **主要特性**:
  - 插件系统，支持功能扩展
  - 高级规则管理功能
  - 暗色主题支持
  - 增强的IP解析算法
  - 智能规则过滤功能
  - 增量更新机制
  - 现代化UI界面，参考PyCharm的Git界面风格
  - 实时状态监控
  - 一键备份恢复功能
  - 并发处理能力

### v3.0 版本
- **主要特性**:
  - 增强的IP解析算法
  - 智能规则过滤功能
  - 增量更新机制
  - 现代化UI界面，参考PyCharm的Git界面风格
  - 实时状态监控
  - 一键备份恢复功能
  - 自动更新检查功能
  - 并发处理能力

## 系统要求

- Windows 7 或更高版本
- Linux 内核 3.0 或更高版本
- macOS 10.12 或更高版本
- Python 3.6 或更高版本

## 使用说明

1. 确保系统已安装 Python 3.6 或更高版本
2. 选择需要的版本目录（PySide6 或 PyQt）
3. 在终端或命令提示符中运行程序:
   - Windows: `python [版本文件名].py` 或双击运行
   - Linux/macOS: `python3 [版本文件名].py` (可能需要使用 sudo)
4. 程序会自动检测系统语言并显示相应界面
5. 点击"更新规则"获取最新 Hosts 规则
6. 点击"应用规则"将规则写入系统 Hosts 文件
7. 建议刷新 DNS 缓存以使更改立即生效

## CLI 命令行版本

我们还提供了一个命令行版本 ([Terminal-All-in-One](Terminal-All-in-One))，适用于服务器环境或自动化脚本使用。

### CLI 版本特性：
- 无图形界面，纯命令行操作
- 支持所有平台（Windows、Linux、macOS）
- 包含所有核心功能（下载、应用、备份、恢复规则）
- 支持命令行参数，便于脚本集成
- 支持从文件读取规则或下载最新规则

### CLI 使用方法：
```bash
# 查看帮助
python mini_switchhosts_V3.5_Terminal.py -h

# 下载并应用 GitHub 规则
python mini_switchhosts_V3.5_Terminal.py -d -a

# 下载并应用 Replit 规则
python mini_switchhosts_V3.5_Terminal.py -d -a -t replit

# 仅创建备份
python mini_switchhosts_V3.5_Terminal.py -b

# 从备份恢复
python mini_switchhosts_V3.5_Terminal.py -r

# 使用本地规则文件
python mini_switchhosts_V3.5_Terminal.py -a --rules my_rules.txt
```

## PyQt CLI 命令行版本

我们也提供了一个基于 PyQt 的命令行版本 ([mini_switchhosts_V3.5_pyqt_cli.py](file:///e:/github/mini-SwitchHosts/Stable%20version/All-In-One-Series/mini_switchhosts_V3.5_pyqt_cli.py))，它与 PyQt GUI 版本共享相同的依赖库。

### PyQt CLI 版本特性：
- 无图形界面，纯命令行操作
- 与 PyQt GUI 版本共享依赖库
- 支持所有核心功能（下载、应用、备份、恢复规则）
- 支持命令行参数，便于脚本集成

### PyQt CLI 使用方法：
```bash
# 查看帮助
python mini_switchhosts_V3.5_pyqt_cli.py -h

# 下载并应用 GitHub 规则
python mini_switchhosts_V3.5_pyqt_cli.py -d -a

# 下载并应用 Replit 规则
python mini_switchhosts_V3.5_pyqt_cli.py -d -a -t replit

# 仅创建备份
python mini_switchhosts_V3.5_pyqt_cli.py -b

# 从备份恢复
python mini_switchhosts_V3.5_pyqt_cli.py -r

# 使用本地规则文件
python mini_switchhosts_V3.5_pyqt_cli.py -a --rules my_rules.txt
```

## 多语言支持

程序会自动检测系统语言并显示相应界面：
- 如果系统语言为英语，显示英文界面
- 如果系统语言为中文，显示中文界面
- 也可以在程序中手动切换语言

## 跨平台兼容性

### Windows
- 支持 Windows 7 及以上所有版本
- 自动请求管理员权限
- 支持 Windows 11 特性优化

### Linux
- 支持主流 Linux 发行版 (Ubuntu, CentOS, Debian 等)
- 需要使用 sudo 运行以获取管理员权限
- 适配不同 Linux 发行版的特性

### macOS
- 支持 macOS 10.12 及以上版本
- 兼容 Apple Silicon 芯片
- 适配 macOS 系统权限机制

## 安全提示

- 程序在修改 Hosts 文件前会自动创建备份
- 如遇到网络问题，可随时使用"恢复备份"功能
- 建议定期检查和更新规则以确保最佳效果

## 版本优势

相比于分别维护不同平台和语言的版本，All-in-One 版本具有以下优势：
1. **统一维护**: 只需维护一个代码库，减少维护成本
2. **功能一致**: 所有平台和语言版本功能完全一致
3. **易于分发**: 用户只需下载一个文件即可使用
4. **自动适配**: 自动适配不同平台和语言环境
5. **更新便捷**: 更新时只需替换一个文件

## 故障排除

### Windows
- 如果程序无法获取管理员权限，请右键选择"以管理员身份运行"

### Linux/macOS
- 如果遇到权限问题，请使用 sudo 运行程序:
  ```
  sudo python3 [版本文件名].py
  ```

### 通用问题
- 如果程序无法连接网络，请检查防火墙设置
- 如果规则应用失败，请检查杀毒软件是否阻止了操作