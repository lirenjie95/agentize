# Git 消息标签

本文档定义了 git 提交消息中使用的标签。

## 提交标签

- `feat`：添加了新功能。
- `sdk`：修改或创建 SDK 模板。
- `cli`：命令行界面相关的变更。
- `bugfix`：修复了一个 bug。
- `docs`：更新或添加了文档。
- `test`：添加或修改了测试用例以及测试相关的基础设施。
  - 当同时存在 `bugfix`、`sdk` 或 `feat` 时，不要使用此标签。
  - 仅在只修改测试用例时使用此标签。
- `refactor`：在不改变功能的前提下重构了代码。
- `chore`：日常任务，如代码格式化、依赖更新等。
- `agent.<sub-tag>`：与 AI agent 配置或行为相关的变更。
  - `.skill`：修改现有 skill 或添加新 skill。
  - `.command`：对 slash command 的变更。
  - `.settings`：对 agent 设置或配置的变更。
  - `.workflow`：对基于 agent 的工作流或流程的变更。
- `review`：当此代码变更由代码评审意见驱动时。
  - 此标签应在所有其他标签之前附加使用。
  - 通常不能作为独立标签使用。

## Issue 标签

- `plan`：由 `/plan-to-issue`（简单）或 `/ultra-planner`（复杂）命令创建的计划。
- `discussion`：由一次讨论的总结创建的 issue。
- `roadmap`：通过向 `/roadmapper` 命令提供一个 `discussion` issue 而创建的 issue。
