---
name: extracting-session-data
description: Locates, lists, filters, and extracts structured data from Claude Code native session logs. Supports both single and multiple session analysis.
---

# Extracting Session Data Skill

## Purpose

This skill provides comprehensive access to Claude Code's native session logs stored in `~/.claude/projects/{project-dir}/{session-id}.jsonl`. It handles:

1. **Location**: Finding session log directories and specific log files
2. **Enumeration**: Listing available sessions with metadata
3. **Extraction**: Pulling structured data (messages, tools, errors, statistics)
4. **Filtering**: Finding sessions matching specific criteria

This skill focuses on **raw data access** - it locates and extracts data with minimal processing. Analysis and interpretation should be performed by the calling skill (e.g., retrospecting).

## When to Use This Skill

Use this skill whenever you need to access Claude Code session logs:

- **Before retrospective analysis**: Locate and list available sessions
- **During data collection**: Extract specific data types (errors, tool usage, etc.)
- **For session discovery**: Find sessions matching criteria (timeframe, branch, keywords)
- **For multi-session analysis**: Compare or aggregate data across multiple sessions

## Core Capabilities

### 1. Locate Session Logs

**Script**: `scripts/locate-logs.sh`

Find the log directory or specific session file path.

```bash
# Get logs directory for current working directory
scripts/locate-logs.sh

# Get logs directory for specific project
scripts/locate-logs.sh /path/to/project

# Get specific session log file
scripts/locate-logs.sh /path/to/project abc123-session-id
```

**When to use**:
- You need the full path to session logs
- You're building dynamic paths for other operations
- You're verifying log files exist before processing

### 2. List Available Sessions

**Script**: `scripts/list-sessions.sh`

Enumerate all sessions with metadata (ID, size, lines, date, branch).

```bash
# List all sessions for current project (table format)
scripts/list-sessions.sh

# List with JSON output
scripts/list-sessions.sh --format json

# List sorted by size
scripts/list-sessions.sh --sort size

# List for specific project
scripts/list-sessions.sh /path/to/project --sort date
```

**Output formats**: `table` (default), `json`, `csv`
**Sort options**: `date` (default), `size`, `lines`

**When to use**:
- Starting a retrospective (show available sessions to user)
- Need session metadata without reading full logs
- Building session selection interface
- Checking for recent sessions

### 3. Extract Structured Data

**Script**: `scripts/extract-data.sh`

Parse JSONL logs and extract specific data types.

**Available extraction types**:
- `metadata` - Session info (ID, timestamps, branch, working dir)
- `user-prompts` - All user messages
- `tool-usage` - Tool call statistics (which tools, how many times)
- `errors` - Failed tool calls with timestamps
- `thinking` - Thinking blocks (if extended thinking enabled)
- `text-responses` - Assistant text responses only
- `statistics` - Session metrics (message counts, tool calls, errors)
- `all` - Combined extraction of key data

```bash
# Extract statistics from current session
scripts/extract-data.sh --type statistics --session abc123

# Extract all errors from all sessions
scripts/extract-data.sh --type errors

# Extract tool usage from specific session
scripts/extract-data.sh --type tool-usage --session abc123

# Get first 10 user prompts
scripts/extract-data.sh --type user-prompts --limit 10

# Extract from different project
scripts/extract-data.sh --type metadata --project /path/to/project
```

**When to use**:
- Need specific data without loading entire log into context
- Generating metrics or statistics
- Identifying errors or patterns
- Extracting user feedback from session

### 4. Filter Sessions

**Script**: `scripts/filter-sessions.sh`

Find sessions matching specific criteria.

**Filter options**:
- `--since DATE` - Sessions modified since date (e.g., "2 days ago", "2025-10-20")
- `--until DATE` - Sessions modified until date
- `--branch NAME` - Sessions on specific git branch
- `--min-size SIZE` - Minimum file size (e.g., "1M", "500K")
- `--max-size SIZE` - Maximum file size
- `--min-lines N` - Minimum line count
- `--max-lines N` - Maximum line count
- `--has-errors` - Only sessions with failed tool calls
- `--keyword WORD` - Sessions containing keyword

