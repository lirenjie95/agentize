# Plan 标签页 UI

本文件夹为 webview 提供 Plan Activity Bar 的 UI 实现。

## 组织结构

- `index.ts` 渲染会话、处理输入（包括细化操作），并发送消息（包括来自 plan 终端的停止请求）。它会被编译为 `out/index.js`
  供 webview 运行时使用。
- `widgets.ts` 实现会话时间线的 widget 追加辅助函数和 widget 句柄路由，包括终端头部中可选的停止控件。
- `utils.ts` 提供步骤解析、指示器渲染和链接检测的共享辅助函数。
- `types.ts` 定义 plan webview 使用的消息结构。
- `styles.css` 定义 Plan 标签页的极简可读样式。
- `skeleton.html` 定义由 VS Code webview HTML 和截图 harness 共同使用的共享启动骨架标记。
