"""Compatibility re-exports for the old `gh` module.

New code should import from `agentize.workflow.api.forge` directly.
This module exists so that existing imports do not break.
"""

from __future__ import annotations

from agentize.workflow.api.forge import (
    issue_body,
    issue_create,
    issue_edit,
    issue_url,
    issue_view,
    label_add,
    label_create,
    label_remove,
    pr_checks,
    pr_create,
    pr_view,
)

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
