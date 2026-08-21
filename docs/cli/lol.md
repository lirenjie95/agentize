# lol CLI

`lol` 命令提供 SDK 管理工具：升级、项目管理、用量报告、规划以及自动化服务器能力。

## 入口

**Shell（规范入口）：**
```bash
source setup.sh  # Source src/cli/lol.sh
lol <command> [options]
```

**Python（可选）：**
```bash
python -m agentize.cli <command> [options]
```

Python 入口对大多数命令会委托给 shell 函数。`lol impl` 运行 Python 工作流实现（通过 `agentize.workflow.api`），而 shell 的 `impl.sh` 委托给它。`lol` 是唯一的公开 shell 入口；辅助函数是私有的实现细节。对于非 source 环境或偏好 argparse 风格解析的脚本场景，请使用 Python 入口。

## 命令

### lol upgrade

升级 agentize 安装。

```bash
lol upgrade [--keep-branch]
```

默认情况下，`lol upgrade` 在拉取更新前会切换到默认分支。
使用 `--keep-branch` 可停留在当前分支并从其上游拉取。

升级过程分为三个阶段：
1. **拉取更新**：切换到默认分支（除非使用 `--keep-branch`）并运行 `git pull --rebase`
2. **重建环境**：运行 `make setup`，以应用构建过程中的任何变更重新生成 `setup.sh`
3. **更新 Claude 插件**（可选）：如果 `claude` CLI 可用，更新本地 marketplace 和插件注册。此步骤是非致命的；失败不会阻止升级。

这与 `scripts/install` 中的安装过程一致，确保构建配置和插件的更新得到应用。

### lol use-branch

切换到远程开发分支并重建本地环境。

```bash
lol use-branch <remote>/<branch>
lol use-branch <branch>  # 默认为 origin
```

该命令会获取远程分支，在本地检出（如有需要会创建跟踪分支），
运行 `make setup`，并打印 shell 重载说明。

### lol project

管理 GitHub Projects v2 集成。

```bash
lol project --create [--org <owner>] [--title <title>]
lol project --associate <owner>/<id>
lol project --automation [--write <path>]
```

`--org` 标志接受组织或个人用户登录名。省略时，默认为仓库所有者（可能是组织或个人账户）。

该命令通过共享的项目库（`src/cli/lol/project-lib.sh`）与 `/setup-viewboard` 共享实现。

详见 [Project Management](../architecture/project.md)。

**另请参阅：** `/setup-viewboard`，用于包含标签、自动化和 Status 字段验证的自包含项目设置。

### lol claude-clean

从 Claude 的全局配置文件（`~/.claude.json`）中移除过时的项目条目。

```bash
lol claude-clean [--dry-run]
```

#### 选项

| 选项 | 是否必需 | 默认值 | 描述 |
|--------|----------|---------|-------------|
| `--dry-run` | 否 | - | 显示将被移除的内容而不修改文件 |

#### 行为

1. 读取 `$HOME/.claude.json`（文件缺失时优雅退出）
2. 验证 `jq` 可用（必需依赖）
3. 扫描 `.projects` 键中不存在的目录
4. 扫描 `.githubRepoPaths` 数组中不存在的目录
5. 如果使用 `--dry-run`，打印将被移除的内容并退出
6. 否则，移除过时条目并以原子方式写入更改

#### 示例

```bash
# 预览将被移除的内容
lol claude-clean --dry-run

# 移除过时条目
lol claude-clean
```

### lol usage

报告 Claude Code token 用量统计。

```bash
lol usage [--today | --week]
```

解析 `~/.claude/projects/**/*.jsonl` 中的 JSONL 文件，按时间桶提取并聚合 token 用量统计。同一会话中具有相同 `message.id` 的助手条目会被去重，以避免对流式内容块重复计数。当存在缓存 token 字段时，成本估算使用缓存分层定价。

#### 选项

| 选项 | 是否必需 | 默认值 | 描述 |
|--------|----------|---------|-------------|
| `--today` | 否 | 是 | 按小时显示最近 24 小时的用量 |
| `--week` | 否 | - | 按天显示最近 7 天的用量 |
| `--cache` | 否 | - | 包含缓存 token 统计（cache_read、cache_write 列） |
| `--cost` | 否 | - | 显示基于模型定价的成本估算 |

#### 示例

```bash
# 按小时显示今日用量（默认）
lol usage

# 按天显示每周用量
lol usage --week
```

### lol plan

运行多智能体辩论流水线。

```bash
lol plan [--dry-run] [--verbose] [--editor] [--backend <provider:model>] [--refine <issue-no> [refinement-instructions]] \
  [<feature-description>]
lol plan --refine <issue-no> [refinement-instructions]
```

针对一个特性描述运行完整的多智能体辩论流水线，产出共识实现计划。这是 planner 流水线的首选入口。共识计划以溯源页脚结尾：`Plan based on commit <hash>`。

#### 选项

