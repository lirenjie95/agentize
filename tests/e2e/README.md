# 端到端集成测试

## 目的

端到端集成测试，验证 agentize 框架中的完整工作流和多组件交互。

## 内容

### Worktree E2E 测试（`test-wt-cross-*`、`test-worktree-*`）

worktree 管理的完整工作流测试：

- `test-wt-cross-init-creates-main.sh` - 测试 `wt init` 创建 main worktree
- `test-wt-cross-spawn-from-linked.sh` - 测试从链接的 repo 派生 worktree
- `test-wt-cross-invalid-agentize-home.sh` - 测试 AGENTIZE_HOME 无效时的行为
- `test-wt-cross-missing-agentize-home.sh` - 测试缺少 AGENTIZE_HOME 时的行为
- `test-worktree-flag-order-after-issue.sh` - 标志解析边界情况的占位
- `test-worktree-reject-description-arg.sh` - 参数校验边界情况的占位
- `test-worktree-spawn-yolo-no-agent.sh` - 无 agent 派生边界情况的占位

### Project 自动化 E2E 测试（`test-lol-project-*`）

GitHub Projects 集成工作流：

- `test-lol-project-create.sh` - 测试通过 `lol project create` 创建项目
- `test-lol-project-create-user.sh` - 测试创建用户拥有的项目
- `test-lol-project-associate.sh` - 测试将 issue 关联到项目
- `test-lol-project-auto-field.sh` - 测试自动字段填充
- `test-lol-project-automation.sh` - 测试项目自动化工作流
- `test-lol-project-automation-write.sh` - 测试写入自动化配置
- `test-lol-project-help.sh` - 测试 project 命令帮助文本
- `test-lol-project-metadata-preservation.sh` - 测试元数据持久性
- `test-lol-project-missing-metadata.sh` - 测试缺少元数据时的行为
- `test-lol-project-status-missing.sh` - 测试 Status 字段验证自动创建缺失的选项

### Issue 管理 E2E 测试（`test-open-issue-*`）

issue 创建和更新工作流：

- `test-open-issue-with-draft.sh` - 测试从草稿文件创建 issue
- `test-open-issue-without-draft.sh` - 测试无草稿创建 issue
- `test-open-issue-draft-non-plan.sh` - 测试非规划类 issue 创建
- `test-open-issue-update-mode.sh` - 测试更新已有 issue
- `test-open-issue-update-maintains-format.sh` - 测试更新期间的格式保持

### 多 Agent E2E 测试（`test-external-consensus-*`）

多 agent 辩论与共识工作流：

- `test-external-consensus-issue-interface.sh` - 测试基于共识的 issue 创建接口

### Linter E2E 测试

- `test-lint-documentation.sh` - 在真实场景中测试文档 linter

## 用法

运行所有 E2E 测试：
```bash
make test-e2e
# or
bash tests/test-all.sh --category e2e
```

运行特定的 E2E 测试：
```bash
bash tests/e2e/test-wt-cross-spawn-from-linked.sh
```

在多个 shell 下运行 E2E 测试：
```bash
TEST_SHELLS="bash zsh" bash tests/e2e/test-lol-project-create.sh
```

## 测试特征

E2E 测试与单元测试的区别：

- **执行较慢**：完整工作流验证，多步操作
- **设置复杂**：可能创建临时 repo、模拟 GitHub CLI、设置 worktree
- **多组件**：测试 CLI、脚本和外部工具之间的交互
- **真实场景**：端到端模拟实际用户工作流

E2E 测试使用 `tests/helpers-*.sh` 中的辅助函数实现通用的设置/清理模式。

## 测试 Fixture

E2E 测试可能使用 `tests/fixtures/` 中的 fixture：
- 模拟 GitHub API 响应
- 示例项目结构
- 配置模板

## 相关文档

- [tests/cli/](../cli/) - CLI 单元测试（更快，聚焦单个命令）
- [tests/fixtures/](../fixtures/) - 测试 fixture 和模拟数据
- [tests/helpers-worktree.sh](../helpers-worktree.sh) - Worktree 测试辅助函数
- [tests/README.md](../README.md) - 测试套件概览
