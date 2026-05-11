"""Forge-agnostic CLI helpers for GitHub (gh) and GitLab (glab)."""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Iterable

from agentize.server.platform import _get_platform, detect_platform, get_host, load_project_config


def _resolve_overrides() -> Path | None:
    overrides_path = os.environ.get("AGENTIZE_SHELL_OVERRIDES")
    if not overrides_path:
        return None
    candidate = Path(overrides_path).expanduser()
    if not candidate.exists():
        return None
    return candidate


def _shell_command(parts: Iterable[str]) -> str:
    return " ".join(shlex.quote(str(part)) for part in parts)


def _forge_cmd(platform: str | None = None) -> str:
    """Return the CLI binary name for the current platform."""
    if platform is None:
        platform, _ = _get_platform()
    return "glab" if platform == "gitlab" else "gh"


def _forge_available(platform: str | None = None) -> bool:
    """Check if the forge CLI is available and authenticated."""
    cmd = _forge_cmd(platform)
    overrides = _resolve_overrides()
    if overrides is None and shutil.which(cmd) is None:
        return False
    if overrides is not None:
        check_cmd = _shell_command([cmd, "auth", "status"])
        result = subprocess.run(
            ["bash", "-c", f"source {shlex.quote(str(overrides))} && {check_cmd}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0
    result = subprocess.run(
        [cmd, "auth", "status"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def _run_forge(
    args: Iterable[str],
    *,
    cwd: str | Path | None = None,
    platform: str | None = None,
) -> subprocess.CompletedProcess:
    cmd = _forge_cmd(platform)
    if not _forge_available(platform):
        raise RuntimeError(f"{cmd} CLI not available or not authenticated")
    overrides = _resolve_overrides()
    if overrides is not None:
        shell_cmd = _shell_command([cmd, *args])
        result = subprocess.run(
            ["bash", "-c", f"source {shlex.quote(str(overrides))} && {shell_cmd}"],
            capture_output=True,
            text=True,
            cwd=str(cwd) if cwd else None,
        )
    else:
        result = subprocess.run(
            [cmd, *args],
            capture_output=True,
            text=True,
            cwd=str(cwd) if cwd else None,
        )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        hint = detail if detail else f"exit code {result.returncode}"
        raise RuntimeError(f"{cmd} {' '.join(args)} failed ({hint})")
    return result


def _run_forge_with_status(
    args: Iterable[str],
    *,
    cwd: str | Path | None = None,
    capture_output: bool = True,
    platform: str | None = None,
) -> subprocess.CompletedProcess:
    cmd = _forge_cmd(platform)
    if not _forge_available(platform):
        raise RuntimeError(f"{cmd} CLI not available or not authenticated")
    overrides = _resolve_overrides()
    if overrides is not None:
        shell_cmd = _shell_command([cmd, *args])
        result = subprocess.run(
            ["bash", "-c", f"source {shlex.quote(str(overrides))} && {shell_cmd}"],
            capture_output=capture_output,
            text=True,
            cwd=str(cwd) if cwd else None,
        )
    else:
        result = subprocess.run(
            [cmd, *args],
            capture_output=capture_output,
            text=True,
            cwd=str(cwd) if cwd else None,
        )
    return result


def _body_args(body: str, platform: str | None = None) -> tuple[list[str], str | None]:
    if "\n" in body or "\r" in body:
        handle = tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8")
        handle.write(body)
        handle.close()
        if platform == "gitlab":
            return ["--description", body], None
        return ["--body-file", handle.name], handle.name
    if platform == "gitlab":
        return ["--description", body], None
    return ["--body", body], None


def _parse_issue_number(issue_url: str) -> str | None:
    match = re.search(r"([0-9]+)$", issue_url.strip())
    if not match:
        return None
    return match.group(1)


def _parse_mr_number(mr_url: str) -> str | None:
    match = re.search(r"/merge_requests/([0-9]+)", mr_url.strip())
    if match:
        return match.group(1)
    match = re.search(r"/pull/([0-9]+)", mr_url.strip())
    if match:
        return match.group(1)
    match = re.search(r"([0-9]+)$", mr_url.strip())
    if match:
        return match.group(1)
    return None


# ---------------------------------------------------------------------------
# Issue operations
# ---------------------------------------------------------------------------


def issue_create(
    title: str,
    body: str,
    labels: list[str] | None = None,
    *,
    cwd: str | Path | None = None,
    platform: str | None = None,
) -> tuple[str | None, str]:
    """Create an issue and return (number, url)."""
    plat = platform or _get_platform()[0]
    body_args, temp_body = _body_args(body, plat)
    args: list[str] = ["issue", "create", "--title", title]
    if plat == "gitlab":
        args = ["issue", "create", "--title", title, *body_args]
        if labels:
            for lbl in labels:
                args.extend(["--label", lbl])
    else:
        args = ["issue", "create", "--title", title, *body_args]
        if labels:
            args.extend(["--label", ",".join(labels)])
    try:
        result = _run_forge(args, cwd=cwd, platform=plat)
    finally:
        if temp_body:
            Path(temp_body).unlink(missing_ok=True)
    lines = [ln for ln in result.stdout.strip().splitlines() if ln.strip()]
    issue_url = lines[-1] if lines else ""
    if not issue_url:
        raise RuntimeError(f"{_forge_cmd(plat)} issue create returned no URL")
    return _parse_issue_number(issue_url), issue_url


def issue_view(
    issue_number: str | int,
    query: str | None = None,
    *,
    cwd: str | Path | None = None,
    platform: str | None = None,
) -> str:
    """View an issue.  If *query* is given it is a jq expression (GitHub only)."""
    plat = platform or _get_platform()[0]
    if plat == "gitlab":
        args = ["issue", "view", str(issue_number), "--output", "json"]
        result = _run_forge(args, cwd=cwd, platform=plat)
        if query:
            # glab does not support --jq; post-process with jq if available
            try:
                jq_result = subprocess.run(
                    ["jq", "-r", query],
                    input=result.stdout,
                    capture_output=True,
                    text=True,
                )
                if jq_result.returncode == 0:
                    return jq_result.stdout
            except FileNotFoundError:
                pass
            # Fallback: best-effort manual extraction for common queries
            return _glab_extract_json_field(result.stdout, query)
        return result.stdout
    # GitHub
    args = ["issue", "view", str(issue_number), "--json", "title,body,labels"]
    if query:
        args.extend(["-q", query])
    result = _run_forge(args, cwd=cwd, platform=plat)
    return result.stdout


def issue_body(issue_number: str | int, *, cwd: str | Path | None = None, platform: str | None = None) -> str:
    """Return the body text of an issue."""
    plat = platform or _get_platform()[0]
    if plat == "gitlab":
        result = _run_forge(
            ["issue", "view", str(issue_number), "--output", "json"],
            cwd=cwd,
            platform=plat,
        )
        return _glab_extract_json_field(result.stdout, ".description") or ""
    result = _run_forge(
        ["issue", "view", str(issue_number), "--json", "body", "-q", ".body"],
        cwd=cwd,
        platform=plat,
    )
    return result.stdout


def issue_url(
    issue_number: str | int, *, cwd: str | Path | None = None, platform: str | None = None
) -> str | None:
    """Return the web URL of an issue."""
    plat = platform or _get_platform()[0]
    if plat == "gitlab":
        result = _run_forge(
            ["issue", "view", str(issue_number), "--output", "json"],
            cwd=cwd,
            platform=plat,
        )
        return _glab_extract_json_field(result.stdout, ".web_url")
    result = _run_forge(
        ["issue", "view", str(issue_number), "--json", "url", "-q", ".url"],
        cwd=cwd,
        platform=plat,
    )
    url = result.stdout.strip()
    return url if url else None


def issue_edit(
    issue_number: str | int,
    *,
    title: str | None = None,
    body: str | None = None,
    body_file: str | Path | None = None,
    add_labels: list[str] | None = None,
    remove_labels: list[str] | None = None,
    cwd: str | Path | None = None,
    platform: str | None = None,
) -> None:
    """Edit an issue."""
    plat = platform or _get_platform()[0]
    if plat == "gitlab":
        args = ["issue", "update", str(issue_number)]
        if title:
            args.extend(["--title", title])
        if body is not None:
            args.extend(["--description", body])
        if body_file is not None:
            args.extend(["--description", Path(body_file).read_text()])
        if add_labels:
            args.extend(["--label", ",".join(add_labels)])
        _run_forge(args, cwd=cwd, platform=plat)
        if remove_labels:
            for lbl in remove_labels:
                _run_forge(
                    ["issue", "unlabel", str(issue_number), lbl],
                    cwd=cwd,
                    platform=plat,
                )
    else:
        args = ["issue", "edit", str(issue_number)]
        if title:
            args.extend(["--title", title])
        if body is not None:
            args.extend(["--body", body])
        if body_file is not None:
            args.extend(["--body-file", str(body_file)])
        if add_labels:
            args.extend(["--add-label", ",".join(add_labels)])
        if remove_labels:
            args.extend(["--remove-label", ",".join(remove_labels)])
        _run_forge(args, cwd=cwd, platform=plat)


# ---------------------------------------------------------------------------
# Label operations
# ---------------------------------------------------------------------------


def label_create(
    name: str,
    color: str,
    description: str = "",
    *,
    cwd: str | Path | None = None,
    platform: str | None = None,
) -> None:
    """Create a label (force if it already exists)."""
    plat = platform or _get_platform()[0]
    if plat == "gitlab":
        args = ["label", "create", name, "--color", color]
        if description:
            args.extend(["--description", description])
        _run_forge_with_status(args, cwd=cwd, platform=plat)
    else:
        args = ["label", "create", name, "--color", color, "--force"]
        if description:
            args.extend(["--description", description])
        _run_forge(args, cwd=cwd, platform=plat)


def label_add(
    issue_number: str | int,
    labels: list[str],
    *,
    cwd: str | Path | None = None,
    platform: str | None = None,
) -> None:
    """Add labels to an issue."""
    if not labels:
        return
    plat = platform or _get_platform()[0]
    if plat == "gitlab":
        _run_forge(
            ["issue", "update", str(issue_number), "--label", ",".join(labels)],
            cwd=cwd,
            platform=plat,
        )
    else:
        _run_forge(
            ["issue", "edit", str(issue_number), "--add-label", ",".join(labels)],
            cwd=cwd,
            platform=plat,
        )


def label_remove(
    issue_number: str | int,
    labels: list[str],
    *,
    cwd: str | Path | None = None,
    platform: str | None = None,
) -> None:
    """Remove labels from an issue."""
    if not labels:
        return
    plat = platform or _get_platform()[0]
    if plat == "gitlab":
        for lbl in labels:
            _run_forge_with_status(
                ["issue", "unlabel", str(issue_number), lbl],
                cwd=cwd,
                platform=plat,
            )
    else:
        _run_forge(
            ["issue", "edit", str(issue_number), "--remove-label", ",".join(labels)],
            cwd=cwd,
            platform=plat,
        )


# ---------------------------------------------------------------------------
# PR / MR operations
# ---------------------------------------------------------------------------


def pr_create(
    title: str,
    body: str,
    *,
    draft: bool = False,
    base: str | None = None,
    head: str | None = None,
    cwd: str | Path | None = None,
    platform: str | None = None,
) -> tuple[str | None, str]:
    """Create a PR/MR and return (number, url)."""
    plat = platform or _get_platform()[0]
    body_args, temp_body = _body_args(body, plat)
    if plat == "gitlab":
        args = ["mr", "create", "--title", title, *body_args]
        if draft:
            args.append("--draft")
        if base:
            args.extend(["--target-branch", base])
        if head:
            args.extend(["--source-branch", head])
    else:
        args = ["pr", "create", "--title", title, *body_args]
        if draft:
            args.append("--draft")
        if base:
            args.extend(["--base", base])
        if head:
            args.extend(["--head", head])
    try:
        result = _run_forge(args, cwd=cwd, platform=plat)
    finally:
        if temp_body:
            Path(temp_body).unlink(missing_ok=True)
    lines = [ln for ln in result.stdout.strip().splitlines() if ln.strip()]
    pr_url = lines[-1] if lines else ""
    if not pr_url:
        raise RuntimeError(f"{_forge_cmd(plat)} pr/mr create returned no URL")
    return _parse_mr_number(pr_url), pr_url


def pr_view(
    pr_number: str | int,
    fields: str = "mergeStateStatus,mergeable,url",
    *,
    cwd: str | Path | None = None,
    platform: str | None = None,
) -> dict[str, Any]:
    """View PR/MR metadata."""
    plat = platform or _get_platform()[0]
    if plat == "gitlab":
        result = _run_forge(
            ["mr", "view", str(pr_number), "--output", "json"],
            cwd=cwd,
            platform=plat,
        )
        if not result.stdout.strip():
            return {}
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            return {}
        # Normalise to gh-like field names
        normalized: dict[str, Any] = {}
        if isinstance(data, dict):
            normalized["url"] = data.get("web_url", "")
            normalized["mergeable"] = "MERGEABLE" if data.get("merge_status") == "can_be_merged" else "CONFLICTING"
            normalized["mergeStateStatus"] = data.get("merge_status", "")
            normalized["headRefName"] = data.get("source_branch", "")
            normalized["closingIssuesReferences"] = []
        return normalized
    result = _run_forge(
        ["pr", "view", str(pr_number), "--json", fields],
        cwd=cwd,
        platform=plat,
    )
    if not result.stdout.strip():
        return {}
    return json.loads(result.stdout)


def pr_checks(
    pr_number: str | int,
    *,
    watch: bool = False,
    interval: int = 30,
    cwd: str | Path | None = None,
    platform: str | None = None,
) -> tuple[int, list[dict]]:
    """Check PR/MR CI status.

    Returns (exit_code, checks_list).  Exit code meaning:
    - GitHub: 0=pass, 1=fail, 8=pending
    - GitLab: best-effort mapping from pipeline status.
    """
    plat = platform or _get_platform()[0]
    if plat == "gitlab":
        # glab does not have pr checks; use pipeline status
        result = _run_forge_with_status(
            ["ci", "status"],
            cwd=cwd,
            platform=plat,
        )
        # Parse glab ci status output (text-based)
        stdout = result.stdout.lower()
        if "failed" in stdout or "error" in stdout:
            exit_code = 1
        elif "running" in stdout or "pending" in stdout:
            exit_code = 8
        else:
            exit_code = result.returncode
        checks: list[dict] = []
        # Try to get JSON list of pipelines
        try:
            pipe_result = _run_forge(
                ["ci", "list", "--output", "json"],
                cwd=cwd,
                platform=plat,
            )
            if pipe_result.stdout.strip():
                pipes = json.loads(pipe_result.stdout)
                if isinstance(pipes, list) and pipes:
                    latest = pipes[0]
                    checks.append({
                        "name": "pipeline",
                        "state": latest.get("status", "unknown"),
                        "link": latest.get("web_url", ""),
                    })
        except (RuntimeError, json.JSONDecodeError):
            pass
        return exit_code, checks

    # GitHub path
    if watch and interval <= 0:
        raise ValueError("interval must be positive")
    args = ["pr", "checks", str(pr_number)]
    if watch:
        args.extend(["--watch", "--interval", str(interval)])
    result = _run_forge_with_status(args, cwd=cwd, capture_output=not watch, platform=plat)
    exit_code = result.returncode
    if exit_code not in (0, 1, 8):
        detail = ""
        if result.stdout:
            detail = result.stdout.strip()
        if result.stderr:
            detail = result.stderr.strip() or detail
        hint = detail if detail else f"exit code {exit_code}"
        raise RuntimeError(f"gh {' '.join(args)} failed ({hint})")
    checks = []
    try:
        checks_result = _run_forge(
            ["pr", "checks", str(pr_number), "--json", "name,state,link"],
            cwd=cwd,
            platform=plat,
        )
        if checks_result.stdout.strip():
            checks = json.loads(checks_result.stdout)
    except RuntimeError:
        checks = []
    return exit_code, checks


# ---------------------------------------------------------------------------
# Helper: best-effort JSON field extraction for glab
# ---------------------------------------------------------------------------


def _glab_extract_json_field(json_text: str, query: str) -> str | None:
    """Best-effort field extraction from glab JSON output without external jq."""
    try:
        data = json.loads(json_text)
    except json.JSONDecodeError:
        return None

    if not isinstance(data, dict):
        return None

    # Normalise query like .body, .description, .web_url, .url
    field = query.lstrip(".").strip()
    value = data.get(field)
    if value is None:
        # Try common aliases
        aliases = {
            "body": ["description"],
            "url": ["web_url"],
        }
        for alt in aliases.get(field, []):
            value = data.get(alt)
            if value is not None:
                break
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value)


__all__ = [
    "issue_create",
    "issue_view",
    "issue_body",
    "issue_url",
    "issue_edit",
    "label_create",
    "label_add",
    "label_remove",
    "pr_create",
    "pr_view",
    "pr_checks",
]
