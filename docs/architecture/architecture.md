# 开发架构

本文档概述本项目的开发架构，以便最好地融入 agentize 的生态系统。
虽然并非强制要求——其中一些也只是常见的软件工程实践——但强烈建议
在本地代码结构、git 和 GitHub 使用方式上遵循这些实践。

使用 Agentize 框架的项目应遵循此架构。


## 本地代码库

代码库应遵循如下结构：

```plaintext
docs/                # 高层文档文件与设计文档
└── git-msg-tags.md  # Git 提交消息标签文档
scripts/             # CLI 与工具脚本
└── pre-commit       # Git pre-commit 钩子脚本
src/                 # 源代码文件，也可以是 `lib`
tests/               # 测试用例
Makefile             # 本项目的高层入口
README.md            # 几乎每个目录都应有一个 README.md 来说明其用途
.gitignore           # Git 忽略文件
```

关于 SDK 结构的更多信息，请参阅 `./sdk.md`。

### Makefile 接口

- `make test` - 运行所有测试用例（通过 bash 运行 shell 测试 + pytest 运行 Python 测试）
- `make test-shells` - 在多个 shell（bash 和 zsh）下运行所有测试用例
- `make test-sdk` - 运行 SDK 模板测试
- `make test-cli` - 运行 CLI 命令测试
- `make test-lint` - 运行校验与 lint 测试
- `make test-e2e` - 运行端到端集成测试
- `make test-fast` - 运行快速测试（sdk + cli + lint + pytest）
- `make setup` - 创建用于搭建开发环境的 `setup.sh` 脚本
  - 注意：这并不会运行 setup 本身，因为它只影响子 shell
  - 要运行 setup，请使用 `source ./setup.sh`
  - 当然，`setup.sh` 应该被加入 `.gitignore`
  - 这样设计是因为许多项目在其 `setup.sh` 中依赖仓库路径，
  而将其硬编码在 `setup.sh` 中是一种不好的做法。
  - `.claude/hooks/session-init.sh` 钩子使用 `make setup` 并 source `setup.sh`，
  为当前活跃的 worktree（main 或链接的）导出 `AGENTIZE_HOME`
- `make pre-commit` - 安装 git pre-commit 钩子
- `make clean` - 清理生成的文件
- `make help` - 显示可用 Makefile 目标的帮助信息

## Git 使用

### 安装

**一条命令安装（推荐）：**

```bash
curl -fsSL https://raw.githubusercontent.com/SyntheSys-Lab/agentize/main/scripts/install | bash
```

安装器会：
1. 将仓库克隆到 `$HOME/.agentize`（或自定义的 `--dir`）
2. 运行 `make setup` 生成 `setup.sh`
3. 注册本地 Claude Code 插件市场并安装插件（如果 `claude` 可用）
4. 打印 shell RC 集成说明

选项与故障排查参见 [docs/feat/cli/install.md](../feat/cli/install.md)。

**手动设置：**

本开发工作流使用 bare 仓库来支持多个 worktree：
- 克隆你的仓库 `git clone --bare <repo-url> <repo-name>.git`
- 初始化 worktree 环境 `wt init`（运行一次，创建 `trees/main`）
- 在 `trees/main` 中运行 `make setup`，生成设置了 `AGENTIZE_HOME` 的 `setup.sh`
- Source `setup.sh` 以启用 `wt` 和 `lol` 命令

### Worktree 管理

- 切换到 main worktree：`wt goto main`
- 为 issue 创建 worktree：`wt spawn <issue-number>`
  - 注意：`spawn` 是一条全功能命令，它会创建 worktree、`cd` 进入其中，并携带 issue 实现提示启动 Claude Code
  - 示例：`wt spawn 42`

**仓库结构：**

```plaintext
<repo-name>.git/      # Bare git 仓库
├── trees/            # Worktree 目录
│     ├── main/       # Main worktree（在此运行 'make setup'）
│     ├── issue-42/   # issue #42 的 worktree
│     └── ...         # 其他 worktree
└── .../              # 其他 git 内部文件
```

## CLI 实现

Agentize CLI 命令（`wt`、`lol`）遵循 source 优先的架构：
- 规范实现位于 `src/cli/`，作为可被 source 的库
- `setup.sh` source 这些库以提供 shell 函数
- `scripts/` 中的封装脚本委托给库函数

这种模式提供：
- CLI 逻辑的单一事实来源
- 通过 `setup.sh` 在交互式 shell 中可用的函数
- 可直接执行脚本以进行测试和非交互式使用

**可选的 Python 封装：** `python -m agentize.cli` 提供基于 argparse 的入口，用于非 source 场景。大多数命令委托给 shell 函数；`lol impl` 以 Python 实现，shell 命令会委托给它。

## GitHub 使用

建议将每个仓库关联到一个 GitHub Projects v2 看板，以便更好地进行 issue 跟踪和项目管理。

**创建或关联项目：**
- `lol project --create [--org <owner>] [--title <title>]` - 创建一个新的 GitHub Projects v2 看板并关联
- `lol project --associate <owner>/<id>` - 将当前仓库关联到已有的 GitHub Projects v2 看板

`--org` 标志接受 GitHub 组织或个人用户登录名。省略时默认为仓库所有者。

**生成自动化模板：**
- `lol project --automation [--write <path>]` - 生成用于项目自动化的 GitHub Actions 工作流，带生命周期管理（自动添加 issue/PR，为 issue 设置 Status 为 "Proposed"，PR 合并时关闭关联的 issue）

**元数据存储：**
- 项目关联信息存储在 `.agentize.yaml` 的 `project.org` 和 `project.id` 字段中
- 关于 `.agentize.yaml` 结构的更多信息，请参阅 `./metadata.md`

**相关文档：**
- 关于看板设计与项目管理工作流，请参阅 `./project.md`
- 关于自动化设置，请参阅 `../workflows/github-projects-automation.md`

## Python 工作流模块

`python/agentize/workflow` 模块为 planner 管线和 impl 工作流提供 Python 原生的编排：

- 通过 `setup.sh` 使用 `acw` 执行 LLM
- 复用 `.claude-plugin/agents/*.md` 提示词以保持行为一致性
- 将产物写入 `.tmp/`，使用稳定前缀以保证可复现性
- 支持 critique/reducer 并行执行以及用于测试的可注入 runner
- 使用基于文件的提示模板运行 `lol impl` 的 issue 到实现循环

这使得 Python 脚本集成成为可能，同时保留 shell 作为规范的 CLI 实现。
