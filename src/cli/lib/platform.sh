#!/usr/bin/env bash
# Platform detection and forge-agnostic utilities for GitHub/GitLab support.
# Source this file to use _platform_detect, _platform_cmd, _platform_parse_remote.

# Detect platform from .agentize.yaml or git remote origin.
# Sets: _PLATFORM (github|gitlab), _HOST (hostname), _FORGE_CMD (gh|glab)
# Returns: 0 on success
_platform_detect() {
    _PLATFORM=""
    _HOST=""
    _FORGE_CMD=""

    local config_file=""
    local project_root=""
    project_root="$(git rev-parse --show-toplevel 2>/dev/null)" || true

    if [ -n "$project_root" ] && [ -f "$project_root/.agentize.yaml" ]; then
        config_file="$project_root/.agentize.yaml"
    elif [ -f ".agentize.yaml" ]; then
        config_file=".agentize.yaml"
    fi

    # Read platform from config
    if [ -n "$config_file" ]; then
        local cfg_platform
        cfg_platform="$(grep -E '^\s*platform:' "$config_file" 2>/dev/null | head -1 | sed 's/.*platform:\s*//' | tr -d '[:space:]"'"'"' | tr '[:upper:]' '[:lower:]')"
        if [ -n "$cfg_platform" ]; then
            _PLATFORM="$cfg_platform"
        fi
        local cfg_host
        cfg_host="$(grep -E '^\s*host:' "$config_file" 2>/dev/null | head -1 | sed 's/.*host:\s*//' | tr -d '[:space:]"'"'"')"
        if [ -n "$cfg_host" ]; then
            _HOST="$cfg_host"
        fi
    fi

    # Auto-detect from git remote if not configured
    if [ -z "$_PLATFORM" ]; then
        local remote_url
        remote_url="$(git remote get-url origin 2>/dev/null)" || remote_url=""
        if [ -n "$remote_url" ]; then
            case "$remote_url" in
                *github.com*)
                    _PLATFORM="github"
                    ;;
                *gitlab*)
                    _PLATFORM="gitlab"
                    ;;
                *)
                    _PLATFORM="github"
                    ;;
            esac
            # Extract host if not already set
            if [ -z "$_HOST" ]; then
                if [[ "$remote_url" =~ ^git@([^:]+): ]]; then
                    _HOST="${BASH_REMATCH[1]}"
                elif [[ "$remote_url" =~ ^https?://([^/]+)/ ]]; then
                    _HOST="${BASH_REMATCH[1]}"
                fi
            fi
        fi
    fi

    # Default fallback
    if [ -z "$_PLATFORM" ]; then
        _PLATFORM="github"
    fi

    if [ "$_PLATFORM" = "gitlab" ]; then
        _FORGE_CMD="glab"
    else
        _FORGE_CMD="gh"
    fi
}

# Return the forge CLI command (gh or glab).
# Detects on first call and caches result.
_platform_cmd() {
    if [ -z "$_FORGE_CMD" ]; then
        _platform_detect
    fi
    echo "$_FORGE_CMD"
}

# Parse owner/repo from a git remote URL (any host).
# Usage: eval "$(_platform_parse_remote <url>)"
# Sets: _REMOTE_OWNER, _REMOTE_REPO
_platform_parse_remote() {
    local url="$1"
    _REMOTE_OWNER=""
    _REMOTE_REPO=""

    local path=""
    if [[ "$url" =~ ^git@([^:]+):(.+)$ ]]; then
        path="${BASH_REMATCH[2]}"
    elif [[ "$url" =~ ^https?://[^/]+/(.+)$ ]]; then
        path="${BASH_REMATCH[1]}"
    fi

    if [ -z "$path" ]; then
        return 1
    fi

    # Remove .git suffix
    path="${path%.git}"
    path="${path%/}"

    local parts
    parts="$(echo "$path" | tr '/' '\n')"
    local owner=""
    local repo=""
    local idx=0
    while IFS= read -r part; do
        if [ -n "$part" ]; then
            if [ "$idx" -eq 0 ]; then
                owner="$part"
            elif [ "$idx" -eq 1 ]; then
                repo="$part"
                break
            fi
            idx=$((idx + 1))
        fi
    done <<< "$parts"

    _REMOTE_OWNER="$owner"
    _REMOTE_REPO="$repo"
}
