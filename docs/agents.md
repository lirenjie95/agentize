# Agents（智能体）

本文档介绍 Claude Code 的 agent 定义。Agent 是面向复杂任务的专用 AI 助手，具备独立的上下文和特定的模型配置。

## 目的

Agent 为复杂的多步骤任务提供隔离的执行环境。每个 agent 定义为 `.claude-plugin/agents/` 目录下一个带 YAML frontmatter 配置的 markdown 文件。

## 配置

Agent 文件包含：
- YAML frontmatter：配置（name、description、model、tools、skills）
- Markdown 内容：agent 的行为规范与工作流

## 可用 Agents

### 评审与分析

- `code-quality-reviewer`：使用 Opus 模型进行长上下文分析，以更高的质量标准进行全面的代码评审

### 基于辩论的规划

用于协作式方案开发的多视角规划 agents：

- `understander`：收集代码库上下文并评估复杂度（为路由决策提供依据）
- `planner-lite`：面向简单修改的轻量级单 agent 规划器（<5 个文件，<150 行代码，仅仓库内）
- `bold-proposer`：调研 SOTA 方案，提出创新、大胆的方法
- `proposal-critique`：验证假设并分析技术可行性
- `proposal-reducer`：遵循“少即是多”哲学简化方案

这些 agents 在 `/ultra-planner` 工作流中协同工作：
1. Understander 首先运行，收集上下文并检查轻量条件
2. 若满足轻量条件（仅仓库内、<5 个文件、<150 行代码）：Planner-lite 直接创建计划
3. 若需要完整流程（需要调研或较复杂）：Bold-proposer + Critique + Reducer 进行辩论
4. 外部共识综合生成最终计划（仅完整路径）

**插件模式调用：** 当 Agentize 作为 Claude Code 插件安装时，agents 会以 `agentize:` 前缀作为命名空间（例如 `agentize:understander`、`agentize:bold-proposer`）。该插件内的 commands 和 skills 在使用 Task 工具调用时应使用带前缀的名称。
