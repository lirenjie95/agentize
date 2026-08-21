# Settings UI（VS Code）

VS Code 扩展中的 Settings 标签页提供了一种轻量方式，
让你无需离开编辑器即可配置 Agentize 后端默认值。

## 目标

- 让后端配置对扩展的新用户易于发现。
- 将项目元数据与开发者个人设置分离。
- 让 UX 聚焦于 CLI 所期望的 `provider:model` 配对。

## 范围与文件

UI 镜像了现有的配置层级：

- `.agentize.yaml` 以**只读**方式显示为项目元数据。
- `.agentize.local.yaml`（仓库级）存储当前项目的开发者个人设置。
- `~/.agentize.local.yaml`（全局）存储跨仓库使用的用户级默认值。

只有 `planner.backend` 会在 Settings UI 中直接编辑。所有其他 YAML 键
保持不变。

## 后端格式

后端以 `provider:model` 字符串的形式存储。UI 将 provider 限制在
常用列表（`claude`、`openai`、`codex`、`cursor`、`kimi`）内，而 model
字段保持自由格式，以支持新发布的模型而无需更新 UI。

## 工作流

1. 打开 Agentize Activity Bar 视图中的 Settings 标签页。
2. 为仓库级或全局范围选择 provider 和 model。
3. 保存以将 `planner.backend` 写入所选的 `.agentize.local.yaml` 文件。
4. 规划运行从 YAML 读取后端；实现运行在可用时复用相同的值作为
   `lol impl --backend`。

## 数据流

- webview 向扩展宿主请求设置快照。
- 扩展直接读取 YAML 文件（不做 AST 解析）并提取 `planner.backend`。
- 保存操作会更新或插入 `planner.backend` 键，同时保留其他内容。

## 限制

- 如果围绕 `planner.backend` 重写文件，YAML 注释可能会丢失。
- UI 不会可视化继承关系；每个范围显示其各自文件的内容。
