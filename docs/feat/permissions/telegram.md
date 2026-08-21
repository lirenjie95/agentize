# Telegram 审批

通过 Telegram 进行手动审批的工作流，用于无干预自动化。

## 概述

Telegram 是权限评估流程中的**单一最终升级点**。当所有其他阶段（全局规则、工作流自动允许、Haiku LLM）都得出 `ask` 结果时，系统会升级到 Telegram 进行手动审批。这让你能从手机上批准/拒绝工具调用，实现安全的无干预操作。

**在评估顺序中的位置：**
```
Global Rules → Workflow Auto-Allow → Haiku LLM → Telegram (final)
```

Telegram 升级**仅在最后发生一次**，而非在多个点发生。这防止了重复的审批请求并提供干净的升级路径。完整评估顺序见 [rules.md](rules.md)。

## 配置

在 `.agentize.local.yaml` 中配置 Telegram 审批：

```yaml
telegram:
  enabled: true                    # 启用 Telegram 审批
  token: "123456:ABC-DEF..."       # 来自 @BotFather 的 Bot API token
  chat_id: "-1001234567890"        # 聊天/频道 ID
  timeout_sec: 60                  # 审批超时时间（默认：60，最大：7200）
  poll_interval_sec: 5             # 轮询间隔（默认：5）
  allowed_user_ids: "123,456,789"  # 允许的用户 ID（CSV，可选）
```

**YAML 查找顺序：**
1. 项目根目录 `.agentize.local.yaml`
2. `$AGENTIZE_HOME/.agentize.local.yaml`
3. `$HOME/.agentize.local.yaml`（用户级，由安装脚本创建）

### 设置参考

| YAML 路径 | 类型 | 必需 | 默认值 | 描述 |
|-----------|------|----------|---------|-------------|
| `telegram.enabled` | bool | 是 | `false` | 设为 `true` 启用 |
| `telegram.token` | string | 是 | - | Telegram Bot API token |
| `telegram.chat_id` | string | 是 | - | 发送审批请求的聊天 ID |
| `telegram.timeout_sec` | int | 否 | `60` | 超时秒数（最大：7200） |
| `telegram.poll_interval_sec` | int | 否 | `5` | 轮询间隔秒数 |
| `telegram.allowed_user_ids` | CSV | 否 | - | 允许的用户 ID 逗号分隔列表 |

## 审批流程

1. Server 向你的 Telegram 聊天发送包含工具详情的消息：
   - 工具名称
   - 目标（命令/文件路径）
   - 会话 ID（截断）

2. 你使用内联按钮或文本命令响应：
   - **按钮**：点击 "Allow" 或 "Deny"
   - **命令**：发送 `/allow` 或 `/deny`

3. 原始消息会更新以显示决策结果

4. 如果超时内无响应，返回 `ask`（回退到 Claude Code 的默认行为）
