# Shell 补全脚本

本目录包含 Agentize CLI 命令的 shell 补全脚本。

## 目的

为 CLI 命令提供交互式 tab 补全支持，通过以下方式改善用户体验：
- 提示可用的子命令和标志
- 提供上下文感知的值补全（例如语言值、文件路径）
- 通过自动补全减少输入并防止错误

## 文件组织

补全脚本遵循 zsh 补全的 `_<command>` 命名模式：

- `_wt` - `wt`（worktree）命令的补全
- `_lol` - `lol`（SDK CLI）命令的补全
- `_acw` - `acw`（Agent CLI Wrapper）命令的补全

## 补全如何加载

当用户运行 `make setup` 并 source 生成的 `setup.sh` 时，补全自动启用：

1. `make setup` 生成 `setup.sh`，它会将 `src/completion/` 添加到 zsh 的 `fpath`
2. 当用户 source `setup.sh` 时，zsh 的补全系统（`compinit`）会发现补全文件
3. 本目录中所有具有 `_<command>` 文件的命令都可使用 tab 补全

## 添加新的补全脚本

为新命令添加补全支持：

1. **在命令脚本中添加补全辅助函数**（例如 `scripts/new-command-cli.sh`）：
   ```bash
   new_command_complete() {
       local topic="$1"
       case "$topic" in
           commands)
               echo "subcommand1"
               echo "subcommand2"
               ;;
           # ... 其他主题
       esac
   }

   new_command() {
       if [ "$1" = "--complete" ]; then
           new_command_complete "$2"
           return 0
       fi
       # ... 命令实现的其余部分
   }
   ```

2. **创建 zsh 补全脚本** `src/completion/_new_command`：
   ```zsh
   #compdef new_command

   _new_command() {
       # 使用 new_command --complete 进行动态补全
       # 并回退到静态列表
       # ... 遵循 _wt 或 _lol 模式实现
   }

   _new_command "$@"
   ```

3. **添加测试**，位于 `tests/cli/` 和 `tests/lint/`：
   - `test-new-command-complete-commands.sh` - 测试命令补全
   - `test-new-command-complete-flags.sh` - 测试标志补全
   - `tests/lint/test-new-command-zsh-completion-file.sh` - 验证文件存在

4. **在命令文档中记录**（例如 `docs/cli/new-command.md`）：
   - 添加 "Shell Completion (zsh)" 章节及设置说明
   - 添加 "Completion Helper Interface" 章节记录各主题

## 设计模式

所有补全脚本遵循一致的模式：

**Shell 无关的辅助函数**（`<command> --complete <topic>`）：
- 返回换行符分隔的 token
- 不含 shell 特定语法
- 可独立测试
- 在完整环境设置之前即可工作

**Zsh 补全脚本**（`_<command>`）：
- 尝试通过 `<command> --complete` 动态获取
- 命令不可用时回退到静态列表
- 添加描述以获得更好的用户体验
- 处理子命令特定的补全

这种两层方案确保：
- 即使命令不在 PATH 中，补全也能工作
- 补全逻辑易于测试
- 未来可扩展到其他 shell（bash、fish）
- 命令结构有唯一的权威来源