| 选项 | 是否必需 | 默认值 | 描述 |
|--------|----------|---------|-------------|
| `--dry-run` | 否 | - | 跳过 GitHub issue 创建；使用基于时间戳的产物命名 |
| `--verbose` | 否 | - | 打印详细的阶段日志（默认安静模式） |
| `--editor` | 否 | - | 打开 $EDITOR 编写特性描述；与 `--refine` 组合时，编辑器文本成为细化重点 |
| `--backend <provider:model>` | 否 | - | 为本次运行覆盖 `planner.backend` |
| `--refine <issue-no> [refinement-instructions]` | 否 | - | 细化已有的计划 issue；如果在使用 `--editor` 时提供了位置参数形式的指令，它们会追加在编辑器文本之后 |

默认情况下，当 `gh` 可用时 `lol plan` 会创建一个 GitHub issue 并应用 `agentize:plan` 标签（如缺失则按需创建）。使用 `--dry-run` 可跳过 issue 创建，改用基于时间戳的产物命名。
`--editor` 要求设置 `$EDITOR`；如果未设置，请直接传递描述（例如 `lol plan "Add JWT auth"`）。

设置 `--refine` 时，会从 GitHub 获取 issue 正文并用作辩论上下文。可选的细化指令会追加到上下文中以引导智能体。细化运行的产物以 `issue-refine-<N>` 为前缀，并且除非提供 `--dry-run`，否则会更新现有 issue。此模式需要已认证的 `gh` 访问权限来读取 issue 正文。

#### 后端配置（.agentize.local.yaml）

通过 `.agentize.local.yaml` 而非 CLI 标志配置 planner 后端：

```yaml
planner:
  backend: claude:opus
  understander: claude:sonnet
  bold: claude:opus
  critique: claude:opus
  reducer: claude:opus
```

阶段特定的键会覆盖 `planner.backend`。如果某个键缺失，默认值仍为 understander 使用 `claude:sonnet`，bold/critique/reducer 使用 `claude:opus`。

使用 `--backend <provider:model>` 可在不修改 YAML 文件的情况下为单次运行覆盖 `planner.backend`。

#### 示例

```bash
# 使用默认的 issue 创建运行流水线
lol plan "Add user authentication with JWT tokens"

# 运行流水线但不创建 GitHub issue
lol plan --dry-run "Refactor database layer for connection pooling"

# 运行流水线并输出详细阶段信息
lol plan --verbose "Add real-time notifications"

# 细化已有的计划 issue
lol plan --refine 42 "Focus on reducing complexity"

# 细化但不发布回 GitHub（仍会写入 issue-refine 产物）
lol plan --dry-run --refine 42 "Add more error handling and edge cases"

# 在编辑器中编写特性描述
lol plan --editor --dry-run
```

流水线阶段详情和产物命名请参阅 [planner pipeline module](planner.md)。

### lol simp

在不改变语义的前提下简化代码。

```bash
lol simp [file] [<description>]
lol simp [file] --focus "<description>"
lol simp [file] --editor
```

如果提供了 `file`，工作流将聚焦于该文件。省略时，
工作流会选择一小部分随机的被跟踪文件（`git ls-files`），
并将选择记录到 `.tmp/simp-targets.txt` 中以保证可复现性。

当只提供一个位置参数时，如果该文件存在则视为文件；
否则视为聚焦描述。

简化报告必须以 `Yes.` 或 `No.` 开头。报告始终
写入 `.tmp/simp-output.md` 并记录本地路径。当报告
以 `Yes.` 开头且提供了 `--issue` 时，报告会发布到
指定的 issue。

#### 选项

| 选项 | 是否必需 | 默认值 | 描述 |
|--------|----------|---------|-------------|
| `--focus` | 否 | - | 用于引导简化的聚焦描述 |
| `--editor` | 否 | - | 打开 `$EDITOR` 编写聚焦描述 |
| `--issue` | 否 | - | 报告通过时发布到 issue（要求 `Yes.` 前缀） |

#### 示例

```bash
# 简化随机选择的一组文件
lol simp

# 简化指定文件
lol simp README.md

# 带聚焦描述进行简化
lol simp "Refactor for clarity"

# 简化文件并附带聚焦描述
lol simp src/main.py --focus "Reduce nesting in error handling"

# 在编辑器中编写聚焦描述
lol simp --editor

# 简化并在通过时将结果发布到 issue
lol simp --issue 42
```

产物写入 `.tmp/` 下：
- `.tmp/simp-input.md` - 渲染后的提示词，包含所选文件内容
- `.tmp/simp-output.md` - 简化报告（以 `Yes.` 或 `No.` 开头）
- `.tmp/simp-targets.txt` - 所选文件列表

### lol impl

使用 `wt` + 共享的 ACW runner（底层调用 `acw`）自动化 issue 到实现的循环。
当 `lol` 已被 source 且 `wt` 可用时，包装器会确保 worktree 存在（`wt pathto` / `wt spawn`），并在运行工作流前进入该 worktree（`wt goto`）（见 `docs/feat/cli/wt.md`）。

```bash
lol impl <issue-no> [--backend <provider:model>] [--max-iterations <N>] [--yolo] [--wait-for-ci]
```

#### 选项

