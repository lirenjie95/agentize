# Workflow 模块

多阶段 LLM planner 工作流、`lol impl` 循环以及 `lol simp` 简化器工作流的 Python 原生编排。

## 用途

本模块提供 Python 入口，用于运行驱动 `lol plan` 的 5 阶段 planner 流程、`lol impl` 的 issue 到实现循环，以及 `lol simp` 的简化器工作流。planner 流水线复用 `.claude-plugin/agents/` 中已有的提示词模板，以保持行为一致性，同时支持 Python 脚本集成和外部共识合成。像 `impl` 和 `simp` 这样的独立工作流将提示词模板与模块放在一起，以保持清晰。

## 架构

workflow 模块封装了 `acw` shell 函数（Agentize Claude Wrapper）来执行各个流水线阶段。提示词通过组合以下内容进行渲染：

1. 来自 `.claude-plugin/agents/*.md` 的基础 agent 提示词
2. 来自 `.claude-plugin/skills/plan-guideline/SKILL.md` 的 plan-guideline 内容（适用于相应阶段）
3. 调用方提供的功能描述
4. 上一阶段的输出（用于链式阶段）

产物（输入提示词和输出）以可配置的前缀和输出后缀写入 `.tmp/`。

## 模块

| 模块 | 用途 |
|--------|---------|
| `__init__.py` | 包导出：`run_acw`、`ACW`、`run_planner_pipeline`、`run_impl_workflow`、`StageResult`、`ImplError` |
| `utils/` | 用于 ACW 调用、GitHub 操作、提示词渲染和路径解析的辅助包 |
| `planner/` | 独立的规划流水线包（`python -m agentize.workflow.planner`） |
| `planner.py` | **已弃用** - 为向后兼容而做的再导出（将被移除） |
| `impl/` | issue 到实现的工作流（Python），带基于文件的提示词和 `python -m agentize.workflow.impl` 入口 |
| `simp/` | 保持语义的简化器工作流，带模块本地的提示词和 `python -m agentize.workflow.simp` 入口 |

## 流水线阶段

```
understander → bold → critique → reducer → consensus (optional)
                      ↓           ↓
                     (parallel-only)
```

1. **Understander**：收集代码库上下文和约束
2. **Bold**：提出创新的实现方案
3. **Critique**：验证假设并分析可行性
4. **Reducer**：遵循“少即是多”的理念简化方案
5. **Consensus**：合成统一的实现计划（库使用时可选；CLI 委托给外部共识脚本）

critique 和 reducer 始终并行执行。

## 用法

```python
from agentize.workflow import run_planner_pipeline

results = run_planner_pipeline(
    "Add user authentication with JWT tokens",
    output_dir=".tmp",
    output_suffix="-output.md",
    skip_consensus=True,
)

# 访问各阶段结果
for stage, result in results.items():
    print(f"{stage}: {result.output_path}")
```

## 依赖

- 通过 `setup.sh` 提供的 `acw` shell 函数
- `.claude-plugin/agents/` 和 `.claude-plugin/skills/` 中的提示词模板
- 仅使用 Python 标准库（无第三方依赖）
