#!/bin/bash
# list-sessions.sh - List available Claude Code sessions with metadata
# Usage: ./list-sessions.sh [project-directory] [options]
#
# Lists all session log files with metadata (ID, size, date, branch, lines)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default options
OUTPUT_FORMAT="table"  # table, json, csv
SORT_BY="date"         # date, size, lines

# Parse arguments
PROJECT_DIR="${PWD}"
while [[ $# -gt 0 ]]; do
    case $1 in
        --format)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        --sort)
            SORT_BY="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [project-directory] [options]"
            echo ""
            echo "Options:"
            echo "  --format FORMAT    Output format: table (default), json, csv"
            echo "  --sort FIELD       Sort by: date (default), size, lines"
            echo "  --help             Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                              # List sessions for current directory"
            echo "  $0 /path/to/project             # List sessions for specific project"
            echo "  $0 --format json --sort size    # JSON output sorted by size"
            exit 0
            ;;
        *)
            PROJECT_DIR="$1"
            shift
            ;;
    esac
done

# Get logs directory
LOGS_DIR=$("${SCRIPT_DIR}/locate-logs.sh" "${PROJECT_DIR}")

if [ ! -d "${LOGS_DIR}" ]; then
    echo "Error: Logs directory not found: ${LOGS_DIR}" >&2
    exit 1
fi

# Check for session files
SESSION_FILES=$(find "${LOGS_DIR}" -maxdepth 1 -name "*.jsonl" -type f 2>/dev/null || true)

if [ -z "${SESSION_FILES}" ]; then
    echo "No session log files found in: ${LOGS_DIR}" >&2
    exit 0
fi

# Extract metadata for each session
declare -a SESSIONS

while IFS= read -r file; do
    SESSION_ID=$(basename "${file}" .jsonl)
    FILE_SIZE=$(du -h "${file}" | cut -f1)
    FILE_SIZE_BYTES=$(stat -f%z "${file}" 2>/dev/null || stat -c%s "${file}" 2>/dev/null)
    LINE_COUNT=$(wc -l < "${file}" | tr -d ' ')
    MODIFIED_DATE=$(stat -f%Sm -t "%Y-%m-%d %H:%M:%S" "${file}" 2>/dev/null || stat -c%y "${file}" 2>/dev/null | cut -d'.' -f1)

    # Try to extract git branch from first line
    GIT_BRANCH=$(head -1 "${file}" | jq -r '.gitBranch // "unknown"' 2>/dev/null || echo "unknown")

    SESSIONS+=("${SESSION_ID}|${FILE_SIZE}|${FILE_SIZE_BYTES}|${LINE_COUNT}|${MODIFIED_DATE}|${GIT_BRANCH}")
done <<< "${SESSION_FILES}"

# Sort sessions
case ${SORT_BY} in
    date)
        IFS=$'\n' SORTED=($(sort -t'|' -k5 -r <<< "${SESSIONS[*]}"))
        ;;
    size)
        IFS=$'\n' SORTED=($(sort -t'|' -k3 -rn <<< "${SESSIONS[*]}"))
        ;;
    lines)
        IFS=$'\n' SORTED=($(sort -t'|' -k4 -rn <<< "${SESSIONS[*]}"))
        ;;
    *)
        SORTED=("${SESSIONS[@]}")
        ;;
esac

# Output in requested format
case ${OUTPUT_FORMAT} in
    json)
        echo "["
        FIRST=true
        for session in "${SORTED[@]}"; do
            IFS='|' read -r id size size_bytes lines date branch <<< "${session}"
            if [ "${FIRST}" = true ]; then
                FIRST=false
            else
                echo ","
            fi
            echo "  {"
            echo "    \"sessionId\": \"${id}\","
            echo "    \"size\": \"${size}\","
            echo "    \"sizeBytes\": ${size_bytes},"
            echo "    \"lines\": ${lines},"
            echo "    \"modifiedDate\": \"${date}\","
            echo "    \"gitBranch\": \"${branch}\""
            echo -n "  }"
        done
        echo ""
        echo "]"
        ;;
    csv)
        echo "SessionID,Size,SizeBytes,Lines,ModifiedDate,GitBranch"
        for session in "${SORTED[@]}"; do
            IFS='|' read -r id size size_bytes lines date branch <<< "${session}"
            echo "${id},${size},${size_bytes},${lines},${date},${branch}"
        done
        ;;
    table|*)
        printf "%-40s %-10s %-10s %-20s %-20s\n" "SESSION_ID" "SIZE" "LINES" "MODIFIED" "BRANCH"
        printf "%-40s %-10s %-10s %-20s %-20s\n" "----------------------------------------" "----------" "----------" "--------------------" "--------------------"
        for session in "${SORTED[@]}"; do
            IFS='|' read -r id size size_bytes lines date branch <<< "${session}"
            printf "%-40s %-10s %-10s %-20s %-20s\n" "${id}" "${size}" "${lines}" "${date}" "${branch}"
        done
        ;;
esac
