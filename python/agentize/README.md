# Agentize Python 包

面向 AI 驱动的软件工程工作流的 Python SDK。

## 结构

```
python/agentize/
├── __init__.py           # 包根目录
├── cli.py                # Python CLI 入口（python -m agentize.cli）
├── cli.md                # CLI 接口文档
├── shell.py              # 共享的 shell 函数调用工具
├── usage.py              # Claude Code token 用量统计
├── workflow/             # Python planner + impl 工作流编排
│   └── impl/             # issue 到实现的工作流（lol impl）
└── server/               # 轮询服务器模块
    └── __main__.py       # 服务器入口（python -m agentize.server）
```

**注意**：共享工具（permission、workflow、telegram_utils、logger）已合并至 `.claude-plugin/lib/`。详情请参阅 [.claude-plugin/lib/README.md](../../.claude-plugin/lib/README.md)。

## 用法

### CLI 入口

```bash
python -m agentize.cli <command> [options]
```

Python CLI 通过共享的 `shell.py` 模块（已设置 `AGENTIZE_HOME`）将大多数命令委托给 shell 函数。`impl` 命令运行 Python 工作流实现。接口详情请参阅 `cli.md`。

### Shell 工具

```python
from agentize.shell import get_agentize_home, run_shell_function

# 自动检测 AGENTIZE_HOME
home = get_agentize_home()

# 在已设置 AGENTIZE_HOME 的情况下运行 shell 函数
result = run_shell_function("wt spawn 123", capture_output=True)
print(result.returncode, result.stdout)
```

`shell.py` 模块为从 Python 调用 shell 函数提供了统一接口。它负责 `AGENTIZE_HOME` 的自动检测，并在运行命令前 source `setup.sh`。

### Permission 模块

Permission 模块已迁移至 `.claude-plugin/lib/permission/`。用法请参阅 lib README：

```python
# 从 lib 导入（将 .claude-plugin 加入 sys.path 之后）
from lib.permission import determine
```

## Server 模块

Server 模块（`python -m agentize.server`）从 `.claude-plugin/lib/` 导入共享工具，用于 Telegram 通知。
