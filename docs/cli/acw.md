# acw - Agent CLI Wrapper

用于调用多种 AI CLI 工具的统一文件式接口。

## 概要

```bash
acw [--chat [session-id]] [--editor] [--stdout] <cli-name> <model-name> [<input-file>] [<output-file>] [cli-options...]
acw --chat-list
acw --complete <topic>
acw --help
```

## 描述

`acw` 为调用不同的 AI CLI 工具（claude、codex、opencode、cursor/agent、kimi）提供一致的接口，输入/输出均基于文件。可选标志允许使用编辑器输入和 stdout 输出，同时保留默认的基于文件的工作流。Python 工作流通过 `agentize.workflow.api.acw` 包装 `acw`，以保持相同的调用语义和计时日志。

## 参数

| 参数 | 是否必需 | 描述 |
|----------|----------|-------------|
| `cli-name` | 是 | 提供方名称：`claude`、`codex`、`opencode`、`cursor`、`kimi`、`gemini` |
| `model-name` | 是 | 传递给提供方的模型标识符（Kimi 会忽略此参数并使用其默认模型） |
| `input-file` | 条件必需 | 包含提示词的文件路径（除非使用 `--editor`，否则必需） |
| `output-file` | 条件必需 | 响应写入的文件路径（除非使用 `--stdout`，否则必需） |
| `cli-options` | 否 | 传递给提供方 CLI 的附加选项 |

## 选项

| 选项 | 描述 |
|--------|-------------|
| `--chat [session-id]` | 开始或继续一个聊天会话。若未提供 ID 则创建新会话。 |
| `--chat-list` | 列出可用的聊天会话并退出。 |
| `--editor` | 使用 `$EDITOR` 创建输入内容（与 `input-file` 互斥） |
| `--stdout` | 将输出写入 stdout（与 `output-file` 互斥）。不与 `--chat` 组合时，将提供方的 stderr 合并进 stdout。与 `--chat` 组合时，提供方的 stderr 会写入 `<session-id>.stderr` 附属文件，且当 stdout 是 TTY 时 `--editor` 会将提示词回显到 stdout。 |
| `--complete <topic>` | 打印给定主题的补全值 |
| `--help` | 显示帮助文本 |

## 支持的提供方

| 提供方 | CLI 二进制 | 状态 |
|----------|------------|--------|
| `claude` | `claude` | 完整支持 |
| `codex` | `codex` | 完整支持 |
| `opencode` | `opencode` | 尽力支持 |
| `cursor` | `agent` | 尽力支持 |
| `kimi` | `kimi` | 尽力支持 |
| `gemini` | `gemini` | 尽力支持 |

## 退出码

| 退出码 | 描述 |
|------|-------------|
| 0 | 成功 |
| 1 | 缺少必需参数 |
| 2 | 未知的提供方 |
| 3 | 输入文件不存在或不可读 |
| 4 | 提供方 CLI 二进制文件未找到 |
| 5 | 聊天会话错误（ID 无效、文件缺失或格式错误） |
| 127 | 提供方执行失败 |

## 示例

### 基本用法

```bash
# 使用提示词文件调用 Claude
acw claude claude-sonnet-4-20250514 prompt.txt response.txt
# 文件模式下，提供方的 stderr 会写入 response.txt.stderr

# 调用 Codex
acw codex gpt-4o prompt.txt response.txt

# 调用 Kimi（model-name 会被忽略；Kimi 使用其默认模型）
acw kimi default prompt.txt response.txt

# 调用 Gemini（model-name 会被忽略；Gemini 使用其默认模型）
acw gemini default prompt.txt response.txt

# 向提供方传递附加选项
acw claude claude-sonnet-4-20250514 prompt.txt response.txt --max-tokens 4096

# 在编辑器中编写提示词
acw --editor claude claude-sonnet-4-20250514 response.txt

# 将输出流式输出到 stdout（与提供方 stderr 合并）
acw --stdout claude claude-sonnet-4-20250514 prompt.txt

# 开始新的聊天会话（打印会话 ID）
acw --chat claude claude-sonnet-4-20250514 prompt.txt response.txt

# 继续已有的聊天会话
acw --chat abc12345 claude claude-sonnet-4-20250514 prompt.txt response.txt

# 列出所有聊天会话
acw --chat-list
```

