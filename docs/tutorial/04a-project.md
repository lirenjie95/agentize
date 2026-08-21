# 教程 04：配置项目看板自动化

**阅读时间：3-5 分钟**

运行 `/setup-viewboard` 之后，你需要配置一个 Personal Access Token (PAT) 以启用 issue 到项目的自动同步。

## 为什么需要这样做

`/setup-viewboard` 命令会创建一个 GitHub Actions 工作流（`.github/workflows/add-to-project.yml`），自动将新 issue 添加到你的项目看板。该工作流需要一个具有项目权限的 PAT 才能正常工作。

## 步骤 1：打开 GitHub 设置

点击右上角的头像，然后选择 **Settings**。

![Open Settings](images/open-settings.png)

## 步骤 2：进入开发者设置

滚动到左侧边栏底部，点击 **Developer settings**。

![Developer Settings](images/developer-settings.png)

## 步骤 3：创建 Personal Access Token

在开发者设置中，展开 **Personal access tokens** 并点击 **Tokens (classic)**。

![Create PAT](images/create-pat.png)

## 步骤 4：生成 Classic Token

点击 **Generate new token** 并选择 **Generate new token (classic)**。

![Classic Token](images/classic-token.png)

## 步骤 5：配置 Token

为你的 token 起一个描述性的名称（例如 `agentize-project-automation`）。

![Give a Name to PAT](images/give-a-name-to-pat.png)

## 步骤 6：授予所需权限

向下滚动，在权限中勾选以下 scope：

1. **`repo`** — 允许从仓库读取 issue 和 PR 数据
2. **`project`** — 允许对 Projects v2 看板的完整读写访问
3. **`read:org`** — 允许解析组织级的项目 URL

组织级 Projects v2 看板需要全部三个 scope。

![Give Project Permission](images/give-proj-permission.png)

点击底部的 **Generate token**，并**立即复制 token 值**——你将无法再次看到它。

## 步骤 7：进入仓库设置

导航到你的仓库，点击仓库导航栏中的 **Settings**。

![Go to Repo Settings](images/go-to-repo-settings.png)

## 步骤 8：创建仓库 Secret

在仓库设置侧边栏中：
1. 展开 **Secrets and variables**
2. 点击 **Actions**
3. 点击 **New repository secret**
4. 名称：`ADD_TO_PROJECT_PAT`
5. 值：粘贴你之前复制的 token
6. 点击 **Add secret**

![Secrets for Variable](images/secrets-for-variable.png)

## 验证

配置完成后，仓库中创建的任何新 issue 都会自动添加到你的项目看板。你可以通过以下方式验证：

1. 创建一个测试 issue
2. 检查 **Actions** 标签页中的工作流运行情况
3. 确认该 issue 出现在你的项目看板中

## 故障排除

**工作流失败，报错 "Could not resolve to a node with the global id"**
- 这是一个误导性错误，由 PAT 缺少 scope 引起
- 确保 Classic PAT 具有全部三个 scope：`repo`、`project`、`read:org`

**工作流失败，报错 "Resource not accessible by integration"**
- 确保 PAT 具有 `project` scope
- 确认 secret 名称恰好是 `ADD_TO_PROJECT_PAT`

**Issue 未出现在看板上**
- 检查 `.agentize.yaml` 中的项目 ID 是否与你的实际项目匹配
- 确认工作流文件存在于 `.github/workflows/add-to-project.yml`

## 下一步

项目自动化配置完成后，你的 issue 将自动流入项目看板，你可以在其中跟踪它们经过 agentize 工作流各阶段的状态：Proposed → Refining → Plan Accepted → In Progress → Done。
