# Doc-Architect Skill

分析功能实现计划，并生成覆盖设计文档、文件夹 README 和接口文档的全面文档清单。

## 用途

确保在规划阶段系统地识别文档影响，避免文档债务，并确保所有必需的文档在实现过程中被创建/更新。

## 用法

```
/doc-architect
```

该 skill 从对话上下文中分析当前功能需求，并产出 Documentation Planning 章节。

## 输出格式

```markdown
## Documentation Planning

### High-level design docs (docs/)
- `docs/workflows/feature-name.md` — create/update workflow documentation
- `docs/tutorial/XX-feature-name.md` — create/update tutorial with new feature

### Folder READMEs
- `path/to/module/README.md` — update purpose and organization

### Interface docs
- `src/module/component.md` — update interface documentation
```

## 集成

该 skill 设计为在规划工作流（例如 `/ultra-planner`、`/make-a-plan`）中被调用，产出包含在共识计划中的 Documentation Planning 章节。`/issue-to-impl` 工作流在第 5 步（文档更新）中消费该章节。
