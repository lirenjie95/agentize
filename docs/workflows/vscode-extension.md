# VS Code 扩展工作流

本文档描述 VS Code 扩展暴露的"规划到实现"（Plan-to-Implement）工作流。
它侧重于 UI 与状态流转背后的设计依据，以便在未来更新中保持行为一致。

## 目标

- 将规划（Plan）、实现（Implementation）和改进（Refinement）的输出呈现为仅追加的 widget 时间线。
- 保持用户操作互斥，使同一时间只能运行一个活动阶段。
- 保留一个轻量的 UI 模型，无需引入新框架即可轻松扩展。
- 尽早捕获 issue 编号，使后续操作保持顺畅无阻。

## 基于 Widget 的会话模型

每个会话维护一个有序的 widget 列表。widget 随会话进展而追加，
而不是预先创建。这使 UI 布局保持显式，并允许
不同阶段复用相同的 widget 类型。

widget 类型包括：
- `text`：简短的状态或 prompt 摘要。
- `terminal`：带标题的终端框，通过句柄（handle）接收追加的日志行。
- `progress`：阶段指示 widget，监听终端输出并跟踪已用时间。
- `buttons`：操作组（Plan、Implement、Refine、View Plan、View PR、Re-implement）。
- `input`：用于改进重点（refinement focus）的内联输入 widget。
- `status`：用于阶段转换的紧凑状态徽标。

终端 widget 暴露句柄，使后续更新可以定位到正确的 widget 而无需
重建 DOM。进度 widget 订阅终端句柄，并在检测到阶段行时
更新自身。

## 会话阶段

会话跟踪一个阶段字符串来协调 UI 操作：

1. `idle`：会话存在但尚未开始规划。
2. `planning`：规划运行正在执行。
3. `plan-completed`：规划运行已结束（成功或出错），操作可用。
4. `refining`：改进运行处于活动状态。
5. `implementing`：实现运行处于活动状态。
6. `completed`：实现运行已结束。

阶段变化驱动按钮状态更新，使 Refine 和 Implement 互斥
且仅在适当的时机启用。

## 进程控制

在规划运行活动期间，终端头部会暴露一个 Stop 控件，发送
`plan/stop` 消息。扩展会终止正在运行的规划进程，在规划日志中记录
停止标记，并将会话标记为 `error`、阶段为 `plan-completed`，
以便操作行立即返回，同时对于被中断的运行保持 Implement 禁用。

## Issue 编号捕获

规划器会输出诸如 `Created placeholder issue #N` 或 GitHub issue URL 之类的行。
扩展实时扫描 stdout/stderr 行，并将第一个匹配的 issue 编号
存储在会话上。在执行期间捕获 issue 编号，可确保 UI 在规划
完成后立即呈现 Implement 和 View PR 操作。

规划和实现日志还会将规范的 GitHub issue 和 pull request URL 链接化。
外部打开仅限规范的 `github.com/<owner>/<repo>/issues/<id>` 和
`github.com/<owner>/<repo>/pull/<id>` 路由。

当规划输出本地 markdown 路径（例如 `.tmp/issue-928.md`）时，UI
会呈现一个 View Plan 按钮，在工作区内打开该文件。

## 改进流程

规划完成后，用户可以发起一次改进运行。点击 Refine 会追加一个
内联输入 widget。通过 Cmd+Enter / Ctrl+Enter 提交会启动改进并追加一个
新的终端 widget 用于改进日志。Esc 关闭输入 widget 而不启动
运行。

## 实现流程

实现运行以有效的 issue 编号和成功的规划为前提。当实现
完成时，如果退出码为零，UI 会追加一个 View PR 按钮；如果退出码
非零，则追加一个 Re-implement 按钮。

## 向后兼容

会话持久化使用 schema 版本控制。存储的会话在加载时会进行迁移，
旧的日志数组会被转换为终端 widget 而不会丢失数据。
