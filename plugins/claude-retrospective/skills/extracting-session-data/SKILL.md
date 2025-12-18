---
name: extracting-session-data
description: Locates, lists, filters, and extracts structured data from Claude Code native session logs. Supports both single and multiple session analysis.
---

# Extracting Session Data Skill

## Core Responsibility

Provide raw access to Claude Code session logs stored in `~/.claude/projects/{project-dir}/{session-id}.jsonl`.

**Key Principle**: This skill extracts data only - return raw data to calling skills for analysis. Do not analyze or interpret within this skill.

## Available Scripts

All scripts located in `scripts/` subdirectory relative to this skill.

### 1. locate-logs.sh

Find log directory or specific session file path.

```bash
# Get logs directory for current working directory
scripts/locate-logs.sh

# Get logs directory for specific project
scripts/locate-logs.sh /path/to/project

# Get specific session log file path
scripts/locate-logs.sh /path/to/project abc123-session-id
```

**Use when**: Building dynamic paths, verifying logs exist before processing.

### 2. list-sessions.sh

Enumerate all sessions with metadata (ID, size, lines, date, branch).

```bash
# List all sessions (table format)
scripts/list-sessions.sh

# JSON output
scripts/list-sessions.sh --format json

# Sort by size or lines
scripts/list-sessions.sh --sort size
scripts/list-sessions.sh --sort lines

# Specific project
scripts/list-sessions.sh /path/to/project
```

**Output formats**: `table`, `json`, `csv`
**Sort options**: `date`, `size`, `lines`

**Use when**: Starting retrospective, showing available sessions to user, checking for recent sessions.

### 3. extract-data.sh

Parse JSONL logs and extract specific data types.

**Available extraction types**:

- `metadata` - Session info (ID, timestamps, branch, working dir)
- `user-prompts` - All user messages
- `tool-usage` - Tool call statistics
- `errors` - Failed tool calls with timestamps
- `thinking` - Thinking blocks (if extended thinking enabled)
- `text-responses` - Assistant text responses only
- `statistics` - Session metrics (message counts, tool calls, errors)
- `all` - Combined extraction

```bash
# Extract from specific session
scripts/extract-data.sh --type statistics --session SESSION_ID
scripts/extract-data.sh --type errors --session SESSION_ID
scripts/extract-data.sh --type tool-usage --session SESSION_ID

# Extract from all sessions (omit --session)
scripts/extract-data.sh --type statistics

# Limit output
scripts/extract-data.sh --type user-prompts --limit 10

# Different project
scripts/extract-data.sh --type metadata --project /path/to/project
```

**Use when**: Need specific data without loading entire log, generating metrics, identifying errors.

### 4. filter-sessions.sh

Find sessions matching criteria.

**Filter options**:

- `--since DATE` - Sessions modified since date ("2 days ago", "2025-10-20")
- `--until DATE` - Sessions modified until date
- `--branch NAME` - Sessions on specific git branch
- `--min-size SIZE` - Minimum file size ("1M", "500K")
- `--max-size SIZE` - Maximum file size
- `--min-lines N` - Minimum line count
- `--max-lines N` - Maximum line count
- `--has-errors` - Only sessions with failed tool calls
- `--keyword WORD` - Sessions containing keyword

**Output formats**: `list`, `paths`, `json`

```bash
# Recent sessions
scripts/filter-sessions.sh --since "2 days ago"

# Large sessions with errors
scripts/filter-sessions.sh --min-lines 500 --has-errors

# Sessions on main branch in last week
scripts/filter-sessions.sh --branch main --since "7 days ago"

# Sessions containing keyword
scripts/filter-sessions.sh --keyword "authentication"

# Get paths only (for piping)
scripts/filter-sessions.sh --since "1 day ago" --format paths
```

**Use when**: User requests analysis of recent sessions, finding sessions for specific feature/branch, identifying problematic sessions.

## Working Process

### Single Session Analysis

```bash
# 1. Verify session exists and get metadata
scripts/extract-data.sh --type metadata --session SESSION_ID

# 2. Get session statistics (to determine size)
scripts/extract-data.sh --type statistics --session SESSION_ID

# 3. Extract specific data as needed
scripts/extract-data.sh --type errors --session SESSION_ID
scripts/extract-data.sh --type tool-usage --session SESSION_ID
```

### Multiple Session Analysis

```bash
# 1. Filter to find relevant sessions
scripts/filter-sessions.sh --since "7 days ago" --branch main

# 2. Extract data from all filtered sessions
scripts/extract-data.sh --type statistics

# 3. Or iterate through filtered subset
SESSIONS=$(scripts/filter-sessions.sh --has-errors --format paths)
for session in $SESSIONS; do
    SESSION_ID=$(basename "$session" .jsonl)
    scripts/extract-data.sh --type errors --session $SESSION_ID
done
```

### Integration Pattern for Calling Skills

When another skill (like retrospecting) needs session data:

