# Review Standard Skill

本目录包含用于对变更进行全面代码审查的 review-standard skill。

## 用途

review-standard skill 为 AI agent 提供系统化的指导，用于在合并到 main 之前审查代码变更。它确保质量、一致性，并遵循项目文档和代码复用标准。

## 集成

该 skill 由 `/code-review` 命令调用，并与以下组件集成：
- `document-guideline` skill - 引用文档标准作为审查标准
- `scripts/lint-documentation.sh` - 用于结构性文档验证
- Git 和 GitHub CLI - 用于访问变更 diff 和仓库上下文

## 用法

完整的审查流程和标准请参阅 `SKILL.md`。
