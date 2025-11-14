# mini-SwitchHosts

![Logo](logo/logo.png)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-blue)](#)
[![Language](https://img.shields.io/badge/language-Python-green.svg)](#)

## 项目简介

mini-SwitchHosts 是一个跨平台的 Hosts 管理工具，专门用于优化 GitHub 和 Replit 等开发平台的访问速度。通过自动获取并更新最新的 IP 地址映射，该工具能够有效解决因 DNS 污染或网络延迟导致的访问缓慢问题。

本工具支持 Windows、Linux 和 macOS 三大主流操作系统，提供中英文双语界面，采用 PySide6 框架构建图形用户界面，操作简单直观。

## 功能特点

- **跨平台支持**：完美支持 Windows、Linux 和 macOS 系统
- **自动更新**：从多个可靠源自动获取最新的 Hosts 规则
- **一键应用**：简单操作即可将规则应用到系统 Hosts 文件
- **安全备份**：自动备份原有 Hosts 文件，支持随时恢复
- **双语界面**：提供中文和英文两种界面语言选择
- **智能识别**：自动识别并替换已存在的相关规则，避免冲突
- **版本更新检查**：支持自动检查新版本并提示更新
- **一体化设计**：单一可执行文件支持所有平台和语言

## 系统要求

- Windows 7 或更高版本
- Linux 内核 3.0 或更高版本
- macOS 10.12 或更高版本
- Python 3.6 或更高版本

## 版本系列说明

项目版本文件按系列组织在 [Stable version](Stable%20version) 目录中：

### [All-in-One-Series](Stable%20version/All-in-One-Series)（推荐使用）
一体化版本系列，单一文件支持所有平台和语言：
- [All-in-One](Stable%20version/All-in-One-Series/All-in-One) - All-in-One 一体化版本

### [Legacy-Series](Stable%20version/Legacy-Series)
传统版本系列，按平台和语言分别维护：
- [Windows](Stable%20version/Legacy-Series/Windows) - Windows 平台版本
- [Linux](Stable%20version/Legacy-Series/Linux) - Linux 平台版本
- [macOS](Stable%20version/Legacy-Series/macOS) - macOS 平台版本

每个目录中包含该系列的所有版本文件，以及详细的版本说明文档。

## 推荐使用：All-in-One 一体化版本

为了简化使用和维护，我们强烈推荐使用 [All-in-One-Series](Stable%20version/All-in-One-Series) 中的 [All-in-One](Stable%20version/All-in-One-Series/All-in-One) 版本，该版本具有以下优势：
- 单一文件支持所有平台（Windows、Linux、macOS）
- 自动适配系统语言（英文、中文）
- 包含所有功能特性
- 易于分发和更新

## 使用说明

1. 根据您的需求选择系列：
   - 追求便捷性：选择 [All-in-One-Series](Stable%20version/All-in-One-Series)
   - 需要特定平台版本：选择 [Legacy-Series](Stable%20version/Legacy-Series) 中的对应平台
2. 进入选择的系列目录
3. 下载需要的版本文件
4. 以管理员权限运行程序
5. 点击"更新规则"获取最新 Hosts 规则
6. 点击"应用规则"将规则写入系统 Hosts 文件
7. 建议刷新 DNS 缓存以使更改立即生效

## 安全提示

- 请务必使用最新稳定版本，以获得最佳安全性和稳定性
- 在修改 Hosts 文件前，程序会自动创建备份
- 如遇到网络问题，可随时使用"恢复备份"功能

## 免责声明

本工具仅用于学习和研究目的，请遵守相关法律法规。使用本工具造成的任何后果，作者不承担任何责任。

尽管本工具支持 Linux 和 macOS 平台，但这些平台的版本可能未经过充分测试。作者已对相关代码进行了理论审查，但无法保证在所有系统配置下的完全兼容性和稳定性。在 Linux 和 macOS 系统上使用本工具时，风险由用户自行承担。

## 许可证

本项目采用 MIT 许可证，详情请见 [LICENSE](LICENSE) 文件。