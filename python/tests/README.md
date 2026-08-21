# Python 测试

本目录包含针对 `agentize.server` 模块和 `.claude-plugin/lib` 模块的 pytest 测试。

## 用途

这些测试验证服务器端功能和插件库模块，包括：
- Worker 状态文件操作
- GitHub API 过滤和发现函数
- 运行时配置加载
- Telegram 通知格式化
- 会话查找工具
- 模块导出和导入
- 工作流检测和续接提示词（`.claude-plugin/lib/workflow.py`）
- 会话工具（`.claude-plugin/lib/session_utils.py`）

## 运行测试

**安装依赖：**
```bash
python -m pip install -r python/requirements-dev.txt
```

**运行所有 pytest 测试：**
```bash
pytest python/tests
```

**以详细输出运行：**
```bash
pytest python/tests -v
```

**运行特定测试文件：**
```bash
pytest python/tests/test_workers.py
```

测试也会通过 `make test` 和 `make test-fast` 自动运行。

## 测试组织

| 文件 | 覆盖范围 |
|------|----------|
| `test_workers.py` | Worker 状态操作、失效 PID 清理 |
| `test_github_filtering.py` | Issue/PR 过滤、就绪状态检查 |
| `test_github_discovery.py` | 候选发现、状态查询 |
| `test_runtime_config.py` | 配置加载、优先级解析、handsoff 配置段 |
| `test_local_config.py` | YAML 配置查找、环境变量覆盖、类型强制转换 |
| `test_notify.py` | Telegram 消息格式化 |
| `test_session.py` | 会话查找和状态获取 |
| `test_module_exports.py` | 模块导入和再导出 |
| `test_workflow.py` | 工作流检测、issue 提取、续接提示词、supervisor 配置 |
| `test_permission_determine.py` | 权限辅助函数（_escape_html、inline keyboard、回调解析、Telegram 守卫） |

## Fixtures

`conftest.py` 文件提供：
- `project_root`：仓库根目录路径
- `set_agentize_home`：将 `AGENTIZE_HOME` 设置为临时目录以隔离测试
- 为 `python/` 和 `.claude-plugin` 导入自动设置 `PYTHONPATH`

## 编写测试

1. 创建匹配 `test_*.py` 的测试文件
2. 使用 `unittest.mock` 模拟子进程和外部调用
3. 按需使用 pytest fixtures（`tmp_path`、`monkeypatch`、`capfd`）
4. 遵循现有测试模式以保持一致性
