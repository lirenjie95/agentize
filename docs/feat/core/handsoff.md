# Handsoff 模式

Handsoff 模式使 `/ultra-planner`、`/issue-to-impl` 和 `/plan-to-issue` 工作流能够在 Claude Code 停止后自动继续，无需人工干预。

## 概述

启用 handsoff 模式（在 `.agentize.local.yaml` 中设置 `handsoff.enabled: true`）后，特定工作流会在每次 Claude Code 停止后自动恢复，直到完成或达到继续次数上限。这使得长时间运行的规划和实现工作流能够自主推进。

**支持的工作流：**
- `/ultra-planner` - 基于多智能体辩论的规划（见 [ultra-planner.md](ultra-planner.md)）
- `/issue-to-impl` - 从 issue 到 PR 的完整开发周期（见 [../tutorial/02-issue-to-impl.md](../tutorial/02-issue-to-impl.md)）
- `/plan-to-issue` - 从用户提供的计划创建 GitHub [plan] issue
- `/setup-viewboard` - GitHub Projects v2 看板设置（见 [../commands/setup-viewboard.md](../commands/setup-viewboard.md)）

## 工作原理

### 会话状态管理

当调用受支持的工作流命令时，`UserPromptSubmit` hook 会创建一个会话状态文件：

```
${AGENTIZE_HOME:-.}/.tmp/hooked-sessions/{session_id}.json
```

当设置了 `AGENTIZE_HOME` 时，会话文件集中存储，实现跨 worktree 可见性。未设置时，文件回退到当前工作目录（`./.tmp/hooked-sessions/`）。

**初始状态结构：**
```json
{
  "workflow": "ultra-planner",
  "state": "initial",
  "continuation_count": 0,
  "issue_no": 42,
  "pr_number": 123
}
```

`pr_number` 字段是可选的，由 `open-pr` skill 在 PR 创建后填充。存在时，server 会在完成通知中包含可点击的 PR 链接。

### Issue 索引文件

当工作流带 issue 号调用时（例如 `/issue-to-impl 42`、`/ultra-planner --refine 42` 或 `/ultra-planner --from-issue 42`），`UserPromptSubmit` hook 还会创建 issue 索引文件：

```
${AGENTIZE_HOME:-.}/.tmp/hooked-sessions/by-issue/{issue_no}.json
```

**索引文件结构：**
```json
{
  "session_id": "<session_id>",
  "workflow": "issue-to-impl"
}
```

该索引使 server 能够查找哪个会话正在处理某个 issue，从而在 worker 完成时支持完成通知。

### 自动继续流程

```
User invokes: /ultra-planner <feature>
       ↓
[UserPromptSubmit Hook]
  - Detects workflow command
  - Creates session state file
  - Initializes continuation_count = 0
       ↓
Claude Code executes workflow
       ↓
Claude Code stops (output limit, token limit, etc.)
       ↓
[Stop Hook]
  - Reads session state file
  - Checks continuation_count < HANDSOFF_MAX_CONTINUATIONS
  - Increments continuation_count
  - Injects workflow-specific auto-continuation prompt
  - Blocks stop with continuation prompt
       ↓
Claude Code automatically resumes with continuation prompt
       ↓
(Repeat until workflow completes or max continuations reached)
```

## 配置

在 `.agentize.local.yaml` 中配置 handsoff 模式：

```yaml
handsoff:
  enabled: true                    # 启用 handsoff 自动继续
  max_continuations: 10            # 每个工作流的最大自动继续次数
  auto_permission: true            # 启用基于 Haiku LLM 的自动权限
  debug: false                     # 启用调试日志
  supervisor:
    provider: claude               # AI 提供方（none、claude、codex、cursor、opencode）
    model: opus                    # supervisor 使用的模型
    flags: ""                      # acw 的额外标志
```

**YAML 查找顺序：**
1. 项目根目录 `.agentize.local.yaml`
2. `$AGENTIZE_HOME/.agentize.local.yaml`
3. `$HOME/.agentize.local.yaml`（用户级，由安装脚本创建）

### 设置参考

| YAML 路径 | 类型 | 默认值 | 描述 |
|-----------|------|---------|-------------|
| `handsoff.enabled` | bool | `true` | 启用 handsoff 自动继续 |
| `handsoff.max_continuations` | int | `10` | 每个工作流的最大自动继续次数 |
| `handsoff.auto_permission` | bool | `true` | 启用基于 Haiku LLM 的自动权限 |
| `handsoff.debug` | bool | `false` | 启用调试日志 |
| `handsoff.supervisor.provider` | string | `none` | AI 提供方（none、claude、codex、cursor、opencode） |
| `handsoff.supervisor.model` | string | 视提供方而定 | supervisor 使用的模型 |
| `handsoff.supervisor.flags` | string | `""` | acw 的额外标志 |

