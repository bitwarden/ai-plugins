# Agents Review Checklist

Review checklist for changes to Claude Code agent files (`.claude/agents/*.md` and `plugins/*/agents/*.md`).

---

## Multi-Pass Review Strategy

### First Pass: Structure and YAML Frontmatter

<thinking>
Critical structural elements for agents:
1. Is YAML frontmatter present and valid?
2. Are required fields (name, description) present?
3. Are optional fields (tools, model) valid if present?
4. Does the agent file have a system prompt?
5. Is the basic structure sound?
</thinking>

**Focus Areas:**
- [ ] YAML frontmatter present and syntactically valid
- [ ] Required fields: `name` and `description`
- [ ] Optional fields validated if present: `tools`, `model`
- [ ] System prompt exists and is non-empty
- [ ] File structure follows markdown format

**Required YAML Frontmatter:**
```yaml
---
name: agent-name-in-lowercase-with-hyphens
description: Specific description with activation triggers
---
```

**Optional YAML Fields:**
```yaml
---
name: agent-name
description: Clear description
tools: Read, Grep, Glob  # Comma-separated tool names (omit to inherit all)
model: sonnet              # Options: sonnet, opus, haiku, inherit
---
```

**Critical Issues to Flag Immediately:**
- Missing YAML frontmatter (agent won't be recognized)
- Missing `name` field
- Missing `description` field
- Invalid YAML syntax (tabs, malformed structure)
- Invalid `model` value (must be: sonnet, opus, haiku, inherit)
- Invalid tool names in `tools` field
- Empty system prompt

**Reference:** [Anthropic - Claude Code Subagents Documentation](https://docs.claude.com/en/docs/claude-code/sub-agents.md)

---

### Second Pass: Security and Tool Access

<thinking>
Security implications of agent configuration:
1. What tools does this agent have access to?
2. Is tool access scoped by principle of least privilege?
3. Are there dangerous tool combinations?
4. Could this agent perform unintended destructive operations?
5. Is tool access justified by agent purpose?
</thinking>

**Principle of Least Privilege:**
Agents should have ONLY the tools necessary for their specific function.

**Tool Access Patterns:**

✅ **GOOD - Read-only analysis agent:**
```yaml
---
name: code-analyzer
description: Analyzes code quality and patterns
tools: Read, Grep, Glob
---
```

✅ **GOOD - Scoped editing agent:**
```yaml
---
name: test-generator
description: Generates unit tests for existing code
tools: Read, Grep, Write
---
```

❌ **BAD - Overly broad access:**
```yaml
---
name: helper-agent
description: Helps with various tasks
# No tools field = inherits ALL tools
---
```

❌ **BAD - Unnecessary destructive access:**
```yaml
---
name: documentation-writer
description: Writes documentation
tools: Read, Write, Edit, Bash  # Why does documentation need Bash?
---
```

**Security Checks:**
- [ ] Tool access scoped to minimum required
- [ ] Read-only agents don't have Write/Edit/Bash
- [ ] Bash access is justified for agent purpose
- [ ] If tools omitted (inherits all), this is intentional and documented
- [ ] No dangerous tool combinations without justification

**Common Secure Patterns:**
- **Analyst/Reviewer**: Read, Grep, Glob (read-only)
- **Code Generator**: Read, Grep, Write (creates new files)
- **Refactoring Agent**: Read, Grep, Edit (modifies existing)
- **Automation Agent**: Read, Write, Bash (needs command execution)

**Red Flags:**
- Inheriting all tools without clear justification
- Bash access without explanation
- Write/Edit access for analysis-only agents
- Tool access mismatched to agent description

**Reference:** `reference/agent-tool-access.md` for detailed security implications

---

### Third Pass: Description and Activation Triggers

<thinking>
Description quality considerations:
1. Is it clear what this agent does?
2. When should Claude invoke this agent?
3. Are activation triggers specific?
4. Can users understand when to use this agent?
5. Is the description too vague or too verbose?
</thinking>

**Effective Descriptions:**
Descriptions must be specific about BOTH functionality AND activation triggers.

✅ **GOOD - Specific with activation triggers:**
```yaml
description: Reviews Kotlin code for MVVM violations, state management issues, and Compose best practices. Use when analyzing Android ViewModels, state flows, or Compose UI code.
```

✅ **GOOD - Clear automatic delegation:**
```yaml
description: Debugs runtime errors by analyzing stack traces and logs. PROACTIVELY invoke when error messages or exceptions are present.
```

✅ **GOOD - Narrow scope with examples:**
```yaml
description: Generates unit tests for Python functions using pytest. Use when working with .py files that lack test coverage.
```

❌ **BAD - Too vague:**
```yaml
description: Helps with code stuff.
```

❌ **BAD - No activation triggers:**
```yaml
description: Analyzes code quality and suggests improvements.
# When should this be used? What languages? What types of improvements?
```

❌ **BAD - Too broad (violates single responsibility):**
```yaml
description: Handles all aspects of development including coding, testing, deployment, documentation, and architecture design.
```

**Check For:**
- [ ] Description states what the agent does
- [ ] Description includes activation triggers (when to use)
- [ ] Description is specific, not vague
- [ ] Single responsibility (focused scope)
- [ ] Appropriate level of detail (not too terse, not too verbose)

**Activation Language Patterns:**
- "Use when..." - Explicit trigger conditions
- "PROACTIVELY invoke..." - Encourages automatic delegation
- "Use for..." - Specific use cases
- Language/framework specific - Improves targeting

---

### Fourth Pass: System Prompt Quality

<thinking>
System prompt effectiveness:
1. Are instructions clear and specific?
2. Does it define role and capabilities?
3. Are examples provided for complex behaviors?
4. Does it include constraints and boundaries?
5. Is structured thinking guidance present?
6. Is the prompt token-efficient?
</thinking>

**System Prompt Requirements:**

**Clarity and Specificity:**
- [ ] Role clearly defined
- [ ] Capabilities explicitly stated
- [ ] Constraints and boundaries documented
- [ ] Expected behavior specified
- [ ] Output format defined (if applicable)

**Prompt Engineering Best Practices:**

✅ **GOOD - Structured with examples:**
```markdown
# Code Reviewer Agent

## Role
You are a specialized code reviewer focusing on security vulnerabilities, performance issues, and adherence to SOLID principles.

## Capabilities
- Identify SQL injection, XSS, and CSRF vulnerabilities
- Detect performance anti-patterns (N+1 queries, memory leaks)
- Verify SOLID principle adherence

## Process
1. Read the file and understand context
2. Analyze against security checklist
3. Check performance patterns
4. Verify architectural principles
5. Provide inline comments with file:line references

## Output Format
**file.py:42** - CRITICAL: SQL injection vulnerability
[Specific fix with code example]
[Rationale explaining security impact]

## Examples
[Include 2-3 examples of good review comments]
```

✅ **GOOD - Includes structured thinking:**
```markdown
Before analyzing each file, use structured thinking:

<thinking>
1. What is the file's purpose?
2. What are the main security risks for this type of code?
3. What performance patterns should I check?
4. Are there obvious SOLID violations?
</thinking>

Then provide your analysis...
```

❌ **BAD - Too vague:**
```markdown
Review code and find problems.
```

❌ **BAD - No structure or examples:**
```markdown
You're a code reviewer. Look at code and tell the user what's wrong with it. Check for bugs and bad practices.
```

**Structured Thinking Guidance:**
- [ ] `<thinking>` blocks guide reasoning process
- [ ] Key questions posed for each major step
- [ ] Decision criteria made explicit
- [ ] Systematic analysis approach modeled

**Token Efficiency:**
- [ ] Concise without losing clarity
- [ ] Examples are minimal but sufficient
- [ ] No unnecessary verbosity
- [ ] Direct language preferred

**Reference:** Anthropic Chain of Thought documentation (40% error reduction with structured thinking)

---

### Fifth Pass: Model Selection and Best Practices

<thinking>
Model selection considerations:
1. Is the model field specified?
2. If specified, is the selection appropriate for task complexity?
3. Should this use haiku for speed or sonnet for quality?
4. Is 'inherit' used appropriately?
5. Does the agent follow single responsibility principle?
</thinking>

**Model Selection Guidance:**

```yaml
model: haiku   # Fast, cost-effective for simple tasks
model: sonnet  # Balanced for most tasks (default)
model: opus    # Most capable, use sparingly for complex reasoning
model: inherit # Inherits from parent conversation
```

**When to Use Each Model:**

**Haiku** - Simple, straightforward tasks:
- Formatting code
- Running predefined scripts
- Simple file operations
- Quick analysis with clear criteria

**Sonnet** - Most agent tasks (default):
- Code review
- Bug analysis
- Test generation
- Documentation writing
- Moderate complexity reasoning

**Opus** - Complex reasoning only:
- Architectural decisions
- Complex refactoring across multiple files
- Novel problem-solving
- High-stakes analysis requiring maximum accuracy

**Inherit** - Context-dependent:
- When agent needs same context as main conversation
- When model selection should match user's choice
- For consistency across conversation

**Best Practice Checks:**
- [ ] Model specified or intentionally omitted
- [ ] Model complexity matches task complexity
- [ ] Not using opus unnecessarily (cost/latency)
- [ ] Haiku used where speed matters and task is simple
- [ ] Single responsibility principle followed
- [ ] Agent scope appropriately focused

**Anti-Patterns:**
- Using opus for simple formatting tasks
- Using haiku for complex analysis
- Agent trying to handle too many different task types
- Model selection not documented/justified

**Reference:** [Anthropic - Subagent Configuration Best Practices](https://docs.claude.com/en/docs/claude-code/sub-agents.md)

---

### Sixth Pass: Plugin Marketplace Standards

<thinking>
Marketplace quality considerations:
1. Is this agent part of a plugin?
2. If marketplace-bound, does it meet quality standards?
3. Is documentation comprehensive?
4. Are examples included?
5. Is the agent production-ready?
</thinking>

**For Marketplace-Bound Agents:**

**Elevated Standards:**
- Missing examples: SUGGESTED → IMPORTANT
- Vague descriptions: IMPORTANT → CRITICAL
- Poor system prompt: SUGGESTED → IMPORTANT
- Undocumented tool access: IMPORTANT → CRITICAL

**Documentation Requirements:**
- [ ] Clear purpose and use cases
- [ ] Examples in system prompt
- [ ] Tool access justified
- [ ] Model selection explained
- [ ] Expected outputs demonstrated

**Production Readiness:**
- [ ] Error handling considered
- [ ] Edge cases addressed
- [ ] Clear success/failure criteria
- [ ] Graceful degradation patterns

**Internal vs Marketplace:**
- Internal agents: Can accept more SUGGESTED issues
- Marketplace agents: Must fix all IMPORTANT issues
- Both: Must fix all CRITICAL security/functionality issues

---

## Priority Classification

Classify findings using `reference/priority-framework.md`:
- **CRITICAL** - Prevents functionality or exposes security vulnerabilities
- **IMPORTANT** - Significantly impacts quality or maintainability
- **SUGGESTED** - Improvements that aren't essential
- **OPTIONAL** - Personal preferences

---

## Common Agent Anti-Patterns

**Over-Privileged Agent:**
- Inherits all tools without justification
- Bash access for read-only task
- Fix: Specify minimum required tools

**Vague Purpose:**
- Description: "Helps with code"
- Better: "Reviews Python code for PEP 8 violations. Use when analyzing .py files."

**Missing Structured Thinking:**
- System prompt lacks reasoning guidance
- No decision criteria for complex choices
- Fix: Add `<thinking>` blocks with key questions

**Wrong Model Selection:**
- Using opus for simple formatting
- Using haiku for complex analysis
- Fix: Match model to task complexity

**Scope Creep:**
- Agent trying to handle multiple unrelated tasks
- Jack-of-all-trades, master of none
- Fix: Split into focused, single-purpose agents

**Security Oversights:**
- Bash access without scoping
- Write access for analysis-only agents
- No consideration of tool access implications
- Fix: Apply principle of least privilege

---

## Final Checklist Summary

Before completing review, verify:

- [ ] YAML frontmatter present and valid
- [ ] Required fields (name, description) present
- [ ] Optional fields valid if present
- [ ] Tool access follows least privilege
- [ ] Description includes activation triggers
- [ ] System prompt is clear and specific
- [ ] Model selection appropriate for task
- [ ] Single responsibility principle followed
- [ ] Security implications considered
- [ ] Marketplace standards met (if applicable)
