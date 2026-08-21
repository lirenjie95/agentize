# 测试与 Dogfooding 状态

本文档追踪本项目中 AI 规则、skills 和 commands 的测试状态。由于这些 AI 规则是主观的且依赖 LLM 行为，dogfooding（使用系统开发系统自身）提供了最真实的验证。

## 目的

- 追踪哪些 skills/commands 已成功 dogfooding
- 记录真实使用示例
- 识别通过 dogfooding 发现的问题或改进点
- 提供对每个组件成熟度的信心

## 状态定义

- ✅ **已验证**：成功 dogfooding，有文档化示例
- 🔄 **进行中**：当前正在测试
- ⚠️ **部分**：可用但有已知限制
- ❌ **未测试**：尚无 dogfooding 验证
- 🔧 **需要修订**：dogfooding 期间发现问题

---

## Skills

### fork-dev-branch
**状态**：✅ 已验证

**Dogfooding 示例**：
- Issue #30：用于为 document-guideline skill 创建开发分支
- PR #33：分支创建按预期工作

**备注**：成功从 GitHub issue 创建标准化分支名。

---

### plan-to-issue（command）
**状态**：✅ 已验证

**Dogfooding 示例**：
- Issue #30：为 document-guideline skill 创建了计划 issue，带有正确的 `[plan][agent.skill]` 标签

**备注**：
- 正确从 `docs/git-msg-tags.md` 读取标签标准
- 正确格式化 issue，包含 Problem Statement、Proposed Solution 和 Test Strategy 部分
- 与 GitHub CLI 的集成顺畅

---

### issue-to-impl（command）
**状态**：✅ 已验证

**Dogfooding 示例**：
- Issue #30：从 issue 到实现的完整工作流
  - 通过 fork-dev-branch 创建分支
  - 从 issue 正文读取实现计划
  - 生成文档和测试
  - 创建第一个 milestone

**备注**：
- 成功编排完整开发工作流
- 集成 fork-dev-branch、milestone 和 commit-msg skills
- 正确处理多步骤实现

---

### milestone
**状态**：✅ 已验证

**Dogfooding 示例**：
- Issue #30、PR #33：
  - 实现期间准确追踪 LOC 计数
  - 在 `.tmp/milestones/` 目录创建 milestone 文档
  - 测试状态追踪正常工作
  - 按预期在 800 LOC 阈值处停止

**备注**：
- 通过 `git diff --stat` 的 LOC 追踪可靠
- Milestone 文档格式清晰且有用
- 与 commit-msg skill 的集成对 milestone 提交运作良好

---

### commit-msg
**状态**：✅ 已验证（通过 milestone 集成）

**Dogfooding 示例**：
- Issue #30：创建了带正确 `[milestone][agent.skill]` 标签的 milestone 提交
- 对 milestone 提交正确使用 `--no-verify` 标志

**备注**：被 milestone skill 调用时运作良好

---

### make-a-plan（现为 plan-guideline）
**状态**：⚠️ 部分

**备注**：
- 已重命名为 plan-guideline
- 已用于创建计划，但需要更多 dogfooding 验证
- 应测试各种 issue 类型

---

### git-commit（现为 commit-msg）
**状态**：✅ 已验证

**备注**：成功重命名并集成到工作流中

---

### open-pr
**状态**：🔄 进行中

**Dogfooding 示例**：
- PR #33：需要验证该 PR 是通过命令创建还是手动创建的

**近期变更**：
- Issue #37：添加远程分支验证步骤（6.5），防止分支仅存在于本地时 PR 创建失败
  - 处理三种情况：无 upstream、本地领先、已最新
  - 包含认证和分支分叉的错误处理
  - 需要 dogfooding 验证以测试新的远程分支推送逻辑

**备注**：需要显式的 dogfooding 验证，特别是针对新的远程分支验证功能

---

### miles2miles
**状态**：❌ 已移除

**备注**：
- 命令已移除，改用自然语言恢复
- 用户现在使用以下方式恢复："Continue from the latest milestone"

---

### open-issue
**状态**：⚠️ 部分

**备注**：
- 现对 `[plan]` issue 命名为 plan-to-issue
- 需要澄清是否有针对非计划 issue 的独立 skill

---

### document-guideline
**状态**：✅ 已验证

**Dogfooding 示例**：
- Issue #30、PR #33：作为 dogfooding 练习的一部分创建
- 实现了 pre-commit linting 指南

**备注**：成功添加以提高文档质量

---

### review-standard
**状态**：✅ 已验证

**Dogfooding 示例**：
- Issue #34：用于审查其自身的实现（dogfooding 期间的自审查）
  - 成功识别 SKILL.md frontmatter 中不正确的 skill 描述
  - 验证文档结构遵循项目约定
  - 确认文件夹 README.md 存在且准确

**有效的方面**：
- 系统化的两阶段审查流程（文档质量 + 代码质量）
- 清晰、可操作的反馈，带具体的 文件:行号 引用
- 与 document-guideline 标准的集成正常运作
- 发现了否则会被忽视的关键问题

**无效的方面 / 改进点**：
- 手动审查流程彻底但耗时（命令自动化将有帮助）
- 阶段 2 的代码质量检查对仅文档变更作用有限（预期内）

**备注**：
- Dogfooding 验证了该 skill 能有效发现真实问题
- 审查报告格式提供清晰的评估类别（✅/⚠️/❌）
- 成功引用 document-guideline skill 和 lint-documentation.sh
- 准备好与 code-review 命令集成

---

### ultra-planner 自动路由
**状态**：🔄 进行中

