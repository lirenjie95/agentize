# 测试目录

本目录包含用于验证 Agentize SDK 功能和命令的测试套件。

## 目的

自动化测试脚本验证 SDK 模板、CLI 工具和基础设施组件在不同编程语言和环境下是否正确工作。

## 测试组织

### 测试基础设施

- `test-all.sh` - 主测试运行器，执行所有测试套件并报告摘要
- `common.sh` - 共享测试辅助脚本，提供 `PROJECT_ROOT`、测试结果辅助函数和资源管理
- `helpers-worktree.sh` - 共享的 worktree 测试设置/清理辅助函数
- `helpers-gh-mock.sh` - 用于 issue/PR 测试的共享 gh 模拟辅助函数
- `helpers-makefile-validation.sh` - makefile 校验测试的共享辅助函数

### 测试组织模式

每个测试脚本遵循命名模式 `test-<feature>-<case>.sh`，代表一个**单独的测试用例**。所有测试脚本都会加载 `common.sh` 以获得共享功能，并保持 shell 中立兼容性。

测试文件组织在分类子目录中：
- **`tests/sdk/`** - SDK 模板测试（SDK 生成的快速单元测试）
- **`tests/cli/`** - CLI 命令和工具测试（CLI 工具的单元测试）
- **`tests/lint/`** - 校验与 lint 测试（静态检查和 makefile 校验）
- **`tests/e2e/`** - 端到端集成测试（含完整工作流的较慢测试）

### 测试 Fixture

- `fixtures/` - 测试使用的测试数据和模拟文件

## 运行测试

运行所有测试（仅 bash）：
```bash
make test
# or
bash tests/test-all.sh
```

在多个 shell（bash 和 zsh）下运行所有测试：
```bash
make test-shells
# or
TEST_SHELLS="bash zsh" tests/test-all.sh
```

按类别运行测试：
```bash
make test-sdk        # 快速 SDK 单元测试
make test-cli        # CLI 工具测试
make test-lint       # 校验与 lint 测试
make test-e2e        # 端到端集成测试
make test-fast       # sdk + cli + lint 的别名
```

运行特定的测试套件：
```bash
bash tests/sdk/test-c-sdk.sh
bash tests/e2e/test-worktree.sh
```

在 zsh 下运行特定测试：
```bash
zsh tests/sdk/test-c-sdk.sh
```

## 测试结构

每个测试脚本代表一个单独的测试用例，遵循以下模式：

1. 加载共享测试辅助脚本：`source "$(dirname "$0")/common.sh"`
2. 设置测试环境（通过 `make_temp_dir` 创建临时目录）
3. 执行被测功能
4. 验证预期结果（使用 `test_pass` 或 `test_fail`）
5. 清理测试产物（使用 `cleanup_dir` 或隐式清理）
6. 以状态码退出（0 = 通过，1 = 失败）

共享辅助脚本 `tests/common.sh` 提供：
- `PROJECT_ROOT` 和 `TESTS_DIR` 变量
- 终端输出的颜色常量
- 测试结果辅助函数：`test_pass`、`test_fail`、`test_info`
- 资源管理：`make_temp_dir`、`cleanup_dir`

## 添加新测试

### Shell 测试

所有 shell 测试必须位于 `tests/` 下的分类子目录中。不要在 `.claude/*/tests/` 或其他位置创建测试。

1. 选择合适的类别目录：
   - `tests/sdk/` 用于 SDK 模板测试
   - `tests/cli/` 用于 CLI 命令测试
   - `tests/lint/` 用于校验测试
   - `tests/e2e/` 用于端到端集成测试
2. 创建新的测试脚本：`tests/<category>/test-<feature>-<case>.sh`
3. 加载通用辅助脚本：`source "$(dirname "$0")/../common.sh"`
4. 如有需要，加载特定功能的辅助脚本：`source "$(dirname "$0")/../helpers-*.sh"`
5. 实现一个带清晰断言的单独测试用例
6. 使用 `common.sh` 或特定功能辅助脚本中的辅助函数
7. 测试将被 `test-all.sh` 自动发现（无需手动注册）
8. 更新 `.claude/settings.local.json` 以允许无需权限提示的执行（参见 `tests/CLAUDE.md`）

### Python 测试（pytest）

服务器模块的 Python 单元测试位于 `python/tests/`：

1. 创建测试文件：`python/tests/test_<module>.py`
2. 测试会被 pytest 自动发现（匹配 `test_*.py` 的文件）
3. 使用 `conftest.py` fixture 进行路径设置（`PROJECT_ROOT`、`PYTHONPATH`）
4. 使用 `unittest.mock` 模拟子进程调用和外部依赖
5. 运行方式：`pytest python/tests` 或通过 `make test`/`make test-fast`

## 集成

测试文档在以下位置跟踪：
- [docs/test/workflow.md](../docs/test/workflow.md) - Dogfooding 验证状态
- [docs/test/agents.md](../docs/test/agents.md) - Agent 基础设施测试覆盖
