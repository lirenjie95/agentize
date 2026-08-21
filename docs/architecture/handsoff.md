# Handsoff 模式

Handsoff 模式旨在最大限度地减少开发过程中的人工干预。
默认情况下，agent 会自动推进任务而不询问用户，
包括后续步骤和权限。

要禁用 handsoff 模式，在 `.agentize.local.yaml` 中设置：

```yaml
handsoff:
  enabled: false
  auto_permission: false
```

`handsoff.enabled` 启用工作流的自动续接。
在 Claude 的 `stop.py` 触发时，它会回喂一个提示，让 agent
自动判断当前工作流的状态。
如果已完成，则停止工作流；否则继续下一步。
目前我们支持：

- `ultra-planner` 用于规划任务，直到详细的实现计划发布到 GitHub Issues。
- `issue-to-impl` 用于实现任务，直到实现完成并创建 PR。
  - 创建 PR 之前，agent 会运行测试、linter 和代码评审以确保代码质量。
- `plan-to-issue` 用于从用户提供的计划创建 GitHub [plan] issue，直到 issue 成功创建。

为了区分各个工作流，在用户提交提示时，我们有一个钩子来创建元数据文件，
用于存储工作流状态元数据，包括当前步骤、issue 编号、PR 编号等。
目前，我们为 `ultra-planner`、`issue-to-impl` 和 `plan-to-issue` 工作流注册了该钩子。

## Handsoff 模式检查

需要遵循 handsoff 模式的钩子使用一个集中式的辅助函数：

```python
from lib.session_utils import is_handsoff_enabled

if not is_handsoff_enabled():
    sys.exit(0)  # handsoff 禁用时跳过钩子
```

该辅助函数从 `.agentize.local.yaml` 读取 `handsoff.enabled`（查找顺序：项目根目录 → `$AGENTIZE_HOME` → `$HOME`）。未配置时默认返回 `True`。
