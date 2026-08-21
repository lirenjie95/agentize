# Scripts 目录

本目录包含本项目的实用脚本、git hooks 和包装器入口。

**规范 CLI 源：** 主要的 CLI 实现位于 `src/cli/`。本目录中的脚本要么是独立的实用工具，要么是委托给 `src/cli/` 库的薄包装器。

## 文件

### 安装器
- `install` - 一条命令即可完成安装的 Agentize 安装脚本
  - 用法：`curl -fsSL https://raw.githubusercontent.com/SyntheSys-Lab/agentize/main/scripts/install | bash`
  - 选项：
    - `--dir <path>` - 安装目录（默认：`$HOME/.agentize`）
    - `--repo <url-or-path>` - Git 仓库 URL 或本地路径（默认：官方 GitHub 仓库）
    - `--help` - 显示帮助并退出
  - 行为：
    - 验证依赖（`git`、`make`、`bash`）
    - 将仓库克隆到安装目录（或从本地路径复制）
    - 运行 `make setup` 生成 `setup.sh`
    - 注册本地 Claude Code 插件 marketplace 并安装插件（如果 `claude` 可用）
    - 打印 shell RC 集成说明
  - 安全特性：
    - 不自动修改 RC 文件
    - 如果安装目录已存在则失败（防止覆盖）
  - 退出码：0（成功），1（错误）
  - 详细文档请参阅 [docs/feat/cli/install.md](../docs/feat/cli/install.md)

### Pre-commit Hook
- `pre-commit` - Git pre-commit hook 脚本
  - 在测试之前运行文档 linter
  - 通过 `tests/test-all.sh` 执行所有测试套件
  - 里程碑提交可用 `--no-verify` 绕过

### 文档 Linter
- `lint-documentation.sh` - Pre-commit 文档 linter
  - 验证文件夹文档（README.md，skill 目录则为 SKILL.md）
  - 验证源代码 .md 文件的对应关系
  - 验证测试文档是否存在
  - 退出码：0（通过），1（失败）

- `lint-documentation.md` - linter 自身的文档
  - 外部接口（用法、退出码）
  - 内部辅助函数（check 函数）
  - 用法和输出示例

### Git Worktree 辅助工具
- `wt-cli.sh` - Worktree CLI 包装器（source `src/cli/wt.sh`）
  - 用法：`./scripts/wt-cli.sh <command> [args]`
  - 规范源：`src/cli/wt.sh`
  - 命令：
    - `init` - 初始化 worktree 环境（创建 trees/main）
    - `main` - 切换到主 worktree（在 source 时）
    - `spawn <issue-number>` - 创建 worktree 并进行 GitHub 验证
    - `list` - 显示所有活动 worktree
    - `remove <issue-number>` - 按 issue 编号移除 worktree
    - `prune` - 清理过时的 worktree 元数据
    - `help` - 显示帮助信息
  - 退出码：0（成功），1（错误）

- `worktree.sh` - 旧版 worktree 管理（请改用 `wt-cli.sh`）

### GitHub API 包装器

- `gh-graphql.sh` - GitHub Projects v2 API 的 GraphQL 包装器
  - 用法：`./scripts/gh-graphql.sh <operation> [args...]`
  - 操作：create-project、lookup-owner、lookup-project、add-item、list-fields、get-issue-project-item、update-field、create-field-option、review-threads
  - 支持通过 `AGENTIZE_GH_API=fixture` 使用 fixture 模式进行测试
  - 完整文档请参阅 `gh-graphql.md`

### SDK CLI 包装器

这些脚本委托给 `src/cli/lol.sh`：

- `agentize-project.sh` - Project 命令包装器（调用 `_lol_cmd_project`）
  - 用法：由 `lol project` 命令调用，或携带环境变量直接调用
  - 环境变量：`AGENTIZE_PROJECT_MODE`、`AGENTIZE_PROJECT_ORG` 等
  - 退出码：0（成功），1（失败）

- `detect-lang.sh` - 语言检测包装器（调用 `_lol_detect_lang`）
  - 用法：`./scripts/detect-lang.sh <project_path>`
  - 退出码：0（检测到），1（无法检测）

### Makefile 实用工具

#### 参数验证
- `check-parameter.sh` - agentize target 的基于模式的参数验证
  - 用法：`./scripts/check-parameter.sh <mode> <project_path> <project_name> <project_lang>`
  - 根据模式（init/update）验证必需参数
  - 对于 **init 模式**：验证 PROJECT_PATH、PROJECT_NAME、PROJECT_LANG 以及模板是否存在
  - 对于 **update 模式**：仅验证 PROJECT_PATH
  - 退出码：0（成功），1（验证失败）
  - 示例：
    ```bash
    ./scripts/check-parameter.sh "init" "/path/to/project" "my_project" "python"
    ```

## 用法

### 安装 Pre-commit Hook

pre-commit hook 应链接到 `.git/hooks/pre-commit`：

```bash
# 链接到 git hooks（通常在项目设置时完成）
ln -sf ../../scripts/pre-commit .git/hooks/pre-commit
```

### 跨项目函数设置

对于 agentize 仓库本身，使用 `make setup` 生成带有硬编码路径的 `setup.sh`：

```bash
make setup
source setup.sh
# 将 'source /path/to/agentize/setup.sh' 添加到你的 shell RC 以持久化
```

这将使 `wt` 和 `lol` CLI 命令在任何目录中都可用。

### 手动运行 Linter

```bash
# 对所有被跟踪文件运行
./scripts/lint-documentation.sh

# 检查特定文件（通过 git staging）
git add path/to/files
git commit  # Linter 自动运行
```

### 绕过 Hooks

对于文档已存在但实现尚不完整的里程碑提交：

```bash
git commit --no-verify -m "[milestone] message"
```