### 脚本集成

```bash
#!/usr/bin/env bash
source "$AGENTIZE_HOME/src/cli/acw.sh"

# 在你的脚本中使用 acw
acw claude claude-sonnet-4-20250514 /tmp/prompt.txt /tmp/response.txt
if [ $? -eq 0 ]; then
    echo "Response written to /tmp/response.txt"
fi
```

## 聊天会话

聊天会话通过将历史记录持久化为 markdown 文件来支持多轮对话。

### 会话存储

会话以带有 YAML front matter 的 markdown 文件形式存储在 `$AGENTIZE_HOME/.tmp/acw-sessions/` 下：

```markdown
---
provider: claude
model: claude-sonnet-4-20250514
created: 2025-01-15T10:30:00Z
---

# User
What is the capital of France?

# Assistant
The capital of France is Paris.
```

### 会话 ID

- 格式：8 字符的 base62 字符串（a-z、A-Z、0-9）
- 当使用 `--chat` 且未提供 ID 时自动生成
- 创建新会话时打印到 stderr

### 聊天流程

1. **新会话**：`acw --chat` 创建会话文件、打印其 ID，并运行第一轮对话。
2. **继续会话**：`acw --chat <id>` 将会话历史前置于当前输入，并在提供方响应后追加新的一轮。
3. **列出会话**：`acw --chat-list` 列出会话 ID 及其提供方、模型标签和创建日期。Kimi 会话存储 `model: default` 以反映提供方默认值。

## 环境变量

| 变量 | 描述 |
|----------|-------------|
| `AGENTIZE_HOME` | 必需。agentize 安装路径。 |
| `EDITOR` | 使用 `--editor` 时必需。用于编写提示词的命令。 |

## Shell 补全

`acw` 支持 zsh 的 shell 自动补全。补全功能由 `src/completion/_acw` 提供。

### 补全主题

使用 `acw --complete <topic>` 以编程方式获取补全值：

| 主题 | 描述 |
|-------|-------------|
| `providers` | 支持的提供方列表（claude、codex、opencode、cursor、kimi、gemini） |
| `cli-options` | 常用 CLI 选项（例如 --help、--editor、--stdout、--model、--max-tokens、--yolo） |

Kimi 会忽略 `<model-name>`，因此提供方补全中仍为其他 CLI 包含 `--model`，而 Kimi 使用其默认模型。

### 配置

对于 zsh，将补全目录添加到你的 `fpath`：

```bash
fpath=($AGENTIZE_HOME/src/completion $fpath)
autoload -Uz compinit && compinit
```

## 注意事项

- 输出目录不存在时会自动创建（使用 `--stdout` 时跳过）
- 提供方特定选项会原样透传，但 `--yolo` 会被规范化为 Claude 的 `--dangerously-skip-permissions` 和 Codex 的 `--full-auto`
- 包装器在成功执行时返回提供方的退出码
- 尽力支持的提供方（opencode、cursor、kimi）功能可能受限
- 只有 `acw` 是公开函数；所有辅助函数（提供方调用、补全、校验）都是内部的（以 `_acw_` 为前缀），不会出现在 tab 补全中
- `acw` 的标志必须出现在 `cli-name` 之前。使用 `--` 传递与 `acw` 标志冲突的提供方选项。
- `--stdout` 行为：
  - 不带 `--chat`：将提供方 stderr 合并进 stdout，以便进度和输出可以一起通过管道传输。
  - 带 `--chat`：提供方 stderr 被追加到 `.tmp/acw-sessions/<session-id>.stderr`，以保持 stdout 干净便于管道传输。由 `acw` 创建的空附属文件会被自动删除。
  - 带 `--chat --editor`：当 stdout 是 TTY 时，用户提示词会在提供方调用前立即回显，随后在助手输出前打印 `Response:` 头。
- 在文件模式（无 `--stdout`）下，提供方 stderr 写入 `<output-file>.stderr`。提供方退出后，空的附属文件会被删除。
- Kimi 输出被强制为 `--output-format stream-json`，并被剥离为纯助手文本。在非聊天 `--stdout` 模式下，合并的 stderr 中非 JSON 的行可能会在剥离过程中被丢弃。

## 另请参阅

- `src/cli/acw.md` - 接口文档
- `src/cli/acw/README.md` - 模块架构
