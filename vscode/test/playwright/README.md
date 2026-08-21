# Playwright 软性测试

本文件夹包含基于 Playwright 的 VS Code webview 软性 UI 流程脚本。

## 组织结构

- `test-session-append.js`：模拟 Plan -> Refine 追加流程，并将确定性截图输出到 worktree 的 `.tmp`。
- `test-session-append.md`：记录脚本行为、流程契约和运行时前置条件。

## 范围

这些脚本用于带截图产物和软性检查的视觉行为验证。
它们有意避免严格的像素断言，以便人工检查 UI 意图。
