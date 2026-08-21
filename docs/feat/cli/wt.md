# `wt`：Git worktree 辅助工具

## 快速上手

运行 `make setup` 并 source `setup.sh` 后，`wt` 命令即可在终端中使用。`wt` 是对 `git worktree` 的封装，用于在 bare 仓库中管理多个 worktree。

**安装背景：**
- 安装脚本（`scripts/install`）会自动设置 bare 仓库结构
- 手动设置：以 bare 方式克隆仓库，运行 `wt init`，然后在 `trees/main` 中运行 `make setup`

**仓库背景：**
- `wt` 命令作用于 bare git 仓库（而非普通克隆）
- worktree 创建在 bare 仓库根目录下的 `trees/` 目录中
- 安装脚本创建的结构为：`<repo>.git/trees/main`，其中 `make setup` 生成 `setup.sh`

> 注意：`wt` 实现为一个轻量加载器（`src/cli/wt.sh`），从 `src/cli/wt/` 加载模块化文件。`wt` 函数封装通过 `setup.sh` 导出。模块映射见 `src/cli/wt/README.md`。

- `wt clone <url> [destination]`：以 bare 方式克隆仓库，初始化 worktree，并设置 `trees/main`
  - 等价于：`git clone --bare <url> <dest>`，随后执行 `wt init` 和 `wt goto main`
  - 若省略 `destination`，默认为 `<basename>.git`（例如从 `https://github.com/org/repo.git` 得到 `repo`）
  - 当被 source 时，用户会停留在 `trees/main`（与 `wt goto` 行为一致）
  - 若目标目录已存在则失败
- `wt common`：打印 bare 仓库路径（`git rev-parse --git-common-dir`）
- `wt init`
  - 如果 `wt common` 不是 bare 仓库，则报错并退出。
  - 这是**强制性**的：1）每个仓库运行一次；2）仓库必须是 bare git 克隆（没有现有 worktree）
  - 它在该仓库中创建 `trees/` 目录，并将 main/master worktree 检出到 `trees/main`
  - 如果已经初始化过，应保持幂等，仅输出 "This repository is already initialized."
  - 若设置了 `WT_DEFAULT_BRANCH` 环境变量则使用它，否则默认为 `main` 或 `master`
- `wt goto <issue-no>|main`：切换到目标 worktree 所在目录
  - `wt goto main`：切换到 `trees/main`
  - `wt goto <issue-no>`：切换到 `trees/issue-<issue-no>`（为兼容性使用通配模式 `issue-<issue-no>*`）
  - `main` 和 `issue-<issue-no>` 都应支持自动补全
- `wt spawn <issue-no>`：从 `main` 分支为给定 issue 号创建新 worktree
  - 创建 worktree 之前，会先从 bare 仓库 rebase 到最新的默认分支
  - 创建 worktree 之后，尝试将该 issue 的 GitHub Projects v2 状态更新为 "In Progress"（尽力而为）
  - `--no-agent`：跳过 worktree 创建后的自动 Claude 调用
  - `--model <model>`：指定要使用的 Claude 模型（opus、sonnet、haiku）；未指定时使用默认模型
  - `--yolo`：通过向 Claude 传递 `--dangerously-skip-permissions` 跳过权限提示
    - **警告**：启用后，Claude 将在绕过所有权限检查的情况下运行
    - Claude 调用前会在 stderr 显示警告信息
  - `--headless`：以非交互模式运行 Claude，用于 server 守护进程场景
    - 使用 `claude --print` 进行非交互执行
    - 日志输出到 `.tmp/logs/issue-<N>-<timestamp>.log`
    - 立即返回（非阻塞），并输出结构化内容：
      ```
      PID: <claude-pid>
      Log: <log-file-path>
      ```
    - PID 对应实际的 `claude` 进程，用于存活追踪
- `wt remove <issue-no>`：移除给定 issue 号对应的 worktree
  - `--delete-branch`：同时删除分支，即使未合并
  - `-D` / `--force`：`--delete-branch` 的遗留别名
- `wt list`：列出所有现有 worktree
- `wt prune`：清理过期 worktree 元数据（`git worktree prune`）
- `wt purge`
  - 遍历每个以 `issue-` 开头的 worktree，并通过 `gh` CLI 检查对应 issue。若 issue 已关闭，则同时移除 worktree 和分支。
  - 每次移除也应删除分支，并在 stdout 输出 "Branch and worktree of issue-<issue-no> removed." 消息。
- `wt pathto <target>`：打印某个 worktree 的绝对路径
  - `wt pathto main`：打印 `trees/main` 的路径
  - `wt pathto <issue-no>`：打印 `trees/issue-<issue-no>*` 的路径
  - 成功时退出码为 `0`，未找到 worktree 时为 `1`
  - 适用于脚本和程序化 worktree 查找
- `wt rebase <pr-no>`：通过 Claude Code 会话将给定 PR 的 worktree rebase 到默认分支
  - 使用回退策略从 PR 元数据解析 issue/worktree：
    1. 分支名模式 `issue-<N>`
    2. PR 的 `closingIssuesReferences`
    3. PR 正文中的 `#<N>` 标记
  - 调用带有 `/sync-master` skill 的 Claude Code 执行 rebase
  - `--model <model>`：指定要使用的 Claude 模型（opus、sonnet、haiku）；未指定时使用默认模型
  - `--headless`：以非交互模式运行 Claude，用于 server 守护进程场景
    - 使用 `claude --print` 进行非交互执行
    - 日志输出到 `.tmp/logs/rebase-<pr-no>-<timestamp>.log`
    - 立即返回（非阻塞），并输出结构化内容：
      ```
      PID: <claude-pid>
      Log: <log-file-path>
      ```
  - `--yolo`：通过向 Claude 传递 `--dangerously-skip-permissions` 跳过权限提示
