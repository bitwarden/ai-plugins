# Session Logging Architecture

## Overview

The claude-retrospective plugin leverages Claude Code's native session logging for retrospective analysis. No custom hooks are required.

## Architecture

Claude Code automatically logs all session activity to:
```
~/.claude/projects/{project-dir}/{session-id}.jsonl
```

The retrospective skill reads these native logs to perform comprehensive session analysis.

## Native Log Capabilities

Claude's session logs capture:
- **User prompts**: Every message sent by the user
- **Assistant responses**: All text, thinking blocks, and tool invocations
- **Tool execution**: Tool inputs, outputs, and error states
- **Session metadata**: Timestamps, git context, working directory
- **Conversation flow**: Parent-child relationships between messages

## Log Format

JSONL format (newline-delimited JSON) with one message per line:

```json
{
  "type": "user" | "assistant" | "file-history-snapshot",
  "sessionId": "uuid",
  "timestamp": "ISO-8601",
  "cwd": "/working/directory",
  "gitBranch": "branch-name",
  "message": {
    "role": "user" | "assistant",
    "content": "string" | [{"type": "text|thinking|tool_use|tool_result", ...}]
  },
  "parentUuid": "uuid"
}
```

## Data Sources for Retrospective

The retrospective skill combines multiple data sources:

- ✅ **Git history**: Commits, diffs, file changes during session
- ✅ **Claude logs**: Native session logs from `~/.claude/projects/`
- ✅ **Project files**: Test coverage, code quality, compilation status
- ✅ **User feedback**: Direct input about goals and satisfaction
- ✅ **Sub-agent interactions**: When sub-agents were used, their feedback

## Processing Examples

### Bash
```bash
# Find project directory
PROJECT_DIR=$(echo "${PWD}" | sed 's/\//-/g')

# Count user prompts
grep -c '"type":"user"' ~/.claude/projects/${PROJECT_DIR}/<session-id>.jsonl

# Extract tool usage
grep '"type":"assistant"' session.jsonl | jq -r '.message.content[]? | select(.type=="tool_use") | .name' | sort | uniq -c

# Find errors
grep '"is_error":true' session.jsonl
```

### Python
```python
import json

def read_session_log(session_path):
    events = []
    with open(session_path, 'r') as f:
        for line in f:
            events.append(json.loads(line.strip()))
    return events

def count_tool_uses(events):
    tool_uses = {}
    for event in events:
        if event.get('type') == 'assistant':
            content = event.get('message', {}).get('content', [])
            if isinstance(content, list):
                for item in content:
                    if item.get('type') == 'tool_use':
                        tool_name = item.get('name', 'unknown')
                        tool_uses[tool_name] = tool_uses.get(tool_name, 0) + 1
    return tool_uses
```

## Integration with Retrospective Skill

The retrospective skill workflow:

1. **User triggers**: "Run a retrospective on this session"
2. **Scope definition**: Identify session timeframe or commit range
3. **Data collection**: Read native logs, git history, project files
4. **Analysis**: Calculate metrics, identify patterns, extract insights
5. **Report generation**: Create comprehensive retrospective report
6. **Validation**: Gather user feedback on findings

## Benefits

### Reliability
- **Always available**: Native logs are core Claude Code functionality
- **High fidelity**: Complete capture of all session activity
- **No overhead**: Zero performance impact (no custom hooks)
- **Consistent format**: Stable log structure across versions

### Completeness
- **Full conversation**: Every user prompt and assistant response
- **Tool tracking**: All tool invocations with inputs and outputs
- **Error capture**: Failed operations and error messages
- **Context preservation**: Git state, working directory, timestamps
- **Thinking blocks**: When enabled, captures reasoning process

### Analysis Power
- **Quantitative metrics**: Tool usage counts, timing, success rates
- **Qualitative insights**: Full conversation context for pattern analysis
- **Workflow optimization**: Identify bottlenecks and inefficiencies
- **Learning opportunities**: Understand successful approaches and anti-patterns

## Usage

### Automatic Operation
Claude Code logs sessions automatically. No setup or configuration required.

### Retrospective Analysis
```
User: "Run a retrospective on the last 2 hours"
Claude: [Invokes retrospective skill]
        [Reads native session logs]
        [Analyzes git history]
        [Calculates metrics]
        [Generates comprehensive report with insights]
```

### Manual Analysis
```bash
# View session log
PROJ_DIR=$(echo "${PWD}" | sed 's/\//-/g')
cat ~/.claude/projects/${PROJ_DIR}/<session-id>.jsonl | jq

# Extract user prompts
grep '"type":"user"' session.jsonl | jq -r '.message.content'

# Count assistant responses
grep -c '"type":"assistant"' session.jsonl
```

## Documentation

- **[README.md](README.md)**: Usage guide and log format reference
- **[VERIFICATION.md](VERIFICATION.md)**: Verification steps
- **[retrospecting SKILL.md](../skills/retrospecting/SKILL.md)**: Detailed retrospective workflow

---

**Status**: ✅ Ready to Use

The retrospective plugin uses Claude Code's native logging infrastructure for comprehensive session analysis.
