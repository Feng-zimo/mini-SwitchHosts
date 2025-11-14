# 项目文件命名规范

## Python源文件命名规范

所有发布文件需按格式命名：`项目名_系统标识_版本信息_语言标识.py`

### 组成部分说明

1. **项目名**：`mini_switchhosts`（全小写，单词间用下划线分隔）
2. **系统标识**：
   - Windows系统：`Windows`
   - Linux系统：`Linux`
   - macOS系统：`macOS`
3. **版本信息**：`V主版本号.次版本号` 或 `V主版本号.次版本号.plus`（plus表示增强版）
4. **语言标识**：
   - 英文版本：`EN`
   - 简体中文版本：`ZH`

### 示例

正确的命名示例：
- `mini_switchhosts_Windows_V2.0_EN.py`
- `mini_switchhosts_Linux_V2.0.plus_ZH.py`
- `mini_switchhosts_macOS_V3.0_EN.py`
- `mini_switchhosts_Windows_V3.0_ZH.py`

## 目录结构规范

```
项目根目录/
├── Stable version/
│   ├── Windows/
│   │   ├── mini_switchhosts-English/
│   │   │   ├── mini_switchhosts_Windows_V2.0_EN.py
│   │   │   ├── mini_switchhosts_Windows_V2.0.plus_EN.py
│   │   │   └── mini_switchhosts_Windows_V3.0_EN.py
│   │   └── mini_switchhosts-简体中文/
│   │       ├── mini_switchhosts_Windows_V2.0_ZH.py
│   │       ├── mini_switchhosts_Windows_V2.0.plus_ZH.py
│   │       └── mini_switchhosts_Windows_V3.0_ZH.py
│   ├── Linux/
│   │   ├── mini_switchhosts-English/
│   │   │   └── 符合命名规范的.py文件
│   │   └── mini_switchhosts-简体中文/
│   │       └── 符合命名规范的.py文件
│   └── macOS/
│       ├── mini_switchhosts-English/
│       │   └── 符合命名规范的.py文件
│       └── mini_switchhosts-简体中文/
│           └── 符合命名规范的.py文件
└── beta/
    └── README.md （说明beta版本的用途和注意事项）
```

## 不符合规范的命名示例

以下命名方式应该避免：
- 使用连字符(-)替代下划线(_)：`mini-switchhosts-Windows-V2.0-EN.py`
- 大小写混用：`Mini_SwitchHosts_WINDOWS_V2.0_en.py`
- 版本信息格式不统一：`V2.0.plus` 应该为 `V2.0.plus`

## 可执行文件打包输出路径规范

打包输出路径按平台和语言分类：`--distpath "dist/平台/语言代码"`
例如：`--distpath "dist/Windows/EN"`

## 可执行文件打包参数规范

使用PyInstaller打包时需指定以下参数：
- `--onefile`（单文件打包）
- `--windowed`（无控制台窗口）
- `--name`（自定义名称）