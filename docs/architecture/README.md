# 架构文档

本目录包含关于 Agentize 内部架构与设计的文档。

## 目的

这些文档解释 Agentize 核心系统的工作方式、设计决策和实现细节。它们是理解代码库结构和扩展框架的参考资料。

## 文件

### sdk.md
SDK 结构文档。介绍使用 Agentize 框架的 SDK 项目的文件结构、`.claude/` 目录组织以及设置工作流。

### metadata.md
项目元数据文件（`.agentize.yaml`）规范。介绍配置模式、字段定义、`wt` 和 `lol` 命令的使用方式，以及元数据如何驱动项目行为。

### handsoff.md
Handsoff 模式文档。介绍工作流的自动续接机制、环境变量（`HANDSOFF_MODE`、`HANDSOFF_AUTO_PERMISSION`）以及支持的工作流（`ultra-planner`、`issue-to-impl`、`plan-to-issue`）。

### cross-platform.md
跨平台兼容性设计文档（中文）。介绍 Agentize 如何在 Windows 10（Git Bash）和 Ubuntu 22.04（CI 基准环境）上实现兼容，以及背后的设计取舍。

## 集成

架构文档被以下位置引用：
- 主 [README.md](../README.md) 的“架构文档”一节
- [docs/tutorial/](../tutorial/) 中的教程系列
- 依赖这些系统的命令实现

## 用途

这些文档主要面向：
- 希望理解代码库的贡献者
- 希望用自定义模板或集成扩展 Agentize 的用户
- 调试 SDK 初始化或元数据问题的开发者
