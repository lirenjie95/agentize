# SDK 结构

本文档介绍使用 Agentize 框架的 SDK 项目的文件结构。

## SDK 文件结构

一个使用 Agentize 的典型 SDK 项目具有以下结构：

```
your-project/
├── .claude/                    # Claude Code 配置（目录，不是符号链接！）
│   ├── settings.json          # Claude Code 设置
│   ├── commands/              # 自定义 slash command
│   │   └── commit-msg/
│   ├── skills/                # Agent skill
│   │   ├── commit-msg/
│   │   └── open-issue/
│   └── hooks/                 # Git 与事件钩子
├── .git/hooks/
│   └── pre-commit             # 指向 scripts/pre-commit 的符号链接（可选）
├── CLAUDE.md                  # 面向 Claude 的项目专属指令
├── docs/
│   └── git-msg-tags.md        # Git 提交消息标签定义
├── scripts/
│   └── pre-commit             # Pre-commit 钩子脚本
├── src/                       # 源代码
├── tests/                     # 测试文件
└── [语言相关文件]              # Makefile、CMakeLists.txt、setup.sh 等
```

### 重要：`.claude/` 目录结构

**在 agentize 项目本身中：**
- `.claude/` 是包含所有 agent 规则、skill 和 command 的**规范目录**
- 它是开发的单一事实来源

**在 SDK 项目中：**
- `.claude/` 是一个**独立目录**（从 agentize 的 `.claude/` 复制而来）
- 这使 SDK 项目独立自足
- 修改 SDK 不会影响 agentize 仓库

这是一个关键的架构差异，它使得：
1. **Agentize 开发**：对 `.claude/` 的修改定义了框架
2. **SDK 独立性**：每个 SDK 项目都有自己可定制的配置

## 设置

设置一个 SDK 项目：

1. **复制 `.claude/` 目录**，从 Agentize 安装中复制：
   ```bash
   cp -r $AGENTIZE_HOME/.claude /path/to/your/project/
   ```

2. **复制文档模板**（可选）：
   ```bash
   cp $AGENTIZE_HOME/docs/git-msg-tags.md /path/to/your/project/docs/
   ```

3. **复制 pre-commit 钩子**（可选）：
   ```bash
   cp $AGENTIZE_HOME/scripts/pre-commit /path/to/your/project/scripts/
   ln -s ../../scripts/pre-commit /path/to/your/project/.git/hooks/pre-commit
   ```

或者，将 Agentize 作为 Claude Code 插件使用：
```bash
claude --plugin-dir /path/to/agentize/.claude-plugin
```

## 会创建什么

1. **Claude Code 配置**（`.claude/`）
   - 用于 git 操作的 skill
   - 用于开发工作流的 command
   - 设置与钩子

2. **文档**（可选）
   - `CLAUDE.md` - 项目专属指令
   - `docs/git-msg-tags.md` - 提交消息标签定义

3. **Pre-commit 钩子**（可选）
   - `scripts/pre-commit` - 钩子脚本
   - `.git/hooks/pre-commit` - 指向钩子脚本的符号链接

## 常见工作流

### 设置一个新的 SDK

```bash
# 1. 创建项目目录
mkdir ~/projects/mylib
cd ~/projects/mylib
git init

# 2. 复制 SDK 配置
cp -r $AGENTIZE_HOME/.claude .

# 3. 开始使用 Claude Code
claude
```

### 更新 SDK 配置

```bash
# 当 agentize 发布新 skill 或更新时
cd /path/to/agentize
git pull origin main

# 更新你的 SDK 项目
cp -r $AGENTIZE_HOME/.claude /path/to/your/project/

# 检查变更
git diff .claude/
```

## 最佳实践

1. **保持 CLAUDE.md 的定制**
   - 在此记录项目专属的上下文
   - 这个文件指导 Claude 在你项目中的行为

2. **使用版本控制**
   - 将你的 SDK 项目提交到 git
   - 跟踪 `.claude/` 配置的变更
   - 需要时易于回退

3. **定制 git 提交标签**
   - 为你的项目编辑 `docs/git-msg-tags.md`
   - 定义项目专属的标签类别
