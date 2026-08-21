# GitHub Projects v2 自动化

本文档描述在使用 `lol project` 创建或关联项目后，如何为 GitHub Projects v2 看板设置自动化。

## 概述

`lol project` 命令通过将项目元数据存储在 `.agentize.yaml` 中，将 GitHub Projects v2 看板与你的仓库关联起来。自动化设置（自动将 issue 和 pull request 添加到项目）通过 GitHub 的原生功能单独处理。

## 自动化方法

### 方法 1：GitHub 内置自动添加过滤器（推荐）

GitHub Projects v2 提供内置的自动添加工作流，无需任何代码或 Actions 设置。

**设置步骤：**

1. 在 GitHub 上打开你的项目看板
2. 点击右上角的三点菜单（⋯）
3. 选择 **Workflows**
4. 启用 **Auto-add to project**
5. 配置过滤器：
   - **针对 issue：** `is:issue is:open repo:owner/repo`
   - **针对 pull request：** `is:pr is:open repo:owner/repo`

**优势：**
- 无需 GitHub Actions
- 无需维护工作流文件
- 立即生效
- 无 API 速率限制

**限制：**
- 仅支持基本过滤器
- 无法运行自定义逻辑或设置字段值

### 方法 2：GitHub Actions 工作流（高级）

如需对自动化有更多控制（例如设置自定义字段值、复杂过滤），使用 `actions/add-to-project` action 配合 GitHub GraphQL API 进行生命周期管理。

**设置步骤：**

1. 生成并配置工作流模板：
   ```bash
   lol project --automation --write .github/workflows/add-to-project.yml
   ```

   该命令将：
   - 查询项目的默认 Status 字段
   - 如需要，使用 agentize 选项（Proposed、Plan Accepted、In Progress、Done）配置 Status 字段
   - 生成使用 `status-field: Status` 和 `status-value: Proposed` 的工作流
   - 将完整配置的工作流写入指定路径

2. **重要：** 如果你在使用 agentize 的 refinement 工作流，请在项目的 Status 字段中手动添加一个 "Refining" 选项（位于 "Proposed" 和 "Plan Accepted" 之间）。这是 server 自动改进功能所需的。

