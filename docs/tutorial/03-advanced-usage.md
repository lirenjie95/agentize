# 教程 03：进阶用法——并行开发

**阅读时间：3-5 分钟**

通过并行运行多个 AI 智能体来扩大开发规模，每个智能体同时处理不同的 issue。

## 选择你的工作流

**使用多个克隆的场景：**
- 跨不同机器工作
- 偏好 worker 之间的完全隔离
- 每个 worker 需要独立的 fetch/push 操作

**使用单仓库 + worktree 的场景：**
- 磁盘空间有限（worktree 共享 `.git`）
- 在同一台机器上使用多个终端
- 想要更快的搭建速度而无需重新克隆

两种方法都使用 `wt` CLI——根据你的隔离需求来选择。

## 何时使用并行开发

**适合：**
- 多个相互独立的功能
- 拆分为多个独立 issue 的大型重构
- 文档更新 + 功能开发
- 不修改相同文件的 bug 修复

**避免使用：**
- issue 修改相同文件（冲突风险高）
- issue 之间相互依赖
- 你刚接触该框架（请先完成教程 02）

## 方法 1：仓库克隆

### 搭建

使用 `wt clone` 创建带有 worktree 环境的 bare 仓库：

```bash
# source wt.sh 以获得 shell 集成
source src/cli/wt.sh

# 创建并行 worker（每个都是带 trees/main 的 bare 仓库）
cd ~/projects
wt clone https://github.com/your-org/my-project.git my-project-worker-1.git
wt clone https://github.com/your-org/my-project.git my-project-worker-2.git
wt clone https://github.com/your-org/my-project.git my-project-worker-3.git
```

每次 `wt clone` 都会创建一个 bare 仓库并自动初始化 `trees/main`。

### 工作流

在每个克隆中派生 issue worktree。使用 `--yolo` 跳过权限提示：

**终端 1（Worker 1 - Issue #45）：**
```bash
cd ~/projects/my-project-worker-1.git
wt spawn 45 --yolo
# Claude 自动在 trees/issue-45-*/ 中启动
```

**终端 2（Worker 2 - Issue #46）：**
```bash
cd ~/projects/my-project-worker-2.git
wt spawn 46 --yolo
# Claude 自动在 trees/issue-46-*/ 中启动
```

**终端 3（Worker 3 - Issue #47）：**
```bash
cd ~/projects/my-project-worker-3.git
wt spawn 47 --yolo
# Claude 自动在 trees/issue-47-*/ 中启动
```

每个 AI 独立工作。用 `wt goto <issue>` 恢复里程碑，然后启动 claude-code。

### 清理

合并 PR 之后：

```bash
# 移除特定 issue 的 worktree
wt remove 45 --delete-branch
wt remove 46 --delete-branch

# 或删除整个 worker 仓库
rm -rf ~/projects/my-project-worker-*.git
```

## 方法 2：Git Worktree

Worktree 共享 `.git` 目录，同时提供隔离的工作目录——节省磁盘空间。

### 搭建

初始化一次，然后为每个 issue 派生 worktree：

```bash
# source wt.sh 以获得 shell 集成
source src/cli/wt.sh

# 首次搭建：初始化 worktree 环境
cd ~/projects/my-project.git
wt init

# 创建 worktree（从 GitHub 获取标题，启动 Claude）
wt spawn 42
# 创建：trees/issue-42-<title>/
# 分支：issue-42-<title>
```

`spawn` 命令会自动：
- 创建 `trees/issue-<N>-<title>/`（已被 gitignore）
- 按命名约定创建分支
- 在 worktree 中调用 Claude

### 工作流

使用 `--yolo` 跳过权限提示，使用 `--headless` 进入非交互模式：

**终端 1（Issue #45）：**
```bash
cd ~/projects/my-project.git
wt spawn 45 --yolo
# Claude 自动在 trees/issue-45-*/ 中启动
```

**终端 2（Issue #46）：**
```bash
cd ~/projects/my-project.git
wt spawn 46 --yolo
# Claude 自动在 trees/issue-46-*/ 中启动
```

每个 worktree 在自己的分支上独立运作。

### 重要：路径规则

对于路径解析，每个 worktree 都是自己的"项目根目录"。所有路径都相对于活动的 worktree：
- ✅ `docs/tutorial/03-advanced-usage.md`（相对于 worktree 根目录）
- ❌ `../main-repo/docs/...`（跨越了 worktree 边界）

`CLAUDE.md` 中"DO NOT use `cd`"的规则在每个 worktree 内单独生效。

### 清理

```bash
# 移除特定 worktree（保留分支）
wt remove 42

# 移除 worktree 并删除分支
wt remove 42 --delete-branch

# 列出所有 worktree
wt list

# 清理过期的元数据
wt prune

# 移除所有已关闭 issue 的 worktree
wt purge
```

## 进度管理

### 跟踪分配情况

用简单的笔记记录哪个 worker/worktree 处理哪个 issue：

```
Worker 1 / trees/issue-45-*: Issue #45 - Rust SDK
Worker 2 / trees/issue-46-*: Issue #46 - Docs update
Worker 3 / trees/issue-47-*: Issue #47 - Performance fix
```

### 里程碑之后恢复

如果某个 worker 创建了里程碑，在同一个 worktree 中恢复：

```bash
# 导航到 worktree
wt goto 45

# 启动 Claude 并恢复
claude-code
# User: Continue from the latest milestone
```

## 避免冲突

### 为独立性做规划

设计 issue 时避免文件重叠：
- ✅ Issue #45 修改 `templates/rust/`
- ✅ Issue #46 修改 `docs/`
- ✅ Issue #47 修改 `src/performance.c`

### 错开合并

不要一次性合并所有 PR：

1. 完成第一个 worker/worktree
   - `/code-review`
   - `/sync-master`
   - 创建并合并 PR

2. 将其余分支更新到最新的 main
   ```bash
   git checkout main
   git pull origin main
   git checkout issue-46-*
   git rebase main
   ```

3. 对每个剩余 issue 重复评审和合并

### 解决冲突

如果 rebase 期间出现冲突：

```bash
git rebase main
# CONFLICT (content): Merge conflict in src/main.c

# 在编辑器中修复，然后：
git add src/main.c
git rebase --continue
```

## 最佳实践

1. **限制 worker 数量**：3-4 个并行是可管理的，更多会变得混乱
2. **清晰命名**：使用有描述性的目录/worktree 名称
3. **跟踪分配**：记录哪个 worker 处理哪个 issue
4. **PR 前先同步**：创建 PR 之前始终执行 `/sync-master`
5. **先评审**：合并前始终执行 `/code-review`
6. **从小做起**：先尝试 2 个并行 issue，再逐步扩大规模

## 何时使用串行 vs 并行

**使用串行（教程 02）的场景：**
- 正在学习该框架
- issue 涉及相同代码
- issue 之间相互依赖

**使用并行（本教程）的场景：**
- issue 相互独立
- 已熟悉该工作流
- 想要最大化吞吐量

## 下一步

你已完成所有教程！你现在知道如何：
- ✅ 初始化 Agentize（教程 00）
- ✅ 规划 issue（教程 01）
- ✅ 实现功能（教程 02）
- ✅ 通过并行开发扩大规模（教程 03）

探索完整文档：
- `.claude/commands/*.md` - 所有可用命令
- `.claude/skills/*/SKILL.md` - skill 的工作原理
- `docs/milestone-workflow.md` - 深入了解里程碑
- `README.md` - 架构与理念
