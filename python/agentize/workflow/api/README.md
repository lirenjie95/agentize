# Workflow API 包

用于构建命令式 agent 流水线的公共工作流 API。本包公开了 Session DSL，以及用于 ACW 调用、提示词渲染、GitHub 自动化和路径解析的共享辅助函数。

## 组织

- `__init__.py` - 公共 API 符号的便捷再导出
- `session.py` - 用于运行分阶段工作流（单个和并行）的 Session DSL
- `acw.py` - 带计时日志和 provider 校验的 ACW 调用辅助函数
- `gh.py` - 用于 issue/标签/PR 操作的 GitHub CLI 封装
- `prompt.py` - `{#TOKEN#}` 和 `{{TOKEN}}` 占位符的提示词渲染
- `path.py` - 相对于模块文件的路径解析辅助函数
- 配套的 `.md` 文件记录了接口和内部辅助函数