3. 设置 Personal Access Token（见下文[安全：Personal Access Token (PAT)](#安全personal-access-token-pat)部分）

4. 提交并推送：
   ```bash
   git add .github/workflows/add-to-project.yml
   git commit -m "Add GitHub Projects automation workflow"
   git push
   ```

5. 在 **Actions** 标签页验证工作流运行

**注意：** 如果命令无法访问你的项目（例如未认证或项目不存在），它将生成带占位符值的模板，需要你手动配置。见下文[手动配置](#手动配置)。

**模板参考：** 见 [`templates/github/project-auto-add.yml`](../../templates/github/project-auto-add.yml)

**自动化能力：**
- 自动将新 issue 和 PR 添加到项目看板
- 将新打开的 issue 的 Status 设为 "Proposed"（使用默认 Status 字段）
- 当关联的 PR 被合并时关闭链接的 issue（使用 GitHub 的 `closingIssuesReferences`）
- 归档项目看板中已合并的 PR 条目（减少活跃视图的杂乱）
- 看板视图列自动反映 4 个 Status 选项

**优势：**
- 对自动化逻辑的细粒度控制
- 使用默认 Status 字段实现看板视图集成
- 通过 GitHub 的 closingIssuesReferences 原生链接 PR 与 issue
- 支持复杂过滤条件
- 无需创建自定义字段——使用内置 Status 字段

**限制：**
- 需要维护工作流文件
- 消耗 GitHub Actions 分钟数
- 在大型仓库上可能触发 API 速率限制
- 仅归档已合并的 PR 条目（不包含手动 issue 归档；更广泛的生命周期处理请使用 GitHub 内置的自动归档）

## 设置自定义字段值

生成的工作流模板使用 `actions/add-to-project` action 的内置 `status-field` 和 `status-value` 参数，自动将新 issue 的 Status 字段设为 "Proposed"。

**基本自定义：**

编辑生成的工作流以更改字段名或值：
```yaml
- uses: actions/add-to-project@v1.0.2
  with:
    project-url: https://github.com/orgs/${{ env.PROJECT_ORG }}/projects/${{ env.PROJECT_ID }}
    github-token: ${{ secrets.ADD_TO_PROJECT_PAT }}
    # 自定义字段名和值：
    status-field: Status  # 或 "Stage"、"Priority" 等
    status-value: Proposed  # 或 "Backlog"、"To Do" 等
```

**高级生命周期自动化：**

模板还包含一个 PR 合并任务，在 PR 合并时关闭链接的 issue。这使用 GitHub CLI 的 `gh issue close` 命令，比 GraphQL mutation 更简单且不需要 option ID。

所有可用的 action 参数见 [`actions/add-to-project` 文档](https://github.com/actions/add-to-project)。

## 手动配置

**何时需要手动配置？**

`lol project --automation --write` 命令会自动为你配置 Status 字段。但是，以下情况可能需要手动配置：
- 你未通过 GitHub CLI 认证（`gh auth login`）
- 项目不存在或你没有访问权限
- 项目的 Status 字段选项需要手动调整

如果自动配置失败，命令将生成带占位符值的模板并提供手动设置说明。

### 手动查找字段 ID

生成的工作流模板使用 `actions/add-to-project` action 将新 issue 的 Status 字段设为 "Proposed"。如需手动配置，请按以下步骤操作。

**步骤 1：获取项目的 GraphQL ID**

将项目编号转换为其 GraphQL node ID。使用 `repositoryOwner` 查询，它对组织和个人用户账户都适用：

```bash
gh api graphql -f query='
query($owner: String!, $number: Int!) {
  repositoryOwner(login: $owner) {
    ... on Organization { projectV2(number: $number) { id title } }
    ... on User { projectV2(number: $number) { id title } }
  }
}' -f owner="YOUR_OWNER" -F number=YOUR_PROJECT_NUMBER
```

保存 `id` 值（例如 `PVT_xxx`）以供下一步使用。

**步骤 2：列出所有字段**

查询所有单选字段（如 Stage/Status）：

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

**步骤 3：验证 Status 字段选项**

从查询输出中，找到 "Status" 字段并验证它具有预期的选项（Proposed、Plan Accepted、In Progress、Done）。`actions/add-to-project` action 直接使用字段名（"Status"）和选项名（"Proposed"）——工作流中不需要字段 ID。

**步骤 4：更新工作流环境变量**

简化后的工作流只需要 owner 和项目 ID：

```yaml
env:
  PROJECT_ORG: YOUR_OWNER_HERE           # 组织或个人用户登录名
  PROJECT_OWNER_PATH: orgs               # 组织用 "orgs"，个人账户用 "users"
  PROJECT_ID: YOUR_PROJECT_ID_HERE
```

**注意：** 工作流使用 `status-field: Status` 和 `status-value: Proposed` 设置初始状态。不需要字段 ID，因为 `actions/add-to-project` action 会自动解析字段名。

## 安全：Personal Access Token (PAT)

如果使用**方法 2**，工作流需要具有项目权限的 GitHub Personal Access Token (PAT)。

**创建 PAT：**

1. 前往 `https://github.com/settings/personal-access-tokens/new`（或 **Settings** > **Developer settings** > **Personal access tokens** > **Fine-grained tokens** > **Generate new token**）
2. 配置 token 设置：
   - **Token name：** 例如 "Add to Project Automation"
   - **Expiration：** 90 天（出于安全考虑推荐）
   - **Repository access：** 选择你的仓库
3. 设置权限：
   - **Repository permissions：**
     - `Issues`：**Read and write**（关闭 issue 所需）
     - `Pull requests`：**Read and write**（读取 PR 链接的 issue 所需）
     - `Metadata`：Read-only（自动授予）
   - **Organization permissions：**
     - `Projects`：**Read and write**（向项目添加条目所需）
4. 点击 **Generate token**
5. 复制 token（之后将无法再看到）

**将 PAT 添加到仓库：**

**选项 A：使用 GitHub CLI（推荐）：**
```bash
gh secret set ADD_TO_PROJECT_PAT
# 提示时粘贴你的 token
```

**选项 B：使用 GitHub 网页界面：**
1. 前往仓库的 **Settings** > **Secrets and variables** > **Actions**
2. 点击 **New repository secret**
3. 名称：`ADD_TO_PROJECT_PAT`
4. 值：粘贴你的 token
5. 点击 **Add secret**

## 故障排查

### 工作流未触发

- 验证工作流文件在 `.github/workflows/` 中且以 `.yml` 扩展名命名
- 检查 **Actions** 标签页中的错误信息
- 确保 PAT 具有正确的权限且未过期

### 条目未被添加

- 检查 **Actions** 标签页中的工作流运行日志
- 验证项目 URL 和组织/项目 ID 正确
- 对于方法 1，检查自动添加过滤器语法

### 权限错误

- 确保 PAT 具有所有必需的权限：
  - 仓库：`Issues`（Read and write）、`Pull requests`（Read and write）
  - 组织：`Projects`（Read and write）
- 验证 PAT 已作为 `ADD_TO_PROJECT_PAT` 存储在仓库 secrets 中
- 检查工作流使用的是 `secrets.ADD_TO_PROJECT_PAT`，而非 `secrets.GITHUB_TOKEN`

## 相关命令

- `lol project --create` - 创建新的 GitHub Projects v2 看板
- `lol project --associate <owner>/<id>` - 关联现有项目
- `lol project --automation` - 打印工作流模板
- `lol project --automation --write <path>` - 将模板写入文件

## 参考资料

- [GitHub Projects v2 文档](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [actions/add-to-project action](https://github.com/actions/add-to-project)
- [GitHub 自动添加工作流](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/adding-items-automatically)