**实现状态**：
- Issue #405：添加基于复杂度的自动路由
  - Understander 检查 lite 条件并输出 `recommended_path: lite | full`
  - Lite 条件：仅仓库内知识、<5 个文件、<150 LOC
  - Ultra-planner 根据 understander 推荐进行路由
  - 简单修改使用 planner-lite 智能体（无共识步骤）

**计划的 Dogfooding 测试**：
1. **Lite 路径测试**：运行 `/ultra-planner <simple-feature>` 并验证：
   - Understander 输出 `recommended_path: lite`（所有条件满足）
   - 调用 planner-lite 智能体（无 Bold/Critique/Reducer/Consensus）
   - 总时间约 1-2 分钟
2. **Full 路径测试**：运行 `/ultra-planner <complex-feature>` 并验证：
   - Understander 输出 `recommended_path: full`（需要研究或超出限制）
   - 运行完整辩论（Bold + Critique + Reducer + Consensus）
   - 总时间约 6-12 分钟
3. **Force-full 测试**：运行 `/ultra-planner --force-full <simple-feature>` 并验证：
   - 尽管满足 lite 条件仍运行完整辩论
   - 覆盖正常工作

**备注**：保守的阈值（<5 个文件、<150 LOC）以避免假阴性

---

### code-review（command）
**状态**：✅ 已验证

**Dogfooding 示例**：
- Issue #34：在实现分支上手动执行审查流程
  - 审查了 3 个文件（+861 行）
  - 发现 1 个关键问题（不正确的 frontmatter 描述）
  - 通过第二轮审查验证修复

**有效的方面**：
- 命令接口规范清晰完整
- Skill 集成步骤定义良好
- 错误处理覆盖关键边界情况（main 分支、无变更等）
- 输入/输出规范符合 review-standard skill 预期

**备注**：
- 命令提供干净的接口来调用 review-standard skill
- 准备好与 `/code-review` 调用的端到端集成
- 与手动审查流程相比将加快代码审查

---

### lol project（command）
**状态**：🔄 进行中

**实现状态**：
- Issue #179：实现已开始，包含文档和测试
  - 文档完成（lol.md、metadata.md、project.md、architecture.md）
  - 自动化模板和指南已创建（github-projects-automation.md、project-auto-add.yml）
  - 测试套件已创建（test-lol-project.sh），带 mock GraphQL 的 fixtures
  - 测试目前跳过，等待 agentize-project.sh 实现

**计划的功能**：
- `lol project --create [--org <org>] [--title <title>]` - 创建新的 GitHub Projects v2 看板
- `lol project --associate <org>/<id>` - 关联现有项目看板
- `lol project --automation [--write <path>]` - 生成自动化工作流模板

**备注**：
- 设计遵循 dogfooding 优先方法，默认使用 mock GraphQL
- 测试将验证元数据保留和正确的 YAML 更新
- 需要实现 agentize-project.sh 和 gh-graphql.sh 封装
- 等待 milestone 1 完成和实现循环

---

## 集成测试

### 完整工作流：Issue → 分支 → 实现 → PR
**状态**：✅ 已验证

**示例**：Issue #30 → PR #33
1. ✅ 使用 `/plan-to-issue` 创建计划 issue
2. ✅ 使用 `fork-dev-branch` skill 创建分支（通过 issue-to-impl）
3. ✅ 使用 milestone skill 追踪实现
4. ✅ 创建 milestone 提交
5. 🔄 创建 PR（需要确认是否通过 `/open-pr`）

**成功率**：80%（5 步中确认 4 步）

---

## 已知问题与改进

### Issue #30 / PR #33 的经验

**运作良好的方面**：
- 分支命名约定清晰一致
- Milestone 追踪使工作可管理
- 标签系统提供良好的分类
- 基于 LOC 的节奏防止过大的提交

**改进空间**：
- 需要更清晰的文档说明何时使用 milestone 提交与交付提交
- 考虑为标签选择添加验证
- 测试状态解析可以更健壮
- GitHub CLI 未认证时需要更好的错误消息

**主观元素**（需要人工判断）：
- 适当的标签选择（例如 `[agent.skill]` vs `[feature]`）
- 将工作分解为逻辑块
- 决定实现何时"完成"
- 编写清晰的提交消息

---

## 测试建议

### 高优先级（未测试的核心功能）
1. **miles2miles**：从 milestone 恢复 - 对多会话工作至关重要
2. **open-pr**：端到端 PR 创建
3. **plan-guideline**：各种 issue 类型和复杂度级别

### 中优先级（需要更多示例）
1. **fork-dev-branch**：边界情况（已关闭 issue、无效 issue 号）
2. **commit-msg**：直接调用（非通过 milestone）
3. **milestone**：非常大的实现（>1600 LOC，多个 milestone）

### 低优先级（已充分验证）
1. 更多 issue-to-impl 示例
2. 不同的仓库结构
3. 各种测试框架

---

## Dogfooding 最佳实践

dogfooding 新 skills/commands 时：

1. **记录示例**：链接到具体的 issue/PR 号
2. **记录有效的方面**：需要保留的成功行为
3. **记录无效的方面**：需要修复或改进的问题
4. **更新本文件**：保持测试状态最新
5. **记录主观决策**：记录需要人工判断的地方

---

## 维护

**最后更新**：2025-12-25（更新了 open-pr skill 远程分支验证 - issue #37）

**更新频率**：每次 dogfooding 会话后或 skills/commands 重大变更后

**维护者**：开发期间由 AI 智能体和人工审查者更新
