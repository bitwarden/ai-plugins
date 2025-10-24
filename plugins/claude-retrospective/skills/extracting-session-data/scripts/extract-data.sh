#!/bin/bash
# extract-data.sh - Extract structured data from Claude Code session logs
# Usage: ./extract-data.sh --type TYPE [--session SESSION_ID] [options]
#
# Extracts specific data types from one or more session log files

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check dependencies
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed. Install with: brew install jq" >&2
    exit 1
fi

# Default options
EXTRACT_TYPE=""
SESSION_ID=""
PROJECT_DIR="${PWD}"
OUTPUT_FORMAT="text"
LIMIT=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --type)
            EXTRACT_TYPE="$2"
            shift 2
            ;;
        --session)
            SESSION_ID="$2"
            shift 2
            ;;
        --project)
            PROJECT_DIR="$2"
            shift 2
            ;;
        --format)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        --limit)
            LIMIT="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 --type TYPE [options]"
            echo ""
            echo "Required:"
            echo "  --type TYPE           Data to extract: metadata, user-prompts, tool-usage,"
            echo "                        errors, thinking, text-responses, statistics, all"
            echo ""
            echo "Options:"
            echo "  --session ID          Extract from specific session (default: all sessions)"
            echo "  --project DIR         Project directory (default: current directory)"
            echo "  --format FORMAT       Output format: text (default), json, csv"
            echo "  --limit N             Limit output to first N items"
            echo "  --help                Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --type statistics                    # Stats for all sessions"
            echo "  $0 --type errors --session abc123       # Errors from specific session"
            echo "  $0 --type tool-usage --format json      # Tool usage in JSON format"
            exit 0
            ;;
        *)
            echo "Error: Unknown argument: $1" >&2
            exit 1
            ;;
    esac
done

# Validate required arguments
if [ -z "${EXTRACT_TYPE}" ]; then
    echo "Error: --type is required" >&2
    echo "Run '$0 --help' for usage information" >&2
    exit 1
fi

# Get session files
if [ -n "${SESSION_ID}" ]; then
    # Single session
    SESSION_FILE=$("${SCRIPT_DIR}/locate-logs.sh" "${PROJECT_DIR}" "${SESSION_ID}")
    if [ ! -f "${SESSION_FILE}" ]; then
        echo "Error: Session file not found: ${SESSION_FILE}" >&2
        exit 1
    fi
    SESSION_FILES=("${SESSION_FILE}")
