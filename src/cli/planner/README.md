# planner CLI 模块映射

## 目的

`lol plan` 使用的内部流水线模块；独立的 `planner` 命令已被移除。

## 内容

```
planner.sh           - 加载器：确定脚本目录，source 各模块
planner/pipeline.sh  - 将 `lol plan` 输入转发给 Python 后端的薄适配器
planner/forge.sh     - 面向 GitHub/GitLab 的 forge 无关 issue 辅助函数
```

## 加载顺序

1. `pipeline.sh` - 定义 `_planner_run_pipeline()` 适配器
2. `github.sh` - 旧版 GH 辅助函数（适配器不调用）

## 相关文档

- [src/cli/planner.md](../planner.md) - 接口文档
- [docs/cli/planner.md](../../../docs/cli/planner.md) - 面向用户的流水线参考
