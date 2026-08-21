# 项目元数据文件（.agentize.yaml）

`.agentize.yaml` 文件为基于 agentize 的项目提供规范的项目配置。

## 配置文件概览

Agentize 使用两个用途不同的配置文件：

| 文件 | 用途 | 是否提交？ |
|------|---------|------------|
| `.agentize.yaml` | 项目元数据（org、项目 ID、语言） | 是 |
| `.agentize.local.yaml` | 开发者设置（handsoff、Telegram、server、workflows） | 否 |

**分离的理由：**
- `.agentize.yaml` 包含应在所有开发者之间共享的项目级配置
- `.agentize.local.yaml` 包含随环境而异的部署相关设置（密钥、机器相关的调优）

**`.agentize.local.yaml` 的范围：**
- Handsoff 模式设置（`handsoff.*`）
- Telegram 审批设置（`telegram.*`）
- Server 运行时设置（`server.*`）
- 工作流模型分配（`workflows.*`）

**优先级顺序：** `.agentize.local.yaml` > 默认值

**`.agentize.local.yaml` 的 YAML 查找顺序：**
1. 项目根目录的 `.agentize.local.yaml`
2. `$AGENTIZE_HOME/.agentize.local.yaml`
3. `$HOME/.agentize.local.yaml`（用户级，由安装器创建）

完整的配置模式和环境变量映射，参见[配置参考](../envvar.md)。

## 设置界面

VS Code 扩展包含一个设置界面（Settings UI），将这些文件呈现出来用于后端
配置。它将 `.agentize.yaml` 展示为只读元数据，并允许你在仓库和用户
作用域中编辑 `planner.backend` 的值。用法详情参见
[`docs/vscode/settings-ui.md`](../vscode/settings-ui.md)。

## 位置

元数据文件位于项目根目录：
- 标准布局：`<project-root>/.agentize.yaml`
- Worktree 布局：`<repo-root>/trees/main/.agentize.yaml`

`wt` 命令会自动搜索这两个位置。

## 模式（Schema）

```yaml
project:
  name: project-name           # 项目标识符
  lang: python|bash|c|cxx      # 主要编程语言
  source: src                  # 源代码目录（可选）
  org: organization-name       # GitHub 组织（可选，用于 Projects v2）
  id: 3                        # GitHub 项目编号（可选，用于 Projects v2）

git:
  remote_url: https://github.com/org/repo  # Git 远程 URL（可选）
  default_branch: main         # 默认分支（main、master、trunk 等）

agentize:
  commit: abc123...            # 上次更新的 Agentize 提交哈希（可选）

worktree:
  trees_dir: trees            # Worktree 目录（可选，默认为 "trees"）

pre_commit:
  enabled: true               # 启用 pre-commit 钩子安装（可选，默认为 true）

permissions:                  # 用户可配置的权限规则（可选）
  allow:
    - "^npm run build"        # 简单字符串（隐含 Bash 工具）
    - pattern: "^cat .*\\.md$"
      tool: Read              # 带显式工具的扩展格式
  deny:
    - "^rm -rf /tmp"
```

## 字段

### project.name（必填）
用于模板和文档中的项目标识符。

**示例：** `agentize`、`my-project`

### project.lang（必填）
项目的主要编程语言。

**支持的值：**
- `python` - Python 项目
- `bash` - Bash 脚本项目
- `c` - C 语言项目
- `cxx` - C++ 项目

**用途：** 决定语言相关的默认值和工具行为。

### project.source（可选）
相对于项目根目录的源代码目录路径。

**默认值：** 语言相关的默认值（Python 为 `src`，Bash 为 `scripts`）

**示例：** `lib`、`src`、`custom/path`

### git.remote_url（可选）
Git 远程仓库 URL。

**示例：** `https://github.com/synthesys-lab/agentize`

**用途：** 文档和工具引用。server 使用它在 worker 分配的 Telegram 通知中生成 GitHub issue 链接。

### git.default_branch（可选但推荐）
用于创建 worktree 的默认分支名。

**默认值：** 自动检测（先尝试 `main`，再尝试 `master`）

**示例：** `main`、`master`、`trunk`、`develop`

**为什么要指定：** 非标准分支名（例如 `trunk`）时必需。缺省时，`wt` 会回退到自动检测并显示提示。

### worktree.trees_dir（可选）
创建 worktree 的目录。

**默认值：** `trees`

**示例：** `worktrees`、`branches`、`trees`

**用途：** 允许自定义 worktree 的组织方式。

### project.org（可选）
用于 Projects v2 集成的 GitHub 所有者（组织或个人用户登录名）。

**示例：** `Synthesys-Lab`、`my-org`、`my-username`

