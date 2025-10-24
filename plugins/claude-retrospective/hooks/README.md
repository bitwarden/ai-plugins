# Claude Retrospective Hooks

## Overview

The claude-retrospective plugin uses Claude Code's native session logs for retrospective analysis. No custom hooks are required.

## Claude Native Session Logs

Claude Code automatically logs all session data to:
```
~/.claude/projects/{project-dir}/{session-id}.jsonl
```

These logs contain:
- User prompts
- Assistant responses (including thinking blocks when enabled)
- Tool usage with inputs and outputs
- Error states
- Timestamps and git context
- Session metadata

## Log Format

Each line in the JSONL file is a JSON object:

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
  }
}
```

**Key fields:**
- **User messages**: `type:"user"`, `message.content` contains prompt
- **Assistant responses**: `type:"assistant"`, `message.content` array with text/thinking/tool_use
- **Tool results**: Embedded in assistant messages as `tool_result` content blocks
- **Thinking blocks**: When enabled, appear as `type:"thinking"` in content array

## Processing Session Logs

### Bash Examples

```bash
# Find project directory (paths are sanitized with / replaced by -)
PROJECT_DIR=$(echo "${PWD}" | sed 's/\//-/g')

# List available sessions
ls ~/.claude/projects/${PROJECT_DIR}/*.jsonl

# Count user prompts
grep -c '"type":"user"' session.jsonl

# Count assistant responses
grep -c '"type":"assistant"' session.jsonl

# Extract tool usage statistics
grep '"type":"assistant"' session.jsonl | jq -r '.message.content[]? | select(.type=="tool_use") | .name' | sort | uniq -c

# Find errors
grep '"is_error":true' session.jsonl

# Get user prompts
grep '"type":"user"' session.jsonl | jq -r '.message.content'

# Get assistant text responses
grep '"type":"assistant"' session.jsonl | jq -r '.message.content[] | select(.type=="text") | .text'
```

### Python Examples

```python
import json
from pathlib import Path

def read_session_log(session_path):
    """Read and parse Claude native session log."""
    events = []
    with open(session_path, 'r') as f:
        for line in f:
            events.append(json.loads(line.strip()))
    return events

def count_tool_uses(events):
    """Count tool usage from session events."""
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

def extract_conversation(events):
    """Extract user prompts and assistant responses."""
    conversation = []
    for event in events:
        if event.get('type') == 'user':
            conversation.append({
                'role': 'user',
                'content': event.get('message', {}).get('content', ''),
                'timestamp': event.get('timestamp')
            })
        elif event.get('type') == 'assistant':
            content = event.get('message', {}).get('content', [])
            if isinstance(content, list):
                text_parts = [c.get('text', '') for c in content if c.get('type') == 'text']
                conversation.append({
                    'role': 'assistant',
                    'content': '\n'.join(text_parts),
                    'timestamp': event.get('timestamp')
                })
    return conversation
```

## For Plugin Developers

See the [retrospecting SKILL.md](../skills/retrospecting/SKILL.md) for detailed examples of parsing and analyzing Claude's native log format for comprehensive session analysis.

## Security Considerations

- Claude's native logs are stored in `~/.claude/projects/` directory
- Logs contain full session transcripts including prompts and responses
- Logs are managed by Claude Code with automatic retention
- Consider data sensitivity when analyzing session logs
- Do not manually delete or modify Claude's native logs
