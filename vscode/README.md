# VS Code Agentize 扩展

本目录包含一个 VS Code Activity Bar 扩展，它封装了 Agentize CLI 的规划工作流，
并将其与 Worktree 和 Settings 面板一起呈现。

## 组织结构

- `src/` 包含扩展后端代码（state、runner 和 view 接线）。
- `webview/` 包含在 Activity Bar webview 中渲染的 Plan、Worktree 和 Settings 标签页 UI 资源。
- `resources/` 包含 Activity Bar 容器和各个标签页的图标。
- `bin/` 包含扩展运行时使用的辅助可执行文件。

## 从规划到实现的流程

当规划成功完成且规划器创建了占位 GitHub issue 后，
Plan 标签页会显示一个 Implement 按钮。点击它会在单独的
Implementation Log 面板中启动 `lol impl <issue-number>`，
从而使规划输出和实现输出保持分离。

## Settings UI

Settings 标签页为 Agentize 工作流提供后端配置 UI。它显示
`.agentize.yaml`（只读）以及可编辑的仓库级和全局 `.agentize.local.yaml` 作用域。
后端选择以 `provider:model` 格式存储为 `planner.backend` 值，
扩展在运行实现工作流时会使用这些值。

## 前置条件

- Node.js + npm（用于编译扩展的 TypeScript）。
- Bash（由 `lol` wrapper 使用）。
- 仓库根目录中生成的 `setup.sh`（在包含 `vscode/` 的仓库根目录下运行 `make setup`）。

## 构建

```bash
npm --prefix vscode install
npm --prefix vscode run compile
```

开发监视模式：

```bash
npm --prefix vscode run watch
```

## 在 VS Code 中加载

- 命令行：`code --extensionDevelopmentPath ./vscode`
- 或使用 VS Code 命令面板："Developer: Install Extension from
  Location..."，然后选择 `vscode/` 文件夹。

## 工作区要求

Plan runner 需要一个 Agentize CLI 可用的工作目录。
它按以下规则解析规划工作目录：

- 如果任何已打开的工作区文件夹包含 `trees/main`（由 `wt init` 或
  `wt clone` 创建），runner 使用 `<workspace>/trees/main`。
- 否则，回退到工作区文件夹根目录（适用于直接打开单个 worktree
  如 `trees/issue-866` 的情况）。

## 细化规划

当规划会话完成（成功或出错）时，会话卡片上会出现一个 Refine 按钮。

1. 在已完成的会话上点击 Refine。
1. 会话内会出现一个内联文本框（如有需要请展开会话）。
1. 输入细化重点或指令，然后按 Cmd+Enter / Ctrl+Enter。

扩展会运行 `lol plan --refine <issue> "<focus>"`，
并像其他运行一样在规划视图中流式输出细化会话。