```bash
# Recent sessions (last 2 days)
scripts/filter-sessions.sh --since "2 days ago"

# Large sessions with errors
scripts/filter-sessions.sh --min-lines 500 --has-errors

# Sessions on main branch in last week
scripts/filter-sessions.sh --branch main --since "7 days ago"

# Sessions containing "authentication"
scripts/filter-sessions.sh --keyword "authentication"

# Get paths only (for piping to other commands)
scripts/filter-sessions.sh --since "1 day ago" --format paths
```

**Output formats**: `list` (default), `paths`, `json`

**When to use**:
- User requests analysis of recent sessions
- Finding sessions for specific feature or branch
- Identifying problematic sessions (errors, large size)
- Comparing similar sessions across timeframes

## Working Process

### Single Session Analysis

When analyzing one specific session:

```bash
# 1. Verify session exists and get metadata
scripts/extract-data.sh --type metadata --session SESSION_ID

# 2. Get session statistics
scripts/extract-data.sh --type statistics --session SESSION_ID

# 3. Extract specific data as needed
scripts/extract-data.sh --type errors --session SESSION_ID
scripts/extract-data.sh --type tool-usage --session SESSION_ID
```

### Multiple Session Analysis

When analyzing multiple sessions:

```bash
# 1. Filter to find relevant sessions
scripts/filter-sessions.sh --since "7 days ago" --branch main

# 2. Extract data from all filtered sessions (omit --session flag)
scripts/extract-data.sh --type statistics

# 3. Or extract from filtered subset
SESSIONS=$(scripts/filter-sessions.sh --has-errors --format paths)
for session in $SESSIONS; do
    SESSION_ID=$(basename "$session" .jsonl)
    scripts/extract-data.sh --type errors --session $SESSION_ID
done
```

### Integration with Other Skills

When another skill (like retrospecting) needs session data:

1. **Discovery Phase**: Use `list-sessions.sh` or `filter-sessions.sh` to find relevant sessions
2. **Size Check**: Use `extract-data.sh --type statistics` to determine session complexity
3. **Targeted Extraction**: Use `extract-data.sh` with specific types to get needed data
4. **Raw Data Return**: Return extracted data to caller for analysis

## Output Standards

### Raw Data Format

This skill returns **raw extracted data** with minimal formatting:

- **Text output**: One item per line, or structured sections
- **No analysis**: Just data extraction, no interpretation
- **No context consumption**: Use bash tools to process, don't load full logs
- **Streaming-friendly**: Output designed for piping and further processing

Example raw outputs:

```
# Statistics output
Session: abc123
  Total Lines: 450
  User Messages: 12
  Assistant Messages: 23
  Tool Calls: 45
  Errors: 2

# Tool usage output
=== Tool Usage: abc123 ===
Read                          15
Bash                          12
Edit                          8
Grep                          5
Write                         3
```

### When to Load Full Logs

**Avoid loading full session logs into context** when possible. Use bash scripts to extract summaries.

Only read full logs when:
- Session is small (<500 lines)
- Specific content analysis requires it
- User explicitly requests full session review

For large logs (>500 lines):
1. Use `extract-data.sh` to get statistics first
2. Extract specific sections (errors, tool usage)
3. Synthesize extracted data into compact summary
4. Present summary to user, offer to dig deeper if needed

## Context Budget Management

**This skill is designed for context efficiency**:

- Scripts output data to stdout (no Read tool needed)
- Bash processing filters/aggregates before loading context
- Raw data returned for caller to manage context
- Multi-session analysis via sequential bash calls

When calling skill invokes this skill:

```bash
# Good: Extract summary data via bash
STATS=$(scripts/extract-data.sh --type statistics)
# Process $STATS variable, stays in bash context

# Bad: Reading full log files
Read ~/.claude/projects/-path-to-project/session.jsonl
# Loads entire file into context
```

