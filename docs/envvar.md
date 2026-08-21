# 配置参考

本文档提供 Agentize 的统一配置参考。Telegram 和 handsoff 设置仅使用 YAML 配置。

## 配置文件

| 文件 | 用途 | 是否提交？ |
|------|---------|------------|
| `.agentize.yaml` | 项目元数据（org、项目 ID、语言） | 是 |
| `.agentize.local.yaml` | 开发者设置（凭据、handsoff、Telegram） | 否 |

**优先级顺序（从高到低）：**
1. `.agentize.local.yaml`
2. 默认值

**YAML 查找顺序：**
1. 项目根目录的 `.agentize.local.yaml`
2. `$AGENTIZE_HOME/.agentize.local.yaml`
3. `$HOME/.agentize.local.yaml`（用户级，由安装器创建）

将 `.agentize.local.example.yaml` 复制为 `.agentize.local.yaml` 并按需定制，或者在 `$HOME/.agentize.local.yaml` 中配置你的凭据以跨所有项目使用。

## YAML 配置模式

```yaml
# .agentize.local.yaml - 开发者专属的本地配置

# Handsoff 模式 - 自动工作流续接
handsoff:
  enabled: true                    # 启用 handsoff 自动续接
  max_continuations: 10            # 每个工作流的最大自动续接次数
  auto_permission: true            # 启用基于 Haiku LLM 的自动权限
  debug: false                     # 启用调试日志，输出到 .tmp/
  supervisor:
    provider: claude               # AI 提供方（none, claude, codex, cursor, opencode）
    model: opus                    # supervisor 使用的模型
    flags: ""                      # 传给 acw 的额外参数

# Telegram 审批 - 通过 Telegram bot 远程审批
telegram:
  enabled: false                   # 启用 Telegram 审批
  token: "123456:ABC..."           # 来自 @BotFather 的 Bot API token
  chat_id: "-100123..."            # 聊天/频道 ID
  timeout_sec: 60                  # 审批超时时间（最大：7200）
  poll_interval_sec: 5             # 轮询间隔
  allowed_user_ids: "123,456"      # 允许的用户 ID（CSV）

# Server 运行时 - lol serve 配置
server:
  period: 5m                       # 轮询间隔
  num_workers: 5                   # worker 池大小

# Impl 默认值 - lol impl 配置
impl:
  model: codex:gpt-5.2-codex       # lol impl 的默认后端（provider:model）
  max_iter: 10                     # lol impl 的默认最大迭代次数

# 工作流模型分配
workflows:
  impl:
    model: opus                    # 实现工作流
  refine:
    model: sonnet                  # 精炼工作流
  dev_req:
    model: sonnet                  # dev-req 规划
  rebase:
    model: haiku                   # PR rebase

# Planner 后端 - lol plan 各阶段配置
planner:
  backend: claude:opus             # 所有阶段的默认后端
  understander: claude:sonnet      # 覆盖 understander 阶段
  bold: claude:opus                # 覆盖 bold-proposer 阶段
  critique: claude:opus            # 覆盖 critique 阶段
  reducer: claude:opus             # 覆盖 reducer 阶段
```

## YAML 设置参考

所有 Telegram 和 handsoff 设置仅通过 YAML 配置。

### Handsoff 模式

| YAML 路径 | 类型 | 默认值 | 描述 |
|-----------|------|---------|-------------|
| `handsoff.enabled` | bool | `true` | 启用 handsoff 自动续接 |
| `handsoff.max_continuations` | int | `10` | 每个工作流的最大自动续接次数 |
| `handsoff.auto_permission` | bool | `true` | 启用基于 Haiku LLM 的自动权限 |
| `handsoff.debug` | bool | `false` | 启用调试日志 |
| `handsoff.supervisor.provider` | string | `none` | AI 提供方（none, claude, codex, cursor, opencode） |
| `handsoff.supervisor.model` | string | 随提供方而定 | supervisor 使用的模型 |
| `handsoff.supervisor.flags` | string | `""` | 传给 acw 的额外参数 |

详细文档参见 [Handsoff 模式](feat/core/handsoff.md)。

### Telegram 审批

| YAML 路径 | 类型 | 默认值 | 描述 |
|-----------|------|---------|-------------|
| `telegram.enabled` | bool | `false` | 启用 Telegram 审批 |
| `telegram.token` | string | - | 来自 @BotFather 的 Bot API token |
| `telegram.chat_id` | string | - | 聊天/频道 ID |
| `telegram.timeout_sec` | int | `60` | 审批超时时间（最大：7200） |
| `telegram.poll_interval_sec` | int | `5` | 轮询间隔 |
| `telegram.allowed_user_ids` | CSV | - | 允许的用户 ID（逗号分隔） |

详细文档参见 [Telegram 审批](feat/permissions/telegram.md)。

### Server 运行时

