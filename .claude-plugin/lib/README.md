# 可复用插件库

本目录包含 Claude Code 插件系统的所有可复用库。

## 架构

```
.claude-plugin/
├── lib/                           # 所有可复用库（本目录）
│   ├── __init__.py
│   ├── README.md
│   ├── permission/                # 权限评估逻辑
│   │   ├── __init__.py
│   │   ├── determine.py           # 主要权限判定
│   │   ├── rules.py               # 规则匹配逻辑
│   │   ├── parser.py              # Hook 输入解析
│   │   └── strips.py              # 命令规范化
│   ├── local_config.py            # 带缓存的 YAML 配置加载器
│   ├── local_config.md            # 本地配置文档
│   ├── local_config_io.py         # 共享的 YAML 文件发现/解析
│   ├── local_config_io.md         # 共享 I/O 文档
│   ├── workflow.py                # Handsoff 工作流定义
│   ├── logger.py                  # 调试日志工具
│   ├── session_utils.py           # 会话目录路径解析
│   ├── session_utils.md           # 会话工具文档
│   ├── telegram_utils.py          # Telegram Bot API 辅助函数
│   └── telegram_utils.md          # Telegram 工具文档
├── hooks/                         # 仅入口（从 lib/ 导入）
└── ...
```

## 设计原则

**关注点分离：**
- `hooks/` = 由 Claude Code 调用的入口
- `lib/` = 由 hook 和 server 共享的可复用库

**依赖方向：**
- `hooks/` → `lib/`
- `server/` → `lib/`
- `lib/` 模块之间可以相互依赖

## 模块

### permission/

PreToolUse hook 的工具权限评估。提供基于规则的匹配、Haiku LLM 回退和 Telegram 审批集成。

**入口：** `from lib.permission import determine`

### local_config.py

`.agentize.local.yaml` 的本地配置加载器。供 hook 读取 handsoff、Telegram 及其他开发者专属设置。

**YAML 搜索顺序：**
1. 从当前目录向上查找 `.agentize.local.yaml`
2. `$AGENTIZE_HOME/.agentize.local.yaml`
3. `$HOME/.agentize.local.yaml`（用户级，由安装程序创建）

**用法：**
```python
from lib.local_config import get_local_value, coerce_bool, coerce_int

# 从 YAML 获取 handsoff 启用状态
enabled = get_local_value('handsoff.enabled', True, coerce_bool)

# 获取 Telegram token
token = get_local_value('telegram.token', '')
```

详情请参阅 [local_config.md](local_config.md)。

### local_config_io.py

`.agentize.local.yaml` 的共享 YAML 文件发现和解析辅助函数。同时供 `local_config.py`（hook）和 server 的 `runtime_config.py` 使用，以确保一致的文件查找行为。

**注意：** 本模块不缓存结果。缓存由调用方处理：
- `local_config.py` 为 hook 做缓存（避免重复 I/O）
- `runtime_config.py` 不做缓存（server 每次轮询都需要最新配置）

**用法：**
```python
from lib.local_config_io import find_local_config_file, parse_yaml_file

# 使用标准搜索顺序查找配置文件
config_path = find_local_config_file(start_dir)

# 解析 YAML 文件
config = parse_yaml_file(config_path)
```

详情请参阅 [local_config_io.md](local_config_io.md)。

### workflow.py

handsoff 模式的统一工作流定义。集中了工作流检测、issue 提取和续接提示词。

**自包含设计：** 本模块包含自己的 `_run_acw()` 辅助函数，通过本地符号链接（`lib/acw.sh` → `src/cli/acw.sh`）调用 `acw` shell 函数，无需从 `agentize.shell` 导入或依赖 `setup.sh`。根据 [Claude Code 插件文档](https://code.claude.com/docs/en/plugins-reference#working-with-external-dependencies)，该符号链接在插件缓存复制时会被解析，使插件在安装时自包含。

**用法：**
```python
from lib.workflow import detect_workflow, get_continuation_prompt
```

### logger.py

hook 的调试日志工具。当启用 `HANDSOFF_DEBUG` 或 `handsoff.debug` 时，以统一格式将权限决策记录到 `.tmp/hooked-sessions/permission.txt`。

**用法：**
```python
from lib.logger import logger, log_tool_decision
```

### session_utils.py

hook 的共享会话工具：目录路径解析、handsoff 模式检查和 issue 索引文件管理。

**用法：**
```python
from lib.session_utils import session_dir, is_handsoff_enabled, write_issue_index

# 会话目录路径解析
path = session_dir()              # 获取路径但不创建
path = session_dir(makedirs=True) # 获取路径并创建目录

# Handsoff 模式检查（从 YAML 读取，支持环境变量覆盖）
if not is_handsoff_enabled():
    sys.exit(0)  # handsoff 禁用时跳过 hook

# issue 索引文件创建
write_issue_index(session_id, issue_no, workflow, sess_dir=sess_dir)
```

### telegram_utils.py

共享的 Telegram Bot API 辅助函数，包括 HTML 转义和 HTTP 请求处理。

**用法：**
```python
from lib.telegram_utils import escape_html, telegram_request
```

## 导入模式

### 从 hook 导入（在 .claude-plugin/hooks/ 中）

```python
import sys
from pathlib import Path

# 将 .claude-plugin 加入路径
plugin_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(plugin_dir))

from lib.permission import determine
from lib.workflow import detect_workflow
from lib.logger import logger
```

### 从 server 导入（在 python/agentize/server/ 中）

```python
import sys
from pathlib import Path

# 将 .claude-plugin 加入路径
repo_root = Path(__file__).resolve().parents[3]
plugin_dir = repo_root / ".claude-plugin"
sys.path.insert(0, str(plugin_dir))

from lib.telegram_utils import escape_html, telegram_request
```
