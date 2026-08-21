# AI 驱动的软件开发 SDK

[![Tests](https://github.com/SyntheSys-Lab/agentize/actions/workflows/test.yml/badge.svg)](https://github.com/SyntheSys-Lab/agentize/actions/workflows/test.yml)

## 前置要求

### 必需工具

- **Git** - 版本控制（安装时会检查）
- **Make** - 构建自动化（安装时会检查）
- **Bash** - Shell 解释器，版本 3.2+（安装时会检查）
- **GitHub CLI（`gh`）** 或 **GitLab CLI（`glab`）** - 代码托管平台集成功能所需
  - GitHub：https://cli.github.com/ — 使用 `gh auth login` 进行认证
  - GitLab：https://gitlab.com/gitlab-org/cli — 使用 `glab auth login` 进行认证
    - 自托管 GitLab：`glab auth login --hostname gitlab.company.com`
  - 被以下功能使用：`/setup-viewboard`、`/open-issue`、`/open-pr`、`/open-mr`、工作流自动化
- **Python 3.10+** - 权限自动化模块所需，否则你只能对着提示无限地输入 `yes`！
  - 使用 Python `venv` 或 `anaconda` 来管理一个良好的 Python 发行版！
  - 需要 **PyYAML**（`pip install pyyaml`）用于 YAML 配置解析

### Windows 支持

Agentize 通过 **Git Bash**（随 [Git for Windows](https://git-scm.com/download/win) 附带）支持 Windows 10。

**Windows 前置要求：**
1. 安装 [Git for Windows](https://git-scm.com/download/win)（包含 Git Bash）
2. 打开 **Git Bash** 并安装 `make`：
   ```bash
   pacman -S make
   ```
3. 在运行安装器之前，确保 `bash`、`git` 和 `make` 在 Git Bash 中可用。

所有 Agentize 命令（`wt`、`lol`）都应在 Git Bash 内运行。Python 模块会自动从常见的 Git for Windows 安装位置发现 `bash.exe`。

### 推荐库

- **Anthropic Python Library** - 用于自定义 AI 集成（可选）
  - 安装：`pip install anthropic`
  - 注意：核心 SDK 功能不需要它，但如果你计划扩展或定制 AI 驱动的功能，建议安装

### 验证

安装完前置要求后，安装器会自动验证 `git`、`make` 和 `bash` 的可用性。代码托管平台 CLI 的认证可以用以下命令验证：

```bash
gh auth status      # GitHub
glab auth status    # GitLab
```

## 快速开始

Agentize 是一个 AI 驱动的 SDK，帮助你借助 Claude Code 强大地构建软件项目。
它分为两个主要组件：

1. **Claude Code 插件**：当 `claude` CLI 可用时，安装过程中自动注册。
   详情请参见[教程 00a：Claude UI 设置](./docs/tutorial/00a-claude-ui-setup.md)。
2. **CLI 工具**：一个 source 优先的 CLI 工具，帮助你使用 Agentize 管理项目。
   CLI 工作流请参见[教程 00：CLI 快速上手](./docs/tutorial/00-cli-quickstart.md)。

```bash
curl -fsSL https://raw.githubusercontent.com/SyntheSys-Lab/agentize/main/scripts/install | bash
```

然后添加到你的 shell RC 文件（`~/.bashrc`、`~/.zshrc` 等）：

```bash
source $HOME/.agentize/setup.sh
```

安装选项与故障排查参见 [docs/feat/cli/install.md](./docs/feat/cli/install.md)。

**升级：** 运行 `lol upgrade` 拉取最新变更。

## 你的第一个 15 分钟

安装完成后，安装器会在你的主目录创建 `~/.agentize.local.yaml`。该文件控制规划和实现使用哪些 AI 后端。

### Agentize CLI 五步工作流

1. **配置**（已完成）- 确认 `~/.agentize.local.yaml` 存在，并按需调整后端

2. 使用 worktree **克隆**：
   ```bash
   wt clone https://github.com/org/repo.git myproject.git
   # 或者 GitLab：
   wt clone https://gitlab.com/org/repo.git myproject.git
   ```
   `wt clone` 会建立一个 bare 仓库，并让你停留在 `trees/main`。

3. **规划**你的第一个功能：
   ```bash
   lol plan --editor
   ```
   检查它创建的 GitHub issue。

4. **实现**该计划：
   ```bash
   lol impl <issue-number>
   ```

5. 在 worktree 之间**导航**：
   ```bash
   wt goto <issue-number>
   wt goto main
   ```

完整演练请参见[教程 00：CLI 快速上手](./docs/tutorial/00-cli-quickstart.md)。

## 故障排查

如果你在使用过程中遇到任何问题，例如：
1. 它对一个非常简单的操作请求权限。
2. 它未能自动继续会话。

在你的 `.agentize.local.yaml` 中启用调试模式：

```yaml
handsoff:
  debug: true
```

然后重新运行命令。这将在以下位置之一生成详细日志：
- `/path/to/your/project/.tmp/handsoff-debug.log` 或
- `$HOME/.agentize/.tmp/handsoff-debug.log`
请把你的日志粘贴到 issue 中让我（@were）来调试！

如需更多帮助，请访问我们的[故障排查指南](./docs/troubleshoot.md)。

## 核心理念

以产物为中心，最大限度地减少人工干预。
- 以会话为中心：人告诉 AI 做什么，然后等到它结束。
  再给出反馈，直到满意为止。人在环路中介入过多
  限制了可扩展性。
- 以产物为中心：人告诉 AI 做什么，AI 先产出一个计划。
  计划是人唯一可以干预的阶段。计划被批准后，
  AI 将执行计划并产出代码合并，供人评审。

人、AI 和形式语言之间的清晰分离。
- 人负责开发意图，包括提出功能需求、
  批准计划和代码合并。
- AI 是软件开发的工作者，既负责制定计划，也负责维护代码库，
  包括测试、文档和代码质量。
- 形式语言用于 AI 与其他系统之间的协调与编排，
  例如 GitHub Issues、Pull Requests 和 CI/CD 管线。
  - 我（@were）发现，skill 让 AI 合成固定代码与这些系统交互很有前途，
    但这些流程比我预期的更加固定和形式化——把它们放在形式语言
    （例如 Python 脚本或 YAML 配置）中，对整个工作流来说更透明、执行更快。

### 工作流：

参见我们详细的工作流图：

- [Ultra Planner 工作流](./docs/feat/core/ultra-planner.md) - 基于多 agent 辩论的规划
- [Issue 到实现工作流](./docs/feat/core/issue-to-impl.md) - 完整的开发周期

**图例**：红框代表人工干预（提供需求、批准/拒绝结果、启动会话）。蓝框代表自动化的 AI 步骤。

## 教程

通过我们的逐步教程在 15 分钟内学会 Agentize（每篇 3-5 分钟）：

1. **[CLI 快速上手](./docs/tutorial/00-cli-quickstart.md)** - 在 15 分钟内学会核心 CLI 工作流
2. **[Claude UI 设置](./docs/tutorial/00a-claude-ui-setup.md)** - 设置 Claude Code 插件和 slash command
3. **[Ultra Planner](./docs/tutorial/01-ultra-planner.md)** - 主要的规划教程（推荐）
4. **[Issue 到实现](./docs/tutorial/02-issue-to-impl.md)** - 使用 `/issue-to-impl` 和 `/code-review` 的完整开发周期
5. **[高级用法](./docs/tutorial/03-advanced-usage.md)** - 通过并行开发工作流扩展规模

## 项目组织

```plaintext
agentize/
├── .claude-plugin/         # 插件根目录（与 --plugin-dir 一起使用）
│   ├── marketplace.json    # 插件清单
│   ├── commands/           # Claude Code 命令
│   ├── skills/             # Claude Code 技能
│   ├── agents/             # Claude Code 智能体
│   └── hooks/              # Claude Code 钩子
├── python/                 # Python 模块（agentize.*）
├── docs/                   # 文档
│   └── git-msg-tags.md     # 提交消息规范
├── src/cli/                # Source 优先的 CLI 库
│   ├── wt.sh               # Worktree CLI 库
│   └── lol.sh              # SDK CLI 库
├── scripts/                # Shell 脚本与封装入口
├── templates/              # SDK 生成模板
├── tests/                  # 测试用例
├── Makefile                # 用于测试和设置的构建目标
└── README.md               # 本 README 文件
```