**调试日志文件：** `${AGENTIZE_HOME:-.}/.tmp/hooked-sessions/permission.txt`（统一权限日志）

### Telegram 审批（可选）

配置后，可通过 Telegram 远程审批工具使用。当 PreToolUse 决策为 `ask` 时，hook 会发送 Telegram 消息，让你可以从手机上批准或拒绝。

```yaml
telegram:
  enabled: true
  token: "123456:ABC-DEF..."       # 来自 @BotFather 的 Bot token
  chat_id: "12345678"              # 聊天/频道 ID
  timeout_sec: 60                  # 审批超时时间（最大：7200）
  poll_interval_sec: 5             # 轮询间隔
  allowed_user_ids: "123,456"      # 允许的用户 ID（CSV，可选）
```

**行为：**
- 当 Telegram 启用并配置好后，`ask` 决策会发送到 Telegram
- 审批消息显示内联键盘按钮（`[✅ Allow]` 和 `[❌ Deny]`），支持一键审批
- 按钮点击会立即确认并更新原始消息
- 超时时，原始消息会被编辑为显示 "⏰ Timed Out" 状态，按钮被移除
- API 出错时，回退到 `ask`（提示本地用户）
- 缺少配置时记录警告并回退到 `ask`

## 各工作流的行为

### `/ultra-planner` 工作流

**目标：** 创建全面的实现计划并发布到 GitHub Issue。

**自动继续提示词（由 Stop hook 注入）：**
```
This is an auto-continuation prompt for handsoff mode, it is currently {N}/{MAX} continuations.
The ultimate goal of this workflow is to create a comprehensive plan and post it on GitHub Issue. Have you delivered this?
1. If not, please continue! Try to be as hands-off as possible, avoid asking user design decision questions, and choose the option you recommend most.
2. If you have already delivered the plan, manually stop further continuations.
3. If you do not know what to do next, or you reached the max continuations limit without delivering the plan,
   look at the current branch name to see what issue you are working on. Then stop manually
   and leave a comment on the GitHub Issue for human collaborators to take over.
```

**完成标准：** 计划 issue 已在 GitHub 上创建/更新。

### `/issue-to-impl` 工作流

**目标：** 在 GitHub 上交付实现对应 issue 的 PR。

**计划缓存：** 在步骤 4（读取实现计划）期间，工作流将提取的 "Proposed Solution" 部分缓存到 `.tmp/plan-of-issue-{N}.md`。该缓存计划会包含在继续提示词中，为自主工作流提供偏差感知和更易恢复的能力。

**自动继续提示词（由 Stop hook 注入）：**
```
This is an auto-continuation prompt for handsoff mode, it is currently {N}/{MAX} continuations.
The ultimate goal of this workflow is to deliver a PR on GitHub that implements the corresponding issue. Did you have this delivered?
1. If you have completed a milestone but still have more to do, please continue on the next milestone!
1.5. Review the cached plan (if available):
   - Plan file: {plan_path}
   {plan_excerpt}
2. If you have every coding task done, start the following steps to prepare for PR:
   2.0 Rebase the branch with upstream or origin (priority: upstream/main > upstream/master > origin/main > origin/master).
   2.1 Run the full test suite following the project's test conventions (see CLAUDE.md).
   2.2 Use the code-quality-reviewer agent to review the code quality.
   2.3 If the code review raises concerns, fix the issues and return to 2.1.
   2.4 If the code review is satisfactory, proceed to open the PR.
3. Prepare and create the PR. Do not ask user "Should I create the PR?" - just go ahead and create it!
4. If the PR is successfully created, manually stop further continuations.
```

**完成标准：** PR 已在 GitHub 上创建且所有测试通过。

### `/plan-to-issue` 工作流

**目标：** 从用户提供的计划创建 GitHub [plan] issue。

**自动继续提示词（由 Stop hook 注入）：**
```
This is an auto-continuation prompt for handsoff mode, it is currently {N}/{MAX} continuations.
The ultimate goal of this workflow is to create a GitHub [plan] issue from the user-provided plan.

1. If you have not yet created the GitHub issue, please continue working on it!
   - Parse and format the plan content appropriately
   - Create the issue with proper labels and formatting
   - Use `--body-file` instead of `--body` to avoid flag parsing issues
2. If you have successfully created the GitHub issue, manually stop further continuations.
3. If you are blocked or reached the max continuations limit without creating the issue:
   - Stop manually and inform the user what happened
   - Include what you have done so far
   - Include what is blocking you
   - Include the session ID for human intervention.
```

**完成标准：** GitHub [plan] issue 创建成功。

### `/setup-viewboard` 工作流

**目标：** 设置具有 agentize 兼容配置的 GitHub Projects v2 看板。

