# /setup-viewboard 命令

为 agentize 工作流集成设置 GitHub Projects v2 看板。

## 概要

```
/setup-viewboard [--org <org-name>]
```

## 描述

`/setup-viewboard` 命令为 GitHub Projects v2 看板提供自包含的设置，包括与 agentize 兼容的 Status 字段、标签和自动化工作流。它通过共享的项目库（`src/cli/lol/project-lib.sh`）直接使用 `gh` GraphQL 操作，而不调用 `lol project` CLI 命令。

## 选项

| 选项 | 是否必需 | 默认值 | 描述 |
|--------|----------|---------|-------------|
| `--org <org-name>` | 否 | 仓库所有者 | 项目看板所属的 GitHub 组织或个人用户登录名 |

## 工作流

该命令执行以下步骤：

0. **检查 `gh` CLI 可用性**：验证 `gh` 已安装。如果未安装，引导用户访问 https://github.com/cli/cli 进行安装。

1. **检查 `.agentize.yaml`**：读取现有的 `project.org` 和 `project.id` 字段，检测已有的项目关联。

2. **创建或关联项目看板**：
   - 如果不存在关联：通过 GraphQL 创建项目（`project_create`）
   - 如果已存在关联：通过 GraphQL 验证项目（`project_associate`）

3. **生成自动化工作流**：通过 `project_generate_automation` 生成工作流并写入 `.github/workflows/add-to-project.yml`

4. **验证并创建 Status 字段选项**：通过 GraphQL 查询项目 Status 字段并自动创建缺失的选项：
   - 如果选项缺失：通过 `createProjectV2FieldOption` mutation 自动创建
   - 如果自动创建失败（权限问题）：显示手动配置的引导 URL
   - 必需选项：Proposed、Refining、Rebasing、Plan Accepted、In Progress、Done

5. **创建标签**：使用 `gh label create --force` 创建 agentize issue 标签：
   - `agentize:plan` - 带有实现计划的 issue
   - `agentize:refine` - 排队待细化的 issue
   - `agentize:dev-req` - 开发者请求 issue（分诊）
   - `agentize:bug-report` - bug 报告 issue（分诊）
   - `agentize:pr` - 为实现创建的 PR

## Status 字段选项

该命令期望 GitHub Projects v2 看板具有以下 Status 字段选项：

| 状态 | 描述 |
|--------|-------------|
| Proposed | 计划已由 agentize 提出，等待批准 |
| Refining | 计划正在被 `/ultra-planner --refine` 细化 |
| Rebasing | PR 正在与主分支 rebase |
| Plan Accepted | 计划已批准，可以开始实现 |
| In Progress | 正在积极开发中 |
| Done | 实现完成 |

这些状态选项与 Board 视图列集成。Status 字段配置详情请参阅 [Project Management](../architecture/project.md)。

## 前置条件

- `gh` CLI 已安装并认证（`gh auth login`）
- `.agentize.yaml` 存在且可写
- 启用自动化时需配置 GitHub Actions secret `ADD_TO_PROJECT_PAT`（见工作流文件）

## 示例

### 创建用户所有的项目看板

```
/setup-viewboard
```

创建一个由当前用户所有的项目看板（默认为仓库所有者）。

### 创建组织所有的项目看板

```
/setup-viewboard --org my-org
```

在指定组织下创建项目看板。

## Handsoff 模式支持

当 `HANDSOFF_MODE=1` 时，`/setup-viewboard` 作为受跟踪的工作流运行，为其特定的 `gh` CLI 命令自动传递权限：

- `gh auth status` - 认证验证
- `gh repo view --json owner -q ...` - 仓库所有者查询
- `gh api graphql` - 项目创建和配置
- `gh label create --force` - 标签创建

这些权限**仅在 setup-viewboard 工作流期间**自动授予，保持全局权限模型不变。工作流跟踪详情请参阅 [Handsoff Mode](../feat/core/handsoff.md)。

## 另请参阅

- [Project Management](../architecture/project.md) - 架构文档
- [Metadata File](../architecture/metadata.md) - `.agentize.yaml` 模式
- [lol project](../cli/lol.md#lol-project) - CLI 接口（与本命令共享实现）
- [Handsoff Mode](../feat/core/handsoff.md) - 工作流跟踪和自动续接
