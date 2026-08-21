# Cursor Hooks

本目录包含在特定生命周期事件时执行的 Cursor IDE hook。

## 用途

Hook 在 Cursor IDE 工作流的关键节点实现自动化行为和集成，无需用户显式输入命令。

## 可用 Hook

### before-prompt-submit.py
**事件**：`beforeSubmitPrompt`（提示词发送给 Cursor 之前）

**用途**：为 handsoff 模式工作流初始化会话状态

**行为**：
- 检测 `/ultra-planner` 和 `/issue-to-impl` 命令
- 在 `${AGENTIZE_HOME:-.}/.tmp/hooked-sessions/` 中创建会话状态文件
- 从命令参数中提取可选的 `issue_no`
- 当存在 issue_no 时，在 `by-issue/` 子目录中创建 issue 索引文件
- 详情请参阅 [docs/feat/core/handsoff.md](../../docs/feat/core/handsoff.md)

**环境变量**：
- `HANDSOFF_MODE`：启用/禁用 hook（默认：`0`，设为 `1` 启用）
- `HANDSOFF_DEBUG`：启用调试日志（默认：`0`，设为 `1` 启用）
- `AGENTIZE_HOME`：会话状态的基础目录（默认：`.`）

**Issue 编号提取模式**：
- `/issue-to-impl <number>` - 直接命令
- `/ultra-planner --refine <number>` - 细化标志
- `/ultra-planner --from-issue <number>` - from-issue 标志

## Hook 调用机制

Hook 在 `.cursor/hooks.json` 中配置：

```json
{
  "version": 1,
  "hooks": {
    "beforeSubmitPrompt": [
      {
        "command": "python .cursor/hooks/before-prompt-submit.py"
      }
    ]
  }
}
```

当对应事件发生时，Cursor IDE 会自动执行指定的脚本。

## 依赖

### logger.py
hook 脚本使用的共享日志工具模块。

**函数**：
- `logger(sid, msg)`：当 `HANDSOFF_DEBUG=1` 时记录调试消息
- `_tmp_dir()`：使用 AGENTIZE_HOME 回退获取 tmp 目录路径

注意：`session_dir()` 现在由 `lib/session_utils.py` 提供。

## 开发指南

创建新 hook 时：
1. **保持主 hook 简单**：复杂逻辑委托给辅助脚本
2. **静默失败**：hook 不应在出错时中断用户工作流
3. **检查前置条件**：仅在相关时执行（例如检查环境变量、分支模式）
4. **提供清晰的输出**：如需显示信息，格式应清晰简洁
5. **编写行为文档**：创建配套的 `.md` 文件说明接口和内部实现

## 与 Claude Hook 的关系

该 Cursor hook 实现复刻了 Claude Code `user-prompt-submit.py` hook（位于 `.claude-plugin/hooks/user-prompt-submit.py`）的功能。两个 hook：

- 使用相同的会话状态文件格式
- 支持相同的工作流命令（`/ultra-planner`、`/issue-to-impl`）
- 使用相同的正则表达式模式提取 issue 编号
- 在相同位置创建会话状态文件（`${AGENTIZE_HOME:-.}/.tmp/hooked-sessions/`）

主要区别是：
- **事件名称**：Cursor 使用 `beforeSubmitPrompt`，Claude 使用 `UserPromptSubmit`
- **配置格式**：Cursor 使用更简单的 JSON 结构，Claude 使用嵌套的 hooks 数组
- **路径解析**：Cursor 使用相对路径，Claude 使用环境变量替换
