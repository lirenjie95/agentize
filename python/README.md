# Python 包

本目录包含 Agentize SDK 的 Python 包。

## 包

- `agentize/` - 核心 SDK 包（参阅 `agentize/README.md`）

## 用法

从 hook 脚本中使用 `sys.path.insert()` 时这些包会自动可用，
或通过 `make setup` 设置 `PYTHONPATH`。

```bash
# 方式 1：source setup.sh（自动设置 PYTHONPATH）
source setup.sh

# 方式 2：手动设置 PYTHONPATH
export PYTHONPATH="$PWD/python:$PYTHONPATH"
```
