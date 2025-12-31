#!/usr/bin/env bash
#
# Shared path sanitization library for plugin validation scripts.
#
# This library provides functions to safely sanitize and validate plugin paths
# to prevent directory traversal attacks, plus compatibility functions for
# cross-platform shell scripting.

# Cross-platform array reading function
# Args:
#   $1 - Array variable name to populate
#   stdin - Input lines to read
array_from_lines() {
    local array_name="$1"
    local line
    local -a temp_array=()

    while IFS= read -r line; do
        temp_array+=("$line")
    done

    # Use eval to assign to the named array variable
    # This is safe because array_name is controlled by the script
    # Handle empty arrays properly with set -u
    if [[ "${#temp_array[@]}" -eq 0 ]]; then
        eval "${array_name}=()"
    else
        eval "${array_name}=($(printf '%q ' "${temp_array[@]}"))"
    fi
}

# Sanitize and validate a plugin path argument
# Args:
#   $1 - The path argument to sanitize
#   $2 - The plugins directory base path
# Returns:
#   The sanitized plugin name on stdout, or empty string if invalid
# Exit codes:
#   0 - Successfully sanitized
#   1 - Invalid path (rejected for security reasons)
sanitize_plugin_path() {
    local arg="$1"
    local plugins_dir="$2"

    # Remove leading ./
    arg="${arg#./}"

    # Remove all occurrences of .. to prevent traversal
    arg="${arg//..}"

    # Remove leading and trailing slashes
    arg="${arg#/}"
    arg="${arg%/}"

    # Normalize multiple slashes
    arg="${arg//\/\///}"

    # Extract plugin name from various path formats
    local plugin_name=""

    if [[ "$arg" =~ ^plugins/([^/]+)$ ]]; then
        # Format: plugins/plugin-name
        plugin_name="${BASH_REMATCH[1]}"
    elif [[ "$arg" =~ ^[a-zA-Z0-9_-]+$ ]]; then
        # Format: plugin-name (just the name)
        plugin_name="$arg"
    else
        # Invalid format or potentially dangerous pattern
        return 1
    fi

    # Validate plugin name contains only safe characters
    if [[ ! "$plugin_name" =~ ^[a-zA-Z0-9_-]+$ ]]; then
        return 1
    fi

    # Construct the full path and verify it exists
    local plugin_path="$plugins_dir/$plugin_name"

    # Verify the path exists and is a directory
    if [[ ! -d "$plugin_path" ]]; then
        return 1
    fi

    # Use realpath to resolve any symlinks and get canonical path
    local canonical_path
    canonical_path="$(cd "$plugin_path" && pwd 2>/dev/null)" || return 1

    # Verify the resolved path is still under plugins_dir
    local canonical_plugins_dir
    canonical_plugins_dir="$(cd "$plugins_dir" && pwd 2>/dev/null)" || return 1

    if [[ ! "$canonical_path" =~ ^"$canonical_plugins_dir"/ ]]; then
        # Path escapes the plugins directory - reject it
        return 1
    fi

    # Return the full canonical path
    echo "$canonical_path"
    return 0
}

# Validate that a plugin name is safe (alphanumeric, hyphens, underscores only)
# Args:
#   $1 - The plugin name to validate
# Returns:
#   0 if valid, 1 if invalid
is_safe_plugin_name() {
    local name="$1"

    if [[ -z "$name" ]]; then
        return 1
    fi

    if [[ ! "$name" =~ ^[a-zA-Z0-9_-]+$ ]]; then
        return 1
    fi

    # Reject names that are just dots or contain path separators
    if [[ "$name" =~ [./] ]]; then
        return 1
    fi

    return 0
}
