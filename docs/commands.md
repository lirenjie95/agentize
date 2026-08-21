# Commands（命令）

本文档介绍 Claude Code 的 command 定义。Command 是可以被调用来执行特定工作流或 skill 的快捷方式。

## 目的

Command 提供调用复杂工作流或 skill 的简单接口。每个 command 定义为 `.claude-plugin/commands/` 目录下一个带 frontmatter 元数据的 markdown 文件。

## 配置

Command 文件包含：
- `name`：命令名（用于调用）
- `description`：命令功能的简要描述
- 关于如何使用该命令以及它调用哪些 skill 的说明

## 可用 Commands

### Git 与 GitHub

- `git-commit`：调用 commit-msg skill，按照项目标准创建带有有意义信息的提交
- `pull-request`：评审代码变更，并可通过 --open 标志创建 pull request
- `sync-master`：使用 rebase 将本地 main/master 分支与 upstream（或 origin）同步

### 代码评审

- `agent-review`：通过具有独立上下文和 Opus 模型的 agent 评审代码变更
- `code-review`：按照评审标准评审从当前 HEAD 到 main/HEAD 的代码变更
- `resolve-review`：获取未解决的 PR 评审线程并自动应用修复；未指定时自动从当前分支检测 PR（对自动化友好，由 server 调用）

### 规划与实现

- `make-a-plan`：遵循设计优先的 TDD 方法创建全面的实现计划
- `plan-to-issue`：以实现计划创建格式规范的 GitHub [plan] issue
- `issue-to-impl`：编排从 issue 到完成的完整实现工作流（创建分支、文档、测试和第一个里程碑）；支持 `--dry-run` 预览
- `ultra-planner`：基于多 agent 辩论的规划，通过 /ultra-planner 命令调用（支持 `--refine` 迭代改进，支持 `--dry-run` 在不改动 GitHub 的情况下预览）

### 项目设置

- `setup-viewboard`：设置带有 agentize 兼容的 Status 字段、标签和自动化工作流的 GitHub Projects v2 看板
