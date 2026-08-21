# Sandbox

agentize SDK 的开发环境容器，带有基于 tmux 的会话管理。

## 目的

本目录包含用于以下用途的 Docker/Podman sandbox 环境：
- 在带有持久 tmux 会话的隔离容器中运行 Claude/CCR
- 需要隔离依赖的开发工作流
- CI/CD 流水线验证

## 内容

- `Dockerfile` - 包含所有必需工具的容器镜像定义
- `install.sh` - Claude Code 安装脚本
- `entrypoint.sh` - 支持 tmux 会话的容器入口
- `run.py` - 基于 Python 的 sandbox 管理器

## 快速开始

```bash
# 创建新 sandbox（首次运行时自动构建镜像）
uv run sandbox/run.py --repo_base /path/to/repo new -n my-sandbox

# 以 CCR（claude code router）模式创建 sandbox
uv run sandbox/run.py --repo_base /path/to/repo new -n my-sandbox --ccr

# 附加到 sandbox
uv run sandbox/run.py --repo_base /path/to/repo attach -n my-sandbox

# 列出所有 sandbox
uv run sandbox/run.py --repo_base /path/to/repo ls

# 删除一个 sandbox
uv run sandbox/run.py --repo_base /path/to/repo rm -n my-sandbox
```

## CLI 接口

```
run.py --repo_base <base_path> <subcommand> [options]
```

### 子命令

| 命令 | 描述 |
|---------|-------------|
| `new -n <name> [--ccr] [-b <branch>]` | 创建新的 worktree + 容器 |
| `ls` | 列出所有 sandbox |
| `rm -n <name>` | 删除 sandbox |
| `attach -n <name>` | 附加到 tmux 会话 |
| `reset` | 移除所有 sandbox 并重置状态 |

## 容器运行时

同时支持 Docker 和 Podman。检测顺序：

1. 本地配置：`sandbox/agentize.toml` 或 `./agentize.toml`
2. 全局配置：`~/.config/agentize/agentize.toml`
3. `CONTAINER_RUNTIME` 环境变量
4. 自动检测：优先 Podman，回退到 Docker

### 配置文件格式

```toml
[container]
runtime = "podman"  # 或 "docker"
```

## 自动构建

镜像在需要时自动构建：
- 镜像不存在时的首次运行
- 当 `Dockerfile`、`install.sh` 或 `entrypoint.sh` 发生变化时
- 使用 `--build` 标志强制重建

## 卷挂载

自动挂载：
- `~/.claude-code-router/config.json` → CCR 配置（只读）
- `~/.config/gh/` → GitHub CLI 配置（只读）
- `~/.git-credentials` → Git 凭据（只读）
- `~/.gitconfig` → Git 配置（只读）
- Worktree 目录 → `/workspace`（读写）
- `GITHUB_TOKEN` 环境变量（如已设置）

## 已安装工具

- Node.js 20.x LTS
- Python 3.12 与 uv
- Claude Code 与 claude-code-router
- Playwright 与 Chromium
- GitHub CLI
- tmux
- Git、curl、wget、vim、jq

## FACT 实验室设置

对于 FACT 实验室机器（例如 mantis）上的用户，你需要为网络文件系统兼容性配置 Podman。

创建 `~/.config/containers/storage.conf`：

```toml
[storage]
driver = "overlay"

[storage.options.overlay]
force_mask = "700"
# 在网络文件系统上使用 fuse-overlayfs 以获得更好的稳定性
mount_program = "/usr/bin/fuse-overlayfs"
```

创建 `~/.config/containers/containers.conf`：

```toml
[engine]
# 禁用 healthcheck 计时器——锁竞争的主要原因
healthcheck_events = false

# 减少并发操作
parallel_pull = 1

# 增加锁等待超时
image_copy_tmp_dir = "/tmp"

[containers]
# 默认禁用容器 healthcheck
init = true
```

如果这仍然不起作用，你的用户名可能未被加入 fakeroot 列表。请联系管理员将你添加到 fakeroot 列表。
