# VS Code 扩展可执行文件

本文件夹包含 VS Code 扩展运行时使用的辅助可执行文件。

## 组织结构

- `lol-wrapper.js` 将基于 shell 的 `lol` CLI 桥接为便于子进程调用的命令。
- `lol-wrapper.md` 记录了 wrapper 的接口和行为。
- `render-plan-harness.js` 在活动 worktree 的 `.tmp/` 中生成 Playwright harness HTML。
- `render-plan-harness.md` 记录了 harness 生成和路径解析。
