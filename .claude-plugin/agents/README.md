# Agents

本目录包含 agentize 插件的专用 agent。

## 概述

Agent 是由命令通过 Task 工具以 `subagent_type` 参数调用的专用 AI 子代理。

## 命名约定

- Agent 通过 `subagent_type` 调用时使用 `agentize:` 前缀
- Mega-planner agent 在文件名中使用 `mega-` 前缀，以区别于 ultra-planner agent

## Ultra-Planner Agent（3-agent 辩论）

| Agent | 角色 | 理念 |
|-------|------|------------|
| `bold-proposer` | 生成创新提案 | 基于现有代码构建，突破边界 |
| `proposal-critique` | 验证单个提案 | 挑战假设，识别风险 |
| `proposal-reducer` | 简化单个提案 | 少即是多，消除不必要的复杂性 |
| `understander` | 收集代码库上下文 | 理解问题领域 |
| `planner-lite` | 为简单功能快速制定计划 | 完整辩论的轻量级替代方案 |
| `code-quality-reviewer` | 审查代码质量 | 确保符合规范 |

## Mega-Planner Agent（5-agent 辩论）

| Agent | 角色 | 理念 |
|-------|------|------------|
| `mega-bold-proposer` | 生成带代码 diff 的创新提案 | 基于现有代码构建，突破边界 |
| `mega-paranoia-proposer` | 生成破坏性的重构提案 | 推倒重来，正确地重建 |
| `mega-proposal-critique` | 验证两份提案 | 挑战双方假设，进行比较 |
| `mega-proposal-reducer` | 简化两份提案 | 对两份提案都奉行少即是多 |
| `mega-code-reducer` | 最小化总代码量 | 只要能缩减代码库，允许大改动 |

## Agent 关系

### Ultra-Planner 流程

```
              +------------------+
              |   understander   |
              +--------+---------+
                       | context
                       v
             +------------------+
             |  bold-proposer   |
             +--------+---------+
                      | proposal
       +--------------+---------------+
       v                              v
+------------------+       +------------------+
|proposal-critique |       |proposal-reducer  |
+------------------+       +------------------+
```

### Mega-Planner 流程

```
              +------------------+
              |   understander   |
              +--------+---------+
                       | context
        +--------------+---------------+
        v                              v
+------------------+       +------------------+
|mega-bold-        |       |mega-paranoia-    |
|proposer          |       |proposer          |
+--------+---------+       +--------+---------+
         |                          |
         +-------------+------------+
                       | both proposals
   +-------------------+-------------------+
   v                   v                   v
+------------+ +---------------+ +------------+
|mega-       | |mega-          | |mega-code-  |
|proposal-   | |proposal-      | |reducer     |
|critique    | |reducer        | |            |
+------------+ +---------------+ +------------+
```

## 用法

**Ultra-planner agent：**
```
subagent_type: "agentize:bold-proposer"
subagent_type: "agentize:proposal-critique"
subagent_type: "agentize:proposal-reducer"
```

**Mega-planner agent：**
```
subagent_type: "agentize:mega-bold-proposer"
subagent_type: "agentize:mega-paranoia-proposer"
subagent_type: "agentize:mega-proposal-critique"
subagent_type: "agentize:mega-proposal-reducer"
subagent_type: "agentize:mega-code-reducer"
```

## 另请参阅

- `/ultra-planner` 命令：`.claude-plugin/commands/ultra-planner.md`
- `/mega-planner` 命令：`.claude-plugin/commands/mega-planner.md`
- `external-synthesize` skill：`.claude-plugin/skills/external-synthesize/`
