# Agent Invocation Operations

Operational considerations for agent invocations, including model overrides, security, performance, and validation priorities.

**Source:** [Anthropic - Common Workflows](https://docs.claude.com/en/docs/claude-code/common-workflows.md)

**Related References:**
- `agent-when-to-invoke.md` - Decision criteria and best practices
- `agent-invocation-techniques.md` - Chaining and prompt engineering

---

## Model Override Considerations

### When to Override Model

**Override to Haiku:**
- Simple, fast task
- Agent default is Sonnet but task is mechanical
- High volume, cost optimization

**Override to Opus:**
- Complex reasoning required
- Critical decision making
- Agent default insufficient for task complexity

**Don't Override:**
- Agent has appropriate default
- No specific reason for different model
- Let agent use configured model

---

### Model Override Examples

**Good Override:**
```markdown
# Agent default is Sonnet, but this is simple formatting
Invoke code-formatter agent with model=haiku
Task: Format files according to project style guide
```

**Bad Override:**
```markdown
# Unnecessary opus override for simple task
Invoke code-formatter agent with model=opus
Task: Format files
```

---

## Security Considerations

### Information Leakage

**Risk:**
```markdown
# Passing sensitive data to agent without considering prompt logging
Invoke agent with API key in prompt
```

**Mitigation:**
- Don't include secrets in invocation prompts
- Use environment variables or secure storage
- Agent system prompts should never log credentials

---

### Tool Access Escalation

**Risk:**
```markdown
# Skill with limited tools invoking agent with full access
# Bypasses skill tool restrictions
```

**Mitigation:**
- Agent inherits session permissions
- Can't escalate beyond user permissions
- Consider agent tool restrictions in allowed-tools

---

### Unintended Command Execution

**Risk:**
```markdown
# Invoking automation agent without specifying safe commands
Invoke deployment-agent to "fix the problem"
```

**Mitigation:**
- Be specific about commands to run
- Agent system prompt should restrict dangerous operations
- Validate commands before agent execution

---

## Performance Considerations

### Latency

- Agent invocation adds latency vs direct tools
- Consider for time-sensitive operations
- Use haiku for speed when appropriate

### Cost

- Each agent invocation costs tokens
- Parallel agents multiply costs
- Use agents judiciously for value-add tasks

### Context Window

- Agents have separate context windows
- Large inputs may hit limits
- Consider chunking for large codebases

---

## Validation Priority Framework

**CRITICAL Issues:**
- Invoking non-existent agents
- Security vulnerabilities in invocation
- Missing required parameters
- Circular dependencies

**IMPORTANT Issues:**
- Insufficient context provided
- Unclear task description
- Wrong agent for task
- Missing error handling

**SUGGESTED Issues:**
- Could add more context
- Could specify output format better
- Alternative agent might be more appropriate

**OPTIONAL Issues:**
- Phrasing alternatives
- Different parameter organization
- Style preferences

---

## Resources

- [Anthropic - Common Workflows](https://docs.claude.com/en/docs/claude-code/common-workflows.md)
- `agent-when-to-invoke.md` - When to use agents
- `agent-invocation-techniques.md` - Advanced techniques
- `agent-tool-access.md` - Tool security considerations
- `agent-configuration.md` - Model selection guidance
