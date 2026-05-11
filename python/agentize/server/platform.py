"""Platform detection and forge-agnostic utilities for GitHub/GitLab support."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Optional


# Well-known forge hostnames
_GITHUB_HOSTS = {"github.com"}
_GITLAB_HOSTS = {"gitlab.com", "gitlab.io"}


def detect_platform(remote_url: str) -> str:
    """Detect forge platform from a git remote URL.

    Args:
        remote_url: Git remote URL (HTTPS or SSH).

    Returns:
        "github" or "gitlab".
    """
    host = get_host(remote_url)
    if host in _GITHUB_HOSTS:
        return "github"
    # Any hostname containing "gitlab" is treated as GitLab (covers self-hosted)
    if host and "gitlab" in host.lower():
        return "gitlab"
    # Default fallback based on common patterns
    if host and "github" in host.lower():
        return "github"
    # Heuristic: SSH git@host:path — if host contains gitlab → gitlab
    if remote_url.startswith("git@"):
        host_part = remote_url.split(":", 1)[0].split("@")[-1]
        if "gitlab" in host_part.lower():
            return "gitlab"
        if "github" in host_part.lower():
            return "github"
    return "github"


def get_host(remote_url: str) -> Optional[str]:
    """Extract hostname from a git remote URL.

    Args:
        remote_url: Git remote URL (HTTPS or SSH).

    Returns:
        Hostname string or None if unrecognised.
    """
    if not remote_url:
        return None

    # SSH format: git@host:path
    if remote_url.startswith("git@"):
        host_part = remote_url.split(":", 1)[0].split("@")[-1]
        return host_part

    # HTTPS format: https://host/path
    m = re.match(r"https?://([^/]+)/", remote_url)
    if m:
        return m.group(1)

    return None


def parse_repo_slug(remote_url: str) -> tuple[str, str]:
    """Parse owner and repo name from a git remote URL.

    Supports any git forge host (GitHub, GitLab, self-hosted).

    Args:
        remote_url: Git remote URL (HTTPS or SSH).

    Returns:
        Tuple of (owner, repo).

    Raises:
        RuntimeError: If the URL format is not recognised.
    """
    if not remote_url:
        raise RuntimeError("Empty remote URL")

    path: str | None = None

    # SSH format: git@host:owner/repo.git
    if remote_url.startswith("git@"):
        path = remote_url.split(":", 1)[1]
    else:
        # HTTPS format: https://host/owner/repo.git
        # Match everything after the hostname
        m = re.match(r"https?://[^/]+/(.+)$", remote_url)
        if m:
            path = m.group(1)

    if not path:
        raise RuntimeError(f"Unrecognised git remote format: {remote_url}")

    # Remove .git suffix and trailing slash
    path = path.rstrip("/")
    if path.endswith(".git"):
        path = path[:-4]

    parts = path.split("/")
    if len(parts) >= 2:
        return parts[0], parts[1]

    raise RuntimeError(f"Cannot parse owner/repo from: {remote_url}")


def build_issue_url(
    owner: str,
    repo: str,
    issue_no: int,
    platform: str = "github",
    host: Optional[str] = None,
) -> str:
    """Build a web URL for an issue."""
    if platform == "gitlab":
        base = host or "gitlab.com"
        return f"https://{base}/{owner}/{repo}/issues/{issue_no}"
    # GitHub default
    return f"https://github.com/{owner}/{repo}/issues/{issue_no}"


def build_mr_url(
    owner: str,
    repo: str,
    mr_no: int,
    platform: str = "github",
    host: Optional[str] = None,
) -> str:
    """Build a web URL for a PR/MR."""
    if platform == "gitlab":
        base = host or "gitlab.com"
        return f"https://{base}/{owner}/{repo}/merge_requests/{mr_no}"
    # GitHub default
    return f"https://github.com/{owner}/{repo}/pull/{mr_no}"


def load_project_config() -> dict:
    """Load project config from .agentize.yaml with platform awareness.

    Returns:
        Dict with keys: org, id, name, lang, platform, host, remote_url.
    """
    yaml_path = Path(".agentize.yaml")
    if not yaml_path.exists():
        current = Path.cwd()
        while current != current.parent:
            yaml_path = current / ".agentize.yaml"
            if yaml_path.exists():
                break
            current = current.parent
        else:
            raise FileNotFoundError(".agentize.yaml not found")

    config: dict[str, str | int | None] = {
        "org": None,
        "id": None,
        "name": None,
        "lang": None,
        "platform": None,
        "host": None,
        "remote_url": None,
    }

    with open(yaml_path) as f:
        in_project = False
        for line in f:
            stripped = line.rstrip("\n")
            # Detect project: section
            if stripped.startswith("project:"):
                in_project = True
                continue
            if in_project and not stripped.startswith(" ") and stripped:
                in_project = False

            if not in_project:
                continue

            # Parse key: value under project:
            if ":" in stripped:
                key, val = stripped.strip().split(":", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key in config:
                    if key == "id":
                        try:
                            config[key] = int(val)
                        except ValueError:
                            config[key] = val
                    else:
                        config[key] = val if val else None

        # Parse top-level git: remote_url
        if "remote_url:" in stripped:
            _, val = stripped.split(":", 1)
            val = val.strip().strip('"').strip("'")
            config["remote_url"] = val if val else None

    # Fallback remote_url from git origin
    if config.get("remote_url") is None:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            url = result.stdout.strip()
            if url:
                config["remote_url"] = url

    # Auto-detect platform if not configured
    remote_url = config.get("remote_url")
    if config.get("platform") is None and remote_url:
        config["platform"] = detect_platform(str(remote_url))

    # Auto-detect host if not configured
    if config.get("host") is None and remote_url:
        detected_host = get_host(str(remote_url))
        if detected_host:
            config["host"] = detected_host

    return config


def _get_platform() -> tuple[str, Optional[str]]:
    """Return (platform, host) from current config or auto-detection."""
    try:
        cfg = load_project_config()
        return str(cfg.get("platform") or "github"), cfg.get("host")
    except Exception:
        return "github", None


def get_forge_cli(platform: str | None = None) -> str:
    """Return the CLI command name for the given platform."""
    if platform == "gitlab":
        return "glab"
    return "gh"
