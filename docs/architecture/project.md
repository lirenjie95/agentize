# 项目管理

在 `./metadata.md` 中，我们讨论了存储 GitHub Projects v2 关联信息的
元数据文件 `.agentize.yaml`：

```yaml
project:
   org: Synthesys-Lab  # 所有者（组织或个人用户登录名）
   id: 3
```

本节讨论如何将 GitHub Projects v2 与 `agentize` 化的项目集成。

## 创建或关联项目

**引导式设置（推荐）：**
使用 `/setup-viewboard` 命令进行自包含的项目设置，包含标签、自动化和 Status 字段验证：
```
/setup-viewboard [--org <org-name>]
```

`/setup-viewboard` 命令直接通过 `gh` GraphQL 执行所有项目操作，而不调用 CLI 命令。它会验证 Status 字段选项，并在选项缺失时提供指导 URL。

详情请参见 [/setup-viewboard 文档](../commands/setup-viewboard.md)。

**CLI 命令：**
创建一个新的 GitHub Projects v2 看板并将其与当前仓库关联：
```bash
lol project --create [--org <owner>] [--title <title>]
```

将已有的 GitHub Projects v2 看板与当前仓库关联：
```bash
lol project --associate <owner>/<id>
```

`--org` 标志接受 GitHub 组织或个人用户登录名。省略时默认为仓库所有者。

这两个命令（以及 `/setup-viewboard`）通过 `src/cli/lol/project-lib.sh` 共享实现，并会用 `project.org`（所有者登录名）和 `project.id` 字段更新 `.agentize.yaml`。

## 自动化

`lol project` 命令提供项目关联，但不会自动安装自动化工作流。要自动将 issue 和 pull request 添加到你的项目看板，请参见 [GitHub Projects 自动化指南](../workflows/github-projects-automation.md)。

生成自动化工作流模板：
```bash
lol project --automation [--write <path>]
```

## 项目字段管理

在配置看板之前，你需要使用 GraphQL API 在 GitHub Projects v2 中创建自定义字段。

### 将项目编号转换为 GraphQL ID

将项目编号（例如 `.agentize.yaml` 中的 `3`）转换为其 GraphQL ID。使用 `repositoryOwner` 查询，它对组织和个人用户账户都适用：

```bash
gh api graphql -f query='
query($owner: String!, $number: Int!) {
  repositoryOwner(login: $owner) {
    ... on Organization { projectV2(number: $number) { id title } }
    ... on User { projectV2(number: $number) { id title } }
  }
}' -f owner="Synthesys-Lab" -F number=3
```

### 配置默认 Status 字段

GitHub Projects v2 包含一个内置的 **Status** 字段，可与 Board 视图原生集成。`lol project --automation` 命令会使用 agentize 特定的选项配置这个默认 Status 字段。

**为什么使用默认 Status 字段？**

- **Board 视图亲和性**：GitHub 的 Board 视图围绕 Status 字段设计——列自动映射到 Status 选项，拖放操作无缝更新 Status 字段。
- **内置自动化**：GitHub 的原生自动化（例如 "Item closed → Done"）开箱即可与 Status 字段配合使用。
- **无需维护自定义字段**：使用内置字段省去了创建和维护自定义字段的需要。

**Status 字段选项：**

| 选项 | 描述 | 看板列 |
|--------|-------------|--------------|
| Proposed | agentize 提出的计划，等待批准 | 最左 |
| Refining | 计划正在通过 `/ultra-planner --refine` 精炼 | 第二列 |
| Rebasing | PR 正在与 main 分支 rebase | 第三列 |
| Plan Accepted | 计划已批准，可以开始实现 | 第四列 |
| In Progress | 正在积极开发中 | 第五列 |
| Done | 实现完成 | 最右 |

**自动配置：**

`lol project --automation --write` 命令会通过 GraphQL 自动查询并配置 Status 字段选项。如果需要手动添加选项，请使用 `updateProjectV2` mutation（参见 GitHub 的 GraphQL API 文档）。

### 查询 Issue 的项目字段

查询 issue 的项目字段值（包括 Status）：

```bash
gh api graphql -f query='
query($owner:String!, $repo:String!, $number:Int!) {
  repository(owner:$owner, name:$repo) {
    issue(number:$number) {
      id
      title
      projectItems(first: 20) {
        nodes {
          id
          project {
            id
            title
            number
          }
          fieldValues(first: 50) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue {
                field { ... on ProjectV2SingleSelectField { name } }
                name
              }
            }
          }
        }
      }
    }
  }
}' -f owner='OWNER' -f repo='REPO' -F number=ISSUE_NUMBER
```

