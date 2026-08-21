# Agentize Server

用于 GitHub Projects v2 自动化的轮询 server。

## 概述

一个长时间运行的 server，监控你的 GitHub Projects 看板并自动执行已批准的计划和改进请求：

1. 使用 `gh issue list --label agentize:plan --state open` 发现候选 issue
2. 通过 GraphQL 检查每个 issue 的项目状态，以强制执行 "Plan Accepted" 审批关卡（用于实现）或检测 "Proposed" + `agentize:refine` 标签（用于改进）
3. 通过 `wt spawn` 为就绪的 issue 派生 worktree，或通过 `/ultra-planner --refine` 触发改进
4. 以有界并发管理并发 worker（默认：5 个 worker）

## 用法

```bash
# 通过 lol CLI（推荐）
lol serve

# 直接 Python 调用
python -m agentize.server
```

在 `.agentize.local.yaml` 中配置 `server.period` 和 `server.num_workers`（见下文[运行时配置](#运行时配置)）。

Telegram 凭据从 `.agentize.local.yaml` 加载。server 按以下顺序查找该文件：项目根目录 → `$AGENTIZE_HOME` → `$HOME`。未配置凭据时，server 以无通知模式运行。

## Worker 池

server 管理一个并发 worker 池，以同时处理多个 issue，同时遵守资源限制。

### 并发控制

- `server.num_workers`：最大并发 headless Claude 会话数（默认：5）
- `server.num_workers: 0`：无限制（保留之前的行为）

在 `.agentize.local.yaml` 中配置。

### Worker 状态文件

Worker 状态在 `.tmp/workers/` 中追踪，每个 worker 槽位一个状态文件：

```
.tmp/workers/
├── worker-0.status
├── worker-1.status
├── worker-2.status
├── worker-3.status
└── worker-4.status
```

**文件格式（每行 key=value）：**

空闲时：
```
state=FREE
```

忙碌时：
```
state=BUSY
issue=42
pid=12345
```

### Worker 分配

当 issue 被分配给 worker 时：
```
issue #42 is assigned to worker 0
```

### Headless Spawn 输出解析

server 解析 `wt spawn --headless` 的输出以提取 worker PID。预期的输出格式为：
```
PID: 12345
Log: .tmp/logs/issue-42-20260110-143022.log
```

server 首先查找显式的 `PID:` 行，然后回退到正则匹配 `PID[:\s]+(\d+)` 以向后兼容。

### 崩溃恢复

启动时，server 读取现有状态文件并检查 PID 存活状态。PID 已死的 worker 会被自动标记为 FREE，实现在意外关闭后的恢复。

## PR 自动 Rebase 工作流

server 自动检测有合并冲突的 PR 并 rebase 其对应的 worktree。

### PR 发现

由 agentize 创建的 PR 带有 `agentize:pr` 标签。server 定期扫描这些 PR：

```bash
gh pr list --label agentize:pr --state open --json number,headRefName,mergeable
```

### Mergeable 状态处理

GitHub 的 `mergeable` 字段有三个可能的值：

| 值 | 含义 | Server 动作 |
|-------|---------|---------------|
| `MERGEABLE` | 无冲突 | 跳过（健康） |
| `CONFLICTING` | 有冲突 | 排队 rebase |
| `UNKNOWN` | 仍在计算 | 跳过并在下次轮询重试 |

`UNKNOWN` 状态出现在 GitHub 正在计算合并状态时。server 跳过这些 PR 以避免抖动，并在下一个轮询周期重试。

### Rebase 分发

当检测到 `mergeable=CONFLICTING` 的 PR 时，server 会：

1. 从 PR 元数据解析 issue 号
2. 检查解析出的 issue 的 Status 是否为 "Rebasing"（如已在处理中则跳过）
3. 通过 `wt pathto <issue-no>` 定位对应的 worktree
4. 通过 `wt_claim_issue_status()` 将 Status 设为 "Rebasing" 以认领该 issue
5. 使用 worker 池执行 `wt rebase <pr-no> --headless`
6. 日志输出到 `.tmp/logs/rebase-<pr-no>-<timestamp>.log`

基于状态的过滤防止重复的 worker 分配：当 `filter_conflicting_prs()` 发现有冲突的 PR 时，它会检查解析出的 issue 的项目状态。如果状态已经是 "Rebasing"（已被之前的轮询周期认领），则跳过该 PR。

如果 rebase 因冲突失败：
- rebase 被中止（`git rebase --abort`）
- worker 被标记为 FREE
- 记录错误并附带日志文件路径以供人工审查

### 调试日志

当 `.agentize.local.yaml` 中设置 `handsoff.debug: true` 时，server 记录 PR 发现和过滤决策：

```
  - PR #123: { mergeable: CONFLICTING, status: Backlog }, decision: QUEUE, reason: needs rebase
  - PR #124: { mergeable: UNKNOWN }, decision: SKIP, reason: retry next poll
  - PR #125: { mergeable: MERGEABLE }, decision: SKIP, reason: healthy
  - PR #126: { mergeable: CONFLICTING, status: Rebasing }, decision: SKIP, reason: already being rebased
[26-01-18-14:30:15] [INFO] [github.py:481:filter_conflicting_prs] Summary: 1 queued, 3 skipped (1 healthy, 1 unknown, 1 rebasing)
```

## 功能请求规划工作流

server 自动发现功能请求 issue 并使用 `/ultra-planner` 生成实现计划。

### 功能请求发现

符合功能请求规划条件的 issue 必须：
1. 带 `agentize:dev-req` 标签
2. 不带 `agentize:plan` 标签（尚未规划）
3. Status 不是 `Done` 或 `In Progress`（终态）

server 使用以下命令轮询这些候选：
```bash
gh issue list --label agentize:dev-req --state open
```

### 功能请求状态机

找到功能请求候选时：

1. **发现**：server 找到带 `agentize:dev-req` 标签的 issue
2. **过滤**：server 排除已带 `agentize:plan` 标签或处于终态的 issue
3. **派生**：server 以 headless 方式运行 `/ultra-planner --from-issue <issue-no>`
4. **清理**：规划完成后：
   - `agentize:dev-req` 标签被移除
   - `agentize:plan` 标签被添加（由 `/ultra-planner` 添加）
   - issue 可以进行审查/改进

### 调试日志（功能请求）

当 `.agentize.local.yaml` 中设置 `handsoff.debug: true` 时：

```
  - Issue #42: { labels: [agentize:dev-req], status: Backlog }, decision: READY, reason: matches criteria
  - Issue #43: { labels: [agentize:dev-req, agentize:plan], status: Proposed }, decision: SKIP, reason: already has agentize:plan
  - Issue #44: { labels: [agentize:dev-req], status: Done }, decision: SKIP, reason: terminal status
[26-01-18-14:30:15] [INFO] [github.py:657:filter_ready_feat_requests] Summary: 1 ready, 2 skipped (1 already planned, 1 terminal status)
```

### 手动触发功能请求

要为 issue 触发功能请求规划：
1. 添加 `agentize:dev-req` 标签（通过 GitHub UI 或 `gh issue edit --add-label agentize:dev-req`）
2. 等待下一个 server 轮询周期

标签可通过 GitHub UI 或 CLI 添加：
```bash
gh issue edit <issue-no> --add-label agentize:dev-req
```

### 迁移说明

如果你有带旧 `agentize:feat-request` 标签的现有 issue，必须将它们重新标记为 `agentize:dev-req` 才能被 server 发现。使用：
```bash
gh issue edit <issue-no> --remove-label agentize:feat-request --add-label agentize:dev-req
```

## PR 审查解决工作流

server 自动发现有未解决审查线程的 PR，并使用 `/resolve-review` 处理它们。

### 审查解决发现

符合审查解决条件的 PR 必须：
1. 带 `agentize:pr` 标签（由 agentize 创建的 PR）
2. 链接的 issue 的 Status = `Proposed`（确保工作已准备好接受审查，而非正在积极开发中）
3. 至少有一个审查线程同时满足 `isResolved == false` 且 `isOutdated == false`

server 使用以下命令轮询候选 PR：
```bash
gh pr list --label agentize:pr --state open --json number,headRefName,body,closingIssuesReferences
```

### 审查解决状态机

找到审查解决候选时：

1. **发现**：server 找到带 `agentize:pr` 标签的 PR
2. **过滤**：server 检查链接 issue 的 Status == `Proposed`，并通过 GraphQL 调用 `has_unresolved_review_threads()`
3. **认领**：server 将链接 issue 的 Status 设为 `In Progress`（并发控制）
4. **派生**：server 在 issue worktree 中以 headless 方式运行 `/resolve-review <pr-no>`
5. **清理**：完成后，Status 重置为 `Proposed`（尽力而为）

### Status 生命周期

审查解决工作流使用 `Proposed → In Progress → Proposed` 状态生命周期：

| 阶段 | Status | 原因 |
|-------|--------|--------|
| 认领前 | `Proposed` | 工作已完成，等待审查解决 |
| 解决期间 | `In Progress` | 防止重复 worker，表示正在积极处理 |
| 完成后 | `Proposed` | 准备进行下一个审查周期或 PR 合并 |

该生命周期使用现有 Status 选项，无需新增如 "Reviewing" 的状态。

### 调试日志（审查解决）

当 `.agentize.local.yaml` 中设置 `handsoff.debug: true` 时：

```
  - PR #123: { issue: 42, status: Proposed, threads: 3 unresolved }, decision: READY, reason: matches criteria
  - PR #124: { issue: 43, status: In Progress }, decision: SKIP, reason: status != Proposed
  - PR #125: { issue: 44, status: Proposed, threads: 0 unresolved }, decision: SKIP, reason: no unresolved threads
[26-01-22-14:30:15] [INFO] [github.py:720:filter_ready_review_prs] Summary: 1 ready, 2 skipped (1 wrong status, 1 no threads)
```

### 手动触发审查解决

要为 PR 触发审查解决：
1. 确保链接的 issue 处于 `Proposed` 状态
2. 在 PR 上添加未解决的审查评论
3. 等待下一个 server 轮询周期

或手动运行（在有开放 PR 的 issue 分支上）：
```bash
claude --print "/resolve-review"
```

### 卡在 In Progress 的恢复

如果 issue 卡在 `In Progress` 状态（例如 server 崩溃后）：
1. 通过 GitHub Projects UI 手动将 Status 重置为 `Proposed`
2. 该 PR 将在下一个轮询周期被拾取

## 计划改进工作流

server 自动发现并处理计划改进候选。

### 改进发现

符合改进条件的 issue 必须：
1. Status = `Proposed`
2. 标签同时包含 `agentize:plan` 和 `agentize:refine`

server 使用以下命令轮询这些候选：
```bash
gh issue list --label agentize:plan,agentize:refine --state open
```

### 改进状态机

找到改进候选时：

1. **认领**：server 将 Status 设为 `Refining`（尽力而为的并发控制）
2. **派生**：server 创建 worktree 并以 headless 方式运行 `/ultra-planner --refine`
3. **清理**：改进完成后：
   - Status 恢复为 `Proposed`
   - `agentize:refine` 标签被移除

### 调试日志（改进）

当 `.agentize.local.yaml` 中设置 `handsoff.debug: true` 时：

```
  - Issue #42: { labels: [agentize:plan, agentize:refine], status: Proposed }, decision: READY, reason: matches criteria
  - Issue #43: { labels: [agentize:plan], status: Proposed }, decision: SKIP, reason: missing agentize:refine label
  - Issue #44: { labels: [agentize:plan, agentize:refine], status: Plan Accepted }, decision: SKIP, reason: status != Proposed
[26-01-18-14:30:15] [INFO] [github.py:386:filter_ready_refinements] Summary: 1 ready, 2 skipped (1 wrong status, 1 missing agentize:refine)
```

### 手动触发改进

要为 issue 触发改进：
1. 确保 issue 处于 `Proposed` 状态
2. 添加 `agentize:refine` 标签
3. 等待下一个 server 轮询周期

标签可通过 GitHub UI 或 CLI 添加：
```bash
gh issue edit <issue-no> --add-label agentize:refine
```

### 卡在 Refining 的恢复

如果 issue 卡在 `Refining` 状态（例如 server 崩溃后）：
1. 通过 GitHub Projects UI 手动将 Status 重置为 `Proposed`
2. 可选地重新添加 `agentize:refine` 标签以重试

## 配置

server 从仓库根目录的 `.agentize.yaml` 读取项目关联：

```yaml
project:
  org: <owner>            # 组织或个人用户登录名
  id: <project-number>

# 可选：Telegram 通知中 issue/PR 超链接的显式远程 URL
# 如果省略，自动从 `git remote get-url origin` 解析
# git:
#   remote_url: https://github.com/org/repo
```

### 运行时配置

对于不应提交的 server 特定设置（凭据、worker 池大小、模型偏好），使用 `.agentize.local.yaml`：

```yaml
# .agentize.local.yaml - 运行时配置（被 git 忽略）
handsoff:
  enabled: true
  max_continuations: 10
  auto_permission: true
  debug: false
  supervisor:
    provider: claude
    model: opus

server:
  period: 5m
  num_workers: 5

telegram:
  enabled: true
  token: "your-bot-token"
  chat_id: "your-chat-id"
  timeout_sec: 60
  poll_interval_sec: 5

workflows:
  impl:
    model: opus
  refine:
    model: sonnet
  dev_req:
    model: sonnet
  rebase:
    model: haiku
```

**配置优先级：** `.agentize.local.yaml` > 默认值

例如：
- YAML 中 `server.period: 2m` 使用 `2m`
- 如果 YAML 未指定值，则使用默认值（period 为 `5m`，workers 为 `5`）

**各部分：**
- `handsoff`：自动继续的 handsoff 模式设置（见 [Handsoff 模式](core/handsoff.md)）
- `server`：轮询周期和 worker 池大小
- `telegram`：Bot token、聊天 ID 和审批设置（见 [Telegram 审批](permissions/telegram.md)）
- `workflows`：按工作流的 Claude 模型选择（opus、sonnet、haiku）

**YAML 查找顺序：**
1. 项目根目录 `.agentize.local.yaml`
2. `$AGENTIZE_HOME/.agentize.local.yaml`
3. `$HOME/.agentize.local.yaml`（用户级，由安装脚本创建）

完整配置模式见[配置参考](../envvar.md)。

**注意：** 此文件不应提交。它会被自动 git 忽略。

### 远程 URL 配置

`git.remote_url` 字段使 Telegram 通知中的 issue 和 PR 号成为可点击的超链接。该字段是**可选的**——未配置时，server 会自动从 `git remote get-url origin` 解析 URL。

**支持的 URL 格式：**
- HTTPS：`https://github.com/org/repo` 或 `https://github.com/org/repo.git`
- SSH：`git@github.com:org/repo.git`

**回退行为：**
1. server 检查 `.agentize.yaml` 中的 `git.remote_url`
2. 如果未找到，运行 `git remote get-url origin` 自动解析
3. 如果两者都失败，通知以纯文本显示 issue 号（优雅降级）

## 故障排查

### Issue 发现错误

如果 `gh issue list` 失败（例如网络错误、认证问题），server 返回空候选列表而不会崩溃，并记录错误以供调查。

### 单 Issue 状态查询错误

错误消息包含源位置（文件:行:函数）以便快速调试：

```
[26-01-09-12:30:47] [ERROR] [__main__.py:163:query_issue_project_status] GraphQL query failed: ...
```

如需更多上下文（查询和变量），在 `.agentize.local.yaml` 中设置 `handsoff.debug: true`：

```yaml
handsoff:
  debug: true
```

这会在失败时记录 GraphQL 查询和变量，帮助诊断变量类型不匹配或查询语法问题。

### Issue 过滤调试日志

当 issue 未被 server 拾取时，在 `.agentize.local.yaml` 中设置 `handsoff.debug: true` 启用调试日志以查看过滤决策。

调试输出显示每个 issue 的检查结果，包括状态、标签和拒绝原因：

```
  - Issue #42: { labels: [agentize:plan, bug], status: Plan Accepted }, decision: READY, reason: matches criteria
  - Issue #43: { labels: [enhancement], status: Backlog }, decision: SKIP, reason: status != Plan Accepted
  - Issue #44: { labels: [feature], status: Plan Accepted }, decision: SKIP, reason: missing agentize:plan label
[26-01-18-14:30:15] [INFO] [github.py:330:filter_ready_issues] Summary: 1 ready, 2 skipped (1 wrong status, 1 missing label)
```

每条扫描行包括：
- 带 2 空格缩进的 issue 号
- 包含标签和状态的结构化格式
- 决策（READY 或 SKIP）及原因
- 带时间戳和源位置的摘要行

## Telegram 通知

当 `.agentize.local.yaml` 中配置了 Telegram 凭据时，server 会发送通知：

### 启动通知

server 启动时发送，包括主机名、项目标识符、轮询周期和工作目录。

### Worker 分配通知

当 issue 成功分配给 worker 时发送，包括：
- Issue 号和标题（指向 GitHub issue 的可点击超链接）
- Worker ID

issue 链接自动从 `git remote get-url origin` 解析。如需显式配置，在 `.agentize.yaml` 中设置 `git.remote_url`。如果 URL 无法解析，通知以纯文本显示 issue 号而不报错。

### Worker 完成通知

当发现 worker PID 已死且关联会话状态为 `done` 时发送，表示成功完成：
- Issue 号（指向 GitHub issue 的可点击超链接）
- Worker ID
- GitHub PR 链接（当会话状态中记录了 `pr_number` 时为可点击超链接）

**完成通知的要求：**
1. Worker PID 必须已死（进程已退出）
2. 会话状态文件必须存在于 `${AGENTIZE_HOME:-.}/.tmp/hooked-sessions/{session_id}.json`
3. 会话状态必须为 `done`
4. Issue 索引文件必须存在于 `${AGENTIZE_HOME:-.}/.tmp/hooked-sessions/by-issue/{issue_no}.json`

**去重：** 成功发送完成通知后，issue 索引文件会被移除，以防止 server 重启周期之间的重复通知。

**失败情况（不发送通知）：**
- 会话状态不是 `done`（例如 `initial`、`in_progress`）
- Issue 索引文件缺失（工作流未带 issue 号调用）
- 未配置 Telegram 凭据

## 实现布局（内部）

server 组织为专注的模块以保证可维护性：

```
python/agentize/server/
├── __main__.py    # CLI 入口点和轮询协调器
├── github.py      # GitHub issue/PR 发现和 GraphQL 辅助
├── workers.py     # Worktree spawn/rebase 和 worker 状态文件
├── notify.py      # Telegram 消息格式化和发送
├── session.py     # 会话状态文件查找
├── log.py         # 共享日志辅助
└── README.md      # 模块布局和重导出策略
```

所有公共函数从 `__main__.py` 重导出，以保持与现有测试导入的向后兼容（例如 `from agentize.server.__main__ import read_worker_status`）。