else
    # All sessions
    LOGS_DIR=$("${SCRIPT_DIR}/locate-logs.sh" "${PROJECT_DIR}")
    if [ ! -d "${LOGS_DIR}" ]; then
        echo "Error: Logs directory not found: ${LOGS_DIR}" >&2
        exit 1
    fi

    SESSION_FILES=()
    while IFS= read -r file; do
        SESSION_FILES+=("$file")
    done < <(find "${LOGS_DIR}" -maxdepth 1 -name "*.jsonl" -type f)

    if [ ${#SESSION_FILES[@]} -eq 0 ]; then
        echo "Error: No session files found in: ${LOGS_DIR}" >&2
        exit 1
    fi
fi

# Apply limit if specified
apply_limit() {
    if [ -n "${LIMIT}" ]; then
        head -n "${LIMIT}"
    else
        cat
    fi
}

# Extract metadata
extract_metadata() {
    local file="$1"
    local session_id=$(basename "${file}" .jsonl)

    local first_line=$(head -1 "${file}")
    local last_line=$(tail -1 "${file}")

    echo "Session ID: ${session_id}"
    echo "First Timestamp: $(echo "${first_line}" | jq -r '.timestamp // "unknown"')"
    echo "Last Timestamp: $(echo "${last_line}" | jq -r '.timestamp // "unknown"')"
    echo "Git Branch: $(echo "${first_line}" | jq -r '.gitBranch // "unknown"')"
    echo "Working Directory: $(echo "${first_line}" | jq -r '.cwd // "unknown"')"
    echo "Total Lines: $(wc -l < "${file}" | tr -d ' ')"
    echo ""
}

# Extract user prompts
extract_user_prompts() {
    local file="$1"
    grep '"type":"user"' "${file}" | jq -r '.message.content' | apply_limit
}

# Extract tool usage statistics
extract_tool_usage() {
    local file="$1"
    grep '"type":"assistant"' "${file}" | \
        jq -r '.message.content[]? | select(.type=="tool_use") | .name' | \
        sort | uniq -c | sort -rn | \
        awk '{printf "%-30s %d\n", $2, $1}' | \
        apply_limit
}

# Extract errors
extract_errors() {
    local file="$1"
    grep '"is_error":true' "${file}" | \
        jq -r '[.timestamp, .message.content[]? | select(.is_error==true) | .content] | @tsv' | \
        apply_limit
}

# Extract thinking blocks
extract_thinking() {
    local file="$1"
    grep '"type":"assistant"' "${file}" | \
        jq -r '.message.content[]? | select(.type=="thinking") | .thinking' | \
        apply_limit
}

# Extract text responses
extract_text_responses() {
    local file="$1"
    grep '"type":"assistant"' "${file}" | \
        jq -r '.message.content[]? | select(.type=="text") | .text' | \
        apply_limit
}

# Extract statistics
extract_statistics() {
    local file="$1"
    local session_id=$(basename "${file}" .jsonl)
    local total_lines=$(wc -l < "${file}" | tr -d ' ')
    local user_msgs=$(grep -c '"type":"user"' "${file}" 2>/dev/null || echo "0")
    local assistant_msgs=$(grep -c '"type":"assistant"' "${file}" 2>/dev/null || echo "0")
    local tool_calls=$(grep '"type":"assistant"' "${file}" | jq -r '.message.content[]? | select(.type=="tool_use") | .name' 2>/dev/null | wc -l | tr -d ' ')
    local errors=$(grep -c '"is_error":true' "${file}" 2>/dev/null || echo "0")
    local thinking_blocks=$(grep '"type":"assistant"' "${file}" | jq -r '.message.content[]? | select(.type=="thinking")' 2>/dev/null | wc -l | tr -d ' ')

    echo "Session: ${session_id}"
    echo "  Total Lines: ${total_lines}"
    echo "  User Messages: ${user_msgs}"
    echo "  Assistant Messages: ${assistant_msgs}"
    echo "  Tool Calls: ${tool_calls}"
    echo "  Errors: ${errors}"
    echo "  Thinking Blocks: ${thinking_blocks}"
    echo ""
}

# Process each session file
for session_file in "${SESSION_FILES[@]}"; do
    case ${EXTRACT_TYPE} in
        metadata)
            extract_metadata "${session_file}"
            ;;
        user-prompts)
            extract_user_prompts "${session_file}"
            ;;
        tool-usage)
            echo "=== Tool Usage: $(basename "${session_file}" .jsonl) ==="
            extract_tool_usage "${session_file}"
            echo ""
            ;;
        errors)
            echo "=== Errors: $(basename "${session_file}" .jsonl) ==="
            extract_errors "${session_file}"
            echo ""
            ;;
        thinking)
            echo "=== Thinking Blocks: $(basename "${session_file}" .jsonl) ==="
            extract_thinking "${session_file}"
            echo ""
            ;;
        text-responses)
            extract_text_responses "${session_file}"
            ;;
        statistics)
            extract_statistics "${session_file}"
            ;;
        all)
            echo "========================================"
            echo "Session: $(basename "${session_file}" .jsonl)"
            echo "========================================"
            echo ""
            extract_metadata "${session_file}"
            extract_statistics "${session_file}"
            echo "--- Tool Usage ---"
            extract_tool_usage "${session_file}"
            echo ""
            echo "--- Errors ---"
            extract_errors "${session_file}"
            echo ""
            ;;
        *)
            echo "Error: Unknown extraction type: ${EXTRACT_TYPE}" >&2
            echo "Valid types: metadata, user-prompts, tool-usage, errors, thinking, text-responses, statistics, all" >&2
            exit 1
            ;;
    esac
done
