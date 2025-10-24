# Verification Guide: Claude Retrospective Plugin

## Quick Verification

The claude-retrospective plugin uses Claude Code's native session logs. This verification confirms that:
1. Claude's native logs are accessible
2. The retrospective skill can read them
3. Log format is as expected

### 1. Verify Claude's Native Logs Exist

```bash
# Find project directory (sanitized path)
PROJECT_DIR=$(echo "${PWD}" | sed 's/\//-/g')

# List session logs
ls -lh ~/.claude/projects/${PROJECT_DIR}/*.jsonl | tail -5
```

You should see `.jsonl` files with recent timestamps.

### 2. Inspect Current Session Log

```bash
# Find current session ID (from environment or recent file)
PROJECT_DIR=$(echo "${PWD}" | sed 's/\//-/g')
LATEST_LOG=$(ls -t ~/.claude/projects/${PROJECT_DIR}/*.jsonl | head -1)

echo "Latest session log: $LATEST_LOG"
wc -l "$LATEST_LOG"
```

The log should contain multiple lines (one JSON object per line).

### 3. Verify Log Contents

```bash
# Get project directory
PROJECT_DIR=$(echo "${PWD}" | sed 's/\//-/g')
LATEST_LOG=$(ls -t ~/.claude/projects/${PROJECT_DIR}/*.jsonl | head -1)

# Check for required fields
echo "Checking log structure..."
head -1 "$LATEST_LOG" | jq 'keys'

# Count message types
echo -e "\nMessage types:"
echo "  User messages: $(grep -c '"type":"user"' "$LATEST_LOG")"
echo "  Assistant messages: $(grep -c '"type":"assistant"' "$LATEST_LOG")"

# Check for tool uses
echo -e "\nTool usage:"
grep '"type":"assistant"' "$LATEST_LOG" | jq -r '.message.content[]? | select(.type=="tool_use") | .name' | sort | uniq -c
```

Expected output:
- Log should contain valid JSON on each line
- Should show counts for user and assistant messages
- Tool usage should show tools used in this session

### 4. Verify Log Format

```bash
# Examine a complete message
PROJECT_DIR=$(echo "${PWD}" | sed 's/\//-/g')
LATEST_LOG=$(ls -t ~/.claude/projects/${PROJECT_DIR}/*.jsonl | head -1)

# Show first user message
grep '"type":"user"' "$LATEST_LOG" | head -1 | jq '.'
```

Should show structure:
```json
{
  "type": "user",
  "sessionId": "uuid",
  "timestamp": "ISO-8601",
  "cwd": "/working/directory",
  "gitBranch": "branch-name",
  "message": {
    "role": "user",
    "content": "user prompt text"
  }
}
```

## What Should Be Logged

Claude's native logs capture:

1. ✅ **User prompts**: Every message you send
2. ✅ **Assistant responses**: All text, thinking blocks, tool invocations
3. ✅ **Tool execution**: Tool inputs, outputs, and error states
4. ✅ **Session metadata**: Timestamps, git context, working directory
5. ✅ **Conversation flow**: Parent-child message relationships

## Manual Verification Steps

### Check Event Counts

```bash
PROJECT_DIR=$(echo "${PWD}" | sed 's/\//-/g')
LATEST_LOG=$(ls -t ~/.claude/projects/${PROJECT_DIR}/*.jsonl | head -1)

echo "Session statistics:"
echo "- User prompts: $(grep -c '"type":"user"' "$LATEST_LOG")"
echo "- Assistant responses: $(grep -c '"type":"assistant"' "$LATEST_LOG")"
echo "- Total lines: $(wc -l < "$LATEST_LOG")"
echo "- File size: $(du -h "$LATEST_LOG" | cut -f1)"
```

### Verify Tool Tracking

```bash
PROJECT_DIR=$(echo "${PWD}" | sed 's/\//-/g')
LATEST_LOG=$(ls -t ~/.claude/projects/${PROJECT_DIR}/*.jsonl | head -1)

# Show tool usage statistics
echo "Tools used in this session:"
grep '"type":"assistant"' "$LATEST_LOG" | \
  jq -r '.message.content[]? | select(.type=="tool_use") | .name' | \
  sort | uniq -c | sort -rn
```

