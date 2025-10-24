#!/bin/bash
# Session Log Analysis Script
# Quickly extracts key metrics from Claude Code session logs
# Usage: ./analyze-session-logs.sh <session-log-file.md> [session-log-file.ndjson]

set -e

if [ $# -lt 1 ]; then
    echo "Usage: $0 <session-log.md> [session-log.ndjson]"
    echo ""
    echo "Analyzes Claude Code session logs and outputs structured summary."
    echo ""
    echo "Arguments:"
    echo "  session-log.md      - Markdown formatted session log (required)"
    echo "  session-log.ndjson  - NDJSON formatted session log (optional, for detailed tool stats)"
    exit 1
fi

MD_LOG="$1"
NDJSON_LOG="$2"

if [ ! -f "$MD_LOG" ]; then
    echo "Error: File not found: $MD_LOG"
    exit 1
fi

echo "==================================="
echo "Session Log Analysis"
echo "==================================="
echo ""
echo "File: $MD_LOG"
echo "Size: $(wc -l < "$MD_LOG") lines ($(du -h "$MD_LOG" | cut -f1))"
echo ""

# Extract session metadata
echo "--- Session Metadata ---"
SESSION_START=$(grep -m1 "Session started" "$MD_LOG" || echo "Not found")
SESSION_END=$(grep -m1 "Session ended" "$MD_LOG" || echo "Not found")
echo "Start: $SESSION_START"
echo "End: $SESSION_END"
echo ""

# Count errors and warnings
echo "--- Error Analysis ---"
ERROR_COUNT=$(grep -ci "error" "$MD_LOG" 2>/dev/null || echo "0")
WARNING_COUNT=$(grep -ci "warning" "$MD_LOG" 2>/dev/null || echo "0")
FAILED_COUNT=$(grep -ci "failed" "$MD_LOG" 2>/dev/null || echo "0")
echo "Errors: $ERROR_COUNT"
echo "Warnings: $WARNING_COUNT"
echo "Failed operations: $FAILED_COUNT"
echo ""

# Show first 10 error lines (if any)
if [ "$ERROR_COUNT" -gt 0 ]; then
    echo "Sample errors:"
    grep -i "error" "$MD_LOG" | head -10 | sed 's/^/  /'
    echo ""
fi

# Extract conversation structure
echo "--- Conversation Structure ---"
SECTION_COUNT=$(grep -c "^##" "$MD_LOG" || echo "0")
echo "Major sections: $SECTION_COUNT"
echo ""
echo "Section headers:"
grep "^##" "$MD_LOG" | head -20 | sed 's/^/  /'
echo ""

# Extract user interactions
echo "--- User Interactions ---"
USER_MESSAGES=$(grep -c "^**User**:" "$MD_LOG" || echo "0")
ASSISTANT_MESSAGES=$(grep -c "^**Assistant**:" "$MD_LOG" || echo "0")
echo "User messages: $USER_MESSAGES"
echo "Assistant messages: $ASSISTANT_MESSAGES"
echo ""

# Tool usage analysis (from NDJSON if provided)
if [ -n "$NDJSON_LOG" ] && [ -f "$NDJSON_LOG" ]; then
    echo "--- Tool Usage (from NDJSON) ---"

    # Extract tool names and count occurrences
    echo "Tool call frequency:"
    grep -o '"tool":"[^"]*"' "$NDJSON_LOG" 2>/dev/null | \
        sed 's/"tool":"//; s/"$//' | \
        sort | uniq -c | sort -rn | \
        awk '{printf "  %-20s %d calls\n", $2, $1}'

    echo ""

    # Total tool calls
    TOOL_CALLS=$(grep -c '"tool":' "$NDJSON_LOG" || echo "0")
    echo "Total tool calls: $TOOL_CALLS"
    echo ""
else
    echo "--- Tool Usage (from Markdown) ---"
    # Fallback: rough estimation from markdown
    BASH_CALLS=$(grep -c "Bash tool" "$MD_LOG" || echo "0")
    READ_CALLS=$(grep -c "Read tool" "$MD_LOG" || echo "0")
    EDIT_CALLS=$(grep -c "Edit tool" "$MD_LOG" || echo "0")
    WRITE_CALLS=$(grep -c "Write tool" "$MD_LOG" || echo "0")

    echo "  Bash:  $BASH_CALLS calls (approximate)"
    echo "  Read:  $READ_CALLS calls (approximate)"
    echo "  Edit:  $EDIT_CALLS calls (approximate)"
    echo "  Write: $WRITE_CALLS calls (approximate)"
    echo ""
    echo "Note: Counts are approximate. Provide .ndjson file for accurate tool stats."
    echo ""
fi

# Decision points and clarifications
echo "--- Communication Patterns ---"
QUESTION_COUNT=$(grep -c "?" "$MD_LOG" || echo "0")
CLARIFICATION_KEYWORDS=$(grep -ci "clarif\|confirm\|verify\|should i\|would you like" "$MD_LOG" || echo "0")
echo "Questions asked: ~$QUESTION_COUNT"
echo "Clarification requests: ~$CLARIFICATION_KEYWORDS"
echo ""

# Code references
echo "--- Code Analysis ---"
FILE_REFS=$(grep -o '`[^`]*\.\(kt\|java\|xml\|gradle\|md\)`' "$MD_LOG" 2>/dev/null | sort -u | wc -l | tr -d ' ' || echo "0")
echo "Unique files referenced: ~$FILE_REFS"
echo ""

# Summary recommendation
echo "==================================="
echo "Recommended Analysis Depth"
echo "==================================="
TOTAL_LINES=$(wc -l < "$MD_LOG")

if [ "$TOTAL_LINES" -lt 500 ]; then
    DEPTH="Quick"
    TIME="5-10 minutes"
elif [ "$TOTAL_LINES" -lt 2000 ]; then
    DEPTH="Standard"
    TIME="15-20 minutes"
else
    DEPTH="Comprehensive"
    TIME="30+ minutes"
fi

echo "Recommended: $DEPTH retrospective (~$TIME)"
echo ""
echo "Rationale:"
echo "  - Log size: $TOTAL_LINES lines"
echo "  - Complexity indicators: $ERROR_COUNT errors, $SECTION_COUNT sections, $USER_MESSAGES user messages"
echo ""

exit 0