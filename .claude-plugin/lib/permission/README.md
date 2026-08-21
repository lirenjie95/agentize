# Permission 模块

本模块为 PreToolUse hook 提供权限判定逻辑。

## 用途

使用规则、Haiku LLM 回退以及可选的 Telegram 审批集成来评估工具权限请求。为 Claude Code 的工具使用返回 `allow`、`deny` 或 `ask` 决策。

只读观察工具（`Grep`、`Glob`、`LSP`、`Monitor`）被硬编码为 `allow`，因为它们无法改变状态。

## 文件

| 文件 | 用途 |
|------|---------|
| `__init__.py` | 导出 `determine()` 函数 |
| `determine.py` | 主入口和编排逻辑 |
| `rules.py` | 权限规则定义和匹配 |
| `parser.py` | Hook 输入解析和目标提取 |
| `strips.py` | Bash 命令规范化（环境变量、shell 前缀） |

## 集成

由 `.claude/hooks/pre-tool-use.py` 调用，后者是一个薄封装：

```python
from agentize.permission import determine
result = determine(sys.stdin.read())
```

## 规则来源

权限规则来自多个来源，按以下顺序评估：

1. **硬编码规则**（`rules.py`）- `PERMISSION_RULES` 字典中的内置规则。此处的 deny 规则始终优先。
2. **项目规则**（`.agentize.yaml`）- `permissions.allow` 和 `permissions.deny` 下的团队共享规则
3. **本地规则**（`.agentize.local.yaml`）- `permissions.allow` 和 `permissions.deny` 下的开发者专属规则

YAML 规则使用字符串或字典的数组：
- 字符串：`"^pattern"` → 默认匹配 Bash 工具
- 字典：`{pattern: "^pattern", tool: "Read"}` → 显式指定工具

规则语法请参阅 `.claude/hooks/pre-tool-use.md`，完整细节请参阅 `docs/feat/permissions/rules.md`。
