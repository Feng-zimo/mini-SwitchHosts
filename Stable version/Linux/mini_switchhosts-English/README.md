# Linux 英文版本文件说明

此目录包含所有 Linux 平台英文版本的 mini-SwitchHosts 文件。

## 版本历史

### [mini_switchhosts_Linux_V2.0.plus_EN.py](file:///e:/github/mini-SwitchHosts/Stable%20version/Linux/mini_switchhosts-English/mini_switchhosts_Linux_V2.0.plus_EN.py)
- **版本**: 2.0.plus
- **发布日期**: 2025-10-26
- **主要特性**:
  - 解决了IP堆叠问题
  - 改进了规则解析和应用逻辑
  - 提升了用户体验
  - 优化了hosts文件更新机制
  - 改进了错误处理和用户反馈
  - 针对Linux系统的特殊优化

## 使用说明

1. 确保系统已安装 Python 3.6 或更高版本
2. 在终端中运行程序: `python3 mini_switchhosts_Linux_V2.0.plus_EN.py`
3. 根据需要更新和应用规则

## 注意事项

- Linux 版本可能需要特定的权限设置
- 请确保运行程序的用户具有修改 /etc/hosts 文件的权限
- 建议在使用前备份现有的 hosts 文件