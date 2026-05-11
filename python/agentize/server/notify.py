"""Telegram notification helpers for the server module."""

from __future__ import annotations

import os
import re
import socket
import sys
from pathlib import Path
from typing import Optional

# Add .claude-plugin to path for lib imports
_repo_root = Path(__file__).resolve().parents[3]
_plugin_dir = _repo_root / ".claude-plugin"
if str(_plugin_dir) not in sys.path:
    sys.path.insert(0, str(_plugin_dir))

from lib.telegram_utils import escape_html, telegram_request
from agentize.server.log import _log
from agentize.server.platform import build_issue_url, build_mr_url, detect_platform, get_host, parse_repo_slug


# Telegram API timeout in seconds
TELEGRAM_API_TIMEOUT_SEC = 10


def parse_period(period_str: str) -> int:
    """Parse period string (e.g., '5m', '300s') to seconds."""
    if period_str.endswith('m'):
        return int(period_str[:-1]) * 60
    elif period_str.endswith('s'):
        return int(period_str[:-1])
    else:
        raise ValueError(f"Invalid period format: {period_str}. Use Nm or Ns.")


def send_telegram_message(token: str, chat_id: str, text: str) -> bool:
    """Send a message to Telegram.

    Args:
        token: Telegram Bot API token
        chat_id: Chat ID to send to
        text: Message text (supports HTML parse mode)

    Returns:
        True if successful, False otherwise
    """
    result = telegram_request(
        token=token,
        method='sendMessage',
        payload={'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'},
        timeout_sec=TELEGRAM_API_TIMEOUT_SEC,
        on_error=lambda e: _log(f"Failed to send Telegram message: {e}", level="ERROR")
    )
    return result.get('ok', False) if result else False


def notify_server_start(token: str, chat_id: str, org: str, project_id: int, period: int) -> None:
    """Send server startup notification to Telegram.

    Args:
        token: Telegram Bot API token
        chat_id: Chat ID to send to
        org: GitHub organization
        project_id: GitHub project number
        period: Polling interval in seconds
    """
    hostname = socket.gethostname()
    cwd = os.getcwd()

    message = (
        f"🚀 <b>Agentize Server Started</b>\n\n"
        f"Host: <code>{hostname}</code>\n"
        f"Project: <code>{org}/{project_id}</code>\n"
        f"Period: <code>{period}s</code>\n"
        f"Working Dir: <code>{cwd}</code>"
    )

    if send_telegram_message(token, chat_id, message):
        print("Telegram notification sent")
    else:
        print("Warning: Failed to send Telegram startup notification", file=sys.stderr)


def _extract_repo_slug(remote_url: str) -> Optional[str]:
    """Extract org/repo slug from a git remote URL.

    Supports any git forge host (GitHub, GitLab, self-hosted).

    Returns:
        org/repo string or None if URL format not recognized.
    """
    if not remote_url:
        return None
    try:
        owner, repo = parse_repo_slug(remote_url)
        return f"{owner}/{repo}"
    except RuntimeError:
        return None


def _format_worker_assignment_message(
    issue_no: int,
    issue_title: str,
    worker_id: int,
    issue_url: Optional[str]
) -> str:
    """Build HTML-formatted Telegram message for worker assignment.

    Args:
        issue_no: Issue number
        issue_title: Issue title (will be HTML-escaped)
        worker_id: Worker slot ID
        issue_url: Full issue URL or None

    Returns:
        HTML-formatted message for Telegram
    """
    escaped_title = escape_html(issue_title)

    if issue_url:
        issue_ref = f'<a href="{issue_url}">#{issue_no}</a>'
    else:
        issue_ref = f'#{issue_no}'

    return (
        f"🔧 <b>Worker Assignment</b>\n\n"
        f"Issue: {issue_ref} {escaped_title}\n"
        f"Worker: {worker_id}"
    )


def _format_worker_completion_message(
    issue_no: int,
    worker_id: int,
    issue_url: Optional[str],
    pr_url: Optional[str] = None
) -> str:
    """Build HTML-formatted Telegram message for worker completion.

    Args:
        issue_no: Issue number
        worker_id: Worker slot ID
        issue_url: Full issue URL or None
        pr_url: Full PR/MR URL or None

    Returns:
        HTML-formatted message for Telegram
    """
    if issue_url:
        issue_ref = f'<a href="{issue_url}">#{issue_no}</a>'
    else:
        issue_ref = f'#{issue_no}'

    lines = [
        f"✅ <b>Worker Completed</b>\n",
        f"Issue: {issue_ref}",
    ]

    if pr_url:
        pr_number = pr_url.rstrip('/').split('/')[-1]
        lines.append(f"PR: <a href=\"{pr_url}\">#{pr_number}</a>")

    lines.append(f"Worker: {worker_id}")

    return '\n'.join(lines)
