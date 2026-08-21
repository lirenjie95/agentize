# 测试：智能体基础设施

针对 issue #38 中创建的智能体基础设施的测试覆盖。

## 被测模块

`.claude/agents/` - 智能体基础设施和目录

## 测试状态

**状态**：待测试（dogfooding）

## 测试用例

### TC-1：智能体目录文档

**测试**：验证 `.claude/agents/README.md` 完整且准确

**验证点**：
- [ ] README 描述 agents 与 commands 与 skills 的区别
- [ ] README 列出可用的 agents（code-review）
- [ ] README 遵循项目文档标准

**预期**：README 提供关于智能体用途和组织的清晰指引

---

### TC-2：智能体发现

**测试**：验证 Claude Code CLI 能发现 `.claude/agents/` 中的智能体

**验证点**：
- [ ] 智能体文件被 CLI 识别
- [ ] 智能体出现在智能体列表中（如果 CLI 提供该功能）
- [ ] 智能体元数据从 frontmatter 正确解析

**预期**：CLI 成功发现并列出 code-review 智能体

---

### TC-3：智能体目录结构

**测试**：验证智能体目录遵循文档化的结构

**验证点**：
- [ ] `.claude/agents/` 目录存在
- [ ] `.claude/agents/README.md` 存在
- [ ] 智能体文件使用 `.md` 扩展名
- [ ] 智能体文件具有 YAML frontmatter

**预期**：结构与 agents/README.md 中记录的模式匹配

## Dogfooding 验证

**首次使用日期**：待定

**验证备注**：待定
