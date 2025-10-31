# Agent Configuration: Models, Naming, and Validation

Guidance on agent model selection, naming conventions, security checklists, and validation criteria.

**Source:** [Anthropic - Claude Code Subagents Documentation](https://docs.claude.com/en/docs/claude-code/sub-agents.md)

**Related References:**
- `agent-tool-access.md` - Tool access security matrix and patterns
- `agent-system-prompts.md` - System prompt engineering patterns

---

## Model Selection Guidelines

### Haiku - Fast and Cost-Effective

**Use For:**
- Simple formatting tasks
- Running predefined scripts
- Quick file operations
- Straightforward analysis with clear criteria
- High-volume, repetitive tasks

**Characteristics:**
- Fastest response time
- Lowest cost
- Good for simple, well-defined tasks
- Less capable reasoning

**Example Agents:**
- Code formatter
- Import organizer
- Simple linter
- File converter

---

### Sonnet - Balanced Default

**Use For:**
- Code review
- Bug analysis
- Test generation
- Documentation writing
- Most agent tasks

**Characteristics:**
- Balanced speed and capability
- Default choice for most agents
- Good reasoning ability
- Cost-effective for quality work

**Example Agents:**
- Code reviewer
- Test generator
- Documentation writer
- Refactoring agent

---

### Opus - Maximum Capability

**Use For:**
- Complex architectural decisions
- Novel problem-solving
- High-stakes analysis
- Multi-file complex refactoring
- Creative solution generation

**Characteristics:**
- Slowest response time
- Highest cost
- Best reasoning capability
- Use sparingly and strategically

**Example Agents:**
- Architecture advisor
- Complex migration planner
- Novel algorithm designer
- High-stakes security analyzer

---

### Inherit - Context-Dependent

**Use For:**
- Agents that should match user's model choice
- Context-dependent decision making
- When parent conversation context matters

**Characteristics:**
- Inherits model from parent conversation
- Maintains consistency
- Good for user-facing agents

**Example Agents:**
- Interactive assistant
- Context-aware helper
- User-preference-dependent agents

---

## Model Selection Decision Tree

```
Is the task simple and well-defined?
├─ YES → Haiku
└─ NO → Continue

Is the task highly complex requiring maximum reasoning?
├─ YES → Opus
└─ NO → Continue

Should the agent match user's model preference?
├─ YES → Inherit
└─ NO → Sonnet (default)
```

---

## Agent Naming Conventions

**Format:** lowercase-with-hyphens

**Good Names:**
- `code-reviewer`
- `test-generator`
- `python-linter`
- `git-workflow-helper`

**Bad Names:**
- `CodeReviewer` (not kebab-case)
- `code_reviewer` (use hyphens, not underscores)
- `helper` (too vague)
- `ai-assistant` (too generic)

**Best Practices:**
- Descriptive and specific
- Indicates purpose clearly
- Follows kebab-case convention
- Matches description scope

---

## Security Checklist by Agent Type

### Analysis Agents (Read-Only)
- [ ] Tools: Read, Grep, Glob only
- [ ] No Write, Edit, or Bash access
- [ ] Model: Sonnet or Haiku
- [ ] System prompt: Analysis focus, no modifications

### Generator Agents (Create Files)
- [ ] Tools: Read, Grep, Glob, Write
- [ ] No Edit or Bash unless justified
- [ ] Model: Sonnet
- [ ] System prompt: Creates new files only

### Refactoring Agents (Modify Code)
- [ ] Tools: Read, Grep, Glob, Edit
- [ ] Bash only if needed for testing
- [ ] Model: Sonnet
- [ ] System prompt: Strong safety guardrails

### Automation Agents (Command Execution)
- [ ] Tools: Include Bash with justification
- [ ] System prompt: Specify safe commands
- [ ] Model: Sonnet or Haiku
- [ ] Document dangerous commands to avoid

---

## Validation Quick Reference

**CRITICAL Issues:**
- Missing YAML frontmatter
- Invalid field types
- Security vulnerabilities (over-privileged access)
- Dangerous tool combinations without justification

**IMPORTANT Issues:**
- Vague descriptions (no activation triggers)
- Poor system prompts
- Inappropriate model selection
- Missing structured thinking

**SUGGESTED Issues:**
- Could add more examples
- Token efficiency improvements
- Alternative patterns available

---

## Resources

- [Anthropic - Subagent Documentation](https://docs.claude.com/en/docs/claude-code/sub-agents.md)
- [Anthropic - Chain of Thought Prompting](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/chain-of-thought)
- `agent-tool-access.md` - Tool security and access patterns
- `agent-system-prompts.md` - Prompt engineering best practices