1. **Discovery**: Use `list-sessions.sh` or `filter-sessions.sh` to find relevant sessions
2. **Size Check**: Use `extract-data.sh --type statistics` to determine session complexity
3. **Targeted Extraction**: Use `extract-data.sh` with specific types for needed data
4. **Return Raw Data**: Return extracted data to caller for analysis

**Example**:

```bash
# Get latest session ID
LATEST=$(scripts/list-sessions.sh --format json --sort date | jq -r '.[0].sessionId')

# Check size before processing
STATS=$(scripts/extract-data.sh --type statistics --session $LATEST)
LINE_COUNT=$(echo "$STATS" | grep "Total Lines:" | awk '{print $3}')

# Extract based on size
if [ "$LINE_COUNT" -lt 500 ]; then
    # Small session: extract detail
    scripts/extract-data.sh --type errors --session $LATEST
    scripts/extract-data.sh --type tool-usage --session $LATEST
else
    # Large session: summary only
    scripts/extract-data.sh --type statistics --session $LATEST
fi
```

## Context Budget Management

**CRITICAL: This skill is designed for context efficiency**

### Use Bash Processing, Not Read Tool

```bash
# GOOD: Extract via bash, stays in bash context
STATS=$(scripts/extract-data.sh --type statistics)
# Process $STATS in bash

# BAD: Reading full log files
Read ~/.claude/projects/-path/session.jsonl
# Loads entire file into context unnecessarily
```

### Check Session Size Before Loading

**Never load full session logs into context without checking size first.**

```bash
# Always check statistics first
scripts/extract-data.sh --type statistics --session SESSION_ID
# Shows total lines, message counts, etc.

# Decision rules:
# - Small (<500 lines): Can extract detail safely
# - Medium (500-2000 lines): Use selective extraction
# - Large (>2000 lines): Statistics only, offer targeted deep-dives
```

### Return Raw Data to Caller

This skill should:

- Execute bash scripts to extract data
- Return raw text output to calling skill
- Let calling skill manage context for analysis
- Avoid interpretation or analysis within this skill

## Output Format

Return **raw extracted data** with minimal formatting:

```
# Statistics output
Session: abc123-def456-ghi789
  Total Lines: 450
  User Messages: 12
  Assistant Messages: 23
  Tool Calls: 45
  Errors: 2

# Tool usage output
=== Tool Usage: abc123-def456-ghi789 ===
Read                          15
Bash                          12
Edit                          8
Grep                          5
Write                         3
```

No analysis, no interpretation - just data extraction.

## Error Handling

All scripts exit with non-zero status on errors and output to stderr.

Check exit status before processing:

```bash
if ! scripts/locate-logs.sh /path/to/project &>/dev/null; then
    # Handle: logs directory doesn't exist
    echo "Project has no session logs yet"
fi

if ! scripts/extract-data.sh --type metadata --session abc123 &>/dev/null; then
    # Handle: session doesn't exist
    echo "Session not found"
fi
```

Common error messages:

- `Error: Logs directory not found: ~/.claude/projects/-path`
- `Error: Session file not found: ~/.claude/projects/-path/session-id.jsonl`
- `Error: --type is required`
- `Error: jq is required but not installed. Install with: brew install jq`

## Path Calculation

Claude Code stores sessions using this pattern:

```
~/.claude/projects/{project-identifier}/{session-id}.jsonl
```

Where `{project-identifier}` is calculated by replacing all `/` with `-` in the absolute working directory path:

```bash
# Example: /Users/user/project → -Users-user-project
PROJECT_ID=$(echo "${PWD}" | sed 's/\//\-/g')
LOGS_DIR="${HOME}/.claude/projects/${PROJECT_ID}"
```

All scripts use `locate-logs.sh` internally for consistent path calculation.

## Anti-Patterns to Avoid

**Don't**:

- Load full session logs into context without checking size
- Parse JSONL manually - use `extract-data.sh`
- Hardcode log paths - use `locate-logs.sh`
- Analyze or interpret data - return raw data to caller
- Process large logs synchronously without user awareness

**Do**:

- Check session size with `--type statistics` before processing
- Use appropriate extraction type for specific needs
- Filter sessions before extraction for efficiency
- Stream/pipe data when processing multiple sessions
- Return raw data for caller to analyze

## Success Criteria

Effective use of this skill means:

1. **Efficient Discovery**: Quickly find relevant sessions without manual searching
2. **Targeted Extraction**: Get exactly the data needed, nothing more
3. **Context Preservation**: Avoid loading unnecessary data into context
4. **Raw Data Focus**: Return unprocessed data for caller to analyze
5. **Multi-Session Support**: Handle analysis across timeframes or branches efficiently

## Dependencies

**Required**:

- `bash` (v4.0+)
- `jq` (JSON parser)

Scripts check for `jq` and provide installation instructions if missing:

```
Error: jq is required but not installed. Install with: brew install jq
```
