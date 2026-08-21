# 教程 01：使用 `lol plan` 进行 CLI 规划

**主要规划教程**：将本教程作为功能规划的默认入口。

**阅读时间：5 分钟**

学习如何使用 `lol plan --editor`（CLI 优先）进行多智能体辩论式规划。如果你偏好 Claude UI，`/ultra-planner` 提供自动路由和 `--force-full`（参见 `docs/feat/core/ultra-planner.md`）。

## 什么是 `lol plan`？

`lol plan` 运行多智能体辩论流水线，产出一份共识实现方案。它是推荐的 CLI 规划入口，文档见 `docs/cli/lol.md` 和 `docs/cli/planner.md`。

### 基本用法

在你的编辑器中编写功能描述：

```
lol plan --editor
```

`--editor` 会打开 `$EDITOR`。如果未设置 `$EDITOR`，则直接传入描述：

```
lol plan "Add user authentication with JWT tokens and role-based access control"
```

### 使用 `--refine` 进行改进

通过再次运行辩论来改进已有的规划 issue：

```
lol plan --refine 42
```

可选的改进重点：

```
lol plan --refine 42 "Focus on reducing complexity"
```

## Claude UI 等价命令：`/ultra-planner`

`/ultra-planner` 是 Claude UI 的规划接口。它使用自动路由并支持 `--force-full`。完整行为细节见 `docs/feat/core/ultra-planner.md`。

### 自动路由

在 **Understander** 智能体收集代码库上下文之后，它会检查 lite 条件：

- **Lite 路径**（全部满足时）：单智能体规划器（1-2 分钟）
  - 所有知识都在仓库内（无需联网调研）
  - 受影响文件 < 5 个
  - 总行数 < 150 LOC
- **Full 路径**（其他情况）：带联网调研的多智能体辩论（6-12 分钟）

### 完整辩论（用于复杂功能）

Full 路径使用**三个 AI 智能体**进行串行辩论工作流：

1. **Bold Proposer**：调研 SOTA 解决方案并提出创新方案
2. **Proposal Critique**：验证假设并识别技术风险
3. **Proposal Reducer**：遵循"少即是多"的哲学进行简化

Bold-proposer 首先运行以生成具体提案，然后 Critique 和 Reducer 都分析该提案（彼此之间并行运行）。一个外部评审者（Codex/Claude Opus）将三个视角综合为一份共识方案。

## 何时使用？

**使用 `lol plan`** 处理 CLI 中的所有功能规划。它始终运行 `docs/cli/lol.md` 中记录的多智能体流水线。

**使用 `/ultra-planner`**：当你想要 Claude UI 的便利性或自动路由时。

**使用 `/ultra-planner --force-full`** 的场景：
- 即使是简单的改动，你也想要彻底的多视角分析
- 即使 LOC 很低，该功能也需要 SOTA 调研

**使用 `/plan-to-issue`** 作为独立的替代方案：
- 当你已有现成的方案，想将其转换为 GitHub issue
- 用于范围明确的时间敏感型规划

## 工作流示例

**1. 调用命令：**
```
lol plan "Add user authentication with JWT tokens and role-based access control"
```

**2. Bold-proposer 生成提案（1-2 分钟）：**
```
BOLD PROPOSER: OAuth2 + JWT + RBAC (~450 LOC)
```

**3. Critique 和 Reducer 分析 Bold 的提案（2-3 分钟）：**
```
CRITIQUE: Medium feasibility, 2 critical risks (token storage, complexity)
REDUCER: Simple JWT only (~180 LOC, 60% reduction)
```

**4. 外部共识综合：**
```
Consensus: JWT + basic roles (~280 LOC)
- From Bold: JWT tokens + role-based access
- From Critique: httpOnly cookies for security
- From Reducer: Removed OAuth2 complexity

Documentation Planning:
- docs/api/authentication.md — create JWT auth API docs
- src/auth/README.md — create module overview
- src/middleware/auth.js — add interface documentation
```

