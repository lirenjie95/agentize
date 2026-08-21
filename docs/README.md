# 文档目录

本目录包含 Agentize 框架的所有面向用户和开发者的文档。

## 组织结构

### 用户教程（顺序学习路径）

总共 15 分钟逐步学习 Agentize（每篇教程 3-5 分钟）：

完整教程系列见 [`tutorial/README.md`](tutorial/README.md)：
- `tutorial/00-cli-quickstart.md` - 从配置到实现的 CLI 工作流（推荐）
- `tutorial/00a-claude-ui-setup.md` - 用于 slash command 的 Claude UI 设置
- `tutorial/01-ultra-planner.md` - 主要的规划教程
- `tutorial/02-issue-to-impl.md` - 完整的开发周期
- `tutorial/03-advanced-usage.md` - 并行开发工作流
- `tutorial/04-project.md` - 使用 PAT 的项目看板自动化

### CLI 参考

Agentize 工具的命令行接口文档：
- `cli/acw.md` - `acw` agent CLI 封装接口
- `cli/lol.md` - `lol` 命令接口与选项
- `cli/planner.md` - `lol plan` 使用的 planner 管线模块
- `cli/wt.md` - `wt` 命令接口与选项

### 架构文档

系统设计与内部架构：
- `architecture/sdk.md` - SDK 生成与模板系统
- `architecture/metadata.md` - 元数据管理与结构
- `architecture/cross-platform.md` - 跨平台兼容性设计（Windows 10 / Ubuntu 22.04）

### 工作流

详细的工作流图与流程文档：

所有工作流图见 [`feat/README.md`](feat/README.md)：
- `feat/core/milestone.md` - 基于里程碑的实现工作流
- `feat/core/ultra-planner.md` - 基于多 agent 辩论的规划
- `feat/core/issue-to-impl.md` - 完整的开发周期
- `feat/core/handsoff.md` - Handsoff 模式自动续接

### 测试文档

测试框架、验证与 agent 测试：
- `test/workflow.md` - 测试框架与验证
- `test/agents.md` - Agent 测试文档
- `test/code-review-agent.md` - 代码评审 agent 测试

### 组件参考

- `agents.md` - Agent 定义与配置
- `commands.md` - Command 快捷方式与工作流
- `skills.md` - 可复用的 skill 定义

### 参考文档

- `envvar.md` - 环境变量参考
- `git-msg-tags.md` - Git 提交消息标签标准

## 入门指南

刚接触 Agentize？按顺序从教程系列开始：

1. 教程 00：CLI 快速上手
2. 教程 00a：Claude UI 设置（UI 用户可选）
3. 教程 01：学习规划功能
4. 教程 02：实现你的第一个 issue
5. 教程 03：通过并行开发扩展规模
6. 教程 04：配置项目自动化

## 维护说明

添加或移动文档文件时，请更新本索引以保持引用准确。
