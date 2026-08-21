# 看板视图管理

## 概述

本文档描述 Agentize 如何与 GitHub Projects V2 集成，提供看板式的视图管理。

- 由 `core/ultra-planner.md` 创建的每个计划都会在视图上显示为一个条目。
- 由 `core/issue-to-impl.md` 从计划执行的每个 PR 都会在视图上显示为一个条目。

"视图"（viewboard）是一个具有多个视图的 GitHub Projects v2 看板（通常 issue 用 Board 视图，PR 用 Table/Board 视图）。Agentize 依赖**默认 Status 字段**，使得在 Board 视图中拖拽即可自动更新生命周期状态。

## 设置

**推荐：** 使用 `/setup-viewboard` 创建/关联 Project v2 看板，配置 Status 选项，并创建标签。

```
/setup-viewboard [--org <org-name>]
```

该工作流：
- 创建或关联 Project v2 看板并存储在 `.agentize.yaml` 中
- 确保 Status 选项存在（Proposed、Refining、Rebasing、Plan Accepted、In Progress、Done）
- 创建用于发现和自动化的 agentize 标签

参见：
- [Setup Viewboard](../commands/setup-viewboard.md)
- [Project Management](../architecture/project.md)

## 视图结构

使用**单个 Project v2** 配合多个过滤视图：

### 计划视图（Issues）

推荐过滤器：
```
is:issue is:open label:agentize:plan
```

此视图是你的计划待办队列和审批队列。

### 实现视图（PRs）

推荐过滤器：
```
is:pr is:open label:agentize:pr
```

此视图追踪活跃实现和审查。

你可以通过按 Status 字段过滤创建其他视图（例如 "Refining"、"Rebasing"）。

## Status 生命周期

Agentize 使用默认的 Project Status 字段驱动看板列：

| Status | 含义 | 典型触发 |
|--------|---------|-----------------|
| Proposed | 新计划已创建，等待审查 | `/ultra-planner`、自动添加工作流 |
| Refining | 计划改进进行中 | `lol serve` + `/ultra-planner --refine` |
| Rebasing | PR 分支正在 rebase | `lol serve` + `wt rebase` |
| Plan Accepted | 已批准实现 | 人工审查关卡 |
| In Progress | Worktree 已创建，实现已开始 | `wt spawn`（尽力而为） |
| Done | 已完成并合并/关闭 | GitHub 自动归档或手动关闭 |

**关键规则：**
- **Plan Accepted 是实现的审批关卡**。`lol serve` 仅在 Status = "Plan Accepted" 时才派生工作。
- **Refining** 是可选的，但启用自动改进时必需。
- **Rebasing** 用于在 server 解决冲突时提供可见性。

更多细节见 [Project Management](../architecture/project.md)。

## 自动化与同步

有两种方式保持 issue/PR 与视图同步：

1. **GitHub 内置自动添加工作流**（推荐，更简单）
2. 由 `lol project --automation --write` 生成的 **GitHub Actions 工作流**

设置细节见 [GitHub Projects v2 自动化](github-workflow.md)。

## Server 集成

本地 server（`lol serve`）轮询视图，并使用 Status + 标签决定运行什么：
- 带 `agentize:plan` 且 Status = `Plan Accepted` 的 issue -> 派生实现 worktree
- 带 `agentize:plan` + `agentize:refine` 且 Status = `Proposed` 的 issue -> 运行改进
- 带 `agentize:pr` 且有合并冲突的 PR -> 触发 rebase

完整生命周期和过滤器见 [Server](server.md)。

## 相关文档

- `github-workflow.md`：用于将看板与计划和实现进度同步的 GitHub Actions。
- `../commands/setup-viewboard.md`：端到端的视图设置工作流。
- `../architecture/project.md`：Status 字段配置和生命周期细节。
- `server.md`：Server 自动化和轮询逻辑。
