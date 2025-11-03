#!/bin/bash
# Session Log Analysis Script
# Quickly extracts key metrics from Claude Code native session logs
# Usage: ./analyze-session-logs.sh <session-id.jsonl>

set -e

if [ $# -lt 1 ]; then
    echo "Usage: $0 <session-log.jsonl>"
    echo ""
    echo "Analyzes Claude Code native session logs and outputs structured summary."
    echo ""
    echo "Arguments:"
    echo "  session-log.jsonl  - Claude Code native session log (JSONL format)"
    echo ""
    echo "Example:"
    echo "  PROJECT_DIR=\$(echo \"\${PWD}\" | sed 's/\\//-/g')"
    echo "  LATEST_LOG=\$(ls -t ~/.claude/projects/\${PROJECT_DIR}/*.jsonl | head -1)"
    echo "  $0 \"\$LATEST_LOG\""
    exit 1
fi

JSONL_LOG="$1"

if [ ! -f "$JSONL_LOG" ]; then
    echo "Error: File not found: $JSONL_LOG"
    exit 1
fi

# Check if jq is available
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed. Install with: brew install jq"
    exit 1
fi

echo "==================================="
echo "Session Log Analysis"
echo "==================================="
echo ""
echo "File: $JSONL_LOG"
echo "Size: $(wc -l < "$JSONL_LOG") lines ($(du -h "$JSONL_LOG" | cut -f1))"
echo ""

# Extract session metadata
echo "--- Session Metadata ---"
SESSION_ID=$(head -1 "$JSONL_LOG" | jq -r '.sessionId // "unknown"')
GIT_BRANCH=$(head -1 "$JSONL_LOG" | jq -r '.gitBranch // "unknown"')
WORKING_DIR=$(head -1 "$JSONL_LOG" | jq -r '.cwd // "unknown"')
FIRST_TIMESTAMP=$(head -1 "$JSONL_LOG" | jq -r '.timestamp // "unknown"')
LAST_TIMESTAMP=$(tail -1 "$JSONL_LOG" | jq -r '.timestamp // "unknown"')

echo "Session ID: $SESSION_ID"
echo "Git Branch: $GIT_BRANCH"
echo "Working Directory: $WORKING_DIR"
echo "First event: $FIRST_TIMESTAMP"
echo "Last event: $LAST_TIMESTAMP"
echo ""

# Count message types
echo "--- Message Statistics ---"
TOTAL_LINES=$(wc -l < "$JSONL_LOG")
USER_MESSAGES=$(grep -c '"type":"user"' "$JSONL_LOG" 2>/dev/null || echo "0")
ASSISTANT_MESSAGES=$(grep -c '"type":"assistant"' "$JSONL_LOG" 2>/dev/null || echo "0")
FILE_SNAPSHOTS=$(grep -c '"type":"file-history-snapshot"' "$JSONL_LOG" 2>/dev/null || echo "0")

echo "Total lines: $TOTAL_LINES"
echo "User messages: $USER_MESSAGES"
echo "Assistant messages: $ASSISTANT_MESSAGES"
echo "File snapshots: $FILE_SNAPSHOTS"
echo ""

# Extract user prompts
echo "--- User Prompts ---"
echo "First 3 user prompts:"
grep '"type":"user"' "$JSONL_LOG" | head -3 | jq -r '.message.content' | head -c 200 | while IFS= read -r line; do
    echo "  $line"
done
echo ""

# Tool usage analysis
echo "--- Tool Usage ---"
echo "Tool call frequency:"
grep '"type":"assistant"' "$JSONL_LOG" | \
    jq -r '.message.content[]? | select(.type=="tool_use") | .name' 2>/dev/null | \
    sort | uniq -c | sort -rn | \
    awk '{printf "  %-20s %d calls\n", $2, $1}'

TOTAL_TOOL_CALLS=$(grep '"type":"assistant"' "$JSONL_LOG" | \
    jq -r '.message.content[]? | select(.type=="tool_use") | .name' 2>/dev/null | wc -l | tr -d ' ')
echo ""
echo "Total tool calls: $TOTAL_TOOL_CALLS"
echo ""

# Error analysis
echo "--- Error Analysis ---"
ERROR_COUNT=$(grep -c '"is_error":true' "$JSONL_LOG" 2>/dev/null || echo "0")
echo "Failed tool calls: $ERROR_COUNT"

if [ "$ERROR_COUNT" -gt 0 ]; then
    echo ""
    echo "Sample errors (first 5):"
    grep '"is_error":true' "$JSONL_LOG" | head -5 | jq -r '.message.content[]? | select(.is_error==true) | .content' 2>/dev/null | head -c 500 | sed 's/^/  /'
fi
echo ""

# Thinking blocks (if enabled)
echo "--- Thinking Blocks ---"
THINKING_BLOCKS=$(grep '"type":"assistant"' "$JSONL_LOG" | \
    jq -r '.message.content[]? | select(.type=="thinking")' 2>/dev/null | wc -l | tr -d ' ')
echo "Thinking blocks captured: $THINKING_BLOCKS"
echo ""

# Communication patterns
echo "--- Communication Patterns ---"
# Count text responses
TEXT_RESPONSES=$(grep '"type":"assistant"' "$JSONL_LOG" | \
    jq -r '.message.content[]? | select(.type=="text") | .text' 2>/dev/null | wc -l | tr -d ' ')
echo "Text responses: $TEXT_RESPONSES"
echo ""

# Session complexity assessment
echo "==================================="
echo "Recommended Analysis Depth"
echo "==================================="

COMPLEXITY_SCORE=0

# Factor 1: Number of interactions
if [ "$USER_MESSAGES" -gt 20 ]; then
    COMPLEXITY_SCORE=$((COMPLEXITY_SCORE + 2))
elif [ "$USER_MESSAGES" -gt 10 ]; then
    COMPLEXITY_SCORE=$((COMPLEXITY_SCORE + 1))
fi

# Factor 2: Tool usage
if [ "$TOTAL_TOOL_CALLS" -gt 50 ]; then
    COMPLEXITY_SCORE=$((COMPLEXITY_SCORE + 2))
elif [ "$TOTAL_TOOL_CALLS" -gt 20 ]; then
    COMPLEXITY_SCORE=$((COMPLEXITY_SCORE + 1))
fi

# Factor 3: Errors
if [ "$ERROR_COUNT" -gt 5 ]; then
    COMPLEXITY_SCORE=$((COMPLEXITY_SCORE + 2))
elif [ "$ERROR_COUNT" -gt 0 ]; then
    COMPLEXITY_SCORE=$((COMPLEXITY_SCORE + 1))
fi

# Factor 4: Log size
if [ "$TOTAL_LINES" -gt 500 ]; then
    COMPLEXITY_SCORE=$((COMPLEXITY_SCORE + 2))
elif [ "$TOTAL_LINES" -gt 200 ]; then
    COMPLEXITY_SCORE=$((COMPLEXITY_SCORE + 1))
fi

# Determine depth
if [ "$COMPLEXITY_SCORE" -le 2 ]; then
    DEPTH="Quick"
    TIME="5-10 minutes"
elif [ "$COMPLEXITY_SCORE" -le 5 ]; then
    DEPTH="Standard"
    TIME="15-20 minutes"
else
    DEPTH="Comprehensive"
    TIME="30+ minutes"
fi

echo "Recommended: $DEPTH retrospective (~$TIME)"
echo ""
echo "Rationale:"
echo "  - Complexity score: $COMPLEXITY_SCORE/8"
echo "  - User messages: $USER_MESSAGES"
echo "  - Tool calls: $TOTAL_TOOL_CALLS"
echo "  - Errors: $ERROR_COUNT"
echo "  - Log lines: $TOTAL_LINES"
echo ""

exit 0
