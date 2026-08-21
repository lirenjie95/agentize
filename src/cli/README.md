# CLI 源文件

## 目的

Agentize CLI 命令的 source 优先库。这些文件是规范的实现，由 `setup.sh` source 以提供 shell 函数。

## 内容

### 关键文件

- `acw.sh` - Agent CLI Wrapper 库（规范源，薄加载器）
  - source `acw/` 目录中的模块化文件
  - 导出 `acw` 命令用于统一的 AI CLI 调用
  - 支持的提供方：`claude`、`codex`、`opencode`、`cursor`、`kimi`
  - 接口文档：`acw.md`

- `planner.sh` - Planner 流水线库（内部；由 `lol plan` 使用）
  - source `planner/` 目录中的模块化文件
  - 仅导出内部的 `_planner_*` 辅助函数
  - 接口文档：`planner.md`

- `term/colors.sh` - 共享的终端样式辅助函数（标签输出 + 光标清除）
  - `term_color_enabled()` - 检查是否允许使用颜色
  - `term_label <label> <text> [style]` - 打印带样式的标签输出
  - `term_clear_line()` - 输出用于动画的光标清除序列

- `acw/` - Agent CLI Wrapper 模块化实现
  - `helpers.sh` - 校验和实用函数
  - `providers.sh` - 提供方特定的调用函数
  - `dispatch.sh` - 主调度器和入口点
  - 模块映射和加载顺序请参阅 `acw/README.md`

- `wt.sh` - Worktree CLI 库（规范源，薄加载器）
  - source `wt/` 目录中的模块化文件
  - 导出 `wt` 命令用于管理 git worktree
  - 支持的子命令：`clone`、`common`、`init`、`goto`、`spawn`、`list`、`remove`、`prune`、`purge`、`pathto`、`rebase`、`help`
  - 接口文档：`wt.md`

- `wt/` - Worktree CLI 模块化实现
  - `helpers.sh` - 仓库检测、路径解析和项目状态辅助函数
  - `completion.sh` - Shell 无关的补全辅助函数
  - `commands.sh` - 命令实现（cmd_*）
  - `dispatch.sh` - 主调度器和入口点
  - 模块映射和加载顺序请参阅 `wt/README.md`

- `lol.sh` - SDK CLI 库（规范源，薄加载器）
  - source `lol/` 目录中的模块化文件
  - 导出 `lol` 命令用于 SDK 管理
  - 支持的子命令：`upgrade`、`project`、`plan`、`serve`、`usage`、`claude-clean`、`version`
  - 接口文档：`lol.md`

- `lol/` - SDK CLI 模块化实现
  - `helpers.sh` - 语言检测和实用函数
  - `completion.sh` - Shell 无关的补全辅助函数
  - `commands.sh` - source `commands/*.sh` 的薄加载器
  - `commands/` - 逐命令实现（upgrade.sh、project.sh 等）
  - `dispatch.sh` - 主调度器、帮助文本和入口点
  - `parsers.sh` - 各命令的参数解析
  - 模块映射和加载顺序请参阅 `lol/README.md`

## 用法

### Worktree CLI（`wt`）

```bash
# 初始化 worktree 环境
wt init

# 为 GitHub issue #42 创建 worktree
wt spawn 42

# 列出所有 worktree
wt list

# 切换到 worktree（在 source 时）
wt goto 42

# 移除 worktree
wt remove 42
```

### SDK CLI（`lol`）

```bash
# 升级 agentize 安装
lol upgrade

# 显示版本
lol --version

# GitHub Projects 集成
lol project --create --org MyOrg --title "My Project"

# 报告 token 用量
lol usage --today

# 清理过时的项目条目
lol claude-clean
```

### 直接脚本调用

用于开发和测试：

```bash
./src/cli/wt.sh <command> [args]
./src/cli/lol.sh <command> [args]
```

## 实现细节

`wt.sh` 和 `lol.sh` 都承担双重角色：
1. **可 source 模式**：通过 `setup.sh` 的主要用法——导出函数用于 shell 集成
2. **可执行模式**：直接执行脚本，用于测试和非交互使用

### Source 优先模式

Source 优先模式确保：
- CLI 逻辑在 `src/cli/` 中有唯一的权威来源
- `scripts/` 中的包装器脚本委托给库函数
- `setup.sh` source 这些库以供交互式 shell 使用

### 命令隔离

`lol.sh` 的命令实现（`_lol_cmd_*`）使用子 shell 函数来：
- 保留 `set -e` 错误处理语义
- 将环境变量与用户的 shell 隔离
- 匹配原始可执行脚本的行为

`lol()` 是唯一的公开 shell 入口；辅助函数和命令函数都是私有的。

## 相关文档

- [tests/cli/](../../tests/cli/) - CLI 命令测试
- [tests/e2e/](../../tests/e2e/) - 端到端集成测试
- [scripts/README.md](../../scripts/README.md) - 包装器脚本概览
- [docs/cli/acw.md](../../docs/cli/acw.md) - `acw` 命令用户文档
- [docs/cli/wt.md](../../docs/cli/wt.md) - `wt` 命令用户文档
- [docs/cli/lol.md](../../docs/cli/lol.md) - `lol` 命令用户文档
