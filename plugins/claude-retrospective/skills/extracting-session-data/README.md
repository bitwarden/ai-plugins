

# Extracting Session Data Skill

Locates, lists, filters, and extracts structured data from Claude Code session logs. Designed for efficient access to single or multiple sessions.

## What It Does

This skill provides programmatic access to Claude Code's native session logs stored in:
```
~/.claude/projects/{project-dir}/{session-id}.jsonl
```

It can:
- **Locate** session log directories and files
- **List** available sessions with metadata (size, date, branch)
- **Extract** specific data (errors, tool usage, messages, statistics)
- **Filter** sessions by criteria (timeframe, branch, errors, keywords)

## When to Use

You typically won't invoke this skill directly. Other skills (like `retrospecting`) use it behind the scenes to access session data efficiently.

However, you might invoke it directly when you want to:
- See what sessions are available
- Find sessions from a specific timeframe or branch
- Extract specific data (like all errors from recent sessions)
- Check session sizes before analysis

### Example Invocations

```
Can you list all my Claude sessions from the last week?
Show me which sessions had errors
What sessions are available for this project?
Extract tool usage statistics from my last session
```

## What to Expect

### Process Flow

When you request session data, the skill will:

1. **Locate** your project's session logs directory
2. **Filter or list** sessions based on your criteria
3. **Extract** the requested data type
4. **Return** raw data for analysis or presentation

### Output Format

This skill returns **raw data** rather than analyzed insights:

```
Session: abc123-def456-ghi789
  Total Lines: 450
  User Messages: 12
  Assistant Messages: 23
  Tool Calls: 45
  Errors: 2
```

Other skills (like retrospecting) interpret this data to generate insights.

## Available Operations

### 1. List Sessions

See all available sessions for your project:

```bash
# Shows table with session IDs, sizes, line counts, dates, and branches
scripts/list-sessions.sh
```

### 2. Filter Sessions

Find sessions matching specific criteria:

```bash
# Recent sessions
scripts/filter-sessions.sh --since "2 days ago"

# Sessions with errors
scripts/filter-sessions.sh --has-errors

# Sessions on specific branch
scripts/filter-sessions.sh --branch main

# Large sessions
scripts/filter-sessions.sh --min-lines 500
```

### 3. Extract Data

Pull specific information from sessions:

```bash
# Session metadata
scripts/extract-data.sh --type metadata --session SESSION_ID

# Statistics (message counts, tool calls, errors)
scripts/extract-data.sh --type statistics --session SESSION_ID

# All errors
scripts/extract-data.sh --type errors --session SESSION_ID

# Tool usage statistics
scripts/extract-data.sh --type tool-usage --session SESSION_ID

# User prompts
scripts/extract-data.sh --type user-prompts --session SESSION_ID
```

## File Organization

```
plugins/claude-retrospective/skills/extracting-session-data/
├── README.md                  # This file (user documentation)
├── SKILL.md                   # Instructions for Claude
└── scripts/
    ├── locate-logs.sh         # Find log directories and files
    ├── list-sessions.sh       # Enumerate sessions with metadata
    ├── extract-data.sh        # Extract structured data from logs
    └── filter-sessions.sh     # Filter sessions by criteria
```

Session logs themselves are stored by Claude Code in:
```
~/.claude/projects/{project-dir}/{session-id}.jsonl
```

## How Session Paths Work

Claude Code calculates the log directory from your working directory:

1. Take the absolute working directory path
2. Replace all `/` with `-`
3. Store logs in `~/.claude/projects/{transformed-path}/`

**Example**:
```
Working Directory: /Users/you/projects/myapp
Project Identifier: -Users-you-projects-myapp
Logs Directory: ~/.claude/projects/-Users-you-projects-myapp/
```

All scripts in this skill handle this transformation automatically.

## Use Cases

### For Users

**"What sessions are available?"**
```
List all sessions: scripts/list-sessions.sh
```

**"Show me recent sessions with errors"**
```
scripts/filter-sessions.sh --since "7 days ago" --has-errors
```

**"How much data is in my last session?"**
```
scripts/extract-data.sh --type statistics --session SESSION_ID
```

### For Skills Integration

**Retrospective Skill** uses this skill to:
- List available sessions for user selection
- Check session sizes before processing
- Extract errors, tool usage, and statistics
- Filter sessions by timeframe or branch

**Future Skills** could use it to:
- Compare sessions across time
- Generate usage reports
- Debug specific session issues
- Archive or export session data

## Requirements

### Dependencies

