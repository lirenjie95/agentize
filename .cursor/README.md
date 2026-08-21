# Cursor 配置

本目录包含 Cursor IDE 集成的配置文件。

## Hooks 支持

**重要**：Cursor hooks 仅在 **UI（IDE）版本**中受支持，CLI 版本不支持。

### UI 支持

Cursor IDE 通过 `.cursor/hooks.json` 支持 hook。这些 hook 在 Cursor IDE 工作流的特定生命周期事件时执行：

- **事件**：`beforeSubmitPrompt` - 在提示词提交给 Cursor 之前执行
- **配置**：在 `.cursor/hooks.json` 中定义
- **实现**：详情请参阅 [hooks/README.md](hooks/README.md)

### CLI 限制

Cursor CLI **不**支持 hook。如果你需要在 CLI 环境中使用 hook 功能，请改用 Claude Code CLI，它通过 `.claude-plugin/hooks/hooks.json` 支持 hook。

## 目录结构

- `hooks.json` - Cursor IDE 的 hook 配置
- `hooks/` - hook 实现脚本
  - `before-prompt-submit.py` - 处理工作流初始化
  - `logger.py` - 共享日志工具

## 与 Claude Code 的关系

本目录提供 Cursor IDE 专属的 hook，复刻了 Claude Code CLI hook（位于 `.claude-plugin/hooks/`）中的功能。两个实现：

- 使用相同的会话状态文件格式
- 支持相同的工作流命令（`/ultra-planner`、`/issue-to-impl`）
- 在相同位置创建会话状态文件（`${AGENTIZE_HOME:-.}/.tmp/hooked-sessions/`）

主要区别在于 Cursor hook 仅在 IDE 中工作，而 Claude Code hook 在 CLI 中工作。
