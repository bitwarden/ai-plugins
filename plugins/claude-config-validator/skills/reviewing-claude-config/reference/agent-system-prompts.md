# Agent System Prompt Engineering

Best practices for crafting effective agent system prompts, including proven patterns and common anti-patterns to avoid.

**Source:** [Anthropic - Chain of Thought Prompting](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/chain-of-thought)

**Related References:**
- `agent-tool-access.md` - Tool access security
- `agent-configuration.md` - Model selection and naming

---

## System Prompt Engineering Patterns

### Pattern 1: Structured Role Definition

```markdown
# [Agent Name]

## Role
You are a [specific role] specialized in [specific domain].

## Capabilities
- [Capability 1]
- [Capability 2]
- [Capability 3]

## Constraints
- [What you DON'T do]
- [Boundaries]
```

**Benefit:** Clear scope and expectations

---

### Pattern 2: Process-Driven

```markdown
## Process

<thinking>
Before analyzing, consider:
1. [Key question 1]
2. [Key question 2]
3. [Key question 3]
</thinking>

Then execute these steps:
1. [Step 1]
2. [Step 2]
3. [Step 3]
```

**Benefit:** Systematic approach, 40% fewer errors (Anthropic research)

---

### Pattern 3: Output Format Specification

```markdown
## Output Format

Provide findings in this format:

**file.py:42** - [PRIORITY]: [Issue]

[Specific fix with code example]

[Rationale]
```

**Benefit:** Consistent, parseable output

---

### Pattern 4: Examples-Based

```markdown
## Examples

### Example 1: Good Code
[Example of good pattern]

### Example 2: Issue Found
[Example with problem]

**Your analysis would be:**
[Example output]
```

**Benefit:** Demonstrates expected behavior

---

## Common Anti-Patterns and Fixes

### Anti-Pattern 1: Over-Privileged Agent

**Problem:**
```yaml
name: documentation-writer
description: Writes documentation
# No tools field - inherits everything including Bash
```

**Fix:**
```yaml
name: documentation-writer
description: Writes documentation
tools: Read, Grep, Glob, Write
```

**Rationale:** Documentation writer doesn't need Bash or Edit

---

### Anti-Pattern 2: Vague Description

**Problem:**
```yaml
description: Helps with code stuff.
```

**Fix:**
```yaml
description: Reviews Python code for PEP 8 style violations and common anti-patterns. Use when analyzing .py files or during pre-commit checks.
```

**Rationale:** Specific triggers enable automatic delegation

---

### Anti-Pattern 3: Wrong Model for Task

**Problem:**
```yaml
name: code-formatter
model: opus  # Expensive overkill for formatting
```

**Fix:**
```yaml
name: code-formatter
model: haiku  # Fast and sufficient
```

**Rationale:** Formatting is mechanical, doesn't need opus reasoning

---

### Anti-Pattern 4: Scope Creep

**Problem:**
```yaml
description: Handles all development tasks including coding, testing, deployment, documentation, and architecture.
```

**Fix:** Split into focused agents:
```yaml
# Agent 1
name: code-reviewer
description: Reviews code for quality issues...

# Agent 2
name: test-generator
description: Generates unit tests...

# Agent 3
name: deployment-helper
description: Assists with deployment tasks...
```

**Rationale:** Single responsibility, clearer delegation

---

### Anti-Pattern 5: Missing Structured Thinking

**Problem:**
```markdown
Review the code and find issues.
```

**Fix:**
```markdown
## Process

<thinking>
Before reviewing, analyze:
1. What is the file's purpose?
2. What are the main risk areas?
3. What patterns should I check?
</thinking>

Then provide your review...
```

**Rationale:** Structured thinking reduces errors by 40%

---

## Resources

- [Anthropic - Chain of Thought Prompting](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/chain-of-thought)
- [Anthropic - Prompt Engineering Overview](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview)
- `agent-tool-access.md` - Secure tool patterns
- `agent-configuration.md` - Model and validation guidance