- **bash** (v4.0+)
- **jq** (JSON parser) - Install with `brew install jq`

If `jq` is not installed, scripts will display installation instructions.

### Session Logs

This skill requires Claude Code's native session logs. These are automatically created by Claude Code when you use it. No manual setup needed.

## Privacy & Security

### What Data is Accessed

- Session log files in `~/.claude/projects/`
- Contains all messages, tool calls, and responses from sessions
- Stored locally on your machine

### Data Storage

- No data is sent to external services
- All processing happens locally
- Scripts only read logs, never modify them
- Extracted data stays in your terminal session unless you save it

### Sensitive Information

If your sessions contained sensitive data:
- Session logs are stored locally only
- You control access to `~/.claude/projects/` directory
- Be cautious when sharing extracted data
- Consider project-specific access controls

## Troubleshooting

### "Logs directory not found"

**Cause**: No sessions exist for the current project yet, or you're in a different directory.

**Solution**:
- Check you're in the correct project directory
- Verify Claude Code has been used in this project
- Manually check: `ls ~/.claude/projects/`

### "Session file not found"

**Cause**: Session ID doesn't exist or is incorrect.

**Solution**:
- List available sessions: `scripts/list-sessions.sh`
- Copy exact session ID from the list
- Ensure you're in the correct project directory

### "jq is required but not installed"

**Cause**: The `jq` JSON parser is not installed.

**Solution**:
```bash
# macOS
brew install jq

# Linux (Ubuntu/Debian)
sudo apt-get install jq

# Linux (Fedora/RHEL)
sudo dnf install jq
```

### "No sessions match the specified criteria"

**Cause**: Filter criteria are too restrictive.

**Solution**:
- Broaden criteria (e.g., longer timeframe)
- List all sessions first: `scripts/list-sessions.sh`
- Check filter syntax in help: `scripts/filter-sessions.sh --help`

## Examples

### Example 1: Finding Recent Work

**Goal**: See what you've worked on in the last 3 days

```bash
scripts/filter-sessions.sh --since "3 days ago"
```

**Output**:
```
Found 5 matching session(s):

Session: abc123...
  Size: 2.5M
  Lines: 1250
  Modified: 2025-10-24 14:30:00
  Branch: feature/auth

Session: def456...
  Size: 1.2M
  Lines: 600
  Modified: 2025-10-23 09:15:00
  Branch: main
...
```

### Example 2: Investigating Errors

**Goal**: Find all sessions with errors and see what failed

```bash
# Find sessions with errors
scripts/filter-sessions.sh --has-errors --since "7 days ago"

# Extract errors from specific session
scripts/extract-data.sh --type errors --session abc123
```

### Example 3: Comparing Tool Usage

**Goal**: See which tools you use most often

```bash
# Get tool usage from multiple recent sessions
for session in $(scripts/filter-sessions.sh --since "7 days ago" --format paths | xargs -n1 basename -s .jsonl); do
    echo "Session: $session"
    scripts/extract-data.sh --type tool-usage --session $session
    echo ""
done
```

## Integration with Other Skills

This skill is designed as a **utility skill** for other skills to use:

### Retrospecting Skill

Uses extracting-session-data to:
1. List available sessions for user selection
2. Check session complexity (size, line count)
3. Extract errors, tool calls, and statistics
4. Avoid loading large logs into context unnecessarily

### Future Session Analysis Skills

Could use extracting-session-data to:
- Compare productivity across sessions
- Track tool usage trends over time
- Identify recurring error patterns
- Generate session summaries

## Tips for Best Results

### Efficient Filtering

**Be specific** with filters to reduce processing:
```bash
# Good: Narrow scope
scripts/filter-sessions.sh --branch main --since "2 days ago" --has-errors

# Less efficient: Processes all sessions
scripts/filter-sessions.sh
```

### Check Size First

**Before extracting** from multiple sessions, check sizes:
```bash
scripts/list-sessions.sh --sort size
```

This helps you understand how much data you're working with.

### Use Appropriate Extraction Types

**Don't extract everything** if you only need specific data:
```bash
# Good: Targeted extraction
scripts/extract-data.sh --type statistics

# Less efficient: Extract all data
scripts/extract-data.sh --type all
```

## Future Enhancements

Planned improvements:
- Parallel processing for multi-session extraction
- Compressed session log support
- Export to standardized formats (CSV, JSON)
- Session comparison utilities
- Trend analysis across sessions

## Feedback

Found an issue or have a suggestion?
- Modify scripts in `scripts/` directory
- Update SKILL.md for Claude's instructions
- Update this README.md for user documentation
