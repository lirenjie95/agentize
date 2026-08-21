# 教程 02：使用 `lol impl` 进行 CLI 实现

**阅读时间：3-5 分钟**

本教程涵盖使用 CLI 优先工作流从 GitHub issue 到可合并代码的完整开发周期。

## 什么是 `lol impl`？

`lol impl` 使用 `wt` + `acw` 自动化"从 issue 到实现"的循环（参见 `docs/cli/lol.md`）。它需要一个真实的 GitHub issue，并协调迭代的实现步骤直至完成。

### 要求

- `gh` 必须已完成认证且能读取该 issue
- issue 编号必须存在于当前仓库中
- 每次迭代需要 `.tmp/commit-report-iter-<N>.txt` 作为提交信息
- 完成需要 `.tmp/finalize.txt`（第一行为 PR 标题；正文中需包含 `Issue <N> resolved`）
- Prompt 模板在渲染时同时接受 `{{TOKEN}}` 和 `{#TOKEN#}` 占位符

### 工作流概述

1. 通过 `gh issue view` 预取 issue 内容并写入 `.tmp/issue-<N>.md`
2. 如果获取失败或 issue 内容为空，则以错误退出
3. 通过 fetch 并 rebase 到默认分支来同步 issue 分支
4. 运行迭代的 `wt + acw` 循环，存在改动时进行提交
5. 当 `.tmp/finalize.txt` 存在且包含 `Issue <N> resolved` 时完成

## 基本用法

```
lol impl 42
```

将 `42` 替换为你在教程 01 中的 issue 编号。

## CLI 示例（高层视角）

```
User: lol impl 42
Agent: Prefetching issue #42 with gh...
Agent: Syncing branch onto origin/main...
Agent: Iteration 1 (uses .tmp/commit-report-iter-1.txt)
...
Agent: Completion detected in .tmp/finalize.txt
```

## Claude UI 等价命令：`/issue-to-impl`（里程碑）

`/issue-to-impl` 是 Claude UI 工作流。它使用基于里程碑的实现循环，文档见 `docs/feat/core/issue-to-impl.md`。如果你偏好 Claude UI 或想要内置的里程碑检查点，请使用它。

### 什么是 `/issue-to-impl`？

`/issue-to-impl` 编排完整的实现工作流：
1. 创建开发分支
2. 更新文档
3. 创建测试用例
4. 增量式实现功能
5. 通过里程碑跟踪进度

### 工作原理

该命令遵循基于里程碑的方法：

- **里程碑 1**：始终自动创建（文档 + 测试，0/N 个测试通过）
- **里程碑 2 及以后**：如果测试尚未全部完成，每约 800 LOC 创建一次
- **完成**：当所有测试通过时，实现即告完成

这使得大型功能可以跨越多个工作会话，同时保持清晰的上下文。

### 基本用法（Claude UI）

```
/issue-to-impl 42
```

### 自动发生的事情

当你运行 `/issue-to-impl` 时：

**1. 分支创建**
- 创建：`issue-42`
- 切换到该分支

**2. 与 origin/<default> 同步**
- 确保工作目录干净
- 从 `origin/main` 或 `origin/master` 获取最新内容
- 将当前分支 rebase 到 `origin/<default>`
- 如果发生 rebase 冲突，则停止并给出指引

**3. 文档（来自方案）**
- 创建/更新文档文件
- 按需添加 README 文件

**4. 方案缓存**
- 从 issue 正文中提取"Proposed Solution"
- 缓存到 `.tmp/plan-of-issue-{N}.md` 以便感知方案漂移
- 方案会被包含在续接 prompt 中，便于恢复

**5. 测试用例（来自方案）**
- 创建测试文件
- 实现测试策略中的测试用例

**6. 里程碑 1 提交**
- 提交文档 + 测试
- 状态：0/N 个测试通过（预期行为）
- 使用 `--no-verify`（测试尚未实现）

**7. 实现循环**
- 按块实现代码（约 100-200 LOC）
- 每块之后运行测试
- 用 `git diff --stat` 跟踪总 LOC
- 如果测试未完成，在 800 LOC 处停止 → 创建里程碑 2
- 或者持续到所有测试通过 → 完成

### 示例：基于里程碑的流程（Claude UI）

