# Hooks

本目录包含在特定生命周期事件时执行的 Claude Code hook。

## 用途

Hook 在 Claude Code 工作流的关键节点实现自动化行为和集成，无需用户显式输入命令。

## 可用 Hook

### session-init.sh
**事件**：SessionStart（每个 Claude Code 会话开始时）

**用途**：初始化项目专属环境

**动作**：
- 设置 `AGENTIZE_HOME` 环境变量
- 运行 `make setup` 以确保项目已初始化

### permission-request.sh
**事件**：工具执行前（需要权限时）

**用途**：工具执行的默认权限策略

**行为**：
- 对所有工具执行返回 `ask` 决策
- 用户必须通过 Claude Code 的权限系统批准每次工具使用

### post-edit.sh
**事件**：通过 Edit 工具编辑文件后

**用途**：项目专属的编辑后处理（如已配置）

### pre-tool-use.py
**事件**：PreToolUse（工具执行前）

**用途**：委托给 `lib/permission/` 模块的薄封装

**行为**：
- 委托给 `lib.permission.determine()` 进行权限决策
- 规则来源于 `lib/permission/rules.py`
- 基于模式匹配返回 `allow/deny/ask` 决策
- 从 `.agentize.local.yaml` 读取 Telegram 和自动权限配置，支持环境变量覆盖
- 当 `HANDSOFF_DEBUG=1` 或 `handsoff.debug: true` 时记录工具使用日志
- 导入/执行出错时回退到 `ask`
- 接口详情请参阅 [pre-tool-use.md](pre-tool-use.md)

### user-prompt-submit.py
**事件**：UserPromptSubmit（提示词发送给 Claude Code 之前）

**用途**：为 handsoff 模式工作流初始化会话状态

**行为**：
- 从 `lib/workflow.py` 导入工作流检测
- 检测 `/ultra-planner`、`/issue-to-impl` 和 `/plan-to-issue` 命令
- 在 `${AGENTIZE_HOME:-.}/.tmp/hooked-sessions/` 中创建会话状态文件
- 从命令参数中提取可选的 `issue_no`
- 详情请参阅 [docs/feat/core/handsoff.md](../../docs/feat/core/handsoff.md)

### stop.py
**事件**：Stop（Claude Code 停止执行前）

**用途**：在 handsoff 模式下自动续接工作流

**行为**：
- 从 `lib/workflow.py` 导入续接提示词
- 从 `${AGENTIZE_HOME:-.}/.tmp/hooked-sessions/` 读取会话状态
- 递增续接计数并检查上限
- 注入工作流专属的续接提示词
- 详情请参阅 [docs/feat/core/handsoff.md](../../docs/feat/core/handsoff.md)

### post-bash-issue-create.py
**事件**：PostToolUse（Bash 工具执行后）

**用途**：在 Ultra Planner 工作流期间从 `gh issue create` 捕获 issue 编号

**行为**：
- 拦截成功的 `gh issue create` 命令
- 从输出 URL 中提取 issue 编号（例如 `https://github.com/owner/repo/issues/544`）
- 检查是否处于 Ultra Planner 工作流上下文中
- 用捕获到的 `issue_no` 更新会话状态文件
- 创建 issue 索引文件以支持反向查找
- 向 Claude 提供 additionalContext 以确认 issue 捕获

## 共享库

所有可复用代码位于 `lib/` 目录（与 `hooks/` 同级）。Hook 从以下来源导入：
- `lib.permission` - 权限评估逻辑
- `lib.workflow` - 工作流检测和续接提示词
- `lib.logger` - 调试日志工具
- `lib.telegram_utils` - Telegram API 辅助函数

详情请参阅 [lib/README.md](../lib/README.md)。

## Hook 调用机制

Hook 在 `.claude/settings.json` 中配置：

```json
{
  "hooks": {
    "SessionStart": ".claude/hooks/session-init.sh"
  }
}
```

当对应事件发生时，Claude Code 会自动执行指定的脚本。

## 开发指南

创建新 hook 时：
1. **保持主 hook 简单**：复杂逻辑委托给辅助脚本
2. **静默失败**：hook 不应在出错时中断用户工作流
3. **检查前置条件**：仅在相关时执行（例如检查环境变量、分支模式）
4. **提供清晰的输出**：如需显示信息，格式应清晰简洁
5. **编写行为文档**：创建配套的 `.md` 文件说明接口和内部实现
