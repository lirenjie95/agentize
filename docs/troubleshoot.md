# 故障排查

## Agentize 未能 handsoff Claude Code 会话

Agentize 应当自动执行所有 `agentize:workflow`，
包括 `/ultra-planner`、`/issue-to-impl`、`/sync-master` 等。
然而，如果它有时未能做到——包括反复请求权限
或不自动继续会话——你可以启用调试日志
来帮助诊断问题。

在 `.agentize.local.yaml` 中设置 `handsoff.debug: true`：

```yaml
handsoff:
  debug: true
```

然后重新运行命令以复现错误。这将在以下位置之一生成详细日志：
- `/path/to/your/project/.tmp/handsoff-debug.log` 或
- `$HOME/.agentize/.tmp/handsoff-debug.log`

如果你不修改 Agentize 代码就无法修复该 bug，请把你的日志粘贴到 issue 中让我（@were）来调试！

这取决于你是否既从 Claude Code Plugin Marketplace 安装了 Agentize，
又运行了我们的 `install` 脚本来安装 CLI 辅助工具。
