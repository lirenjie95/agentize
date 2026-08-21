# acw 模块目录

## 目的

Agent CLI Wrapper（`acw`）命令的模块化实现。

## 模块映射

| 文件 | 依赖 | 导出 |
|------|--------------|---------|
| `helpers.sh` | 无 | 校验辅助函数（`_acw_validate_args`、`_acw_check_cli`、`_acw_ensure_output_dir`、`_acw_check_input_file`）和聊天会话辅助函数（`_acw_chat_*`）（私有） |
| `providers.sh` | `helpers.sh` | `_acw_invoke_claude`、`_acw_invoke_codex`、`_acw_invoke_opencode`、`_acw_invoke_cursor`、`_acw_invoke_kimi`、`_acw_invoke_gemini`（私有） |
| `completion.sh` | 无 | `_acw_complete`（私有） |
| `dispatch.sh` | `helpers.sh`、`providers.sh`、`completion.sh` | `acw`（公开）；编排聊天会话的创建、续接和历史前置 |

## 加载顺序

父级 `acw.sh` 按以下顺序 source 各模块：

1. `helpers.sh` - 无依赖（私有辅助函数）
2. `providers.sh` - 使用辅助函数
3. `completion.sh` - 无依赖（补全支持）
4. `dispatch.sh` - 使用 helpers、providers 和 completion

## 架构

```
acw.sh (thin loader)
    |
    +-- helpers.sh (private)
    |     +-- _acw_validate_args()
    |     +-- _acw_check_cli()
    |     +-- _acw_ensure_output_dir()
    |     +-- _acw_check_input_file()
    |     +-- _acw_chat_session_dir()
    |     +-- _acw_chat_session_path()
    |     +-- _acw_chat_generate_session_id()
    |     +-- _acw_chat_validate_session_id()
    |     +-- _acw_chat_create_session()
    |     +-- _acw_chat_validate_session_file()
    |     +-- _acw_chat_prepare_input()
    |     +-- _acw_chat_append_turn()
    |     +-- _acw_chat_list_sessions()
    |
    +-- providers.sh (private)
    |     +-- _acw_invoke_claude()
    |     +-- _acw_invoke_codex()
    |     +-- _acw_invoke_opencode()
    |     +-- _acw_invoke_cursor()
    |     +-- _acw_invoke_kimi()
    |     +-- _acw_invoke_gemini()
    |
    +-- completion.sh (private)
    |     +-- _acw_complete()
    |
    +-- dispatch.sh
          +-- acw()  [公开入口点]
          +-- _acw_usage()
```

## 提供方支持矩阵

| 提供方 | 二进制 | 输入方式 | 输出方式 | 状态 |
|----------|--------|--------------|---------------|--------|
| claude | `claude` | `-p @file` | `> file` | 完整 |
| codex | `codex` | `< file` | `> file` | 完整 |
| opencode | `opencode` | TBD | TBD | 尽力支持 |
| cursor | `agent` | TBD | TBD | 尽力支持 |
| kimi | `kimi` | `< file`（`--print`） | `> file`（剥离 stream-json） | 尽力支持 |
| gemini | `gemini` | `-p "$(cat file)"` | `> file`（剥离 stream-json） | 尽力支持 |

## 运行时依赖

- Kimi 输出规范化使用 `python`（标准库 JSON）将 stream-json 剥离为纯文本。

## 约定

- 只有 `acw` 是公开函数（无前缀）
- 所有其他函数名以 `_acw_` 为前缀，仅供内部使用
- 退出码遵循 `acw.md` 规范（0-4、127）
- 所有函数同时支持 bash 和 zsh
- `--stdout` 模式将输出路由到 `/dev/stdout`，并在调用时将提供方 stderr 合并进 stdout
