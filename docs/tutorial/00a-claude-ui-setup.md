> **在找 CLI 快速上手？** 参见 [教程 00：CLI 快速上手](./00-cli-quickstart.md) 了解 `wt clone` -> `lol plan` -> `lol impl` 工作流。
>
> 本教程面向偏好使用 `/ultra-planner` 和 `/issue-to-impl` 斜杠命令的用户，介绍 Claude UI 的配置。

# 教程 00a：Claude UI 配置

**阅读时间：3-5 分钟**

本教程演示如何在你的项目中配置 Agentize 框架和 Claude Code 插件。
如果你偏好使用 Claude UI 斜杠命令进行规划和实现，请走这条路径。

## 开始使用

安装 Agentize（见 README.md）之后，你就可以在项目中开始使用它的功能了。

## 安装 Agentize

Agentize 使用一个统一的安装器，同时处理 CLI 工具和 Claude Code 插件：

```bash
curl -fsSL https://raw.githubusercontent.com/SyntheSys-Lab/agentize/main/scripts/install | bash
```

然后将其添加到你的 shell RC 文件（`~/.bashrc`、`~/.zshrc` 等）中：

```bash
source $HOME/.agentize/setup.sh
```

安装器会自动：
1. 克隆仓库并运行 setup
2. 注册本地 Claude Code 插件 marketplace（如果 `claude` CLI 可用）
3. 将 `agentize` 插件安装到 Claude Code 中

如果在 setup 时 `claude` 尚未安装，你可以稍后重新运行安装器来注册插件，或手动注册：

```bash
claude plugin marketplace add "$HOME/.agentize"
claude plugin install agentize@agentize
```

## 验证安装

完成 setup 后，验证 CLI 入口可用（安装器会同时配置 CLI 和 UI 工具）：

```bash
lol plan --help
lol impl --help
```

可选的 Claude UI 检查（参见 `docs/feat/core/ultra-planner.md` 和 `docs/feat/core/issue-to-impl.md`）：

```bash
# 在你的项目目录中使用 Claude Code
/ultra-planner # 应弹出自动补全
/issue-to-impl
```

你应该能看到列出的自定义命令（如 `/issue-to-impl`、`/code-review` 等）。

## 推荐的项目组织方式

0. `docs/` 是 agent 理解你项目的关键。
1. 编辑 `docs/git-msg-tags.md`——当前的标签是为 Agentize 项目本身准备的。你可以自定义这些标签以满足你项目的模块需求。
例如，你可以添加项目专属的标签：
```markdown
- `api`: API changes
- `ui`: User interface updates
- `perf`: Performance improvements
```
2. 建议建立一个 `docs/architecture/` 文件夹，用于记录项目的架构。这能帮助 agent 更好地理解你的项目。


## 下一步

初始化完成后：
- **教程 00**：如果你偏好 CLI 入门，从 [教程 00：CLI 快速上手](./00-cli-quickstart.md) 开始
- **教程 01**：学习使用 `lol plan --editor` 进行 CLI 规划（会用到你刚自定义的 git 标签）
- **教程 02**：学习使用 `lol impl <issue-no>` 的 CLI 实现循环
- **教程 03**：通过并行开发工作流实现规模化

## 配置选项

详细的配置选项：
- 架构概览见 `README.md`
- 设计文档见 `docs/architecture/`
