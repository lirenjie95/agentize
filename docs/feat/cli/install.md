# `install`：Agentize 安装脚本

## 概述

Agentize 的一键安装脚本，可克隆仓库、初始化 worktree 布局、运行 setup，并提供 shell RC 集成说明。

## 用法

```bash
curl -fsSL https://raw.githubusercontent.com/SyntheSys-Lab/agentize/main/scripts/install | bash
```

或使用自定义选项：

```bash
curl -fsSL https://raw.githubusercontent.com/SyntheSys-Lab/agentize/main/scripts/install | bash -s -- [OPTIONS]
```

从本地克隆直接执行：

```bash
./scripts/install [OPTIONS]
```

### Windows 安装

在 Windows 10 上，使用 **Git Bash**（随 [Git for Windows](https://git-scm.com/download/win) 提供）：

1. 安装 [Git for Windows](https://git-scm.com/download/win)
2. 打开 **Git Bash** 并安装 `make`：
   ```bash
   pacman -S make
   ```
3. 在 Git Bash 中运行安装脚本：
   ```bash
   bash scripts/install
   ```

安装完成后，在 Git Bash 中 source `setup.sh` 以启用 `wt` 和 `lol` 命令。

## 选项

- `--dir <path>` - 安装目录（默认：`$HOME/.agentize`）
- `--repo <url-or-path>` - Git 仓库 URL 或本地路径（默认：https://github.com/SyntheSys-Lab/agentize.git）
- `--help` - 显示帮助信息并退出

## 行为

安装脚本执行以下步骤：

1. **依赖检查** - 验证 `git`、`make` 和 `bash` 可用（在 Windows 上，若缺少工具则提供 `pacman -S` 安装指引）
2. **克隆仓库** - 克隆（或从本地路径复制）到安装目录
3. **初始化 worktree** - 运行 `wt init` 创建 `trees/main` worktree
4. **运行 setup** - 在 `trees/main` 中执行 `make setup` 生成 `setup.sh`（Windows 感知的 `PYTHONPATH`，使用 `;` 分隔符）
5. **注册 Claude 插件**（可选）- 如果 `claude` CLI 可用：
   - 移除所有过期的 marketplace/plugin 条目
   - 将安装目录注册为本地插件 marketplace
   - 安装 `agentize@agentize` 插件
   - 所有 Claude 步骤均为非致命操作；失败会记录日志但不会阻塞安装
6. **打印说明** - 显示 shell RC 集成命令

## 安装后步骤

安装完成后，将以下内容添加到你的 shell RC 文件（`~/.bashrc`、`~/.zshrc` 等）：

```bash
source $HOME/.agentize/trees/main/setup.sh
```

然后重启 shell 或 source RC 文件：

```bash
source ~/.bashrc  # 或 ~/.zshrc
```

这样即可在任何目录中使用 `wt` 和 `lol` 命令。

## 退出码

- `0` - 安装成功
- `1` - 安装失败（缺少依赖、克隆失败、初始化失败、setup 失败，或安装目录已存在）

## 示例

**默认安装：**

```bash
curl -fsSL https://raw.githubusercontent.com/SyntheSys-Lab/agentize/main/scripts/install | bash
```

**自定义安装目录：**

```bash
curl -fsSL https://raw.githubusercontent.com/SyntheSys-Lab/agentize/main/scripts/install | bash -s -- --dir ~/my-agentize
```

**从本地仓库安装（用于测试）：**

```bash
./scripts/install --repo /path/to/local/agentize --dir /tmp/test-install
```

## 安全特性

- **不自动修改 RC 文件** - 安装脚本绝不修改 shell RC 文件；仅打印手动集成的说明
- **安装目录检查** - 如果目标目录已存在则失败，防止意外覆盖
- **依赖验证** - 在继续之前检查所需命令

## 故障排查

**错误：安装目录已存在**

安装脚本拒绝覆盖现有安装。请删除该目录或指定不同的 `--dir`。

```bash
rm -rf $HOME/.agentize  # 删除现有安装
```

**错误：缺少依赖**

使用系统包管理器安装所需依赖（`git`、`make`、`bash`）。

**错误：初始化 worktree 失败**

确保克隆的仓库是有效的 git 仓库，且 `wt init` 能成功运行。检查仓库是否有 `main` 或 `master` 分支。

## 实现说明

- 复用现有 `wt init` 行为进行 worktree 初始化
- 复用 `make setup` 进行环境设置
- 不实现回滚、卸载或更新流程
- 插件注册是可选且非致命的；能优雅处理 `claude` CLI 缺失的情况

## 插件注册故障排查

**安装后插件未出现**

本地 marketplace 注册可能在 Claude 重启后失效。手动重新注册：

```bash
claude plugin marketplace add "$HOME/.agentize"
claude plugin install agentize@agentize
```

**过期插件条目**

如果之前的安装留下了过期条目，安装脚本会自动清理。手动清理方法：

```bash
claude plugin uninstall agentize@agentize
claude plugin marketplace remove agentize
claude plugin marketplace add "$HOME/.agentize"
claude plugin install agentize@agentize
```