## Error Handling

All scripts exit with non-zero status on errors and output to stderr.

Common error scenarios:

```bash
# Logs directory doesn't exist
scripts/locate-logs.sh /nonexistent/project
# Error: Logs directory not found: ~/.claude/projects/-nonexistent-project

# Session file not found
scripts/extract-data.sh --type metadata --session invalid-id
# Error: Session file not found: ~/.claude/projects/-path/invalid-id.jsonl

# Missing required argument
scripts/extract-data.sh --session abc123
# Error: --type is required

# jq not installed
scripts/extract-data.sh --type metadata --session abc123
# Error: jq is required but not installed. Install with: brew install jq
```

Check exit status in bash:
```bash
if ! scripts/locate-logs.sh /path/to/project &>/dev/null; then
    echo "Project has no session logs"
fi
```

## Dependencies

**Required**:
- `bash` (v4.0+)
- `jq` (for JSON parsing) - Install with `brew install jq`

**Used commands**:
- `find`, `grep`, `wc`, `head`, `tail`, `stat`, `date`, `sort`, `uniq`

All scripts check for `jq` and provide installation instructions if missing.

## Path Calculation Algorithm

Claude Code stores session logs using this pattern:

```
~/.claude/projects/{project-identifier}/{session-id}.jsonl
```

Where `{project-identifier}` is calculated from the working directory:

```bash
# Transform absolute path: replace all / with -
# Example: /Users/user/project → -Users-user-project

PROJECT_ID=$(echo "${PWD}" | sed 's/\//\-/g')
LOGS_DIR="${HOME}/.claude/projects/${PROJECT_ID}"
```

All scripts in this skill use this algorithm consistently via `locate-logs.sh`.

## Anti-Patterns to Avoid

**Don't**:
- Load full session logs into context without checking size first
- Parse JSONL manually - use `extract-data.sh` instead
- Hardcode log paths - use `locate-logs.sh` to calculate dynamically
- Read logs when bash extraction would suffice
- Process large logs synchronously without user awareness

**Do**:
- Check session size with `--type statistics` before processing
- Use appropriate extraction type for your needs
- Filter sessions before extraction for efficiency
- Stream/pipe data when processing multiple sessions
- Inform user about session size and processing time estimates

## Success Criteria

Effective use of this skill means:

1. **Efficient Discovery**: Quickly find relevant sessions without manual searching
2. **Targeted Extraction**: Get exactly the data needed, nothing more
3. **Context Preservation**: Avoid loading unnecessary data into context
4. **Raw Data Focus**: Return unprocessed data for caller to analyze
5. **Multi-Session Support**: Handle analysis across timeframes or branches

## Integration Example

Example of retrospecting skill using this skill:

```bash
# Step 1: List recent sessions
SESSIONS=$(scripts/list-sessions.sh --format json --sort date)

# Step 2: Let user choose session or auto-select latest
LATEST_SESSION=$(echo "$SESSIONS" | jq -r '.[0].sessionId')

# Step 3: Get session size to determine analysis depth
STATS=$(scripts/extract-data.sh --type statistics --session $LATEST_SESSION)
LINE_COUNT=$(echo "$STATS" | grep "Total Lines:" | awk '{print $3}')

# Step 4: Extract appropriate data based on size
if [ "$LINE_COUNT" -lt 500 ]; then
    # Small session: can extract more detail
    ERRORS=$(scripts/extract-data.sh --type errors --session $LATEST_SESSION)
    TOOLS=$(scripts/extract-data.sh --type tool-usage --session $LATEST_SESSION)
    # Analyze extracted data...
else
    # Large session: extract summary only
    SUMMARY=$(scripts/extract-data.sh --type statistics --session $LATEST_SESSION)
    # Present summary, offer targeted deep-dives...
fi
```

This pattern keeps context usage minimal while providing rich data access.