**步骤 1：开始实现**
```
User: /issue-to-impl 42

Agent: Creating branch issue-42...
Agent: Syncing with origin/main...
  - Fetched latest changes
  - Rebased onto origin/main (clean)
Agent: Updating documentation...
  - docs/typescript-support.md created
  - README.md updated
Agent: Creating test cases...
  - tests/test-typescript.sh created (8 test cases)
Agent: Creating Milestone 1...
  - Committed docs + tests (0/8 tests pass)
Agent: Implementing feature...
  [Agent works for ~45 minutes implementing code]
Agent: Milestone 2 created at 820 LOC (3/8 tests pass)

Work remaining: ~380 LOC
Tests failing: 5

Resume with: "Continue from the latest milestone"
```

**步骤 2：恢复实现（下一会话）**
```
User: Continue from the latest milestone

Agent: Resuming from Milestone 2 for Issue #42
Agent: Test status: 3/8 tests passed
Agent: Continuing implementation...
  [Agent works for ~30 minutes]
Agent: All tests passed (8/8)!

Implementation complete:
- Total LOC: ~1150
- All 8 tests passing

Next step: Review with /code-review
```

## 从里程碑恢复（Claude UI）

如果实现创建了里程碑（未完成），用自然语言恢复：

```
User: Resume from the latest milestone
User: Continue implementation
User: Continue from .tmp/milestones/issue-42-milestone-2.md
```

**工作原理**：系统会自动：
1. 检测你当前的分支（issue-42-*）
2. 在 `.tmp/milestones/` 中找到最新的里程碑文件
3. 从里程碑加载上下文（剩余工作、测试状态）
4. 从该检查点继续实现

## 使用 `/code-review` 进行代码评审

所有测试通过后，评审你的改动：

```
/code-review
```

这会运行一次全面评审，检查：
- **阶段 1**：文档质量
  - 所有文件夹都有 README.md 文件
  - 源文件有对应的 .md 文档
- **阶段 2**：代码质量与复用
  - 检查是否重复造了已有工具的轮子
  - 依据项目模式进行校验

评审结果会显示以下之一：
- ✅ **APPROVED** - 可以合并
- ⚠️  **NEEDS CHANGES** - 有少量问题需要处理
- ❌ **CRITICAL ISSUES** - 合并前必须修复

在继续之前修复所有问题。

## 与主分支同步

在创建 PR 之前，与最新改动同步：

```bash
git checkout main
git pull --rebase origin main
git checkout issue-42
git rebase main
```

如果出现冲突，请手动解决。

## 创建 Pull Request

代码评审通过且已与 main 同步后，让 Claude 创建 PR：

```
User: Create a pull request for this branch
```

Claude 会调用 `open-pr` skill 来创建 pull request，包含：
- 恰当的标题和描述
- 改动摘要
- 测试计划
- 原始 issue 的链接

PR 编号会自动记录在会话状态中，使服务器在 handsoff 模式下运行时能在完成通知中包含 PR 链接。

**关于命令与 skill 的说明**：斜杠命令（如 `/code-review`）是你直接调用的预定义 prompt，而 skill（如 `open-pr`）是当你使用自然语言请求时由 Claude 隐式调用的例程。

## Dry-Run 模式（Claude UI）

在做出改动之前预览实现方案：

```
/issue-to-impl 42 --dry-run
```

**你会看到：**
- 将要创建的分支
- 方案中的文件（文档、测试、实现）
- 每一步的预估 LOC
- 测试策略摘要

**不会发生的：**
- 不创建分支
- 不修改文件
- 不创建提交或里程碑
- 不创建 PR

使用 dry-run 在开始实现之前验证 issue 是否有完整的方案。

## 常见问题

**"No milestone files found"**
- 你所在的分支没有里程碑
- 解决方案：使用 `/issue-to-impl` 开始，而不是手动创建分支

**"Not on development branch"**
- 你在 `main` 或错误的分支上
- 解决方案：运行 `git checkout issue-42` 或用 `/issue-to-impl` 开始

**"Rebase conflict detected"**
- 你的改动与 main 分支冲突
- 解决方案：手动解决冲突，`git add` 文件，`git rebase --continue`

## 下一步

- **教程 03**：学习如何通过并行开发（同时处理多个 issue）实现规模化