这会返回所有项目关联及其字段值，使你可以按状态索引 issue。

### 列出自动化所需的字段和选项 ID

更新项目字段的 GitHub Actions 工作流需要字段和选项 ID。列出所有字段及其选项以配置自动化：

```bash
gh api graphql -f query='
query {
  node(id: "PVT_xxx") {
    ... on ProjectV2 {
      fields(first: 20) {
        nodes {
          ... on ProjectV2SingleSelectField {
            id
            name
            options {
              id
              name
            }
          }
        }
      }
    }
  }
}'
```

将 `PVT_xxx` 替换为你的项目的 GraphQL ID（通过“将项目编号转换为 GraphQL ID”一节中的项目编号查询获得）。

这会返回所有单选字段（如 Stage、Status、Priority）及其选项 ID，通过 GraphQL mutation 更新字段值的自动化工作流需要这些 ID。

### 导出项目配置

自动化工作流可以导出你的项目字段配置并纳入版本控制，以保证可复现性。

## 看板设计 [^1]

我们有两个看板，分别用于计划（GitHub Issues）和实现（Pull Requests）。

### Issue 状态：Board 视图集成

对于 issue，我们使用 GitHub Projects v2 的**默认 Status 字段**，其选项直接映射到 Board 视图的列：

| 状态 | 描述 | 看板列 |
|--------|-------------|--------------|
| Proposed | agentize 提出的计划，等待批准 | 最左 |
| Refining | 计划正在通过 `/ultra-planner --refine` 精炼 | 第二列 |
| Rebasing | PR 正在与 main 分支 rebase | 第三列 |
| Plan Accepted | 计划已批准，可以开始实现 | 第四列 |
| In Progress | 正在积极开发中 | 第五列 |
| Done | 实现完成 | 最右 |

**工作流：**

1. **Proposed**：所有由 AI agent 创建的 issue 都以此状态开始。Issue 正在评审中或等待利益相关者批准。
2. **Refining**：计划正在由 server 通过 `/ultra-planner --refine` 精炼。精炼期间，issue 会被临时锁定以防止并发操作。
3. **Rebasing**：与此 issue 关联的 PR 正在由 `wt rebase` 与 main 分支 rebase。这提供了哪些 issue 正在进行 rebase 操作的可视性。
4. **Plan Accepted**：issue 计划已批准，可以开始实现。`/issue-to-impl` 命令和 `lol serve` 要求 issue 处于此状态（“批准关卡”）。注意：`agentize:plan` 标签用于发现问题，但并不能替代 Plan Accepted 状态关卡。
5. **In Progress**：实现已开始。使用 **assignees** 表明谁在做，使用 **linked PRs** 跟踪进度。
6. **Done**：实现完成。GitHub 的内置自动化可以在 issue 关闭时将其移到此状态。

### 通过 `wt spawn` 进行本地状态更新

当 `wt spawn <issue-no>` 运行时，它会尝试在关联的 GitHub Projects v2 看板上将该 issue 的 Status 设置为 "In Progress"。这是一个**尽力而为**的操作：

- 需要 `.agentize.yaml` 中配置了 `project.org` 和 `project.id`
- 该 issue 必须已经在配置的项目看板上
- 状态更新发生在 worktree 创建成功**之后**
- 失败会被记录，但不会阻塞 worktree 创建或 Claude 调用
- 如果找不到 Status 字段或 "In Progress" 选项，会发出警告

这个本地更新在看板上提供了工作已开始的可视性，是对处理 issue/PR 生命周期自动化的 GitHub Actions 工作流的补充。

**为什么使用默认 Status 字段？**

- **Board 视图亲和性**：GitHub 的 Board 视图围绕 Status 字段设计——列自动映射到 Status 选项，拖放操作会更新 Status 字段。
- **4 个清晰的状态**：覆盖从提案到完成的完整生命周期，没有过度的粒度。
- **内置自动化**：GitHub 的原生自动化（例如 "Item closed → Done"）无缝工作。
- **无自定义字段**：使用内置字段而不是创建自定义的 "Stage" 字段，简化了设置。

### Pull Request 状态

对于 pull request，我们使用标准的 GitHub Projects 工作流：
- `Initial Review`：PR 已创建，等待评审。
- `Changes Requested`：PR 被要求修改。
- `Dependency`：由于依赖其他 PR，此 PR 被阻塞无法合并。
- `Approved`：PR 已批准，可以合并。
- `Merged`：PR 已合并。

[^1]: Kanban **不是**日语词！看（kan4）意为查看，板（ban3）意为板子。所以 Kanban 的字面意思就是“查看板”。
