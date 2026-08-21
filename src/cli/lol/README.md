# lol CLI 模块

## 目的

`lol` SDK CLI 的模块化实现。这些文件由 `lol.sh` 按顺序 source，以提供完整的 `lol` 命令功能。

## 模块映射

| 文件 | 描述 | 导出 |
|------|-------------|---------|
| `helpers.sh` | 语言检测和实用函数 | `_lol_detect_lang`（私有） |
| `completion.sh` | Shell 无关的补全辅助函数 | `_lol_complete`（私有） |
| `project-lib.sh` | 共享的项目设置库 | `project_init_context`、`project_preflight_check`、`project_read_metadata`、`project_update_metadata`、`project_create`、`project_associate`、`project_generate_automation`、`project_verify_status_options` |
| `commands.sh` | source `commands/*.sh` 的薄加载器 | 所有 `_lol_cmd_*` 函数（私有） |
| `commands/` | 逐命令实现文件 | 见下文 |
| `dispatch.sh` | 主调度器和帮助文本 | `lol` |
| `parsers.sh` | 各命令的参数解析 | `_lol_parse_project`、`_lol_parse_serve`、`_lol_parse_usage`、`_lol_parse_claude_clean`、`_lol_parse_plan`、`_lol_parse_impl`、`_lol_parse_simp`（支持 `--editor`、`--focus`）、`_lol_parse_use_branch`、`_lol_parse_upgrade` |

### commands/ 目录

| 文件 | 导出 |
|------|---------|
| `upgrade.sh` | `_lol_cmd_upgrade` |
| `use-branch.sh` | `_lol_cmd_use_branch` |
| `version.sh` | `_lol_cmd_version` |
| `project.sh` | `_lol_cmd_project` |
| `serve.sh` | `_lol_cmd_serve` |
| `claude-clean.sh` | `_lol_cmd_claude_clean` |
| `usage.sh` | `_lol_cmd_usage` |
| `plan.sh` | `_lol_cmd_plan` |
| `impl.sh` | `_lol_cmd_impl`（委托给 Python 工作流） |
| `simp.sh` | `_lol_cmd_simp`（委托给 Python 工作流） |

## 加载顺序

父级 `lol.sh` 按以下顺序 source 各模块：

1. `helpers.sh` - 无依赖
2. `completion.sh` - 无依赖
3. `project-lib.sh` - 依赖 `scripts/gh-graphql.sh`
4. `commands.sh` - source `commands/` 中的所有文件，依赖 helpers 和 project-lib
5. `parsers.sh` - 依赖 commands
6. `dispatch.sh` - 依赖以上所有

## 设计原则

- 每个模块都是自包含的，只 source 其所需的依赖
- `lol()` 是唯一的公开入口；内部辅助函数使用 `_lol_` 前缀
- 命令实现（`_lol_cmd_*`）在子 shell 中运行，以保留 `set -e` 语义
- 解析器将 CLI 参数转换为命令函数的位置参数
- 调度器处理顶层路由和帮助文本

## 相关文档

- `../lol.md` - 接口文档
- `../../docs/cli/lol.md` - 用户文档
