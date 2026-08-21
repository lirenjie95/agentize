# CLI 参考文档

本目录包含 Agentize 命令行工具的详细参考文档。

## 目的

这些文档提供全面的命令行接口规范，包括 Agentize 框架中每个工具的所有标志、选项、用法模式和示例。

**规范源码位置：** CLI 实现以源码优先库的形式存放在 `src/cli/` 中。这里的文档描述面向用户的接口；函数级接口文档见 `src/cli/*.md`，模块映射见 `src/cli/*/README.md`。

## 文件

### acw.md
用于统一调用 AI CLI 的 `acw` 命令。接口文档见 [docs/cli/acw.md](../../cli/acw.md)。为 claude、codex、opencode、cursor 和 kimi CLI 提供基于文件的输入/输出。

### install.md
用于一键安装 Agentize 的 `install` 脚本。文档涵盖安装流程（克隆、worktree 初始化、setup）、命令行选项（--dir、--repo、--help）、安装后 shell RC 集成以及故障排查。

### 关于 lol.md 的说明
`lol.md` 文档已被移除。当前 `lol` 命令文档见 [docs/cli/lol.md](../../cli/lol.md)。`lol` 命令现在提供：`lol upgrade`（安装升级）、`lol project`（GitHub Projects 集成）、`lol usage`（token 用量报告）、`lol claude-clean`（过期条目清理）和 `lol version`（版本信息）。

### wt.md
用于 git worktree 管理的 `wt` 命令接口。文档涵盖 `wt init`（worktree 初始化）、`wt spawn`（基于 issue 的 worktree 创建）、`wt goto`（跳转到 worktree）、`.agentize.yaml` 元数据集成以及 zsh 补全支持。

## 用法

快速参考：
- `lol --help` - 显示 lol 命令帮助
- `wt --help` - 显示 wt 命令帮助

包含示例和高级用法的详细文档，请参阅各个 `.md` 文件。

## 集成

CLI 文档被以下位置引用：
- 主 [README.md](../README.md) 的 "CLI Reference" 部分
- [docs/tutorial/](../tutorial/) 中的教程系列
- 调用这些 CLI 工具的 skills 和 commands

## 故障排查

### Zsh Tab 补全不工作

**问题：** 运行 `make setup` 和 `source setup.sh` 后，`wt`、`lol` 或其他命令的 Tab 补全不工作。

**原因：** 补全文件（`_wt`、`_lol`）移动到 `src/completion/` 之前残留的过期 zsh 补全缓存。

**解决方案：**
```bash
# 删除补全缓存
rm -f ~/.zcompdump ~/.zcompdump.zwc

# 重启 zsh 会话
exec zsh

# 或者只是重新 source setup.sh
source setup.sh
```

完成这次一次性清理后，Tab 补全应能正常工作。

**验证是否生效：**
```bash
# 检查命令是否可用
which wt

# 尝试 Tab 补全
wt <TAB>
```