| YAML 路径 | 类型 | 默认值 | 描述 |
|-----------|------|---------|-------------|
| `server.period` | string | `5m` | 轮询间隔（格式：Nm 或 Ns） |
| `server.num_workers` | int | `5` | worker 池大小 |

### Impl 默认值

| YAML 路径 | 类型 | 默认值 | 描述 |
|-----------|------|---------|-------------|
| `impl.model` | string | `codex:gpt-5.2-codex` | `lol impl` 的默认后端（`provider:model`） |
| `impl.max_iter` | int | `10` | `lol impl` 的默认最大实现迭代次数 |

### 工作流模型

| YAML 路径 | 类型 | 默认值 | 描述 |
|-----------|------|---------|-------------|
| `workflows.impl.model` | string | - | 实现工作流使用的模型 |
| `workflows.refine.model` | string | - | 精炼工作流使用的模型 |
| `workflows.dev_req.model` | string | - | dev-req 规划使用的模型 |
| `workflows.rebase.model` | string | - | PR rebase 使用的模型 |

**注意：** `lol impl` 的默认值来自顶层的 `impl.model` / `impl.max_iter`，而不是 `workflows.impl.model`。

### Planner 后端

| YAML 路径 | 类型 | 默认值 | 描述 |
|-----------|------|---------|-------------|
| `planner.backend` | string | `claude:opus` | 所有 planner 阶段的默认后端 |
| `planner.understander` | string | - | 覆盖 understander 阶段 |
| `planner.bold` | string | - | 覆盖 bold-proposer 阶段 |
| `planner.critique` | string | - | 覆盖 critique 阶段 |
| `planner.reducer` | string | - | 覆盖 reducer 阶段 |

Planner 后端使用 `<provider>:<model>` 格式（例如 `claude:opus`、`claude:sonnet`）。按阶段的覆盖优先于 `planner.backend`。

## 仅环境变量

以下变量由 shell 脚本或运行时设置，没有对应的 YAML 配置：

| 变量 | 类型 | 描述 |
|----------|------|-------------|
| `AGENTIZE_HOME` | path | Agentize 安装的根路径。由 `setup.sh` 自动检测。 |
| `AGENTIZE_SHELL_OVERRIDES` | path | 可选的 shell 脚本，在 `setup.sh` 之后被 source，用于覆盖 shell 函数（测试/桩）。 |
| `PYTHONPATH` | path | 由 `setup.sh` 扩展，以包含 `$AGENTIZE_HOME/python`。 |
| `WT_DEFAULT_BRANCH` | string | 覆盖 worktree 操作的默认分支检测。 |
| `WT_CURRENT_WORKTREE` | path | 由 `wt goto` 自动设置，用于跟踪当前 worktree。 |
| `TEST_SHELLS` | string | 要测试的 shell 列表，以空格分隔（例如 `"bash zsh"`）。 |

**Hook 路径解析：** 当设置了 `AGENTIZE_HOME` 时，hooks 将会话状态和日志存储在 `$AGENTIZE_HOME/.tmp/hooked-sessions/`。这使得工作流续接可以跨 worktree 切换进行。

**聊天会话存储：** `$AGENTIZE_HOME/.tmp/acw-sessions/` 以带 YAML front matter 的 markdown 文件形式存储持久的 `acw` 聊天会话。

## 类型强制转换

| 类型 | 接受的值 | 示例 |
|------|-----------------|---------|
| `bool` | `true`、`false`、`1`、`0`、`on`、`off`、`enable`、`disable` | `enabled: true` |
| `int` | 数字字符串或整数 | `timeout_sec: 60` |
| `CSV` | 逗号分隔的值 | `allowed_user_ids: "123,456,789"` |

**注意：** 极简 YAML 解析器不支持原生数组。列表字段请使用 CSV 字符串。

## 快速配置示例

### 带 Telegram 审批的 Handsoff

```yaml
# .agentize.local.yaml（或使用 $HOME/.agentize.local.yaml 作为用户级配置）
handsoff:
  enabled: true
  max_continuations: 20

telegram:
  enabled: true
  token: "your-bot-token"
  chat_id: "your-chat-id"
  timeout_sec: 300
```

### 最小化 Handsoff 配置

Handsoff 模式默认启用。禁用的方法：

```yaml
# .agentize.local.yaml
handsoff:
  enabled: false
  auto_permission: false
```

### 带调试日志的开发配置

```yaml
# .agentize.local.yaml
handsoff:
  debug: true
```

### Supervisor 配置

```yaml
# .agentize.local.yaml
handsoff:
  supervisor:
    provider: claude
    model: opus
    flags: "--timeout 1800"
```

**各提供方的默认模型：**

| 提供方 | 默认模型 |
|----------|---------------|
| `claude` | `opus` |
| `codex` | `gpt-5.2-codex` |
| `cursor` | `gpt-5.2-codex-xhigh` |
| `opencode` | `openai/gpt-5.2-codex` |
