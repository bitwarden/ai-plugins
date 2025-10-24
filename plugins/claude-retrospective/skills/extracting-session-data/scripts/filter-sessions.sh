#!/bin/bash
# filter-sessions.sh - Filter Claude Code sessions by various criteria
# Usage: ./filter-sessions.sh [options]
#
# Filters session logs based on date, branch, size, errors, or content

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check dependencies
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed. Install with: brew install jq" >&2
    exit 1
fi

# Default options
PROJECT_DIR="${PWD}"
SINCE=""
UNTIL=""
BRANCH=""
MIN_SIZE=""
MAX_SIZE=""
MIN_LINES=""
MAX_LINES=""
HAS_ERRORS=""
KEYWORD=""
OUTPUT_FORMAT="list"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --project)
            PROJECT_DIR="$2"
            shift 2
            ;;
        --since)
            SINCE="$2"
            shift 2
            ;;
        --until)
            UNTIL="$2"
            shift 2
            ;;
        --branch)
            BRANCH="$2"
            shift 2
            ;;
        --min-size)
            MIN_SIZE="$2"
            shift 2
            ;;
        --max-size)
            MAX_SIZE="$2"
            shift 2
            ;;
        --min-lines)
            MIN_LINES="$2"
            shift 2
            ;;
        --max-lines)
            MAX_LINES="$2"
            shift 2
            ;;
        --has-errors)
            HAS_ERRORS="true"
            shift
            ;;
        --keyword)
            KEYWORD="$2"
            shift 2
            ;;
        --format)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --project DIR         Project directory (default: current directory)"
            echo "  --since DATE          Sessions modified since date (YYYY-MM-DD or 'N days ago')"
            echo "  --until DATE          Sessions modified until date (YYYY-MM-DD)"
            echo "  --branch BRANCH       Filter by git branch name"
            echo "  --min-size SIZE       Minimum file size (e.g., 1M, 500K)"
            echo "  --max-size SIZE       Maximum file size"
            echo "  --min-lines N         Minimum line count"
            echo "  --max-lines N         Maximum line count"
            echo "  --has-errors          Only sessions with errors"
            echo "  --keyword WORD        Sessions containing keyword"
            echo "  --format FORMAT       Output format: list (default), paths, json"
            echo "  --help                Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --since '2 days ago'                # Recent sessions"
            echo "  $0 --branch main --has-errors          # Errors on main branch"
            echo "  $0 --min-lines 500 --keyword 'test'    # Large sessions with 'test'"
            exit 0
            ;;
        *)
            echo "Error: Unknown argument: $1" >&2
            exit 1
            ;;
    esac
done

# Get logs directory
LOGS_DIR=$("${SCRIPT_DIR}/locate-logs.sh" "${PROJECT_DIR}")

if [ ! -d "${LOGS_DIR}" ]; then
    echo "Error: Logs directory not found: ${LOGS_DIR}" >&2
    exit 1
fi

# Find all session files
ALL_FILES=()
while IFS= read -r file; do
    ALL_FILES+=("$file")
done < <(find "${LOGS_DIR}" -maxdepth 1 -name "*.jsonl" -type f)

if [ ${#ALL_FILES[@]} -eq 0 ]; then
    echo "No session files found" >&2
    exit 0
fi

# Convert date string to timestamp for comparison
date_to_timestamp() {
    local date_str="$1"
    if [[ "${date_str}" =~ ago ]]; then
        # Handle relative dates like "2 days ago"
        date -j -v-$(echo "${date_str}" | sed 's/ ago//') +%s 2>/dev/null || date -d "${date_str}" +%s 2>/dev/null
    else
        # Handle absolute dates like "2025-10-24"
        date -j -f "%Y-%m-%d" "${date_str}" +%s 2>/dev/null || date -d "${date_str}" +%s 2>/dev/null
    fi
}

# Convert size string to bytes
size_to_bytes() {
    local size_str="$1"
    local num=$(echo "${size_str}" | sed 's/[^0-9.]//g')
    local unit=$(echo "${size_str}" | sed 's/[0-9.]//g' | tr '[:lower:]' '[:upper:]')

    case ${unit} in
        K|KB)
            echo $(echo "${num} * 1024" | bc | cut -d'.' -f1)
            ;;
        M|MB)
            echo $(echo "${num} * 1024 * 1024" | bc | cut -d'.' -f1)
            ;;
        G|GB)
            echo $(echo "${num} * 1024 * 1024 * 1024" | bc | cut -d'.' -f1)
            ;;
        *)
            echo "${num}"
            ;;
    esac
}

# Filter sessions
declare -a FILTERED_FILES