### Verify Error Tracking

```bash
PROJECT_DIR=$(echo "${PWD}" | sed 's/\//-/g')
LATEST_LOG=$(ls -t ~/.claude/projects/${PROJECT_DIR}/*.jsonl | head -1)

# Check for errors
echo "Errors in session:"
grep '"is_error":true' "$LATEST_LOG" | wc -l
```

### Verify Thinking Blocks (if enabled)

```bash
PROJECT_DIR=$(echo "${PWD}" | sed 's/\//-/g')
LATEST_LOG=$(ls -t ~/.claude/projects/${PROJECT_DIR}/*.jsonl | head -1)

# Check for thinking blocks
echo "Thinking blocks in session:"
grep '"type":"assistant"' "$LATEST_LOG" | \
  jq -r '.message.content[]? | select(.type=="thinking")' | \
  wc -l
```

## Troubleshooting

### No Logs Found

**Issue**: `ls ~/.claude/projects/${PROJECT_DIR}/*.jsonl` returns no files

**Possible causes**:
1. Project directory path sanitization is incorrect
2. This is the first session in this project
3. Claude Code version doesn't support native logging

**Solution**:
```bash
# List all project directories
ls ~/.claude/projects/

# Manually find your project
find ~/.claude/projects/ -name "*.jsonl" | head -5
```

### Logs Are Empty

**Issue**: Log files exist but have zero lines

**Possible cause**: Session just started, no activity yet

**Solution**: Wait for session activity (send a prompt, use a tool) and check again

### JSON Parse Errors

**Issue**: `jq` reports JSON parsing errors

**Possible cause**: Log file is being written while reading

**Solution**: Copy log file first, then parse
```bash
cp "$LATEST_LOG" /tmp/session.jsonl
cat /tmp/session.jsonl | jq
```

### Cannot Find Current Session

**Issue**: Don't know which log file corresponds to current session

**Solution**: Use most recent file by modification time
```bash
PROJECT_DIR=$(echo "${PWD}" | sed 's/\//-/g')
ls -t ~/.claude/projects/${PROJECT_DIR}/*.jsonl | head -1
```

## Performance Considerations

Claude's native logs are maintained by Claude Code with minimal overhead:
- Automatic log management
- No custom hook execution
- Efficient JSONL format
- Logs are written asynchronously

To check log sizes:
```bash
PROJECT_DIR=$(echo "${PWD}" | sed 's/\//-/g')
du -sh ~/.claude/projects/${PROJECT_DIR}/
```

## Success Criteria

✅ **Plugin is working correctly if**:

1. `~/.claude/projects/{project-dir}/` contains `.jsonl` files
2. Latest log file has recent modification time
3. Log contains user and assistant messages
4. JSON structure matches expected format
5. Tool usage is tracked in assistant messages
6. Retrospective skill can read and parse logs

## Testing Retrospective Skill

Once logs are verified, test the retrospective skill:

```
User: "Show me the current session ID"
Claude: [Provides session ID from environment]

User: "Run a retrospective on this session"
Claude: [Invokes retrospective skill]
        [Reads native session logs]
        [Analyzes git history]
        [Generates comprehensive report]
```

## Quick Verification One-Liner

```bash
PROJECT_DIR=$(echo "${PWD}" | sed 's/\//-/g') && \
LATEST=$(ls -t ~/.claude/projects/${PROJECT_DIR}/*.jsonl 2>/dev/null | head -1) && \
echo "Latest session: $(basename $LATEST)" && \
echo "Size: $(du -h "$LATEST" | cut -f1)" && \
echo "User prompts: $(grep -c '"type":"user"' "$LATEST")" && \
echo "Assistant responses: $(grep -c '"type":"assistant"' "$LATEST")" && \
echo "✅ Claude native logs verified!"
```

## Next Steps

Once verified:

1. **Use the retrospective skill**: "Run a retrospective on the last 2 hours"
2. **Analyze logs manually**: Parse JSONL for custom metrics
3. **Build on this**: Create additional analysis tools using log data
