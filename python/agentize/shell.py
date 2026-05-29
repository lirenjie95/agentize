"""Utilities for invoking shell functions from Python."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


def _find_bash() -> str:
    """Locate bash executable, with Windows-aware discovery."""
    if sys.platform == "win32":
        # Common Git for Windows install locations
        candidates = [
            r"C:\Program Files\Git\bin\bash.exe",
            r"C:\Program Files (x86)\Git\bin\bash.exe",
            os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Programs\Git\bin\bash.exe"),
            os.path.join(os.environ.get("USERPROFILE", ""), r"scoop\apps\git\current\bin\bash.exe"),
            r"C:\ProgramData\chocolatey\bin\bash.exe",
        ]
        for candidate in candidates:
            if os.path.isfile(candidate):
                return candidate
        # Also check PATH
        found = shutil.which("bash")
        if found:
            return found
    return "bash"


def _normalize_path(path: str | Path) -> str:
    """Normalize path separators for bash on Windows."""
    s = str(path)
    if sys.platform == "win32":
        s = s.replace("\\", "/")
    return s


def get_agentize_home() -> str:
    """Get AGENTIZE_HOME from environment or derive from repo root."""
    if "AGENTIZE_HOME" in os.environ:
        return os.environ["AGENTIZE_HOME"]

    # Try to derive from this file's location
    # shell.py is at python/agentize/shell.py, so repo root is ../../..
    shell_path = Path(__file__).resolve()
    repo_root = shell_path.parent.parent.parent
    if (repo_root / "Makefile").exists() and (repo_root / "src" / "cli" / "lol.sh").exists():
        return str(repo_root)

    raise RuntimeError(
        "AGENTIZE_HOME not set and could not be derived.\n"
        "Please set AGENTIZE_HOME to point to your agentize repository."
    )


def resolve_repo_root() -> Path:
    """Resolve repo root using AGENTIZE_HOME semantics or git rev-parse fallback."""

    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        root = result.stdout.strip()
        if root:
            return Path(root)

    raise RuntimeError(
        "Could not determine repo root. Please run inside a git repo."
    )


def run_shell_function(
    cmd: str,
    *,
    capture_output: bool = False,
    agentize_home: Optional[str] = None,
    cwd: str | Path | None = None,
    overrides_path: str | Path | None = None,
) -> subprocess.CompletedProcess:
    """Run a shell function with AGENTIZE_HOME set.

    Args:
        cmd: The shell command to run (e.g., "wt spawn 123", "_lol_cmd_version")
        capture_output: Whether to capture stdout/stderr
        agentize_home: Override AGENTIZE_HOME (defaults to auto-detection)

    Returns:
        CompletedProcess with result
    """
    home = agentize_home or get_agentize_home()
    env = os.environ.copy()
    env["AGENTIZE_HOME"] = home

    override_candidate = overrides_path or os.environ.get("AGENTIZE_SHELL_OVERRIDES")
    override_path = None
    if override_candidate:
        override_path = Path(override_candidate).expanduser()
        if not override_path.exists():
            override_path = None

    cmd_parts = []
    setup_path = Path(home) / "setup.sh"
    if setup_path.exists():
        cmd_parts.append(f'source "{_normalize_path(setup_path)}"')
    if override_path:
        cmd_parts.append(f'source "{_normalize_path(override_path)}"')
    cmd_parts.append(cmd)
    full_cmd = " && ".join(cmd_parts)

    bash_bin = _find_bash()
    return subprocess.run(
        [bash_bin, "-c", full_cmd],
        env=env,
        capture_output=capture_output,
        text=True,
        cwd=_normalize_path(cwd) if cwd else None,
    )
