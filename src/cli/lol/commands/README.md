# lol 命令实现

## 目的

`lol` CLI 的逐命令实现文件。每个文件恰好导出一个私有的 `_lol_cmd_*` 函数，实现一个特定命令。

## 文件映射

| 文件 | 函数 | 描述 |
|------|----------|-------------|
| `upgrade.sh` | `_lol_cmd_upgrade` | 通过 git 升级 agentize 安装 |
| `use-branch.sh` | `_lol_cmd_use_branch` | 切换到远程开发分支 |
| `version.sh` | `_lol_cmd_version` | 显示版本信息 |
| `project.sh` | `_lol_cmd_project` | GitHub Projects v2 集成 |
| `serve.sh` | `_lol_cmd_serve` | 运行自动化轮询服务器 |
| `claude-clean.sh` | `_lol_cmd_claude_clean` | 从 ~/.claude.json 中移除过时条目 |
| `usage.sh` | `_lol_cmd_usage` | 报告 Claude Code token 用量统计 |
| `plan.sh` | `_lol_cmd_plan` | 运行多智能体辩论流水线 |
| `impl.sh` | `_lol_cmd_impl` | 自动化 issue 到实现的循环 |

## 设计

- 所有函数在子 shell 中运行，以保留 `set -e` 语义
- 父级 `commands.sh` source 本目录中的所有文件
- 函数使用位置参数；`parsers.sh` 中的解析器处理 CLI 标志
