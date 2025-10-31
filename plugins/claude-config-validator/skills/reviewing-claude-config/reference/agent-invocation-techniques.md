# Agent Invocation Techniques

Advanced techniques for agent orchestration, including chaining patterns, prompt engineering, and validation strategies.

**Source:** [Anthropic - Common Workflows](https://docs.claude.com/en/docs/claude-code/common-workflows.md)

**Related References:**
- `agent-when-to-invoke.md` - Decision criteria and best practices
- `agent-invocation-operations.md` - Operations, security, and performance

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

## Prompt Engineering for Agent Invocation

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

### Example: Good Invocation

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

## Validation Checks for Agent Invocations

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

## Resources

- [Anthropic - Common Workflows](https://docs.claude.com/en/docs/claude-code/common-workflows.md)
- [Anthropic - Prompt Engineering](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview)
- `agent-when-to-invoke.md` - When and why to use agents
- `agent-invocation-operations.md` - Security and performance considerations