**自动继续提示词（由 Stop hook 注入）：**
```
This is an auto-continuation prompt for handsoff mode, it is currently {N}/{MAX} continuations.
The ultimate goal of this workflow is to set up a GitHub Projects v2 board. Have you completed all steps?
1. If not, please continue with the remaining setup steps!
2. If setup is complete, manually stop further continuations.
```

**完成标准：** 项目看板已创建，Status 字段选项和标签已配置。

**自动权限：** 当此工作流激活时，以下 `gh` CLI 命令会被自动允许：
- `gh auth status` - 认证验证
- `gh repo view --json owner -q ...` - 仓库所有者查询
- `gh api graphql` - 项目创建和配置
- `gh label create --force` - 标签创建

这些权限**仅在 setup-viewboard 工作流期间**生效，不影响全局权限规则。

## 调试

### 检查会话状态

查看当前会话状态文件：

```bash
cat ${AGENTIZE_HOME:-.}/.tmp/hooked-sessions/{session_id}.json
```

**示例输出：**
```json
{
  "workflow": "issue-to-impl",
  "state": "initial",
  "continuation_count": 5,
  "issue_no": 42
}
```

`issue_no` 字段仅在工作流带 issue 号参数调用时存在（例如 `/issue-to-impl 42` 或 `/ultra-planner --refine 42`）。

### 查看调试日志

在 `.agentize.local.yaml` 中设置 `handsoff.debug: true` 启用调试日志，然后查看日志：

```bash
tail -f ${AGENTIZE_HOME:-.}/.tmp/hook-debug.log
```

**示例日志条目：**
```
[2026-01-07T10:15:23] [abc123] Writing state: {'workflow': 'ultra-planner', 'state': 'initial', 'continuation_count': 0}
[2026-01-07T10:20:45] [abc123] Found existing state file: $AGENTIZE_HOME/.tmp/hooked-sessions/abc123.json
[2026-01-07T10:20:45] [abc123] Updating state for continuation: {'workflow': 'ultra-planner', 'state': 'initial', 'continuation_count': 1}
```

### 手动停止自动继续

在达到上限之前停止自动继续：

1. 从继续提示词或日志中找到会话 ID
2. 编辑会话状态文件：
   ```bash
   # 将 continuation_count 设置为最大值
   echo '{"workflow": "issue-to-impl", "state": "initial", "continuation_count": 10}' > ${AGENTIZE_HOME:-.}/.tmp/hooked-sessions/{session_id}.json
   ```

3. 或直接删除会话状态文件：
   ```bash
   rm ${AGENTIZE_HOME:-.}/.tmp/hooked-sessions/{session_id}.json
   ```

### 通过人工干预恢复会话

如果 Claude Code 在 issue 上留下了请求人工干预的评论：

```bash
# 通过会话 ID 恢复会话
claude -r {session_id}
```

这允许你查看进度、提供指导并手动继续工作流。

## Hook 实现

Handsoff 模式通过三个 Claude Code hook 实现（见 [.claude/hooks/README.md](../../.claude/hooks/README.md)）：

### `pre-tool-use.py`
- **事件：** `PreToolUse`（工具执行前）
- **用途：** 委托给 `.claude-plugin/lib/permission/` 模块的轻量封装
- **位置：** `.claude-plugin/hooks/pre-tool-use.py`

**关键逻辑：**
- 导入并调用 `lib.permission.determine()` 处理所有权限决策
- 规则来源为 `.claude-plugin/lib/permission/rules.py`（规范位置）
- 评估顺序：全局规则 → 工作流自动允许 → Haiku LLM → Telegram（单一最终升级路径）
- 向 Claude Code 返回 `allow/deny/ask` 决策
- 当 `.agentize.local.yaml` 中设置 `handsoff.debug: true` 时记录工具使用
- 任何导入/执行错误时回退到 `ask`

**架构说明：**
- 该 hook 是最小化封装（约 15 行代码），委托给权限模块
- 权限规则定义在 Python 代码中，而非 `.claude/settings.json`
- 单一事实来源：`.claude-plugin/lib/permission/rules.py`
- 故障安全行为：任何错误时返回 `ask`

接口细节见 [.claude-plugin/hooks/pre-tool-use.md](../../.claude-plugin/hooks/pre-tool-use.md)。

### `user-prompt-submit.py`（Claude Code）
- **事件：** `UserPromptSubmit`（提示词发送到 Claude Code 之前）
- **用途：** 为受支持的工作流初始化会话状态
- **位置：** `.claude-plugin/hooks/user-prompt-submit.py`

**关键逻辑：**
- 检测工作流命令：`/ultra-planner`、`/issue-to-impl`、`/plan-to-issue`、`/setup-viewboard`
- 创建 `$AGENTIZE_HOME/.tmp/hooked-sessions/{session_id}.json` 并写入初始状态（若未设置 `AGENTIZE_HOME` 则回退到 worktree 本地的 `.tmp/`）
- 设置 `continuation_count = 0`
- 存在 issue 号时，在 `$AGENTIZE_HOME/.tmp/hooked-sessions/by-issue/{issue_no}.json` 创建 issue 索引文件
- 注意：`/plan-to-issue` 和 `/setup-viewboard` 不接受 issue 号参数

