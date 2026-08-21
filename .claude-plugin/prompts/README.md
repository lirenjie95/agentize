# Prompts 目录

工作流续接提示词的外部模板文件。将提示词内容与代码逻辑分离可以提高可维护性，并便于对提示词文本进行迭代。

## 模板格式

每个工作流都有一个以工作流命名的对应 `.txt` 文件（例如 ultra-planner 工作流对应 `ultra-planner.txt`）。

### 变量语法

模板使用 `{#variable#}` 语法，通过 Python 的 `str.replace()` 进行替换：

| 变量 | 描述 |
|----------|-------------|
| `{#session_id#}` | 当前 Claude Code 会话 ID，用于 `claude -r` 恢复 |
| `{#fname#}` | handsoff 会话状态 JSON 文件路径 |
| `{#continuations#}` | 当前续接计数 |
| `{#max_continuations#}` | 允许的最大续接次数 |
| `{#pr_no#}` | PR 编号（sync-master 工作流使用） |
| `{#plan_context#}` | 可选的计划上下文（issue-to-impl 工作流使用） |

### 为什么用 `{#...#}` 而不是 `{...}`？

`{#variable#}` 分隔符可避免与以下语法冲突：
- Python 格式化字符串（`{variable}`）
- Shell 变量（`$variable`、`${variable}`）
- JSON/jq 语法（`{...}`）
- 包含这些语法的 Markdown 代码块

## 模板文件

| 文件 | 工作流 | 用途 |
|------|----------|---------|
| `ultra-planner.txt` | `/ultra-planner` | 基于多 agent 辩论的规划 |
| `issue-to-impl.txt` | `/issue-to-impl` | 从 issue 到 PR 的完整开发周期 |
| `plan-to-issue.txt` | `/plan-to-issue` | 创建 GitHub [plan] issue |
| `setup-viewboard.txt` | `/setup-viewboard` | GitHub Projects v2 看板设置 |
| `sync-master.txt` | `/sync-master` | 将本地 main/master 与上游同步 |

## 用法

模板由 `workflow.py::get_continuation_prompt()` 和 `workflow.py::_ask_supervisor_for_guidance()` 加载。公共 API 保持不变——调用方继续使用 `get_continuation_prompt(workflow, ...)`，无需了解模板文件的存在。
