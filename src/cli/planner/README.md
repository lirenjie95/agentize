# planner CLI Module Map

## Purpose

Internal pipeline module used by `lol plan`; the standalone `planner` command has been removed.

## Contents

```
planner.sh           - Loader: determines script dir, sources modules
planner/pipeline.sh  - Thin adapter that forwards `lol plan` inputs to the Python backend
planner/forge.sh     - Forge-agnostic issue helpers for GitHub/GitLab
```

## Load Order

1. `pipeline.sh` - Defines `_planner_run_pipeline()` adapter
2. `github.sh` - Legacy GH helpers (not invoked by the adapter)

## Related Documentation

- [src/cli/planner.md](../planner.md) - Interface documentation
- [docs/cli/planner.md](../../../docs/cli/planner.md) - User-facing pipeline reference