### `before-prompt-submit.py`（Cursor IDE）
- **事件：** `beforeSubmitPrompt`（提示词发送到 Cursor 之前）
- **用途：** 为受支持的工作流初始化会话状态
- **位置：** `.cursor/hooks/before-prompt-submit.py`

**关键逻辑：**
- 检测工作流命令：`/ultra-planner`、`/issue-to-impl`、`/plan-to-issue`、`/setup-viewboard`
- 创建 `$AGENTIZE_HOME/.tmp/hooked-sessions/{session_id}.json` 并写入初始状态（若未设置 `AGENTIZE_HOME` 则回退到 worktree 本地的 `.tmp/`）
- 设置 `continuation_count = 0`
- 存在 issue 号时，在 `$AGENTIZE_HOME/.tmp/hooked-sessions/by-issue/{issue_no}.json` 创建 issue 索引文件

**注意：** Cursor hook 复刻了 Claude hook 的功能，使 handsoff 模式工作流能在 Cursor IDE 中使用。两个 hook 使用相同的会话状态文件格式并支持相同的工作流命令。

### `stop.py`
- **事件：** `Stop`（Claude Code 停止执行前）
- **用途：** 使用工作流特定的提示词自动继续工作流
- **位置：** `.claude/hooks/stop.py`

**关键逻辑：**
- 从 `$AGENTIZE_HOME/.tmp/hooked-sessions/{session_id}.json` 读取会话状态（若未设置 `AGENTIZE_HOME` 则回退到 worktree 本地的 `.tmp/`）
- 检查 `continuation_count < HANDSOFF_MAX_CONTINUATIONS`
- 递增 `continuation_count`
- 注入工作流特定的继续提示词
- 阻止停止并触发自动恢复

**事实来源：** 工作流定义集中在 `python/agentize/workflow.py` 中。各 hook 从该模块导入工作流检测、issue 提取和继续提示词。

## 添加新工作流

要向 handsoff 模式添加新工作流，只需编辑 `python/agentize/workflow.py`：

1. **添加工作流常量**，在 `# Workflow name constants` 部分：
   ```python
   MY_WORKFLOW = 'my-workflow'
   ```

2. **添加命令映射**，在 `WORKFLOW_COMMANDS` 中：
   ```python
   WORKFLOW_COMMANDS = {
       ...
       '/my-workflow': MY_WORKFLOW,
   }
   ```

3. **添加继续提示词**，在 `_CONTINUATION_PROMPTS` 中：
   ```python
   _CONTINUATION_PROMPTS = {
       ...
       MY_WORKFLOW: '''
   This is an auto-continuation prompt for handsoff mode...
   ''',
   }
   ```

各 hook 会自动识别新工作流——无需修改 `.claude-plugin/hooks/` 或 `.cursor/hooks/`。

## 限制

- **非工作流提示词：** 常规 Claude Code 使用（非 `/ultra-planner`、`/issue-to-impl`、`/plan-to-issue` 或 `/setup-viewboard`）不受影响
- **会话隔离：** 每个会话有独立状态；切换会话会重置继续追踪
- **最大继续次数：** 工作流在达到 `handsoff.max_continuations` 后停止（默认：10）
- **错误恢复：** 如果 Claude Code 遇到严重错误，可能需要人工干预
- **无跨会话状态：** 会话状态不会在 Claude Code 重启后保留

## 最佳实践

1. **设置适当的上限：** 根据工作流复杂度调整 `handsoff.max_continuations`
   - `/ultra-planner`：通常 5-10 次继续足够
   - `/issue-to-impl`：复杂功能需要 10-20 次继续

2. **监控进度：** 对长时间运行的工作流，定期检查调试日志或会话状态

3. **人工检查点：** 对关键功能，考虑在关键里程碑后进行人工干预，而非完全 handsoff 模式

4. **清理状态文件：** 定期清理 `${AGENTIZE_HOME:-.}/.tmp/hooked-sessions/` 以移除旧会话状态：
   ```bash
   rm ${AGENTIZE_HOME:-.}/.tmp/hooked-sessions/*.json
   ```

5. **启用调试日志：** 在初始 handsoff 设置期间设置 `handsoff.debug: true` 以了解行为

## 另请参阅

- [Ultra-Planner 工作流](ultra-planner.md) - 多智能体规划细节
- [Issue-to-Impl 教程](../tutorial/02-issue-to-impl.md) - 完整开发周期
- [Hooks README](../../.claude/hooks/README.md) - Hook 系统概述
