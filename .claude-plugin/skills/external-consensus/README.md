# External Consensus Skill

## 用途

使用外部 AI 评审（Codex 或 Claude Opus），从多 agent 辩论报告中合成一份平衡的共识实现计划。

该 skill 在 ultra-planner 工作流中充当“裁决者”和“整合者”的角色，解决三个 agent 视角之间的冲突，并将它们的见解组合成一份连贯的实现计划。

## 文件

- **SKILL.md** - 主 skill 实现，包含详细工作流
- **external-review-prompt.md** - 用于外部共识评审的 AI 提示词模板
- **scripts/external-consensus.sh** - 封装所有执行逻辑的规范化脚本

## 集成

### 使用者
- `ultra-planner` 命令 - 在 debate-based-planning skill 完成后调用

### 输出到
- `open-issue` skill - 共识计划成为 GitHub issue 正文
- 用户审批 - 计划在创建 issue 前提交评审

## 依赖

### 必需
- **合并的辩论报告** - debate-based-planning skill 的输出（3 个 agent）
- **提示词模板** - external-review-prompt.md（位于 skill 目录中）

### 外部工具（需要其一）

#### Codex CLI（首选）

该 skill 使用 Codex CLI 的高级特性以获得最佳的共识评审效果：

**安装**：Codex CLI（因发行方式而异）

**用法模式**：
```bash
codex exec \
    -m gpt-5.2-codex \              # 最新的 Codex 模型
    -s read-only \                  # 安全：只读沙箱
    --enable web_search_request \   # 启用外部研究
    -c model_reasoning_effort=xhigh # 最大推理深度
    -i input.md \                   # 输入文件
    -o output.txt                   # 输出文件
```

**使用的特性**：
- **gpt-5.2-codex 模型**：具有增强推理能力的最新版本
- **只读沙箱**：阻止文件写入的安全限制
- **Web 搜索**：事实核查和 SOTA 模式研究
- **xhigh 推理强度**：彻底的权衡分析
- **基于文件的 I/O**：可靠处理大型辩论报告

**优势**：
- 借助 web 研究获得更彻底的分析
- 经过事实核查的技术决策
- 更高质量的共识计划
- 成本：每次评审约 $0.50-1.50
- 时间：2-5 分钟（xhigh 推理）

#### Claude Code CLI（回退）

当 Codex 不可用时，回退到使用 Opus 的 Claude Code：

**安装**：Claude Code CLI（https://github.com/anthropics/claude-code）

**用法模式**：
```bash
claude -p \
    --model opus \                                      # Claude Opus 4.5
    --tools "Read,Grep,Glob,WebSearch,WebFetch" \      # 只读工具
    --permission-mode bypassPermissions \               # 自动化执行
    < input.md > output.txt                            # 通过重定向进行文件 I/O
```

**使用的特性**：
- **Opus 模型**：最高推理能力
- **只读工具**：安全限制（无 Edit/Write）
- **WebSearch 和 WebFetch**：外部研究能力
- **绕过权限**：自动化执行期间无提示
- **文件 I/O**：标准输入/输出重定向

**优势**：
- 与 Codex 相同的研究能力
- Opus 提供高推理质量
- Codex 不可用时无缝回退
- 成本：每次评审约 $1.00-3.00
- 时间：1-3 分钟

### 模板
- **external-review-prompt.md** - 带占位符的提示词模板：
  - `{{FEATURE_NAME}}` - 简短的功能名称
  - `{{FEATURE_DESCRIPTION}}` - 简要描述
  - `{{COMBINED_REPORT}}` - 完整的 3-agent 辩论报告

## 工作原理

该 skill 使用规范化脚本（`scripts/external-consensus.sh`），它会：

1. 解析输入以检测 issue 编号模式或路径模式
2. 解析辩论报告路径（如提供 issue 编号则为 `.tmp/issue-{N}-debate.md`）
3. 验证辩论报告文件存在
4. 使用健壮的模式匹配从报告中提取功能名称：
   - 接受标题（`# Feature:`）、加粗标签（`**Feature**:`）或普通标签（`Feature:`）
   - 对 `Feature`、`Title` 或 `Feature Request` 进行大小写不敏感匹配
   - 按优先级顺序扫描报告 1 → 2 → 3，直到找到第一个匹配
   - 仅当所有报告中都没有标签时回退到 "Unknown Feature"
5. 加载并处理提示词模板，进行变量替换
6. 检查 Codex 是否可用（首选 Codex，回退到 Claude Opus）
7. 以适当的配置调用外部 AI：
   - **Codex**：gpt-5.2-codex、只读沙箱、web 搜索、xhigh 推理
   - **Claude**：Opus 模型、只读工具（Read、Grep、Glob、WebSearch、WebFetch）
8. 将共识计划保存到 `.tmp/issue-{N}-consensus.md`（issue 模式）或 `.tmp/consensus-plan-{timestamp}.md`（路径模式）
9. 返回共识文件路径，用于验证和摘要提取

## 说明

- 外部评审者提供**中立、无偏**的视角
- 首选 Codex 是因为其**高级特性**：web 搜索、xhigh 推理、只读沙箱
- Claude Opus 回退具有**相同的研究能力**：WebSearch、WebFetch、只读工具
- **基于文件的 I/O 模式**：使用带时间戳的 `.tmp/` 目录以避免冲突
- **执行时间**：2-5 分钟（Codex xhigh 推理）、1-3 分钟（Claude）
- **成本考量**：高级特性成本更高，但质量足以 justify
  - Codex：每次评审约 $0.50-1.50
  - Claude：每次评审约 $1.00-3.00
- **安全性**：两者都使用只读限制（沙箱/工具）
- **质量收益**：web 搜索支持事实核查，xhigh 推理产生彻底的分析
- **回退保障**：Claude Code 作为该 skill 的一部分始终可用
