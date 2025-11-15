# mini-SwitchHosts 插件开发官方文档

## 概述

mini-SwitchHosts 是一个用于管理和优化 hosts 文件的工具，支持 GitHub 和 Replit 等平台的访问优化。从 v3.0 版本开始，我们引入了插件系统，允许开发者扩展程序功能。

本文档将指导您如何为 mini-SwitchHosts 开发插件。

## 插件系统架构

### 插件目录结构
```
mini-SwitchHosts/
├── Stable version/
│   └── Pro-Series/
│       └── mini_switchhosts_V3.0_pro.py
├── plugins/              # 插件目录
│   ├── example_plugin.py
│   └── custom_source.py
└── PLUGIN_DEVELOPMENT.md # 本文档
```

### 插件加载机制
插件系统会自动扫描 [plugins](file://e:\github\mini-SwitchHosts\Stable%20version\Pro-Series\mini_switchhosts_V3.0_pro.py#L75-L75) 目录中的所有 `.py` 文件（排除以双下划线开头的文件），并尝试加载它们。

插件加载顺序按照文件名字母顺序进行，每个插件都会被实例化并注册到插件管理系统中。

## 开发您的第一个插件

### 1. 基本插件结构

创建一个 Python 文件，例如 `my_first_plugin.py`：

```python
class MyFirstPlugin:
    def __init__(self, parent):
        self.parent = parent
        self.name = "My First Plugin"
        self.version = "1.0"
        self.description = "我的第一个 mini-SwitchHosts 插件"

    def on_load(self):
        """插件加载时调用"""
        print(f"{self.name} 已加载")

    def on_unload(self):
        """插件卸载时调用"""
        print(f"{self.name} 已卸载")

    def execute(self):
        """插件主要功能"""
        print("执行插件功能")

def create_plugin(parent):
    """插件入口点"""
    return MyFirstPlugin(parent)
```

### 2. 插件规范要求

根据项目规范，插件必须遵循以下要求：

1. 必须提供 `create_plugin(parent)` 函数作为入口点
2. 插件实例必须包含以下属性：
   - `name`: 插件名称
   - `version`: 插件版本
   - `description`: 插件描述
3. 插件实例必须包含以下方法：
   - `on_load()`: 插件加载时调用
   - `on_unload()`: 插件卸载时调用
   - `execute()`: 插件主要功能

### 3. 插件生命周期详解

插件在 mini-SwitchHosts 中有明确的生命周期：

1. **初始化阶段**：当程序启动时，插件系统会扫描 [plugins](file://e:\github\mini-SwitchHosts\Stable%20version\Pro-Series\mini_switchhosts_V3.0_pro.py#L75-L75) 目录并导入所有插件模块
2. **创建阶段**：调用每个插件的 `create_plugin(parent)` 函数创建插件实例
3. **加载阶段**：调用每个插件实例的 `on_load()` 方法
4. **运行阶段**：插件处于活动状态，可以响应事件或执行功能
5. **卸载阶段**：当程序关闭或插件被禁用时，调用 `on_unload()` 方法
6. **销毁阶段**：插件实例被垃圾回收

## 插件API参考

### 核心API

#### `parent` 对象
传递给插件的 `parent` 参数是主应用程序窗口对象，提供了访问主程序功能的方法：

- `parent.add_menu_item(name, callback)`: 添加菜单项
- `parent.get_hosts_content()`: 获取当前 hosts 内容
- `parent.set_hosts_content(content)`: 设置 hosts 内容
- `parent.refresh_ui()`: 刷新用户界面
- `parent.get_config()`: 获取程序配置
- `parent.set_config(key, value)`: 设置程序配置项

#### 插件元数据属性
每个插件必须定义以下属性：

| 属性 | 类型 | 描述 |
|------|------|------|
| `name` | str | 插件显示名称 |
| `version` | str | 插件版本号 |
| `description` | str | 插件功能描述 |
| `author` | str (可选) | 插件作者 |
| `website` | str (可选) | 插件网站 |

### 事件系统

mini-SwitchHosts 提供了事件驱动的插件接口，插件可以监听和响应特定事件：

```python
class EventPlugin:
    def __init__(self, parent):
        self.parent = parent
        self.name = "Event Plugin"
        self.version = "1.0"
        self.description = "事件处理插件"

    def on_load(self):
        # 注册事件监听器
        self.parent.register_event_listener("hosts_changed", self.on_hosts_changed)
        self.parent.register_event_listener("before_save", self.on_before_save)

    def on_unload(self):
        # 取消注册事件监听器
        self.parent.unregister_event_listener("hosts_changed", self.on_hosts_changed)
        self.parent.unregister_event_listener("before_save", self.on_before_save)

    def on_hosts_changed(self, new_content):
        """当 hosts 内容发生变化时调用"""
        print(f"Hosts 内容已更新，新内容长度: {len(new_content)} 字符")

    def on_before_save(self, content):
        """在保存 hosts 文件之前调用"""
        # 可以修改即将保存的内容
        return content + "\n# 由 EventPlugin 添加的注释"

    def execute(self):
        print("事件插件被执行")

def create_plugin(parent):
    return EventPlugin(parent)
```

可用事件包括：
- `hosts_changed`: 当前 hosts 内容发生更改
- `before_save`: 在保存 hosts 文件之前
- `after_save`: 在保存 hosts 文件之后
- `plugin_loaded`: 当其他插件被加载时
- `plugin_unloaded`: 当其他插件被卸载时

## 高级插件功能

### 1. 扩展规则源

您可以创建插件来添加自定义规则源：

```python
class CustomSourcePlugin:
    def __init__(self, parent):
        self.parent = parent
        self.name = "Custom Source Plugin"
        self.version = "1.0"
        self.description = "添加自定义规则源"

    def get_custom_sources(self):
        """返回自定义规则源列表"""
        return [
            "https://example.com/custom-hosts.txt",
            "https://another-example.com/hosts"
        ]

    def on_load(self):
        print(f"{self.name} 已加载")

    def on_unload(self):
        print(f"{self.name} 已卸载")

    def execute(self):
        sources = self.get_custom_sources()
        print(f"可用的自定义源: {sources}")

def create_plugin(parent):
    return CustomSourcePlugin(parent)
```

### 2. 处理规则数据

您可以创建插件来处理下载的规则：

```python
class RuleProcessorPlugin:
    def __init__(self, parent):
        self.parent = parent
        self.name = "Rule Processor Plugin"
        self.version = "1.0"
        self.description = "规则处理器插件"

    def process_rules(self, rules):
        """处理规则数据"""
        # 在这里添加您的规则处理逻辑
        processed_rules = rules.replace("old-pattern", "new-pattern")
        return processed_rules

    def on_load(self):
        print(f"{self.name} 已加载")

    def on_unload(self):
        print(f"{self.name} 已卸载")

    def execute(self):
        print("规则处理器插件已执行")

def create_plugin(parent):
    return RuleProcessorPlugin(parent)
```

### 3. 添加用户界面元素

您可以创建插件来添加菜单项或工具栏按钮：

```python
from PyQt5.QtWidgets import QAction, QMessageBox

class UIExtensionPlugin:
    def __init__(self, parent):
        self.parent = parent
        self.name = "UI Extension Plugin"
        self.version = "1.0"
        self.description = "用户界面扩展插件"

    def on_load(self):
        # 添加菜单项
        self.action = QAction("我的插件功能", self.parent)
        self.action.triggered.connect(self.execute)
        self.parent.menuBar().addAction(self.action)
        print(f"{self.name} 已加载")

    def on_unload(self):
        # 移除菜单项
        self.parent.menuBar().removeAction(self.action)
        print(f"{self.name} 已卸载")

    def execute(self):
        QMessageBox.information(self.parent, "插件", "这是我的插件功能！")

def create_plugin(parent):
    return UIExtensionPlugin(parent)
```

### 4. 配置管理

插件可以拥有自己的配置项：

```python
import json
import os

class ConfigurablePlugin:
    def __init__(self, parent):
        self.parent = parent
        self.name = "Configurable Plugin"
        self.version = "1.0"
        self.description = "可配置插件示例"
        self.config_file = os.path.join(os.path.dirname(__file__), "config.json")
        self.config = {}

    def load_config(self):
        """加载插件配置"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "enabled": True,
                "custom_value": "default"
            }

    def save_config(self):
        """保存插件配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def on_load(self):
        self.load_config()
        print(f"{self.name} 已加载，配置: {self.config}")

    def on_unload(self):
        self.save_config()
        print(f"{self.name} 已卸载，配置已保存")

    def execute(self):
        print(f"使用配置: {self.config}")

def create_plugin(parent):
    return ConfigurablePlugin(parent)
```

## 插件安装和分发

### 1. 手动安装
将插件文件复制到程序的 [plugins](file://e:\github\mini-SwitchHosts\Stable%20version\Pro-Series\mini_switchhosts_V3.0_pro.py#L75-L75) 目录中，然后重启程序。

推荐的插件目录结构：
```
plugins/
├── my_plugin/
│   ├── __init__.py
│   ├── my_plugin.py
│   ├── config.json
│   └── README.md
└── another_plugin.py
```

### 2. 在线安装
用户可以通过程序的插件管理界面，输入插件的 URL 进行安装。

插件包应遵循以下格式：
```
my_plugin.zip
├── manifest.json     # 插件清单文件
├── my_plugin.py      # 插件主文件
├── config.json       # 默认配置文件（可选）
└── README.md         # 插件说明文档（可选）
```

manifest.json 示例：
```json
{
  "name": "My Plugin",
  "version": "1.0.0",
  "description": "这是一个示例插件",
  "author": "开发者姓名",
  "website": "https://example.com",
  "main": "my_plugin.py",
  "dependencies": []
}
```

## 最佳实践

### 1. 错误处理
始终包含适当的错误处理：

```python
def execute(self):
    try:
        # 您的插件逻辑
        pass
    except Exception as e:
        print(f"插件执行出错: {e}")
        # 可选：记录日志或通知用户
        self.parent.show_error_message(f"插件错误: {str(e)}")
```

### 2. 资源管理
确保正确管理插件使用的资源：

```python
def on_load(self):
    # 创建临时文件或分配资源
    self.temp_file = tempfile.NamedTemporaryFile(delete=False)

def on_unload(self):
    # 清理资源
    if hasattr(self, 'temp_file') and os.path.exists(self.temp_file.name):
        os.remove(self.temp_file.name)
```

### 3. 兼容性
确保插件与不同版本的 mini-SwitchHosts 兼容：

```python
def on_load(self):
    # 检查主程序版本
    if hasattr(self.parent, 'version'):
        main_version = self.parent.version
        if main_version < "3.0":
            print("警告：此插件需要 mini-SwitchHosts 3.0 或更高版本")
```

### 4. 性能优化
对于可能耗时的操作，应该在后台线程中执行：

```python
from PyQt5.QtCore import QThread, pyqtSignal

class WorkerThread(QThread):
    finished = pyqtSignal(str)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
    
    def run(self):
        # 执行耗时操作
        result = self.download_data(self.url)
        self.finished.emit(result)

class PerformancePlugin:
    def __init__(self, parent):
        self.parent = parent
        self.name = "Performance Plugin"
        self.version = "1.0"
        self.description = "高性能插件示例"
    
    def execute(self):
        # 启动后台线程执行耗时操作
        self.thread = WorkerThread("https://example.com/data")
        self.thread.finished.connect(self.on_work_finished)
        self.thread.start()
    
    def on_work_finished(self, result):
        print(f"后台任务完成，结果: {result}")
    
    def on_load(self):
        pass
    
    def on_unload(self):
        if hasattr(self, 'thread') and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()

def create_plugin(parent):
    return PerformancePlugin(parent)
```

## 调试插件

1. 使用 `print()` 语句输出调试信息
2. 查看程序日志
3. 使用 Python 调试器 (pdb)

### 调试技巧

```python
import traceback

def execute(self):
    try:
        # 你的代码
        pass
    except Exception as e:
        # 输出详细的错误信息
        print(f"插件执行出错: {e}")
        traceback.print_exc()
```

## 发布插件

插件发布有两种主要方式：

### 1. 自托管发布
您可以将插件托管在自己的服务器上，让用户通过直接输入插件URL进行安装：
1. 将插件打包成ZIP格式
2. 上传到您的Web服务器
3. 提供直接下载链接给用户

### 2. 提交到官方仓库
您可以将高质量的插件提交到mini-SwitchHosts官方插件仓库，让更多用户受益：
1. Fork官方插件仓库
2. 按照规范提交您的插件
3. 创建Pull Request等待审核

推荐的插件发布检查清单：
- [ ] 插件遵循命名规范
- [ ] 包含完整的文档说明
- [ ] 提供示例配置和使用方法
- [ ] 经过充分测试，无明显bug
- [ ] 包含开源许可证信息
- [ ] 支持最新版本的mini-SwitchHosts
- [ ] 提供多语言支持（如果适用）

### 插件质量标准
为了确保插件质量和用户体验，官方推荐插件应满足以下标准：
- 代码结构清晰，注释完整
- 不包含恶意代码或隐私收集功能
- 具备良好的错误处理机制
- 对系统资源占用合理
- 提供详细的使用说明

## 常见问题

### Q: 插件没有加载
A: 检查插件文件是否在 [plugins](file://e:\github\mini-SwitchHosts\Stable%20version\Pro-Series\mini_switchhosts_V3.0_pro.py#L75-L75) 目录中，以及是否包含正确的 `create_plugin` 函数。

### Q: 插件功能未执行
A: 检查是否正确实现了 `execute` 方法，并且插件已成功加载。

### Q: 如何调试插件错误？
A: 使用 `print()` 输出调试信息，查看控制台输出，或使用 `traceback` 模块获取详细的错误堆栈。

### Q: 插件如何与其他插件交互？
A: 可以通过主程序的事件系统进行通信，或者通过共享配置进行协作。

## API 参考手册

### 主程序 API

| 方法 | 参数 | 返回值 | 描述 |
|------|------|--------|------|
| `add_menu_item(name, callback)` | name: 菜单项名称, callback: 回调函数 | None | 添加全局菜单项 |
| `get_hosts_content()` | 无 | str | 获取当前 hosts 文件内容 |
| `set_hosts_content(content)` | content: 新的 hosts 内容 | bool | 设置 hosts 文件内容 |
| `refresh_ui()` | 无 | None | 刷新用户界面 |
| `get_config()` | 无 | dict | 获取程序配置 |
| `set_config(key, value)` | key: 配置键, value: 配置值 | None | 设置程序配置项 |
| `register_event_listener(event, callback)` | event: 事件名, callback: 回调函数 | None | 注册事件监听器 |
| `unregister_event_listener(event, callback)` | event: 事件名, callback: 回调函数 | None | 取消注册事件监听器 |
| `show_message(title, message)` | title: 标题, message: 消息内容 | None | 显示信息对话框 |
| `show_error_message(message)` | message: 错误消息 | None | 显示错误对话框 |

### 插件标准方法

| 方法 | 参数 | 返回值 | 描述 |
|------|------|--------|------|
| `on_load()` | 无 | None | 插件加载时调用 |
| `on_unload()` | 无 | None | 插件卸载时调用 |
| `execute()` | 无 | None | 插件主要功能入口 |

## 联系我们

如果您有任何问题或建议，请通过以下方式联系我们：
- GitHub Issues: [https://github.com/Feng-zimo/mini-SwitchHosts]
- 邮箱: [feng_to_zhang@163.com]

感谢您为 mini-SwitchHosts 开发插件！