| 选项 | 是否必需 | 默认值 | 描述 |
|--------|----------|---------|-------------|
| `--backend` | 否 | `impl.model` 或 `codex:gpt-5.2-codex` | `provider:model` 形式的后端 |
| `--max-iterations` | 否 | `impl.max_iter` 或 `10` | 放弃前的最大 `acw` 迭代次数 |
| `--yolo` | 否 | 关闭 | 透传给提供方 CLI 选项（Claude 经 acw 映射为 `--dangerously-skip-permissions`；Codex 映射为 `--full-auto`） |
| `--wait-for-ci` | 否 | 关闭 | PR 创建后，监控可合并性 + CI 并针对失败进行迭代 |

#### `.agentize.local.yaml` 中的 impl 默认值

```yaml
impl:
  model: codex:gpt-5.2-codex
  max_iter: 10
```

当未提供 `--backend` 和
`--max-iterations` 时，`lol impl` 读取这些值作为默认值。

#### Issue 预取

循环开始前，`lol impl` 会尝试通过 `gh issue view` 获取 issue 的标题/正文（以及标签，如果存在），并写入 `.tmp/issue-<N>.md`。如果获取失败或文件为空，`lol impl` 会以错误退出。请确保 `gh` 已认证且该 issue 存在于当前仓库中。

#### 完成标记

在 worktree 中创建 `.tmp/finalize.txt` 并包含 `Issue <N> resolved` 即可完成。
完成文件的第一行将用作 PR 标题。

#### Git 工作流

在迭代循环之前，`lol impl` 通过 fetch 并 rebase 到默认分支（`upstream/master` 或 `origin/main`）来同步 issue 分支。如果发生 rebase 冲突，命令会以错误退出，并期望手动解决后再重试。

每次迭代都会暂存并提交更改（无更改时跳过提交）。每次迭代都需要一个 `.tmp/commit-report-iter-<N>.txt` 文件，并作为迭代 `<N>` 的提交信息。完成后，分支会被推送到 `upstream`（或 `origin`），PR 目标为 `master`（或 `main`）。

#### PR 后监控（可选）

设置 `--wait-for-ci` 时，`lol impl` 会检查 PR 可合并性，并在检测到冲突时自动 rebase（未解决的冲突会快速失败）。然后运行 `gh pr checks --watch` 流式跟踪 CI 进度。失败的检查会触发另一次迭代，并将 CI 上下文注入提示词；修复会被推送并重新检查 CI，直到成功或达到迭代上限。

#### 示例

```bash
# 为 issue 42 启动实现循环
lol impl 42

# 使用不同的后端
lol impl 42 --backend cursor:gpt-5.2-codex

# 限制迭代次数并启用 yolo 模式
lol impl 42 --max-iterations 5 --yolo

# 创建 PR 并等待可合并性 + CI 状态
lol impl 42 --wait-for-ci
```

### lol serve

长期运行的服务器，轮询 GitHub Projects 中状态为 "Plan Accepted" 的 issue，并自动调用 `wt spawn` 开始实现。

```bash
lol serve
```

在 `.agentize.local.yaml` 中配置 `server.period` 和 `server.num_workers`：

```yaml
server:
  period: 5m       # 轮询间隔（格式：Nm 或 Ns）
  num_workers: 5   # 最大并发无头 worker 数（0 = 不限制）
```

Telegram 凭据也从 `.agentize.local.yaml` 加载。服务器按以下顺序搜索该文件：项目根目录 → `$AGENTIZE_HOME` → `$HOME`。如果未配置凭据，服务器以无通知模式运行。

#### 要求

- 必须在已完成 `wt init` 的裸仓库中运行
- GitHub CLI（`gh`）必须已认证
- 项目必须已通过 `lol project --associate` 关联

#### 行为

**实现发现：**
1. 使用 `gh issue list --label agentize:plan --state open` 发现候选 issue
2. 对每个候选，通过逐 issue 的 GraphQL 查询检查项目状态
3. 按以下条件过滤 issue：
   - 项目 Status 字段 = "Plan Accepted"（批准门禁）
   - 标签 = `agentize:plan`（发现过滤器）
4. 对每个匹配且尚无 worktree 的 issue：
   - 调用 `wt spawn <issue-number>`

**细化发现：**
1. 发现同时具有 `agentize:plan` 和 `agentize:refine` 标签的细化候选
2. 按以下条件过滤 issue：
   - 项目 Status 字段 = "Proposed"
   - 标签同时包含 `agentize:plan` 和 `agentize:refine`
3. 对每个匹配的 issue：
   - 将状态设置为 "Refining"（尽力认领）
   - 以无头方式运行 `/ultra-planner --refine`
   - 完成后：将状态重置为 "Proposed" 并移除 `agentize:refine` 标签

**轮询循环：**
- 持续轮询直到被中断（Ctrl+C）

#### 配置

Telegram 和 handsoff 设置从 `.agentize.local.yaml` 加载：

```yaml
telegram:
  enabled: true
  token: "your-bot-token"
  chat_id: "your-chat-id"
```

完整模式请参阅 [Configuration Reference](../envvar.md)。
