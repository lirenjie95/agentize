# 校验与 Lint 测试

## 目的

静态校验测试，确保项目结构完整性、linter 正确性和 makefile 一致性，无需执行完整工作流。

## 内容

### Makefile 校验测试（`test-makefile-*`）

makefile 目标正确性和参数校验的测试：

- `test-makefile-init-invalid-lang.sh` - 测试 `make init` 拒绝无效语言
- `test-makefile-init-without-lang.sh` - 测试 `make init` 在无语言参数时的行为
- `test-makefile-update-creates-git-tags.sh` - 测试 `make update` 创建 git tag 文档
- `test-makefile-update-infers-lang.sh` - 测试 `make update` 自动检测语言
- `test-makefile-update-preserves-git-tags.sh` - 测试 `make update` 保留已有 git tag
- `test-makefile-update-without-lang.sh` - 测试 `make update` 在未显式指定语言时的行为
- `test-makefile-setup-zsh-completion.sh` - 测试 `make setup` 生成 zsh 补全脚本

### Shell 补全测试（`test-*-zsh-completion-file.sh`）

shell 补全脚本生成和正确性的测试：

- `test-lol-zsh-completion-file.sh` - 验证 `lol` zsh 补全脚本结构
- `test-wt-zsh-completion-file.sh` - 验证 `wt` zsh 补全脚本结构

## 用法

运行所有 lint 测试：
```bash
make test-lint
# or
bash tests/test-all.sh --category lint
```

运行特定的 lint 测试：
```bash
bash tests/lint/test-makefile-update-creates-git-tags.sh
```

在多个 shell 下运行 lint 测试：
```bash
TEST_SHELLS="bash zsh" bash tests/lint/test-lol-zsh-completion-file.sh
```

## 测试特征

Lint 测试与其他测试类别的区别：

- **执行快速**：无外部依赖，无工作流
- **静态校验**：不执行即检查文件、结构和模式
- **前置条件检查**：在运行前验证假设
- **构建期安全**：尽早捕获配置错误

Lint 测试使用 `tests/helpers-makefile-validation.sh` 实现共享的 makefile 测试模式。

## 测试策略

Lint 测试聚焦于：

1. **参数校验**：确保 makefile 目标拒绝无效输入
2. **文件生成**：验证生成的文件具有正确的结构
3. **Shell 兼容性**：验证 bash/zsh 的补全脚本

## 相关文档

- [scripts/lint-documentation.sh](../../scripts/lint-documentation.sh) - 文档 linter 实现
- [tests/e2e/test-lint-documentation.sh](../e2e/test-lint-documentation.sh) - E2E linter 集成测试
- [tests/helpers-makefile-validation.sh](../helpers-makefile-validation.sh) - Makefile 测试辅助函数
- [tests/README.md](../README.md) - 测试套件概览
