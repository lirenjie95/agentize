# 扩展后端

本文件夹承载 Plan Activity Bar 视图的 VS Code 扩展后端模块。

## 组织结构

- `extension.ts` 注册 webview provider 和扩展入口点。
- `state/` 定义 Plan 状态类型和持久化辅助函数。
- `runner/` 执行规划命令并发出运行事件。
- `view/` 渲染 webview HTML 并桥接消息。