**用途：** 由 `lol project --create` 或 `lol project --associate` 设置，用于存储与 GitHub Projects v2 看板关联的所有者。可以是组织登录名或个人用户登录名，从而使组织所有和用户所有的仓库都能使用 Projects v2 集成。

### project.id（可选）
GitHub Projects v2 看板编号（项目 URL 中可见的数字 ID）。

**示例：** `3`、`42`

**用途：** 由 `lol project --create` 或 `lol project --associate` 设置，用于存储项目编号。这是显示在诸如 `https://github.com/orgs/my-org/projects/3`（组织）或 `https://github.com/users/my-username/projects/1`（个人账户）这类 URL 中的项目编号，而不是 GraphQL 的 node_id。

**注意：** `project.org` 和 `project.id` 字段共同唯一标识一个 GitHub Projects v2 看板。URL 路径（`orgs/` 还是 `users/`）根据所有者类型动态确定。

### agentize.commit（可选）
记录 agentize 安装的提交哈希。

**示例：** `e3eab9a1234567890abcdef1234567890abcdef`

**用途：** 记录正在使用的 agentize 版本。这使得可以通过 `lol version` 进行版本跟踪，以便故障排查和兼容性检查。

**注意：** 仅当 `AGENTIZE_HOME` 是有效的 git 仓库时才会记录。如果 git 不可用或 `AGENTIZE_HOME` 不是 git 仓库，此字段会被省略而不会导致错误。

### pre_commit.enabled（可选）
控制 SDK 和 worktree 初始化期间 pre-commit 钩子的自动安装。

**默认值：** `true`（钩子缺失时会安装）

**示例：** `true`、`false`

**用途：** 设为 `false` 可阻止自动安装钩子。当为 `true` 或未设置时，如果钩子脚本存在且尚无自定义钩子，`wt init` 和 `wt spawn` 会将 `scripts/pre-commit` 安装到 `.git/hooks/pre-commit`。

**注意：** 当通过 `core.hooksPath` 全局禁用 Git 钩子时（例如 `core.hooksPath=/dev/null`），也会跳过钩子安装。这确保命令尊重用户在系统范围内禁用钩子的意图。

### permissions（可选）
用户可配置的工具访问控制权限规则。

**示例：**
```yaml
permissions:
  allow:
    - "^npm run (build|test|lint)"
    - pattern: "^cat .*\\.md$"
      tool: Read
  deny:
    - "^rm -rf /tmp"
```

**格式：** 字符串或字典的数组。字符串项默认为 `Bash` 工具。字典项要求 `pattern` 字段，`tool` 字段可选（默认为 `Bash`）。

**合并顺序：** 项目规则（`.agentize.yaml`）首先被评估，然后本地规则（`.agentize.local.yaml`）可以添加额外的模式。`rules.py` 中硬编码的 deny 规则始终优先于 YAML 的 allow。

**用途：** 无需修改核心代码即可实现按项目和按开发者定制权限规则。

## 创建

### 手动创建

手动创建 `.agentize.yaml`：

```bash
cat > .agentize.yaml <<EOF
project:
  name: my-project
  lang: python
  source: src
git:
  default_branch: main
EOF
```

这将启用 worktree 操作（`wt` 命令）和项目管理功能。

## 使用

### Worktree 配置

`wt` 命令读取元数据进行 worktree 操作：

```bash
# 使用 .agentize.yaml 中的 git.default_branch
wt spawn 42

# 使用 .agentize.yaml 中的 worktree.trees_dir
wt list
```

**回退行为：** 当 `.agentize.yaml` 缺失时，`wt` 会回退到：
- 自动检测 `main` 或 `master` 分支
- 使用 `trees` 目录
- 显示手动创建 `.agentize.yaml` 的提示

## 示例：Agentize 项目

```yaml
project:
  name: agentize
  lang: bash
  source: scripts
  org: Synthesys-Lab
  id: 3
git:
  remote_url: https://github.com/synthesys-lab/agentize
  default_branch: main
agentize:
  commit: e3eab9a1234567890abcdef1234567890abcdef
worktree:
  trees_dir: trees
```

## 示例：非标准分支

对于使用 `trunk` 而不是 `main` 的项目：

```yaml
project:
  name: my-project
  lang: python
git:
  default_branch: trunk
```

这使得 `wt spawn` 能正确地从 `trunk` 分叉。

## 保留

**编辑：** 可以安全地手动编辑。该文件使用标准 YAML 格式。用户的修改是安全的。

## 备注

- 使用极简 YAML 解析器（无外部依赖）
- 仅支持文档中记录的字段
- 允许注释（以 `#` 开头的行）
- 对空白不敏感（标准 YAML 缩进）
