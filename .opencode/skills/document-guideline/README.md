# Document Guideline Skill

本文件夹包含 document-guideline skill，用于指导 AI agent 遵循项目的文档标准。

## 用途

document-guideline skill 提供全面的文档标准，它们：
1. **通过 pre-commit linting 自动强制执行**结构性要求
2. **被其他 skill 引用**，用于内容质量指导
3. **通过 dogfooding 验证**（该 skill 要求自身也有文档）

## 文件

- `SKILL.md` - 主 skill 定义，包含 frontmatter 和完整的文档标准
  - 高层设计文档指南（`docs/*`）
  - 文件夹 README.md 要求（由 linting 强制执行）
  - 源代码 .md 文件对应关系（由 linting 强制执行）
  - 测试文档要求（由 linting 强制执行）
  - Milestone 与 linting 交互指南

## 集成

### 与 Pre-commit Linting 集成

该 skill 由 `scripts/lint-documentation.sh` 强制执行，该脚本在 pre-commit hook 期间运行：
- 检查所有文件夹都有 README.md
- 检查所有源文件（`.py`、`.c`、`.cpp`、`.cxx`、`.cc`）都有 `.md` 伴随文件
- 检查所有测试文件都有文档（内联或伴随 .md）

### 与其他 Skill 集成

- **plan-guideline skill**：在创建实现计划时引用文档标准
  - 文档步骤始终优先（设计先行的 TDD）
- **milestone skill**：在增量开发中使用文档指南
  - 在 milestone 期间允许使用 `--no-verify` 绕过，以接受文档与代码的暂时不一致

## 验证方式

该 skill 使用 **dogfooding** 而非显式测试用例：
- linter 验证其自身的文档（`scripts/lint-documentation.md`）
- 该 skill 文件夹要求有此 `README.md`（由 linter 验证）
- pre-commit hook 集成在实际使用中测试

## 用法

AI agent 会在以下情况自动引用该 skill：
- 创建实现计划时（确保包含文档步骤）
- 编写代码时（提醒创建伴随 .md 文件）
- 运行 milestone 提交时（理解何时可以接受绕过 linting）

该 skill 不能被用户直接调用——它提供供其他 skill 引用的指南。
