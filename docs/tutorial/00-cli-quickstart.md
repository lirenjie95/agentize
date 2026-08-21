# 教程 00：CLI 快速上手

**阅读时间：5 分钟**

用大约 15 分钟学会 Agentize CLI 核心工作流：配置 -> 克隆 -> 规划 -> 实现 -> 导航。

## 你将完成什么

- 确认本地 Agentize 配置已存在
- 以 bare + worktree 布局克隆一个仓库
- 用 `lol plan --editor` 创建规划
- 用 `lol impl <issue-number>` 实现该规划
- 用 `wt goto` 在 worktree 之间切换

## 步骤 1：确认本地配置

安装器会在你的主目录下创建 `~/.agentize.local.yaml`。该文件控制规划器和实现工作流使用哪些 AI 后端。

检查它是否存在：

```bash
ls ~/.agentize.local.yaml
```

如果你想更换模型或后端，打开该文件并编辑 planner/impl 设置。完整 schema 参见 `docs/cli/lol.md`。

## 步骤 2：以 worktree 方式克隆

Agentize 使用 bare 仓库配合 worktree，这样每个 issue 都可以拥有自己独立的工作目录，而不会产生分支冲突。

将项目克隆为 bare 仓库并初始化 worktree：

```bash
wt clone https://github.com/org/repo.git myproject.git
```

`wt clone` 会搭建 bare 仓库并把你置于 `trees/main` 中，因此你可以立即开始规划。
完整的 `wt` 命令参考见 `docs/feat/cli/wt.md`。

## 步骤 3：规划你的第一个功能

使用规划器创建一个带有共识实现方案的 GitHub issue：

```bash
lol plan --editor
```

如果你没有配置 `$EDITOR`，可以直接传入描述：

```bash
lol plan "Add user authentication"
```

查看新创建的 issue，确保方案与你想要构建的内容一致。
完整的 `lol` 命令参考见 `docs/cli/lol.md`。

## 步骤 4：实现该规划

为该 issue 启动自动化实现循环：

```bash
lol impl <issue-number>
```

`lol impl` 会创建 issue 对应的 worktree（如有需要）、进入该 worktree，并运行实现工作流。

## 步骤 5：在 worktree 之间导航

迭代过程中在 worktree 之间跳转：

```bash
wt goto <issue-number>
wt goto main
```

随时使用 `wt list` 查看所有可用的 worktree。

## 下一步

- [教程 01：Ultra Planner](./01-ultra-planner.md) 深入了解规划
- [教程 02：从 Issue 到实现](./02-issue-to-impl.md) 了解完整的 CLI 循环
- [教程 03：进阶用法](./03-advanced-usage.md) 了解并行工作流与规模化
