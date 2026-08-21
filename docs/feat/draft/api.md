# 工作流 API 与 Plan 流水线示例

定义一个轻量级的命令式工作流 API 用于协调智能体会话，以 plan 流水线作为规范示例。

## 目标

- 提供符合真实流水线（包括循环）的**命令式**工作流风格。
- 在共享 API 中集中**工件管理、重试、并发和错误处理**。
- 让 **plan** 和 **impl** 流水线成为直接调用 API 的小型示例工作流。
- 将 `workflow/utils/` 重命名为 `workflow/api/`，以反映其公共、面向用户的接口定位。

## 非目标

- 完整的 DAG 调度、高级依赖图或复杂的编排引擎。
- 隐藏所有异常；失败应暴露给调用者。
- 与旧导入路径的长期兼容。

## 需求

### API 接口

- `workflow/api/session.py` 提供 `Session` 作为主要的命令式接口。
- `Session.run_prompt(...)` 运行单个智能体会话，具备：
  - 输入/输出工件命名
  - 输出验证
  - 可配置次数的重试
  - 一致的错误
  - 可选的输入/输出路径覆盖，用于复用固定工件的工作流
- `Session.run_parallel(...)` 以**相同的重试策略**并发运行多个会话。
- `Session.stage(...)` 为 `run_parallel(...)` 构建轻量级调用对象。
- `StageResult` 暴露 `stage`、`input_path`、`output_path` 和 `process`，并带有 `.text()` 辅助方法。
- `PipelineError`（或等价物）携带 `stage`、`attempts` 和 `last_error`。

### 行为

- **重试语义**：`retry=N` 表示最多 `1 + N` 次尝试，首次成功即停止。
- **失败条件**：
  - 进程返回码非零
  - 输出文件缺失
  - 输出文件为空
- **并发模型**：满足并行 ACW 会话（例如两路扇出）的最小调度。

### 示例工作流

- plan 流水线必须使用 API 实现，并作为**主要示例**编写文档。
- plan 流水线是**命令式**的，而非声明式/分阶段式。
- issue 创建返回用作输出前缀的 issue 号。

## 建议的结构

```
python/agentize/workflow/api/
  README.md
  __init__.py
  __init__.md
  acw.py
  acw.md
  gh.py
  gh.md
  path.py
  path.md
  prompt.py
  prompt.md
  session.py
  session.md
```

`workflow/utils/` 重命名为 `workflow/api/`。现有模块连同其 `.md` 伴随文件一起移动，以保持文档完整性。

## API 设计（命令式）

### Session

- **构造函数**：`Session(output_dir, prefix, *, runner=run_acw, input_suffix="-input.md", output_suffix="-output.md")`
- **run_prompt**：
  - `run_prompt(name, prompt, backend, *, tools=None, permission_mode=None, timeout=3600, extra_flags=None, retry=0, retry_delay=0, input_path=None, output_path=None) -> StageResult`
  - 写入输入文件，运行 ACW，验证输出，失败时重试。
- **stage**：
  - `stage(name, prompt, backend, **opts) -> StageCall`
  - 由 `run_parallel` 使用的小型值对象。
- **run_parallel**：
  - `run_parallel(calls, *, max_workers=2, retry=0, retry_delay=0) -> dict[str, StageResult]`
  - 并发执行调用并验证每个结果。

### StageResult

- 字段：`stage`、`input_path`、`output_path`、`process`
- 辅助方法：`.text()` 返回字符串形式的输出

### 错误处理

- API 抛出 `PipelineError`；调用者默认不包装错误。
- 错误包含 `stage`、`attempts` 和 `last_error` 以辅助调试。

## Plan 流水线示例

plan 流水线以**命令式**编写，使用 `Session` 作为其唯一的执行原语：

```python
from agentize.workflow.api.session import Session
from agentize.workflow.api import gh

def pipeline(user_prompt: str):
    issue = gh.create_issue(title="...", body=user_prompt)

    sess = Session(output_dir=".tmp", prefix=f"issue-{issue.number}")

    understander = sess.run_prompt(
        "understander",
        render_prompt("path/to/understander.md", {"feat": user_prompt}),
        backend=("claude", "opus"),
    )

    bold = sess.run_prompt(
        "bold",
        render_prompt("path/to/understand.md", {"feat": user_prompt, "understander": understander.text()}),
        backend=("claude", "opus"),
        retry=5,
    )

    parallel = sess.run_parallel(
        [
            sess.stage("critique", render_critique(bold.text()), backend=("claude", "opus")),
            sess.stage("reducer", render_reducer(bold.text()), backend=("claude", "opus")),
        ],
        retry=5,
    )

    consensus = sess.run_prompt(
        "consensus",
        render_consensus(parallel["critique"].text(), parallel["reducer"].text()),
        backend=("claude", "opus"),
        retry=5,
    )

    gh.edit_issue(body=consensus.text(), title="...")
```

该示例是用户构建自己工作流的规范参考。

## 设计理由与权衡

- **命令式流程**与基于循环的工作流一致，对迭代流水线更易读。
- **API 负责的错误处理**确保一致的验证并避免重复检查。
- **最小并发**减少表面积，同时覆盖主要用例（并行 ACW 会话）。
- 权衡：声明式 DAG 在这里不够易用，但如需要可在以后添加。

## 迁移计划

1. **重命名并移动模块**
   - 将 `workflow/utils/` → `workflow/api/`
   - 更新代码和测试中的所有导入
2. **引入 `api/session.py`**
   - 实现 `Session`、`StageResult`、`StageCall`、`PipelineError`
   - 为 `session.py` 添加 `.md` 伴随文档
3. **将 planner 重构为示例流水线**
   - CLI 保留在 `planner/__main__.py`
   - 将工作流逻辑移入小型的 `planner/pipeline.py`（或等价物）
   - 确保 plan 流水线示例有文档且保持精简
4. **重构 impl 流水线**
   - 用 `Session` 替换内部 runner 逻辑
   - 保留循环式逻辑
5. **更新文档和测试**
   - 更新 `workflow/api/README.md` 以说明公共 API
   - 更新测试和文档中对 `workflow/api` 的引用

## 待实现的新代码

- `python/agentize/workflow/api/session.py`
- `python/agentize/workflow/api/session.md`
- 更新 `python/agentize/workflow/api/README.md` 以包含 `Session`
- `python/agentize/workflow/planner/pipeline.py`（示例工作流入口）
- `python/agentize/workflow/planner/pipeline.md`
- `python/agentize/workflow/impl/pipeline.py`（如果 `impl` 也成为示例）
- `python/agentize/workflow/impl/pipeline.md`
- 在代码和测试中更新导入，将 `workflow.utils` 替换为 `workflow.api`
