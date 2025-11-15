# mini-SwitchHosts

![Logo](logo/logo.png)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-blue)](#)
[![Language](https://img.shields.io/badge/language-Python-green.svg)](#)

## Project Introduction

mini-SwitchHosts is a cross-platform Hosts management tool specifically designed to optimize access speeds for development platforms such as GitHub and Replit. By automatically fetching and updating the latest IP address mappings, this tool effectively solves slow access issues caused by DNS pollution or network latency.

This tool supports the three major mainstream operating systems: Windows, Linux, and macOS, provides bilingual interfaces in Chinese and English, and uses the PySide6 framework to build a graphical user interface that is simple and intuitive to operate.

## Features

- **Cross-platform support**: Perfectly supports Windows, Linux, and macOS systems
- **Automatic updates**: Automatically fetches the latest Hosts rules from multiple reliable sources
- **One-click application**: Simple operation to apply rules to the system Hosts file
- **Safe backup**: Automatically backs up the original Hosts file, supporting recovery at any time
- **Bilingual interface**: Provides interface language options in both Chinese and English
- **Intelligent recognition**: Automatically identifies and replaces existing related rules to avoid conflicts
- **Version update check**: Supports automatic checking for new versions and prompts for updates
- **All-in-one design**: Single executable file supports all platforms and languages

## System Requirements

- Windows 7 or higher
- Linux kernel 3.0 or higher
- macOS 10.12 or higher
- Python 3.6 or higher

## Version Series Description

Project version files are organized by series in the [Stable version](Stable%20version) directory:

### [All-in-One-Series](Stable%20version/All-in-One-Series) (Recommended)
All-in-one version series, single file supports all platforms and languages:
- [All-in-One](Stable%20version/All-in-One-Series/All-in-One) - All-in-One integrated version

### [Legacy-Series](Stable%20version/Legacy-Series)
Traditional version series, maintained separately by platform and language:
- [Windows](Stable%20version/Legacy-Series/Windows) - Windows platform version
- [Linux](Stable%20version/Legacy-Series/Linux) - Linux platform version
- [macOS](Stable%20version/Legacy-Series/macOS) - macOS platform version

Each directory contains all version files of that series, along with detailed version documentation.

## Recommended Use: All-in-One Integrated Version

To simplify usage and maintenance, we strongly recommend using the [All-in-One](Stable%20version/All-in-One-Series/All-in-One) version in [All-in-One-Series](Stable%20version/All-in-One-Series), which has the following advantages:
- Single file supports all platforms (Windows, Linux, macOS)
- Automatically adapts to system language (English, Chinese)
- Contains all functional features
- Easy to distribute and update

## Usage Instructions

1. Select a series based on your needs:
   - For convenience: Choose [All-in-One-Series](Stable%20version/All-in-One-Series)
   - For specific platform version: Choose the corresponding platform in [Legacy-Series](Stable%20version/Legacy-Series)
2. Enter the selected series directory
3. Download the required version file
4. Run the program with administrator privileges
5. Click "Update Rules" to get the latest Hosts rules
6. Click "Apply Rules" to write rules to the system Hosts file
7. It is recommended to flush the DNS cache for changes to take effect immediately

## Security Tips

- Be sure to use the latest stable version for optimal security and stability
- The program will automatically create a backup before modifying the Hosts file
- If network problems occur, you can use the "Restore Backup" function at any time

## Disclaimer

This tool is for learning and research purposes only. Please comply with relevant laws and regulations. The author assumes no responsibility for any consequences caused by using this tool.

Although this tool supports Linux and macOS platforms, versions for these platforms may not have been fully tested. The author has theoretically reviewed the relevant code, but cannot guarantee complete compatibility and stability under all system configurations. When using this tool on Linux and macOS systems, the risk is borne by the user.

## License

This project uses the MIT license. See the [LICENSE](LICENSE) file for details.

## Related Files

- [Chinese Version README](README.md)