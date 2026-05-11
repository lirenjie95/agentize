#!/usr/bin/env bash
# Planner forge-agnostic issue helpers for GitHub (gh) and GitLab (glab).
# Replaces src/cli/planner/github.sh with cross-platform support.

# Source platform detection library
if [ -n "$AGENTIZE_HOME" ] && [ -f "$AGENTIZE_HOME/src/cli/lib/platform.sh" ]; then
    source "$AGENTIZE_HOME/src/cli/lib/platform.sh"
else
    source "${BASH_SOURCE[0]%/*}/../lib/platform.sh" 2>/dev/null || true
fi

# Check if the forge CLI is available and authenticated
# Returns 0 if available, 1 otherwise
_planner_forge_available() {
    local cmd
    cmd="$(_platform_cmd)"
    command -v "$cmd" >/dev/null 2>&1 || return 1
    "$cmd" auth status >/dev/null 2>&1 || return 1
    return 0
}

# Create a placeholder issue for the planning pipeline
# Usage: _planner_issue_create "<title>"
# Outputs: issue number on stdout, or empty string on failure
_planner_issue_create() {
    local title="$1"

    if ! _planner_forge_available; then
        echo "Warning: forge CLI not available or not authenticated, skipping issue creation" >&2
        return 1
    fi

    local cmd
    cmd="$(_platform_cmd)"
    local platform="$_PLATFORM"

    local trimmed="${title:0:50}"
    if [ ${#title} -gt 50 ]; then
        trimmed="${trimmed}..."
    fi

    local issue_url
    if [ "$platform" = "gitlab" ]; then
        issue_url=$(glab issue create \
            --title "[plan] placeholder: ${trimmed}" \
            --description "$title" 2>&1)
    else
        issue_url=$(gh issue create \
            --title "[plan] placeholder: ${trimmed}" \
            --body "$title" 2>&1)
    fi
    local exit_code=$?

    if [ $exit_code -ne 0 ] || [ -z "$issue_url" ]; then
        echo "Warning: Failed to create issue: $issue_url" >&2
        return 1
    fi

    # Parse issue number from URL
    local issue_number
    issue_number=$(echo "$issue_url" | grep -oE '[0-9]+$')

    if [ -z "$issue_number" ]; then
        echo "Warning: Could not parse issue number from URL: $issue_url" >&2
        return 1
    fi

    # Store URL for pipeline rendering
    _PLANNER_ISSUE_URL="$issue_url"

    echo "$issue_number"
    return 0
}

# Fetch existing issue body for refinement
# Usage: _planner_issue_fetch "<issue-number>"
# Outputs: issue body on stdout; returns non-zero on failure
_planner_issue_fetch() {
    local issue_number="$1"

    if ! _planner_forge_available; then
        echo "Error: forge CLI not available or not authenticated; cannot refine issue #$issue_number" >&2
        return 1
    fi

    local cmd
    cmd="$(_platform_cmd)"
    local platform="$_PLATFORM"
    local issue_body
    local body_exit

    if [ "$platform" = "gitlab" ]; then
        issue_body=$(glab issue view "$issue_number" --output json 2>/dev/null)
        body_exit=$?
        if [ $body_exit -eq 0 ] && [ -n "$issue_body" ] && command -v jq >/dev/null 2>&1; then
            issue_body=$(echo "$issue_body" | jq -r '.description // empty' 2>/dev/null)
        fi
    else
        issue_body=$(gh issue view "$issue_number" --json body -q .body 2>/dev/null)
        body_exit=$?
    fi

    if [ $body_exit -ne 0 ] || [ -z "$issue_body" ]; then
        echo "Error: Failed to fetch issue #$issue_number body" >&2
        return 1
    fi

    local issue_url
    if [ "$platform" = "gitlab" ]; then
        issue_url=$(glab issue view "$issue_number" --output json 2>/dev/null)
        if [ $? -eq 0 ] && [ -n "$issue_url" ] && command -v jq >/dev/null 2>&1; then
            issue_url=$(echo "$issue_url" | jq -r '.web_url // empty' 2>/dev/null)
        fi
    else
        issue_url=$(gh issue view "$issue_number" --json url -q .url 2>/dev/null)
    fi
    if [ $? -eq 0 ] && [ -n "$issue_url" ]; then
        _PLANNER_ISSUE_URL="$issue_url"
    fi

    echo "$issue_body"
    return 0
}

# Publish the consensus plan to an issue
# Usage: _planner_issue_publish "<issue-number>" "<title>" "<body-file>"
# Returns 0 on success, 1 on failure
_planner_issue_publish() {
    local issue_number="$1"
    local title="$2"
    local body_file="$3"

    if ! _planner_forge_available; then
        echo "Warning: forge CLI not available, skipping issue publish" >&2
        return 1
    fi

    local cmd
    cmd="$(_platform_cmd)"
    local platform="$_PLATFORM"

    if [ "$platform" = "gitlab" ]; then
        # Update issue title and body
        glab issue update "$issue_number" \
            --title "[plan] $title" \
            --description "$(cat "$body_file")" >/dev/null 2>&1
        local edit_exit=$?

        if [ $edit_exit -ne 0 ]; then
            echo "Warning: Failed to update issue #$issue_number body" >&2
            return 1
        fi

        # Add agentize:plan label
        glab issue update "$issue_number" \
            --label "agentize:plan" >/dev/null 2>&1
        local label_exit=$?

        if [ $label_exit -ne 0 ]; then
            glab label create "agentize:plan" \
                --color "#1d76db" \
                --description "Agentize plan placeholder" >/dev/null 2>&1
            glab issue update "$issue_number" \
                --label "agentize:plan" >/dev/null 2>&1
            label_exit=$?
            if [ $label_exit -ne 0 ]; then
                echo "Warning: Failed to add agentize:plan label to issue #$issue_number" >&2
            fi
        fi
    else
        # GitHub path
        gh issue edit "$issue_number" \
            --title "[plan] $title" \
            --body-file "$body_file" >/dev/null 2>&1
        local edit_exit=$?

        if [ $edit_exit -ne 0 ]; then
            echo "Warning: Failed to update issue #$issue_number body" >&2
            return 1
        fi

        # Add agentize:plan label
        gh issue edit "$issue_number" \
            --add-label "agentize:plan" >/dev/null 2>&1
        local label_exit=$?

        if [ $label_exit -ne 0 ]; then
            gh label create "agentize:plan" \
                --color "1d76db" \
                --description "Agentize plan placeholder" >/dev/null 2>&1
            gh issue edit "$issue_number" \
                --add-label "agentize:plan" >/dev/null 2>&1
            label_exit=$?
            if [ $label_exit -ne 0 ]; then
                echo "Warning: Failed to add agentize:plan label to issue #$issue_number" >&2
            fi
        fi
    fi

    return 0
}
