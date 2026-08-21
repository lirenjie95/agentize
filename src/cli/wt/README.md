# wt CLI 模块

## 目的

`wt` git worktree 辅助工具的模块化实现。这些文件由 `wt.sh` 按顺序 source，以提供完整的 `wt` 命令功能。

## 模块映射

| 文件 | 描述 | 导出 |
|------|-------------|---------|
| `helpers.sh` | 仓库检测和路径解析 | `wt_common`、`wt_is_bare_repo`、`wt_get_default_branch`、`wt_configure_origin_tracking`、`wt_resolve_worktree`、`wt_claim_issue_status`、`wt_invoke_claude` |
| `completion.sh` | Shell 无关的补全辅助函数 | `wt_complete` |
| `commands.sh` | 命令实现 | `cmd_common`、`cmd_init`、`cmd_clone`、`cmd_goto`、`cmd_list`、`cmd_remove`、`cmd_prune`、`cmd_purge`、`cmd_spawn`、`cmd_rebase`、`cmd_help` |
| `dispatch.sh` | 主调度器和入口点 | `wt` |

## 加载顺序

父级 `wt.sh` 按以下顺序 source 各模块：

1. `helpers.sh` - 无依赖
2. `completion.sh` - 无依赖
3. `commands.sh` - 依赖 helpers
4. `dispatch.sh` - 依赖以上所有

## 设计原则

- 每个模块都是自包含的，具有明确定义的导出
- 所有函数使用 `wt_` 或 `cmd_` 前缀以避免命名空间冲突
- 辅助函数（`wt_*`）为路径解析和仓库检测提供可复用的实用工具
- 命令实现（`cmd_*`）直接映射到子命令
- 调度器处理顶层路由并委托给命令实现

## 相关文档

- `../wt.md` - 接口文档
- `../../docs/cli/wt.md` - 用户文档
- `../../docs/feat/cli/wt.md` - 详细标志参考
