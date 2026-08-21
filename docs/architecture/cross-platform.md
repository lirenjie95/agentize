# 跨平台兼容性设计（Windows 10 / Ubuntu 22.04）

本文档说明 Agentize 如何在 Windows 10 和 Ubuntu 22.04 上实现兼容，以及背后的设计取舍。

## 设计原则

Agentize 的主体是 shell 脚本（`wt`、`lol`、`acw` 等 CLI）加少量 Python 模块。跨平台策略的核心是：

1. **单一执行环境抽象**：所有 CLI 只面向 POSIX shell 编写一份实现。Windows 上不维护 PowerShell/CMD 版本，而是借助 Git for Windows 自带的 **Git Bash**（MSYS2/MinGW 环境）获得与 Linux/macOS 一致的 POSIX 层。
2. **Shell 中性（shell-neutral）**：脚本同时兼容 bash 和 zsh，并刻意避开 bash 4.0+ 才有的特性（关联数组、`declare -A`、`${!arr[@]}` 间接展开等），改用 case 分发、位置参数和 POSIX 兼容构造，从而也能在 macOS 自带的 bash 3.2 上运行。
3. **以 CI 环境锚定 Linux 行为**：用 Ubuntu 22.04 LTS 的标准工具链（GNU coreutils、bash 5.x）作为 Linux 侧的基准验证环境。

## Windows 10 支持

Windows 10 的支持全部建立在 Git Bash 之上，共四处机制：

### 1. 入口约定（README.md）

用户侧约定：安装 [Git for Windows](https://git-scm.com/download/win)，在 Git Bash 中执行 `pacman -S make`，之后所有 Agentize 命令（`wt`、`lol`）都在 Git Bash 内运行。

### 2. 安装器平台检测（scripts/install）

依赖检查阶段通过环境变量识别 Windows 环境（`MSYSTEM`、`MINGW_PREFIX` 或 `OSTYPE=cygwin`），缺失 `git`/`make`/`bash` 时给出 `pacman -S <cmd>` 的安装指引，而不是 Linux 风格的提示。

### 3. Windows 感知的环境变量生成（Makefile）

`make setup` 生成 `setup.sh` 时同样检测 Windows 环境：`PYTHONPATH` 在 Windows Python 下用分号 `;` 分隔，其他平台用冒号 `:`。这是因为 Python 在 Windows 上按分号拆分 `PYTHONPATH`，而 bash 脚本本身运行在 Git Bash 中、其他地方仍遵循 POSIX 惯例——只在“传递给 Windows 原生 Python 解释器”这一边界上做适配。

### 4. Python 侧的 bash 发现与路径规整（python/agentize/shell.py）

Python 模块需要回调 shell 函数（如 `run_shell_function`），在 `sys.platform == "win32"` 时做两件事：

- `_find_bash()`：按常见 Git for Windows 安装位置依次查找 `bash.exe`（`C:\Program Files\Git\`、`C:\Program Files (x86)\Git\`、`%LOCALAPPDATA%\Programs\Git\`、Scoop、Chocolatey），最后回退到 `PATH` 查找。这样 Python 进程即使不是从 Git Bash 启动（例如由 IDE 唤起），也能找到 bash。
- `_normalize_path()`：把路径中的 `\` 转成 `/`，保证传给 bash 的路径可被 MSYS 环境识别。

### 设计理由

项目大量依赖 POSIX 工具链（git worktree、make、jq、curl）。Git Bash 以接近零的维护成本提供完整 POSIX 层，使 Windows 支持与 Linux 共用同一份脚本实现；需要特判的只有“Python ↔ shell 边界”上的两处（解释器定位、路径分隔符、环境变量分隔符）。

## Ubuntu 22.04 支持

Ubuntu 22.04 不是通过条件代码“适配”出来的，而是作为 **CI 基准环境** 保证的：

- **GitLab CI**（`.gitlab-ci.yml`）：`unit_tests` 任务使用 `ubuntu:22.04` 镜像，安装 `bash make git python3 python3-pip curl jq` 后运行 `TEST_SHELLS="bash" make test-fast`。另有一个 `shellcheck` 代码质量任务（允许失败）。
- **GitHub Actions**（`.github/workflows/test.yml`）：在 `ubuntu-latest` 上安装 zsh，运行 `TEST_SHELLS="bash zsh" make test-fast`，用 bash/zsh 双 shell 执行同一套测试，验证 shell 中性。

两条流水线都汇聚到同一个测试入口 `make test-fast`，保证脚本在 Ubuntu LTS 工具链下行为一致。

## 测试与验证机制

- **多 shell 测试**：`TEST_SHELLS="bash zsh" make test-fast`，同一测试用例在不同 shell 下重复执行。
- **Shell 中性审查**：`shell-script-review` skill 提供 bash/zsh 兼容的审查规则（见 `src/cli/acw.md` 的 “Bash 3.2 Compatibility” 一节中列举的规避项）。
- **已知盲区**：Windows 侧目前没有 CI 覆盖，依赖 Git Bash 环境下的本地验证；Ubuntu 22.04 之外的环境（如 macOS、其他发行版）依靠 POSIX/shell 中性原则间接覆盖。

## 相关说明

- `sandbox/` 提供与宿主机隔离的沙箱环境，其基础镜像为 `ubuntu:24.04`，与宿主机的 Ubuntu 22.04 兼容性是两个独立层面：前者面向被评测/被执行的工作负载，后者面向 Agentize 自身脚本的运行环境。
- 安装与使用的 Windows 操作步骤详见 `docs/feat/cli/install.md` 的 “Windows Installation” 一节。
