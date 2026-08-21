# CLI 命令测试

## 目的

针对命令行界面命令（`wt`、`lol`）的单元测试，验证各个 CLI 功能、参数解析和错误处理。

## 内容

### Worktree CLI 测试（`test-wt-*`）

`wt`（worktree）命令的测试：

- `test-wt-bare-repo-required.sh` - 验证 worktree 命令要求 bare repo
- `test-wt-clone-basic.sh` - 测试 `wt clone` 的 bare repo 创建和初始化
- `test-wt-complete-commands.sh` - 测试 wt 子命令的 shell 补全
- `test-wt-complete-flags.sh` - 测试 wt 标志的 shell 补全
- `test-wt-goto.sh` - 测试使用 `wt goto` 进行 worktree 导航
- `test-wt-purge.sh` - 测试清理过期的 worktree
- `test-wt-zsh-completion-crash.sh` - 测试 zsh 补全稳定性

### Agentize CLI 测试（`test-lol-*`、`test-agentize-*`）

`lol`（agentize）命令的测试：

- `test-lol-complete-commands.sh` - 测试 lol 子命令的 shell 补全
- `test-lol-complete-flags.sh` - 测试 lol 标志的 shell 补全
- `test-lol-help-text.sh` - 验证帮助文本的格式和内容
- `test-lol-version.sh` - 测试版本命令输出
- `test-lol-claude-clean.sh` - 测试 `lol claude-clean` 命令清理过期条目
- `test-lol-upgrade.sh` - 测试 `lol upgrade` 分支选择和设置工作流
- `test-lol-use-branch.sh` - 测试 `lol use-branch` 远程分支切换
- `test-lol-command-functions-loaded.sh` - `_lol_cmd_*` 可用且不存在 `lol_cmd_*` 的冒烟测试
- `test-lol-project-*.sh` - `lol project` 命令的测试
- `test-agentize-cli-*-agentize-home.sh` - AGENTIZE_HOME 验证的测试

### Plan 流水线测试（`test-lol-plan-*`）

- `test-lol-plan-missing-args.sh` - `lol plan` 缺少参数的错误处理
- `test-lol-plan-backend-flags.sh` - `lol plan` 的后端覆盖处理
- `test-lol-plan-issue-mode.sh` - issue 创建与 `--dry-run` 行为
- `test-lol-plan-pipeline-stubbed.sh` - 使用桩化的 `acw` 和 consensus 的流水线流程

### 其他 CLI 测试

- `test-install-script.sh` - 测试单命令安装脚本
- `test-test-all-strict-shells.sh` - 测试 shell 兼容性强制检查

## 用法

运行所有 CLI 测试：
```bash
make test-cli
# or
bash tests/test-all.sh --category cli
```

运行特定的 CLI 测试：
```bash
bash tests/cli/test-wt-goto.sh
```

在多个 shell 下运行 CLI 测试：
```bash
TEST_SHELLS="bash zsh" bash tests/cli/test-wt-complete-commands.sh
```

## 手动补全检查（Zsh）

这些检查是交互式的，无法在 CI 中自动化。

1. 加载补全文件：`source src/completion/_lol`
2. 验证唯一前缀补全：输入 `lol plan --ed<TAB>`
   - 预期：第一次按 Tab 即补全为 `--editor`
3. 验证歧义前缀行为：输入 `lol plan --<TAB>`
   - 预期：显示所有可用选项

## 测试模式

CLI 测试遵循标准测试结构：

1. 加载 `common.sh` 获取测试辅助函数
2. 设置测试环境（临时目录、模拟仓库）
3. 使用特定参数执行 CLI 命令
4. 验证：
   - 退出码（成功/失败）
   - stdout/stderr 输出
   - 文件系统状态变化
   - 错误消息
5. 清理测试产物

CLI 测试是**快速单元测试**，聚焦于单个命令的行为，与验证完整工作流的 E2E 测试不同。

## 相关文档

- [src/cli/](../../src/cli/) - CLI 源码实现
- [tests/e2e/](../e2e/) - 端到端集成测试
- [tests/README.md](../README.md) - 测试套件概览
- [scripts/README.md](../../scripts/README.md) - 脚本实现
