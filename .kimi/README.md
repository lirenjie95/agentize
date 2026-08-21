# `.kimi/` — Kimi Code CLI 项目配置

本目录为 [Kimi Code CLI](https://moonshotai.github.io/kimi-cli/) 提供项目级配置。

## 目录结构

- `skills` → 符号链接到 `../.claude-plugin/skills`：`.claude-plugin/` 是本项目所有 agent 行为文件的唯一事实来源（single source of truth），Kimi Code CLI 通过该软链加载全部项目级 skills，与其他 CLI 保持一致。

## 说明

- Kimi Code CLI 的项目级 skills 按 `.kimi/skills/`、`.claude/skills/`、`.codex/skills/` 的优先级发现并合并；根目录的 `AGENTS.md` 也会被自动读取，因此无需在本目录重复维护。
- 如需新增或修改 skill，请直接编辑 `.claude-plugin/skills/`，不要在本目录单独维护副本。
