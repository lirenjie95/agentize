# 开发者服务器与 Telegram Bot 集成

在本教程中，我们将指导你启动开发服务器并将其与 Telegram bot 连接。
由于服务器以完全无头（headless）的方式启动 Claude Code 开发会话，[Telegram](https://telegram.org/) bot 可以帮助
你在设备上与会话交互，以批准权限和查看进度。


## 前置条件 1：配置 Viewboard

使用 `\setup-viewboard` 命令为你的仓库配置基于 GitHub Project v2 的 viewboard。
关于如何在本地命令行和 GitHub 上配置项目的更多细节，
请查看 [项目配置](./04a-project.md)。

## 前置条件 2：创建 Telegram Bot

在此之前，你是否已下载并注册了 Telegram？
如果没有，请前往 [Telegram](https://telegram.org/) 创建账号。

接下来，按照以下步骤创建一个 Telegram bot 来接收来自开发服务器的消息：

1. 打开 Telegram 并搜索 `@BotFather` 来创建新 bot。
   - 与 BotFather 开始对话并发送命令 `/newbot`。
   - 按照提示为你的 bot 设置名称和用户名。
   - 创建完成后，BotFather 会为你提供 bot token。请妥善保存该 token。`YOUR_BOT_TOKEN`
2. 找到你的 Telegram 用户 ID：
   - 在 Telegram 上搜索 `@idbot`。
   - 使用 `/getid` 命令获取你的用户 ID，应为 8 位数字。请妥善保存该 ID。`YOUR_USER_ID`
3. 在 `.agentize.local.yaml`（或用于用户级配置的 `$HOME/.agentize.local.yaml`）中配置 Telegram 凭据：

```yaml
telegram:
  enabled: true
  token: "YOUR_BOT_TOKEN"
  chat_id: "YOUR_USER_ID"
```

4. 使用 `lol serve` 子命令启动本地轮询服务器

```bash
lol serve --period=2m --num-workers=5
```

该命令将启动一个本地服务器，每 2 分钟轮询一次你的 issue 看板，并将更新
发送到你的 Telegram bot。

一旦出现以下情况：
- 带有 `agentize:plan` 标签且项目状态为 `Plan Accepted` 的 issue，将启动一个新的开发会话。
- 带有 `agentize:dev-req` 标签的 issue 会触发 `/ultra-planner --refine`（当前服务器行为见 `docs/cli/lol.md`）。
- 状态为不可合并的 PR，将启动一个 `/sync-master` 会话，将 PR 分支 rebase 到 master 上。
- 尚未确定的权限，一条权限请求消息将发送到你的 Telegram bot，供你点击按钮批准或拒绝。
