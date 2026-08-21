# GitHub Projects v2 GraphQL Fixture

本目录包含用于测试 `lol project` 命令的模拟 GraphQL 响应，无需发起真实的 API 调用。

## 文件

### create-project-response.json
`createProjectV2` mutation 的模拟响应。用于测试 `lol project --create`。

**查询：**
```graphql
mutation {
  createProjectV2(input: {ownerId: "...", title: "..."}) {
    projectV2 {
      id
      number
      title
      url
    }
  }
}
```

### lookup-owner-response.json
查询组织 owner 的模拟响应。用于在项目查找之前确定 owner 类型。

**查询：**
```graphql
query($owner: String!) {
  repositoryOwner(login: $owner) {
    id
    __typename
  }
}
```

### lookup-owner-user-response.json
查询用户 owner 的模拟响应。用于 `AGENTIZE_GH_OWNER_TYPE=user` 的场景。

### lookup-project-response.json
查询已有组织项目的模拟响应。用于测试 `lol project --associate`。

**查询：**
```graphql
query($owner: String!, $number: Int!) {
  repositoryOwner(login: $owner) {
    ... on Organization { projectV2(number: $number) { id number title url } }
    ... on User { projectV2(number: $number) { id number title url } }
  }
}
```

### lookup-project-user-response.json
查询用户项目的模拟响应。用于 `AGENTIZE_GH_OWNER_TYPE=user` 的场景。

### create-project-user-response.json
创建用户项目的模拟响应。用于 `AGENTIZE_GH_OWNER_TYPE=user` 的场景。

### add-item-response.json
向项目添加 issue 或 PR 的模拟响应。用于测试可选的 `--add` 功能。

**查询：**
```graphql
mutation {
  addProjectV2ItemById(input: {projectId: "...", contentId: "..."}) {
    item {
      id
    }
  }
}
```

### get-issue-project-item-response.json
查询 issue 项目条目的模拟响应。用于测试 `wt spawn` 状态认领功能。

**查询：**
```graphql
query($owner:String!, $repo:String!, $number:Int!) {
  repository(owner:$owner, name:$repo) {
    issue(number:$number) {
      id
      projectItems(first: 20) {
        nodes {
          id
          project { id }
        }
      }
    }
  }
}
```

### update-field-response.json
更新项目字段值的模拟响应。用于测试 `wt spawn` 状态认领功能。

**查询：**
```graphql
mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
  updateProjectV2ItemFieldValue(input: {
    projectId: $projectId, itemId: $itemId, fieldId: $fieldId,
    value: { singleSelectOptionId: $optionId }
  }) {
    projectV2Item { id }
  }
}
```

## 在测试中使用

测试应设置 `AGENTIZE_GH_API` 环境变量以使用 fixture 替代真实 API：

```bash
export AGENTIZE_GH_API=fixture
```

`scripts/gh-graphql.sh` wrapper 会检查该变量，并在设置时返回 fixture 数据。此外，fixture 模式会绕过 `scripts/agentize-project.sh` 中的 `gh auth status` 预检查，使测试可以在没有 GitHub 认证的 CI 环境中运行。

## Owner 类型选择

默认情况下，fixture 返回组织风格的响应。要测试用户拥有的项目，请设置 `AGENTIZE_GH_OWNER_TYPE`：

```bash
export AGENTIZE_GH_OWNER_TYPE=user
```

这会选用用户专用的 fixture（`lookup-owner-user-response.json`、`lookup-project-user-response.json`、`create-project-user-response.json`），它们返回的 URL 使用 `/users/` 路径而非 `/orgs/`。
