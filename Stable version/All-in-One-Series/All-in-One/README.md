# All-in-One 一体化版本说明

此目录包含 mini-SwitchHosts 的 All-in-One 一体化版本，支持所有主流操作系统和多语言界面。

## 文件说明

### [mini_switchhosts_V3.0_all_in_one.py](file:///e:/github/mini-SwitchHosts/Stable%20version/All-in-One-Series/All-in-One/mini_switchhosts_V3.0_all_in_one.py)
- **版本**: 3.0 All-in-One
- **发布日期**: 2025-11-14
- **主要特性**:
  - 跨平台支持：Windows、Linux、macOS
  - 多语言界面：自动检测系统语言，支持英文和中文
  - 增强的IP解析算法，提高IP地址获取的准确性和速度
  - 智能规则过滤功能，自动过滤无效或低质量的Hosts规则
  - 增量更新机制，只更新变化的部分，提高更新效率
  - 现代化UI界面，参考PyCharm的Git界面风格，更加清晰专业
  - 实时状态监控，显示实时更新进度和系统状态
  - 一键备份恢复功能，简化备份和恢复操作流程
  - 自动更新检查功能，支持检查GitHub最新版本
  - 并发处理能力，支持多线程并发处理多个域名解析请求

## 系统要求

- Windows 7 或更高版本
- Linux 内核 3.0 或更高版本
- macOS 10.12 或更高版本
- Python 3.6 或更高版本

## 使用说明

1. 确保系统已安装 Python 3.6 或更高版本
2. 在终端或命令提示符中运行程序:
   - Windows: `python mini_switchhosts_V3.0_all_in_one.py` 或双击运行
   - Linux/macOS: `python3 mini_switchhosts_V3.0_all_in_one.py` (可能需要使用 sudo)
3. 程序会自动检测系统语言并显示相应界面
4. 点击"更新规则"获取最新 Hosts 规则
5. 点击"应用规则"将规则写入系统 Hosts 文件
6. 建议刷新 DNS 缓存以使更改立即生效

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
  sudo python3 mini_switchhosts_V3.0_all_in_one.py
  ```

### 通用问题
- 如果程序无法连接网络，请检查防火墙设置
- 如果规则应用失败，请检查杀毒软件是否阻止了操作