**5. 规划 issue 自动更新：**
```
Plan issue #42 updated with consensus plan.
URL: https://github.com/user/repo/issues/42

To refine (CLI): lol plan --refine 42
To refine (Claude UI): /ultra-planner --refine 42
To implement (CLI): lol impl 42
```

## 基于标签的自动改进

在使用 `lol serve` 运行时，你可以触发改进而无需手动调用命令：

1. 确保 issue 处于 `Proposed` 状态（而非 `Plan Accepted`）
2. 通过 GitHub UI 或 CLI 添加 `agentize:refine` 标签：
   ```bash
   gh issue edit 42 --add-label agentize:refine
   ```
3. 服务器将在下一次轮询时拾取该 issue 并运行 `/ultra-planner --refine`（当前服务器行为见 `docs/cli/lol.md`）
4. 改进完成后，标签被移除，状态保持为 `Proposed`

这使利益相关者无需 CLI 访问权限即可请求方案改进。

## 提示

1. **提供上下文**：写"Add JWT auth for API access"（而不是只写"Add auth"）
2. **合理确定功能规模**：琐碎的改动不要用，复杂的功能一定要用
3. **审阅所有视角**：Bold 展示创新，Critique 展示风险，Reducer 展示简洁
4. **需要时就改进**：第一次共识不完美？使用 `lol plan --refine`
5. **选择你的界面**：CLI 用 `lol plan`，Claude UI 自动路由用 `/ultra-planner`

## Dry-Run 模式

预览将要创建的内容而不对 GitHub 做任何改动：

```
lol plan --dry-run "Add user authentication with JWT tokens"
```

**会发生的：**
- 完整辩论工作流运行（understander → bold-proposer → critique/reducer → consensus）
- 方案文件保存到 `.tmp/` 供审阅
- 打印将要创建的 issue 摘要

**不会发生的：**
- 不创建占位 issue
- 不更新 issue 正文
- 不添加标签

**成本说明：** token 成本与常规运行相近，因为智能体仍会执行。当你想在提交到 GitHub 之前审阅方案时使用 `--dry-run`。

## 成本与时间（Claude UI 自动路由）

**`/ultra-planner` 的自动路由：**

| 路径 | 条件 | 时间 | 成本 |
|------|------------|------|------|
| Lite | 仅仓库内、<5 个文件、<150 LOC | 1-2 分钟 | ~$0.30-0.80 |
| Full | 需要调研或较复杂 | 6-12 分钟 | ~$2.50-6 |

**为什么 lite 更便宜**：没有外部共识步骤（单智能体，无需综合）

**full 路径的价值**：多视角、彻底验证、均衡的方案

## 规划 → 实现（端到端）

`lol plan` 创建你的 GitHub issue 之后，继续使用 `lol impl <issue-number>`（参见 `docs/tutorial/02-issue-to-impl.md`）。

### 后端配置

在 `.agentize.local.yaml` 中配置规划器后端：

```yaml
planner:
  backend: claude:opus             # 所有阶段的默认后端
  understander: claude:sonnet      # 覆盖 understander 阶段
  bold: claude:opus                # 覆盖 bold-proposer 阶段
  critique: claude:opus            # 覆盖 critique 阶段
  reducer: claude:opus             # 覆盖 reducer 阶段

workflows:
  impl:
    model: opus                    # lol impl 的默认模型
```

**注意：** `lol impl --backend <provider:model>` 会在单次运行中覆盖 `.agentize.local.yaml` 的 `impl.model`（参见 `docs/cli/lol.md`）。

## 下一步

1. 在 GitHub 上审阅规划 issue
2. 运行 `lol impl <issue-number>` 开始实现（教程 02）
3. 如果方案需要调整，使用 `lol plan --refine <issue>`

**拿不准时**：使用 `lol plan`——它让规划保持 CLI 优先，同时 Claude UI 仍然可用。
