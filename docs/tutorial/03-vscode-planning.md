# 教程 03：VS Code 规划

**阅读时间：4 分钟**

使用 VS Code 的 Plan Activity Bar 视图创建规划，并一键启动实现。

## 你将完成什么

- 在 VS Code 中加载 Agentize Plan 扩展
- 在 Plan Activity Bar 面板中运行规划
- 通过 Implement 按钮启动实现
- 分别查看规划日志和实现日志

## 步骤 1：加载扩展

在仓库根目录下，安装依赖并编译扩展：

```bash
npm --prefix vscode install
npm --prefix vscode run compile
```

然后在 VS Code 中打开扩展：

```bash
code --extensionDevelopmentPath ./vscode
```

## 步骤 2：打开工作区

打开一个包含 Agentize worktree 的工作区。扩展会先查找 `trees/main`，
当工作区根目录本身已包含 Agentize CLI 时则回退到工作区根目录。

## 步骤 3：运行规划

1. 打开 Activity Bar 中的 Plan 视图。
2. 点击 **New Plan**。
3. 输入一段简短的 prompt，然后点击 **Run Plan**。

规划输出会流入 Raw Console Log 面板。当规划器创建占位 issue 时，
扩展会从输出中捕获 issue 编号。

## 步骤 4：实现该规划

规划成功完成后，会话头部会显示一个 **Implement** 按钮。
点击它即可运行 `lol impl <issue-number>`。

实现输出会显示在一个独立的 **Implementation Log** 面板中，
并且在实现运行期间该按钮会被禁用。

两个日志都会把规范的 GitHub issue 和 PR URL 渲染为可点击链接。

## 下一步

- [教程 02：从 Issue 到实现](./02-issue-to-impl.md) 了解 CLI 流程
- [教程 03：进阶用法](./03-advanced-usage.md) 了解并行工作流
