# Skills（技能）

本文档介绍 Claude Code 的 skill 定义。Skill 是可复用的 AI 行为，可以被 command 调用或直接调用。

## 目的

Skill 提供模块化、可复用的 AI 能力，可以组合成更大的工作流。每个 skill 定义在 `.claude-plugin/skills/` 下的一个子目录中，其中包含一个带有 frontmatter 和说明的 `SKILL.md` 文件。

## 配置

每个 skill 子目录包含：
- `SKILL.md`：带有 frontmatter（name、description）和说明的 skill 定义
- 可选的辅助文件（脚本、模板）

## 可用 Skills

### Git 操作

- `commit-msg`：以有意义的提交消息将暂存的变更提交到 git
- `fork-dev-branch`：为 GitHub issue 创建标准化命名的开发分支

### GitHub 集成

- `open-issue`：从对话上下文创建格式规范、标签恰当的 GitHub issue
- `open-pr`：从对话上下文创建格式规范、标签恰当的 GitHub pull request

### 规划与文档

- `plan-guideline`：创建包含详细文件级变更和测试策略的全面实现计划
- `doc-architect`：为功能实现生成全面的文档检查清单
- `document-guideline`：设计文档、目录 README、源代码接口和测试用例的文档标准

### 实现

- `milestone`：以自动进度跟踪、LOC 监控和里程碑检查点创建来增量推进实现
- `move-a-file`：移动或重命名文件，同时自动更新源代码和文档中的所有引用

### 评审与质量

- `review-standard`：系统化的代码评审，检查文档质量并促进代码复用
- `shell-script-review`：评审 shell 脚本的 shell 中立行为（bash/zsh 兼容性）
- `external-consensus`：利用外部 AI 评审，从多 agent 辩论报告中综合出共识实现计划

### 调试

- `debug-report`：当测试用例失败时调试代码库，若无法解决则通过 GitHub Issues 报告 bug
