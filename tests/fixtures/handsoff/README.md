# Handsoff Agent 测试 Fixture

## 目的

JSON fixture，提供模拟的工具使用响应，用于测试 handsoff agent 的自动化工作流，无需调用真实的 Claude API。

## 内容

### Fixture 文件

- `bash-add-plan-label.json` - 模拟 Bash 工具为 issue 添加 [agentize:plan] 标签的响应
  - 模拟 `gh issue edit --add-label "agentize:plan"` 命令的执行
  - 用于测试 issue 打标签自动化

- `posttooluse-milestone.json` - 模拟 milestone 创建的工具使用后事件
  - 模拟 milestone 提交的 commit message 技能调用
  - 用于测试 milestone 自动化钩子

- `posttooluse-open-issue-auto.json` - 模拟自动创建 issue 的工具使用后事件
  - 模拟自动化工作流中 open-issue 技能的调用
  - 用于测试 issue 创建自动化

- `posttooluse-open-pr.json` - 模拟 PR 创建的工具使用后事件
  - 模拟自动化工作流中 open-pr 技能的调用
  - 用于测试 PR 创建自动化

## 用法

这些 fixture 由 handsoff agent 测试（通常在 `tests/e2e/` 中）使用，用于：

1. 模拟 GitHub CLI 响应，无需网络访问
2. 模拟工具使用模式，用于测试自动化逻辑
3. 在受控场景中验证 handsoff agent 行为

测试中的示例用法模式：
```bash
# 测试读取 fixture 以模拟工具响应
MOCK_RESPONSE=$(cat tests/fixtures/handsoff/bash-add-plan-label.json)
# 测试验证 handsoff agent 正确处理了模拟数据
```

## Fixture 结构

每个 JSON fixture 遵循工具使用响应的 schema：
- 工具名称（例如 "Bash"、"Skill"）
- 工具调用中使用的参数
- 模拟的输出或结果
- 状态/错误信息（如适用）

## 维护

更新 handsoff agent 自动化时：
- 为新的工具使用模式添加新 fixture
- 如果工具 schema 变化，更新现有 fixture
- 确保 fixture 名称清晰描述所模拟的场景

## 相关文档

- [tests/e2e/test-external-consensus-issue-interface.sh](../../e2e/test-external-consensus-issue-interface.sh) - 使用这些 fixture 的 E2E 测试
- [.claude/skills/](../../../.claude/skills/) - 由这些 fixture 测试的技能实现
