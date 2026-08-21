# 测试文档

本目录包含关于 Agentize 的测试策略、验证工作流和智能体测试的文档。

## 目的

这些文档追踪测试状态、定义测试策略，并记录 AI 驱动组件的验证方法。由于 AI 规则是主观且依赖 LLM 的，本文档强调以 dogfooding（使用 Agentize 开发 Agentize 自身）作为主要验证方法。

## 文件

### workflow.md
测试与 dogfooding 状态追踪器。记录所有 skills、commands 和 agents 的验证状态，附真实使用示例和成熟度指标（✅ 已验证、🔄 进行中、⚠️ 部分、❌ 未测试、🔧 需要修订）。

### agents.md
智能体基础设施测试覆盖。定义 `.claude/agents/` 目录、智能体发现、目录结构验证和 dogfooding 验证标准的测试用例。

### code-review-agent.md
代码审查智能体测试覆盖。记录 code-review 智能体功能、审查标准执行以及与审查工作流集成的测试用例。

## 测试理念

Agentize 遵循 **dogfooding 优先**的测试方法：
- AI 规则通过用它们开发 Agentize 自身来测试
- 真实使用提供最真实的验证
- 传统单元测试补充但不替代 dogfooding
- 验证状态被追踪和记录以保证透明

## 测试运行器

Agentize 使用两个测试框架：

1. **Shell 测试**（`tests/`）：使用 bash/zsh 的 CLI 和 SDK 集成测试
2. **Pytest**（`python/tests/`）：server 组件的 Python 模块单元测试

### Shell 测试运行器

shell 测试套件支持在多个 shell 下运行测试，以确保 shell 中立的兼容性：

- **默认行为**：测试通过 `make test` 在 bash 下运行
- **多 shell 测试**：测试可通过 `make test-shells` 或 `TEST_SHELLS="bash zsh" ./tests/test-all.sh` 在 bash 和 zsh 下运行
- **Shell 可用性**：当显式设置 `TEST_SHELLS` 时，列出的所有 shell 必须可用，否则测试运行器以错误退出。这确保 CI 强制执行能捕获缺失的 shell 安装。
- **CI 强制执行**：GitHub Actions 在每次 push/PR 时运行 `make test-shells`（已安装 zsh），确保保持 bash+zsh 兼容性。

这能在用户在不同 shell 环境中遇到问题之前，及早发现 shell 特定的问题（例如 bashism）。

### Pytest 运行器

server 模块和 `.claude-plugin/lib` 模块的 Python 测试位于 `python/tests/`，通过 pytest 运行：

- 测试由 pytest 自动发现（匹配 `test_*.py` 的文件）
- `make test` 和 `make test-fast` 都会在 shell 测试之后运行 pytest
- 仅运行 pytest：`pytest python/tests`
- 安装开发依赖：`python -m pip install -r python/requirements-dev.txt`
- `.claude-plugin` 目录通过 `conftest.py` 添加到 `sys.path`，以支持测试插件模块

## 测试结构

每个测试脚本代表一个**单一测试用例**，并遵循以下模式：

1. Source 共享测试辅助脚本：`source "$(dirname "$0")/common.sh"`
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

## 运行测试

Shell 测试通过 `tests/test-all.sh` 执行，它会自动发现分类子目录中的测试。Python 测试通过 pytest 运行。`docs/architecture/architecture.md` 中记录的命令：

- `make test` - 运行所有测试（bash 下的 shell 测试 + pytest）
- `make test-shells` - 在 bash 和 zsh 下运行所有测试（zsh 未安装时失败）
- `make test-sdk` - 运行 SDK 模板测试
- `make test-cli` - 运行 CLI 命令测试
- `make test-lint` - 运行验证测试
- `make test-e2e` - 运行端到端集成测试
- `make test-fast` - 运行快速测试（sdk + cli + lint + pytest）

**注意**：当显式设置 `TEST_SHELLS`（例如通过 `make test-shells`）时，测试运行器强制严格的 shell 可用性，若任何必需的 shell 缺失则以错误退出。

## 集成

测试文档被以下位置引用：
- 主 [README.md](../README.md) 的 "Testing Documentation" 部分
- [docs/feat/core/](../feat/core/) 中的工作流
- 各个 skill 和 command 实现
