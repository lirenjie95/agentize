# Agentize Server 模块

用于 GitHub Projects v2 自动化的轮询服务器。

## 用途

本模块实现了一个长时间运行的服务器，它会：
1. 发送 Telegram 启动通知（如已配置）
2. 使用 `gh issue list --label agentize:plan --state open` 发现候选 issue
3. 通过 GraphQL 检查每个 issue 的项目状态，以强制执行：
   - "Plan Accepted" 审批门禁（用于通过 `wt spawn` 进行实现）
   - "Proposed" + `agentize:refine` 标签（用于通过 `/ultra-planner --refine` 进行细化）
4. 使用 `gh issue list --label agentize:dev-req --state open` 发现功能请求 issue
5. 通过 `wt spawn` 为就绪的 issue 创建 worktree、触发细化流程，或通过 `/ultra-planner --from-issue` 运行功能请求规划
6. 通过 `gh pr list` 发现带有 `agentize:pr` 标签的冲突 PR，并自动 rebase 其 worktree
7. 发现存在未解决 review 线程的 PR（Status=`Proposed`），并启动 `/resolve-review` 来处理它们

## 模块布局

| 文件 | 用途 |
|------|---------|
| `__main__.py` | CLI 入口、轮询协调器和再导出中心 |
| `runtime_config.py` | `.agentize.local.yaml` 的运行时配置解析器 |
| `github.py` | 通过 `gh` CLI 和 GraphQL 查询进行 GitHub issue/PR 发现 |
| `workers.py` | 通过 `wt` CLI 进行 worktree 创建/rebase，以及 worker 状态文件管理 |
| `notify.py` | Telegram 消息格式化（启动、分配、完成） |
| `session.py` | 用于完成检测的会话状态文件查找 |
| `log.py` | 带有源码位置格式化的共享 `_log` 辅助函数 |

## 导入策略

所有公共函数都从 `__main__.py` 再导出：

```python
# 测试和外部代码应使用此模式：
from agentize.server.__main__ import read_worker_status

# 内部模块从具体文件导入：
from agentize.server.log import _log
from agentize.server.workers import spawn_worktree
```

此再导出策略保持了与现有从 `__main__` 导入的测试的向后兼容性。

## 模块依赖

```
__main__.py
    ├── github.py
    │       └── log.py
    ├── workers.py
    │       └── log.py
    ├── notify.py
    │       └── log.py
    └── session.py
```

叶子模块 `log.py` 没有内部依赖，以避免导入循环。

## 用法

```bash
# 通过 lol CLI（推荐）
lol serve --period=5m --num-workers=5

# 直接 Python 调用
python -m agentize.server --period=5m --num-workers=5
```

Telegram 凭据从 `.agentize.local.yaml` 加载。服务器按以下顺序搜索该文件：项目根目录 → `$AGENTIZE_HOME` → `$HOME`。

## 配置

从 `.agentize.yaml` 读取项目关联：
```yaml
project:
  org: <organization>
  id: <project-number>
```

### 运行时配置

服务器专属设置使用 `.agentize.local.yaml`（已被 git 忽略）：

```yaml
server:
  period: 5m
  num_workers: 5

telegram:
  token: "your-bot-token"
  chat_id: "your-chat-id"

workflows:
  impl:
    model: opus
  refine:
    model: sonnet
  dev_req:
    model: sonnet
  rebase:
    model: haiku
```

**优先级：** `.agentize.local.yaml` > 默认值

**YAML 搜索顺序：**
1. 项目根目录 `.agentize.local.yaml`
2. `$AGENTIZE_HOME/.agentize.local.yaml`
3. `$HOME/.agentize.local.yaml`（用户级，由安装程序创建）

详情请参阅[服务器运行时配置](../../../docs/feat/server.md#runtime-configuration)。

## 调试日志

在 `.agentize.local.yaml` 中设置 `handsoff.debug: true` 可启用 issue 过滤决策的详细日志。调试消息使用诸如 `[pr-rebase]` 的前缀来表示 PR 冲突处理。输出格式和示例请参阅 [docs/feat/server.md](../../../docs/feat/server.md#issue-filtering-debug-logs)。
