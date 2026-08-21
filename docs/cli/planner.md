# Planner 流水线（内部）

`lol plan` 使用的内部流水线模块，通过 Python 后端运行多智能体辩论工作流。独立的 `planner` 命令已被移除。后端使用工作流辅助函数，使提示词渲染、ACW 调用和 GitHub 发布在 planner 与 implementation 工作流之间保持一致。

## 用法

```bash
lol plan [--dry-run] [--verbose] [--refine <issue-no> [refinement-instructions]] \
  "<feature-description>"
lol plan --refine <issue-no> [refinement-instructions]
```

## 流水线阶段

`lol plan` 针对一个特性描述运行完整的多智能体辩论流水线。阶段 1–4 通过 Python 后端执行，阶段 5 使用 external-consensus 提示词模板通过 `acw` 运行共识综合：

1. **Understander**（sonnet）- 使用 `Read,Grep,Glob` 工具收集代码库上下文
2. **Bold-proposer**（opus）- 研究 SOTA 解决方案并提出创新方案，使用 `Read,Grep,Glob,WebSearch,WebFetch` 工具和 `--permission-mode plan`
3. **Critique**（opus）- 验证假设并分析可行性（始终与 Reducer 并行运行）
4. **Reducer**（opus）- 遵循 "less is more" 哲学简化提案（始终与 Critique 并行运行）
5. **Consensus**（opus）- 使用 external-consensus 提示词从三份报告综合出最终计划

Critique 和 reducer 会追加 plan-guideline 内容，并始终通过 Python 执行器并行运行；不存在顺序模式。

### `--dry-run`（可选标志）

跳过 GitHub issue 创建，使用基于时间戳的产物命名。流水线仍会完整运行；只有 issue 创建/发布步骤被跳过。

### `--refine <issue-no> [refinement-instructions]`

通过从 GitHub 获取已有计划 issue 的正文并重新运行辩论来细化它。可选的细化指令会追加到上下文中以引导智能体。获取到的 issue 正文在复用为辩论上下文之前会被剥离尾部的溯源页脚。细化运行仍会写入以 `issue-refine-<N>` 为前缀的产物，并且除非设置 `--dry-run`，否则会就地更新现有 issue。需要已认证的 `gh` 访问权限来读取 issue 正文。

### `--verbose`（可选标志）

打印额外的详情行（例如产物前缀和共识计划路径）。阶段进度和最终产物位置始终会打印。

### 后端选择（.agentize.local.yaml）

在 `.agentize.local.yaml` 中使用 `provider:model` 字符串配置 planner 后端：

```yaml
planner:
  backend: claude:opus
  understander: claude:sonnet
  bold: claude:opus
  critique: claude:opus
  reducer: claude:opus
```

阶段特定的键会覆盖 `planner.backend`。默认值仍为 `claude:sonnet`（understander）和 `claude:opus`（其他）。

`lol plan --backend <provider:model>` 会将覆盖传递给 Python 后端，为本次运行替换 `planner.backend`，同时不影响阶段特定的键。

### 默认 Issue 创建

默认情况下，`lol plan` 在流水线运行前使用截断的占位标题（`[plan] placeholder: <first 50 chars>...`）创建一个占位 GitHub issue，并使用 `issue-{N}` 产物命名。共识阶段完成后，issue 正文会更新为最终计划并附加尾部溯源页脚（`Plan based on commit <hash>`），标题取自共识文件中第一个 `Implementation Plan:` 或 `Consensus Plan:` 头（回退：截断的特性描述），并应用 `agentize:plan` 标签。

使用 `--refine` 时，不会创建占位 issue。issue 正文会被获取并复用为辩论上下文，并在共识阶段后就地更新（除非设置 `--dry-run`）。

要求 `gh` CLI 已安装并认证。如果 `gh` 不可用或 issue 创建失败，会记录警告并回退到基于时间戳的产物命名。

## 提示词渲染

每个阶段使用 `acw` 进行基于文件的 CLI 调用。提示词在运行时通过拼接以下内容渲染：
- 智能体基础提示词（来自 `.claude-plugin/agents/*.md`）
- Plan-guideline 内容（来自 `.claude-plugin/skills/plan-guideline/SKILL.md`，YAML frontmatter 已剥离）
- 特性描述和上一阶段的输出

提示词模板通过 `agentize.workflow.api.prompt.render` 渲染，它会替换 `{{TOKEN}}` 和 `{#TOKEN#}` 两种占位符，无需更改模板格式。

共识阶段从 `.claude-plugin/skills/external-consensus/external-review-prompt.md` 渲染专用提示词，并嵌入三份报告输出。

## 产物

所有中间产物和最终产物都写入 `.tmp/`：

```
.tmp/{timestamp}-understander.txt       # 默认（无 --issue；Python 后端使用 output_suffix=\".txt\"）
.tmp/{timestamp}-bold.txt
.tmp/{timestamp}-critique.txt
.tmp/{timestamp}-reducer.txt
.tmp/{timestamp}-consensus.md           # 最终共识计划

.tmp/issue-{N}-understander.txt         # 当 --issue 成功时
.tmp/issue-{N}-bold.txt
.tmp/issue-{N}-critique.txt
.tmp/issue-{N}-reducer.txt
.tmp/issue-{N}-consensus.md             # 最终共识计划（同时发布到 issue）
.tmp/issue-refine-{N}-understander.txt  # 细化产物（issue 正文上下文）
.tmp/issue-refine-{N}-bold.txt
.tmp/issue-refine-{N}-critique.txt
.tmp/issue-refine-{N}-reducer.txt
.tmp/issue-refine-{N}-consensus.md      # 细化共识（除非 --dry-run，否则发布）
```

## 与 /ultra-planner 的关系

`/ultra-planner` 命令仍是 Claude Code 中进行多智能体规划（带自动 issue 创建和细化）的接口。`lol plan` 以 shell 函数形式提供相同的辩论流水线，适用于：
- 脚本化或自动化工作流
- CI/CD 集成
- 不依赖 Claude Code 的直接调用

完整的 `/ultra-planner` 命令文档请参阅 `docs/feat/core/ultra-planner.md` 和 `docs/tutorial/01-ultra-planner.md`。

## 输出

Planner 进度以纯文本形式打印到 stderr：

- 流水线开始和特性摘要
- 阶段开始行（包括后端标签）
- 流水线完成和产物位置
- Issue 发布状态和 URL（启用 issue 发布时）

当使用默认的 `acw` runner 时，planner 会在每个阶段运行前记录确切的 `acw` 命令（依据
`docs/cli/acw.md`），随后是 ACW 计时日志。输出校验后，planner 会使用实际的 `.txt`
或 `.md` 产物路径记录 `<stage> dumped to <output-path>`。对于共识阶段，dump 日志在
溯源页脚追加之后发出，因此路径反映最终输出。

## 退出码

| 退出码 | 含义 |
|------|---------|
| 0 | 流水线成功完成 |
| 1 | 参数缺失或无效 |
| 2 | 阶段执行失败 |
