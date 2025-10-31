# Agent Invocation Guide

Comprehensive guide on when and how to invoke agents, including decision criteria, best practices, chaining patterns, prompt engineering, and operational considerations.

**Sources:**
- [Anthropic - Common Workflows - Specialized Subagents](https://docs.claude.com/en/docs/claude-code/common-workflows.md)
- [Anthropic - Prompt Engineering](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview)

---

## Table of Contents

**Decision Criteria:**
- [When to Use Agents vs Direct Tools](#when-to-use-agents-vs-direct-tools)
- [Agent Selection Guidelines](#agent-selection-guidelines)

**Best Practices:**
- [Invocation Best Practices](#invocation-best-practices)
- [Common Anti-Patterns](#common-anti-patterns)

**Advanced Techniques:**
- [Agent Chaining Patterns](#agent-chaining-patterns)
- [Prompt Engineering for Invocation](#prompt-engineering-for-invocation)

**Operations:**
- [Model Override Considerations](#model-override-considerations)
- [Security Considerations](#security-considerations)
- [Performance Considerations](#performance-considerations)
- [Validation Priorities](#validation-priorities)

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

## Agent Selection Guidelines

**Specific vs General:**
```markdown
# For security-focused review
Use security-scanner agent (specialized for vulnerability detection)

# For general code quality
Use code-reviewer agent (broader quality analysis)

# For specific framework
Use android-reviewer agent (MVVM, Compose patterns)
```

**Match Agent to Task:**
- Security analysis → security-scanner
- Test generation → test-generator
- Documentation → documentation-writer
- Refactoring → refactoring-agent

**Don't Force Fit:**
- Don't use test-generator for code review
- Don't use documentation-writer for security analysis
- Use appropriate specialized agent

---

## Invocation Best Practices

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

## Common Anti-Patterns

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

## Agent Chaining Patterns

### Sequential Analysis

**Pattern:**
```markdown
1. Use code-analyzer agent to identify issues
2. Use refactoring-agent to fix identified issues
3. Use test-runner agent to verify fixes
```

**Use When:**
- Each step depends on previous results
- Clear workflow progression
- Validation needed between steps

---

### Parallel Analysis

**Pattern:**
```markdown
Simultaneously:
- Use security-scanner agent for vulnerability analysis
- Use performance-analyzer agent for optimization opportunities
- Use style-checker agent for code style issues

Combine and prioritize results
```

**Use When:**
- Tasks are independent
- Results can be merged
- Time efficiency matters

---

### Conditional Delegation

**Pattern:**
```markdown
Analyze file type:
- If .py file → Use python-linter agent
- If .kt file → Use kotlin-linter agent
- If .ts file → Use typescript-linter agent
- Otherwise → Use generic code-reviewer agent
```

**Use When:**
- Agent selection depends on context
- Different specialized agents available
- Task characteristics vary

---

## Prompt Engineering for Invocation

### Structure of Effective Invocation

```markdown
## Agent Invocation Template

**Agent:** [agent-name]

**Task:** [Specific task description]

**Context:**
- [Relevant context item 1]
- [Relevant context item 2]
- [Relevant context item 3]

**Input:**
- [Files, data, or parameters]

**Expected Output:**
- [Format specification]
- [Content requirements]
- [Success criteria]

**Constraints:**
- [What NOT to do]
- [Boundaries]
- [Limitations]
```

---

### Example: Well-Structured Invocation

```markdown
**Agent:** security-scanner

**Task:** Analyze authentication endpoints for security vulnerabilities

**Context:**
- Application uses JWT for authentication
- Database is PostgreSQL
- Framework is Express.js with TypeScript
- Previous scan found SQL injection in user queries

**Input:**
- src/auth/login.ts
- src/auth/register.ts
- src/middleware/auth.ts

**Expected Output:**
- Inline comments with file:line references
- CRITICAL priority for vulnerabilities
- Specific fix recommendations with code examples
- OWASP category for each finding

**Constraints:**
- Focus on authentication/authorization only
- Skip general code quality issues
- Don't analyze test files
```

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

## Validation Priorities

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

## Common Invocation Mistakes

### Mistake 1: Invoking Non-Existent Agent

**Problem:**
```markdown
Use the my-custom-agent that doesn't exist
```

**Detection:**
- Check if agent file exists in .claude/agents/ or plugins/*/agents/
- Verify agent name spelling

**Fix:**
- Use existing agent
- Create agent if repeatedly needed
- Use direct tools instead

---

### Mistake 2: Circular Agent Invocation

**Problem:**
```markdown
# Agent A invokes Agent B
# Agent B invokes Agent A
```

**Detection:**
- Review agent system prompts for invocations
- Check for mutual dependencies

**Fix:**
- Restructure agent responsibilities
- Use direct tools for specific operations
- Create coordinator agent if needed

---

### Mistake 3: Insufficient Context

**Problem:**
```markdown
Invoke agent without providing relevant conversation history
```

**Fix:**
```markdown
Invoke agent with context:
- Previous conversation summary
- Files already analyzed
- Decisions already made
- Current task status
```

---

### Mistake 4: Ignoring Agent Output

**Problem:**
```markdown
Invoke agent but don't process or validate results
```

**Fix:**
```markdown
Invoke agent
Validate results:
- Check for expected format
- Verify findings make sense
- Flag inconsistencies
- Request clarification if needed
```

---

## Validation Checks

### In Skills

**Check:**
- [ ] Agent name referenced exists
- [ ] Agent is appropriate for task
- [ ] Invocation includes clear task description
- [ ] Context is provided
- [ ] Expected output specified
- [ ] Error handling considered

**Example Review Comment:**
```markdown
**.claude/skills/my-skill/skill.md:45** - IMPORTANT: Agent invocation lacks context

Current:
"Use the code-reviewer agent"

Recommended:
"Use the code-reviewer agent to analyze [specific files] for [specific issues].
Context: [relevant information]
Expected output: [format specification]"

Providing context and expectations improves agent output quality.
```

---

### In Prompts/Commands

**Check:**
- [ ] Agent referenced is likely to exist
- [ ] User provided or default agent used
- [ ] Task description uses prompt template variables
- [ ] Handles case where agent not available

**Example Review Comment:**
```markdown
**.claude/commands/review.md:12** - SUGGESTED: Add fallback for missing agent

Current:
"Use the project-specific-reviewer agent"

Suggested:
"Use the project-specific-reviewer agent if available, otherwise use the built-in code-reviewer agent"

Provides better user experience when custom agents not configured.
```

---

## Resources

- [Anthropic - Common Workflows](https://docs.claude.com/en/docs/claude-code/common-workflows.md)
- [Anthropic - Prompt Engineering](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview)