for file in "${ALL_FILES[@]}"; do
    INCLUDE=true

    # Time filter
    if [ -n "${SINCE}" ] || [ -n "${UNTIL}" ]; then
        FILE_TIMESTAMP=$(stat -f%m "${file}" 2>/dev/null || stat -c%Y "${file}" 2>/dev/null)

        if [ -n "${SINCE}" ]; then
            SINCE_TIMESTAMP=$(date_to_timestamp "${SINCE}")
            if [ "${FILE_TIMESTAMP}" -lt "${SINCE_TIMESTAMP}" ]; then
                INCLUDE=false
            fi
        fi

        if [ -n "${UNTIL}" ]; then
            UNTIL_TIMESTAMP=$(date_to_timestamp "${UNTIL}")
            if [ "${FILE_TIMESTAMP}" -gt "${UNTIL_TIMESTAMP}" ]; then
                INCLUDE=false
            fi
        fi
    fi

    # Branch filter
    if [ -n "${BRANCH}" ] && [ "${INCLUDE}" = true ]; then
        FILE_BRANCH=$(head -1 "${file}" | jq -r '.gitBranch // "unknown"' 2>/dev/null)
        if [ "${FILE_BRANCH}" != "${BRANCH}" ]; then
            INCLUDE=false
        fi
    fi

    # Size filter
    if [ "${INCLUDE}" = true ] && { [ -n "${MIN_SIZE}" ] || [ -n "${MAX_SIZE}" ]; }; then
        FILE_SIZE=$(stat -f%z "${file}" 2>/dev/null || stat -c%s "${file}" 2>/dev/null)

        if [ -n "${MIN_SIZE}" ]; then
            MIN_BYTES=$(size_to_bytes "${MIN_SIZE}")
            if [ "${FILE_SIZE}" -lt "${MIN_BYTES}" ]; then
                INCLUDE=false
            fi
        fi

        if [ -n "${MAX_SIZE}" ]; then
            MAX_BYTES=$(size_to_bytes "${MAX_SIZE}")
            if [ "${FILE_SIZE}" -gt "${MAX_BYTES}" ]; then
                INCLUDE=false
            fi
        fi
    fi

    # Line count filter
    if [ "${INCLUDE}" = true ] && { [ -n "${MIN_LINES}" ] || [ -n "${MAX_LINES}" ]; }; then
        LINE_COUNT=$(wc -l < "${file}" | tr -d ' ')

        if [ -n "${MIN_LINES}" ] && [ "${LINE_COUNT}" -lt "${MIN_LINES}" ]; then
            INCLUDE=false
        fi

        if [ -n "${MAX_LINES}" ] && [ "${LINE_COUNT}" -gt "${MAX_LINES}" ]; then
            INCLUDE=false
        fi
    fi

    # Errors filter
    if [ "${HAS_ERRORS}" = true ] && [ "${INCLUDE}" = true ]; then
        ERROR_COUNT=$(grep -c '"is_error":true' "${file}" 2>/dev/null || echo "0")
        if [ "${ERROR_COUNT}" -eq 0 ]; then
            INCLUDE=false
        fi
    fi

    # Keyword filter
    if [ -n "${KEYWORD}" ] && [ "${INCLUDE}" = true ]; then
        if ! grep -q "${KEYWORD}" "${file}" 2>/dev/null; then
            INCLUDE=false
        fi
    fi

    # Add to filtered list
    if [ "${INCLUDE}" = true ]; then
        FILTERED_FILES+=("${file}")
    fi
done

# Output results
if [ ${#FILTERED_FILES[@]} -eq 0 ]; then
    echo "No sessions match the specified criteria" >&2
    exit 0
fi

case ${OUTPUT_FORMAT} in
    paths)
        for file in "${FILTERED_FILES[@]}"; do
            echo "${file}"
        done
        ;;
    json)
        echo "["
        FIRST=true
        for file in "${FILTERED_FILES[@]}"; do
            SESSION_ID=$(basename "${file}" .jsonl)
            FILE_SIZE=$(du -h "${file}" | cut -f1)
            LINE_COUNT=$(wc -l < "${file}" | tr -d ' ')
            MODIFIED_DATE=$(stat -f%Sm -t "%Y-%m-%d %H:%M:%S" "${file}" 2>/dev/null || stat -c%y "${file}" 2>/dev/null | cut -d'.' -f1)
            GIT_BRANCH=$(head -1 "${file}" | jq -r '.gitBranch // "unknown"' 2>/dev/null || echo "unknown")

            if [ "${FIRST}" = true ]; then
                FIRST=false
            else
                echo ","
            fi
            echo "  {"
            echo "    \"sessionId\": \"${SESSION_ID}\","
            echo "    \"path\": \"${file}\","
            echo "    \"size\": \"${FILE_SIZE}\","
            echo "    \"lines\": ${LINE_COUNT},"
            echo "    \"modifiedDate\": \"${MODIFIED_DATE}\","
            echo "    \"gitBranch\": \"${GIT_BRANCH}\""
            echo -n "  }"
        done
        echo ""
        echo "]"
        ;;
    list|*)
        echo "Found ${#FILTERED_FILES[@]} matching session(s):"
        echo ""
        for file in "${FILTERED_FILES[@]}"; do
            SESSION_ID=$(basename "${file}" .jsonl)
            FILE_SIZE=$(du -h "${file}" | cut -f1)
            LINE_COUNT=$(wc -l < "${file}" | tr -d ' ')
            MODIFIED_DATE=$(stat -f%Sm -t "%Y-%m-%d %H:%M:%S" "${file}" 2>/dev/null || stat -c%y "${file}" 2>/dev/null | cut -d'.' -f1)
            GIT_BRANCH=$(head -1 "${file}" | jq -r '.gitBranch // "unknown"' 2>/dev/null || echo "unknown")

            echo "Session: ${SESSION_ID}"
            echo "  Path: ${file}"
            echo "  Size: ${FILE_SIZE}"
            echo "  Lines: ${LINE_COUNT}"
            echo "  Modified: ${MODIFIED_DATE}"
            echo "  Branch: ${GIT_BRANCH}"
            echo ""
        done
        ;;
esac
