# 基于规则的权限管理

权限规则通过基于优先级的评估流程控制工具访问。

## 概述

权限系统通过多个阶段评估工具请求，具有清晰的优先级排序。每个阶段可以返回 `allow`、`deny` 或 `ask`。关键原则是**全局规则始终优先于工作流特定权限**。

## 评估顺序

权限请求按以下顺序流经各阶段：

```
Tool Request
    │
    ▼
┌─────────────────────────────┐
│  1. Global Rules            │  ← First match wins (deny/allow/ask)
│     deny  → DENY (stop)     │
│     allow → ALLOW (stop)    │
│     ask   → fall through    │
└─────────────────────────────┘
    │ (ask or no match)
    ▼
┌─────────────────────────────┐
│  2. Workflow Auto-Allow     │  ← Workflow-scoped patterns
│     allow → ALLOW (stop)    │
│     none  → fall through    │
└─────────────────────────────┘
    │ (no match)
    ▼
┌─────────────────────────────┐
│  3. Haiku LLM               │  ← Context-aware evaluation
│     deny  → DENY (stop)     │
│     allow → ALLOW (stop)    │
│     ask   → fall through    │
└─────────────────────────────┘
    │ (ask)
    ▼
┌─────────────────────────────┐
│  4. Telegram Escalation     │  ← Single final escalation
│     deny  → DENY (stop)     │
│     allow → ALLOW (stop)    │
│     timeout → ASK (prompt)  │
└─────────────────────────────┘
```

## 各阶段详情

### 阶段 1：全局规则

全局规则定义在 `.claude-plugin/lib/permission/rules.py` 中。它们最先被评估并具有绝对优先级。

**决策行为：**
- `deny` → 请求立即被拒绝。不再进一步评估。
- `allow` → 请求立即被允许。不再进一步评估。
- `ask` → 继续到阶段 2（工作流自动允许）。

**示例规则：**
```python
# 拒绝规则（最高优先级）
('deny', 'Bash', r'^rm\s+-rf'),        # 绝不允许 rm -rf
('deny', 'Bash', r'^sudo\s+'),          # 绝不允许 sudo

# 允许规则
('allow', 'Bash', r'^git\s+status'),    # 始终允许 git status
('allow', 'Read', r'.*'),               # 允许所有文件读取
('allow', 'Monitor', r'.*'),            # 允许流式后台进程事件

# 询问规则（继续向下传递）
('ask', 'Bash', r'^gh\s+api'),          # gh api 调用需要提示
```

### 阶段 2：工作流自动允许

工作流特定权限仅在工作流会话激活时适用。这些模式允许特定工作流上下文中已知安全的操作。

**关键约束：** 工作流自动允许**不能覆盖全局拒绝规则**。如果全局规则拒绝 `rm -rf`，工作流无法自动允许它。

**决策行为：**
- `allow` → 请求被允许。不再进一步评估。
- 无匹配 → 继续到阶段 3（Haiku LLM）。

**示例工作流：**

**setup-viewboard：** 自动允许 GitHub 配置操作：
- `gh auth status`（认证验证）
- `gh repo view --json owner`（仓库查询）
- `gh api graphql`（项目配置）
- `gh label create --force`（标签创建）

**任意工作流：** 自动允许会话状态修改：
- `jq '.state = "done"' ~/.agentize/.tmp/hooked-sessions/{session-id}.json > ... && mv ...`（工作流完成信号）

这允许工作流更新其会话状态文件以发出完成信号，而无需权限提示。该模式要求字面的 `.tmp/hooked-sessions/` 路径和字母数字会话 ID，防止路径遍历攻击。

这些模式按工作流定义，仅在该工作流的会话期间激活。

### 阶段 3：Haiku LLM

当通过 `.agentize.local.yaml` 中的 `handsoff.auto_permission: true` 启用时，Haiku 使用对话上下文评估工具请求。这为未被显式规则覆盖的操作提供智能权限决策。

**决策行为：**
- `deny` → 请求被拒绝。不再进一步评估。
- `allow` → 请求被允许。不再进一步评估。
- `ask` → 继续到阶段 4（Telegram）。

### 阶段 4：Telegram 升级

Telegram 审批是所有 `ask` 结果的**单一最终升级点**。当通过 `.agentize.local.yaml` 中的 `telegram.enabled: true` 启用时，系统会向 Telegram 发送审批请求。

**决策行为：**
- `deny` → 请求被拒绝。
- `allow` → 请求被允许。
- 超时/错误 → 返回 `ask`（通过 Claude Code 提示本地用户）。

**重要：** Telegram 升级**仅在最后发生一次**，而非在多个点发生。这防止了重复的审批请求并提供干净的升级路径。

配置细节见 [telegram.md](telegram.md)。

## 继续向下传递行为

`ask` 决策具有特殊的继续向下传递行为：

1. **全局规则返回 `ask`** → 继续到工作流自动允许，然后 Haiku，然后 Telegram
2. **工作流自动允许无匹配** → 继续到 Haiku，然后 Telegram
3. **Haiku 返回 `ask`** → 继续到 Telegram
4. **Telegram 超时** → 返回 `ask`（提示本地用户）

这确保不确定的决策在最终提示用户之前，逐步通过更具上下文感知能力的阶段升级。

## 错误处理

权限系统是故障安全的：

- **规则评估错误** → 继续到 Haiku
- **Haiku 错误** → 继续到 Telegram
- **Telegram 错误** → 返回 `ask`（提示本地用户）

系统绝不会因错误而崩溃——它会优雅降级到用户提示。

## 配置

### 全局规则

编辑 `.claude-plugin/lib/permission/rules.py` 修改全局规则。规则按顺序评估；首个匹配生效。

### YAML 配置的规则

权限规则也可以通过 `.agentize.yaml`（项目级）和 `.agentize.local.yaml`（本地覆盖）中的 YAML 配置。

**YAML 模式：**

```yaml
permissions:
  allow:
    - "^npm run (build|test|lint)"    # 简单字符串（隐含 Bash 工具）
    - "^make test"
    - pattern: "^cat .*\\.md$"        # 带显式工具的扩展格式
      tool: Read
  deny:
    - "^npm run deploy:prod"
    - pattern: "^rm -rf"
      tool: Bash
```

**条目格式：**
- **字符串**：`"^pattern"` - 默认匹配 Bash 工具
- **字典**：`{pattern: "^pattern", tool: "ToolName"}` - 显式工具指定（省略时默认为 `Bash`）

**合并顺序和优先级：**

1. **硬编码拒绝规则始终生效** - 不能被 YAML 覆盖
2. **项目规则**（`.agentize.yaml`）- 团队共享
3. **本地规则**（`.agentize.local.yaml`）- 开发者特定覆盖

规则按顺序评估：deny → ask → allow。首个匹配生效。

**来源追踪：** 当规则匹配时，来源会包含在调试日志中：
- `rules:hardcoded` - 来自 `rules.py` 的内置规则
- `rules:project` - 来自 `.agentize.yaml`
- `rules:local` - 来自 `.agentize.local.yaml`

### 工作流自动允许

工作流特定模式定义在 `.claude-plugin/lib/permission/determine.py` 中的工作流特定模式列表下（例如 `_SETUP_VIEWBOARD_ALLOW_PATTERNS`）。

### YAML 配置

| YAML 路径 | 用途 |
|-----------|---------|
| `handsoff.auto_permission` | 启用 Haiku LLM 评估（`true` 启用） |
| `telegram.enabled` | 启用 Telegram 升级（`true` 启用） |

完整配置选项见 [telegram.md](telegram.md) 和 [handsoff.md](../core/handsoff.md)。
