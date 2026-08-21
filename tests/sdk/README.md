# SDK 模板测试

## 目的

本目录之前包含 SDK 模板生成的单元测试。SDK 模板测试已随 `lol apply` 命令一同移除。

## 历史背景

SDK 模板测试曾验证：
- C、C++ 和 Python 项目模板生成
- 正确的项目结构和构建配置
- 文件生成和替换的正确性

## 当前状态

`lol apply --init` 和 `lol apply --update` 命令已被移除。SDK 项目现在通过直接从 Agentize 安装目录复制 `.claude/` 目录来设置。

当前 SDK 设置工作流请参见 [docs/architecture/sdk.md](../../docs/architecture/sdk.md)。

## 相关文档

- [templates/](../../templates/) - SDK 模板源文件（供参考）
- [docs/architecture/sdk.md](../../docs/architecture/sdk.md) - SDK 结构文档
- [tests/README.md](../README.md) - 测试套件概览
