#!/bin/bash
# locate-logs.sh - Find Claude Code session log paths
# Usage: ./locate-logs.sh [project-directory] [session-id]
#
# Returns the path to session logs directory or specific session log file
# If no arguments provided, uses current working directory

set -e

# Calculate project identifier from working directory
calculate_project_dir() {
    local work_dir="$1"
    echo "${work_dir}" | sed 's/\//\-/g'
}

# Get session logs directory
get_logs_directory() {
    local work_dir="${1:-${PWD}}"
    local project_id=$(calculate_project_dir "${work_dir}")
    echo "${HOME}/.claude/projects/${project_id}"
}

# Get specific session log file
get_session_file() {
    local work_dir="$1"
    local session_id="$2"
    local logs_dir=$(get_logs_directory "${work_dir}")
    echo "${logs_dir}/${session_id}.jsonl"
}

# Main logic
if [ $# -eq 0 ]; then
    # No arguments: return logs directory for current working directory
    get_logs_directory "${PWD}"
elif [ $# -eq 1 ]; then
    # One argument: treat as project directory
    get_logs_directory "$1"
elif [ $# -eq 2 ]; then
    # Two arguments: project directory + session ID
    get_session_file "$1" "$2"
else
    echo "Error: Invalid arguments" >&2
    echo "Usage: $0 [project-directory] [session-id]" >&2
    echo "" >&2
    echo "Examples:" >&2
    echo "  $0                           # Logs dir for current directory" >&2
    echo "  $0 /path/to/project          # Logs dir for specific project" >&2
    echo "  $0 /path/to/project abc123   # Specific session log file" >&2
    exit 1
fi
