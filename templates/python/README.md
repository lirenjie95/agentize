# Python SDK

- `Makefile`：定义 Python SDK 构建命令的 Makefile。
  - `make setup`：生成一个项目级的 `setup.sh` 脚本，用于为此 SDK 项目设置环境变量（例如 PYTHONPATH）。
  - `make build`：对 Python 是空操作（无需编译）。
  - `make clean`：移除 Python 缓存文件和目录。
  - `make test`：运行 Python SDK 的测试用例。
- `project_name/`：包含 Python 包的文件夹（可通过 `AGENTIZE_PROJECT_NAME` 重命名）。
  - `__init__.py`：包初始化文件，导入时打印 "Hello, World!"。
- `tests/`：包含 Python SDK 测试用例的文件夹。
  - `test_main.py`：一个简单的测试用例，导入该包并检查输出。
