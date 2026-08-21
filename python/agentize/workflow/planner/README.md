# Planner 包

多阶段 planner 流水线的可运行包。同时提供库接口和 CLI 入口。

## 用途

本包包含驱动 `lol plan` 的 5 阶段 planner 流水线（understander → bold → critique → reducer → consensus）。critique 和 reducer 始终并行执行。它被构建为可运行包以支持 `python -m agentize.workflow.planner` 调用，流水线本身作为 Session DSL 示例实现。

## 调用方式

### 作为 CLI

```bash
python -m agentize.workflow.planner --feature-desc "Add dark mode toggle" --issue-mode true
```

**参数：**
- `--feature-desc`：功能描述或细化重点
- `--issue-mode`：`true` 或 `false`（创建/更新 GitHub issue）
- `--verbose`：`true` 或 `false`
- `--refine-issue-number`：要细化的 issue 编号（可选）

### 作为库

```python
from agentize.workflow.planner import run_planner_pipeline, StageResult

results = run_planner_pipeline(
    "Implement JWT authentication",
    output_dir=".tmp",
)

for stage, result in results.items():
    print(f"{stage}: {result.output_path}")
```

## 模块结构

| 文件 | 用途 |
|------|---------|
| `__init__.py` | 包导出：`run_planner_pipeline`、`StageResult` |
| `pipeline.py` | 使用 Session DSL 实现的 planner 流水线 |
| `__main__.py` | CLI 后端和入口 |
| `README.md` | 本文档 |

## 导出

- `run_planner_pipeline`：执行 5 阶段流水线
- `StageResult`：每阶段结果的数据类

## 依赖

- `agentize.workflow.api`：Session DSL、ACW 运行器、提示词渲染和 GitHub 辅助函数
- `agentize.shell`：用于路径解析的 `get_agentize_home()`
- `.claude-plugin/agents/` 和 `.claude-plugin/skills/` 中的提示词模板

## 设计理由

- **可运行包**：使用 `__main__.py` 支持 `python -m` 调用，同时将逻辑保留在单个文件中。
- **关注点分离**：工作流辅助函数位于 `workflow/api/`；流水线编排位于本包。
