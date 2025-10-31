# When to Invoke Agents

Decision criteria for using agents vs direct tools, best practices for agent invocation, and common anti-patterns to avoid.

**Source:** [Anthropic - Common Workflows - Specialized Subagents](https://docs.claude.com/en/docs/claude-code/common-workflows.md)

**Related References:**
- `agent-invocation-techniques.md` - Chaining patterns and prompt engineering
- `agent-invocation-operations.md` - Security, performance, and operations

---

## When to Use Agents vs Direct Tools

### Use Agents When:

**Complex Multi-Step Tasks**
- Task requires multiple decisions and iterations
- Workflow involves conditional logic
- Multiple tools need to be coordinated
- Analysis requires domain expertise

**Example:** Code review requiring security analysis, pattern detection, and architectural assessment

**Specialized Domain Knowledge**
- Task needs specific domain expertise
- Requires understanding of specialized patterns
- Benefits from focused system prompt
- Domain-specific tool access needed

**Example:** Android MVVM review, Kubernetes configuration analysis

**Repetitive Specialized Tasks**
- Same specialized task performed frequently
- Benefits from dedicated configuration
- Tool access pattern is consistent
- Reusable across multiple contexts

**Example:** Test generation, documentation writing

---

### Use Direct Tools When:

**Simple, Single-Step Operations**
- Read a specific file
- Search for a pattern
- Write a known output
- Execute a simple command

**Example:** Reading a configuration file, searching for a specific import

**Immediate Context Tasks**
- Current conversation has full context
- No specialized expertise needed
- Tool usage is straightforward
- No need for separate prompt context

**Example:** Editing a file being discussed in current conversation

**Performance Critical**
- Minimal latency required
- Simple operation doesn't justify agent overhead
- Direct tool access is sufficient

**Example:** Quick grep to find a file

---

## Agent Invocation Best Practices

### Principle 1: Specific Task Description

**Good Invocation:**
```markdown
Invoke the code-reviewer agent to analyze the following files for security vulnerabilities, focusing on SQL injection, XSS, and authentication bypass risks:
- src/auth/login.py
- src/api/users.py
- src/database/queries.py
```

**Bad Invocation:**
```markdown
Review the code.
```

**Why:** Specific instructions improve agent focus and output quality.

---

### Principle 2: Provide Necessary Context

**Good Invocation:**
```markdown
Use the test-generator agent to create unit tests for the UserService class in src/services/user.ts.

Context:
- Uses TypeScript with Jest testing framework
- Existing tests in tests/ directory follow AAA pattern (Arrange-Act-Assert)
- Mock external dependencies (database, API calls)
- Target 80% code coverage
```

**Bad Invocation:**
```markdown
Generate tests for UserService.
```

**Why:** Context helps agent produce relevant, consistent output.

---

### Principle 3: Specify Expected Output

**Good Invocation:**
```markdown
Invoke the documentation-writer agent to create API documentation for the REST endpoints in src/api/.

Expected output:
- OpenAPI 3.0 specification
- Include request/response examples
- Document error codes and meanings
- Follow existing style in docs/api/
```

**Bad Invocation:**
```markdown
Document the API.
```

**Why:** Clear expectations prevent mismatched outputs.

---

### Principle 4: Appropriate Agent Selection

**Good Selection:**
```markdown
# For security-focused review
Use security-scanner agent (specialized for vulnerability detection)

# For general code quality
Use code-reviewer agent (broader quality analysis)

# For specific framework
Use android-reviewer agent (MVVM, Compose patterns)
```

**Bad Selection:**
```markdown
# Using general agent for specialized task
Use code-reviewer for Android MVVM analysis
(Better: Use android-reviewer if available)
```

**Why:** Specialized agents produce better domain-specific results.

---

## Agent Invocation Anti-Patterns

### Anti-Pattern 1: Over-Delegation

**Problem:**
```markdown
# In a skill that just delegates everything
Use the helper-agent to [do the entire task]
```

**Why It's Bad:**
- Adds latency without value
- Skill becomes unnecessary wrapper
- Could use agent directly

**Fix:**
- Skill should add value (routing, preprocessing, validation)
- Only delegate complex portions
- Combine agent output with skill logic

---

### Anti-Pattern 2: Under-Specification

**Problem:**
```markdown
Run the analyzer.
```

**Why It's Bad:**
- Agent doesn't know what to analyze
- No context provided
- Unclear expectations

**Fix:**
```markdown
Use the code-analyzer agent to review src/auth/login.py for:
- Security vulnerabilities
- Error handling completeness
- Input validation

Provide findings in inline comment format.
```

---

### Anti-Pattern 3: Wrong Agent for Task

**Problem:**
```markdown
# Using test-generator for code review
Use test-generator agent to analyze code quality
```

**Why It's Bad:**
- Agent not designed for this task
- Tool access may be insufficient
- System prompt not optimized

**Fix:**
```markdown
# Use appropriate agent
Use code-reviewer agent to analyze code quality
```

---

### Anti-Pattern 4: Missing Error Handling

**Problem:**
```markdown
# No consideration of agent failure
Invoke agent and return results
```

**Why It's Bad:**
- Agent might fail or return unexpected results
- No fallback strategy
- Poor user experience

**Fix:**
```markdown
# Include error handling
Invoke agent
If agent returns errors:
  - Explain what went wrong
  - Suggest manual approach
  - Provide partial results if available
```

---

## Resources

- [Anthropic - Common Workflows](https://docs.claude.com/en/docs/claude-code/common-workflows.md)
- `agent-invocation-techniques.md` - Advanced patterns and techniques
- `agent-invocation-operations.md` - Operations and security
- `agent-tool-access.md` - Tool security matrix