- `wt help`：显示帮助信息

## 远程跟踪配置

使用 `git clone --bare` 创建的 bare 仓库默认不包含 fetch refspec，这会导致 `git fetch` 无法更新 `origin/main` 等远程跟踪引用。`wt clone` 和 `wt init` 会自动配置正确的远程跟踪：

- 将 `remote.origin.fetch` 设置为 `+refs/heads/*:refs/remotes/origin/*`
- 启用 `fetch.prune=true` 以自动清理过期引用
- 执行一次尽力而为的 `git fetch origin` 以填充 `origin/*` 引用

这确保依赖 `origin/*` 引用的工作流（如 `/sync-master` 和 `/issue-to-impl`）能正常工作。

**手动设置 bare 仓库：**
如果你手动创建 bare 仓库而未使用 `wt clone`，运行 `wt init` 即可配置远程跟踪。若不存在 `origin` 远程仓库，则跳过配置步骤。

## Bare 仓库要求

`wt` 仅设计用于 **bare git 仓库**。bare 仓库是没有工作目录的 git 仓库，通常通过 `git clone --bare` 创建。

**为什么使用 bare 仓库？**
- 将仓库存储与工作目录干净地分离
- 允许多个 worktree 共存而不冲突
- 防止意外提交到仓库目录本身

**迁移指南：**
如果你有现有的非 bare 仓库，将其转换为 bare 仓库：

```bash
# 1. 将现有仓库以 bare 方式克隆
git clone --bare /path/to/existing/repo /path/to/bare/repo

# 2. 初始化 worktree 环境
cd /path/to/bare/repo
wt init

# 3. 你的 main 分支现在位于 trees/main
cd trees/main
```

## Shell 补全（zsh）

`wt` 命令为 zsh 用户提供 Tab 补全支持。运行 `make setup` 并 source `setup.sh` 后，补全自动启用。

**特性：**
- 子命令补全（`wt <TAB>` 显示：clone、common、init、goto、spawn、list、remove、prune、purge、pathto、rebase、help）
- `spawn` 的标志补全（`--yolo`、`--no-agent`、`--headless`、`--model`）——标志可出现在 `<issue-no>` 之前或之后
- `remove` 的标志补全（`--delete-branch`、`-D`、`--force`）——标志可出现在 `<issue-no>` 之前或之后
- `rebase` 的标志补全（`--headless`、`--yolo`、`--model`）——标志可出现在 `<pr-no>` 之前或之后
- `goto` 的目标补全（`main` 和 `issue-<N>-*` worktree）
- `pathto` 的目标补全（与 `goto` 相同的目标）

**设置：**
1. 运行 `make setup` 生成 `setup.sh`
2. 在 shell 中 source `setup.sh`：`source setup.sh`
3. `wt` 命令即可使用 Tab 补全

**实现：** zsh 补全系统使用 `wt --complete` 辅助命令（见补全辅助接口）动态获取可用标志和命令。

**注意：** 补全设置仅影响 zsh 用户。Bash 用户可继续使用 `wt`，无需任何更改。

## 补全辅助接口

`wt` 命令包含一个与 shell 无关的补全辅助命令，供补全系统使用：

```bash
wt --complete <topic>
```

**主题：**
- `commands` - 列出可用子命令（clone、common、init、goto、spawn、list、remove、prune、purge、pathto、rebase、help）
- `spawn-flags` - 列出 `wt spawn` 的标志（--yolo、--no-agent、--headless、--model）
- `remove-flags` - 列出 `wt remove` 的标志（--delete-branch、-D、--force）
- `rebase-flags` - 列出 `wt rebase` 的标志（--headless、--yolo、--model）
- `goto-targets` - 列出 `wt goto` 的可用目标（main 加上从 issue-<N>-* worktree 派生的 issue 号）

**输出格式：** 以换行符分隔的 token，无描述。

**示例：**
```bash
$ wt --complete commands
clone
common
init
goto
spawn
list
remove
prune
purge
pathto
rebase
help

$ wt --complete spawn-flags
--yolo
--no-agent
--headless
--model

$ wt --complete goto-targets
main
42
45

$ wt --complete rebase-flags
--headless
--yolo
```

该辅助命令由 zsh 补全系统使用，未来也可供其他 shell 使用。

## Claude CLI 调用接口

调用 Claude CLI 的命令（`spawn`、`rebase`）使用统一的辅助函数 `wt_invoke_claude()`，以确保一致的标志处理和执行模式。

**函数签名：**
```bash
wt_invoke_claude <command> <worktree_path> <yolo> <headless> <log_prefix>
```

**参数：**
- `command`：Claude CLI 命令字符串（例如 `/issue-to-impl 42`、`/sync-master`）
- `worktree_path`：Claude 应在其中执行的 worktree 绝对路径
- `yolo`：布尔值（`true`/`false`）- 向 Claude 传递 `--dangerously-skip-permissions`
- `headless`：布尔值（`true`/`false`）- 使用 `--print` 标志并后台执行
- `log_prefix`：日志文件名前缀（例如 `issue-42`、`rebase-123`）

**行为：**
- **交互模式**（`headless=false`）：使用 `cd` 子 shell 模式在前台运行 Claude
- **Headless 模式**（`headless=true`）：在带 `exec` 的分离子 shell 中运行 Claude，输出结构化的 `PID:` 和 `Log:` 格式，用于 server 集成

**结构化输出格式**（仅 headless 模式）：
```
PID: <claude-process-id>
Log: <log-file-path>
```

该格式使 server 守护进程能够追踪 Claude 进程存活状态并查看输出日志。
