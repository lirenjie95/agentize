# forge.py

Forge-agnostic CLI helpers for GitHub (`gh`) and GitLab (`glab`).

## External Interface

### Issue Operations

- `issue_create(title, body, labels=None, *, cwd=None, platform=None)` - Create an issue and return `(number, url)`.
- `issue_view(issue_number, query=None, *, cwd=None, platform=None)` - View an issue; optional `jq` expression for GitHub.
- `issue_body(issue_number, *, cwd=None, platform=None)` - Return the body text of an issue.
- `issue_url(issue_number, *, cwd=None, platform=None)` - Return the web URL of an issue.
- `issue_edit(issue_number, *, title=None, body=None, body_file=None, add_labels=None, remove_labels=None, cwd=None, platform=None)` - Edit an issue.

### Label Operations

- `label_create(name, color, description="", *, cwd=None, platform=None)` - Create a label (force if it already exists).
- `label_add(issue_number, labels, *, cwd=None, platform=None)` - Add labels to an issue.
- `label_remove(issue_number, labels, *, cwd=None, platform=None)` - Remove labels from an issue.

### PR / MR Operations

- `pr_create(title, body, *, draft=False, base=None, head=None, cwd=None, platform=None)` - Create a PR/MR and return `(number, url)`.
- `pr_view(pr_number, fields="mergeStateStatus,mergeable,url", *, cwd=None, platform=None)` - View PR/MR metadata as a dictionary.
- `pr_checks(pr_number, *, watch=False, interval=30, cwd=None, platform=None)` - Check PR/MR CI status. Returns `(exit_code, checks_list)`.

## Internal Helpers

- `_forge_cmd(platform)` - Return the CLI binary name (`gh` or `glab`).
- `_forge_available(platform)` - Check if the forge CLI is available and authenticated.
- `_run_forge(args, *, cwd=None, platform=None)` - Run a forge CLI command, raising on non-zero exit.
- `_run_forge_with_status(args, *, cwd=None, capture_output=True, platform=None)` - Run a forge CLI command and return the result without raising.
- `_body_args(body, platform)` - Handle multi-line bodies via tempfile or inline arguments.
- `_glab_extract_json_field(json_text, query)` - Best-effort JSON field extraction for `glab` output without external `jq`.

## Design Rationale

- **Unified forge interface**: A single API surface for both GitHub and GitLab reduces platform-specific branching in workflow code.
- **Platform auto-detection**: The default platform is resolved from project configuration, so callers rarely need to specify it explicitly.
- **Graceful glab fallback**: Where `glab` lacks `gh` features (e.g., `--jq`, `pr checks`), the helpers provide best-effort emulation or clear degradation.
