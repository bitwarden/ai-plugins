# Review Output Examples

Sample reviews demonstrating proper feedback format, priority classification, and constructive tone for Claude configuration reviews.

---

## Available Examples

Load the appropriate example based on the file type you're reviewing:

### [Example 1: Skill Review - Multiple Issues](./example-skill-review.md)

**Use when:** Reviewing skill.md files or skill supporting files

**Demonstrates:**
- YAML frontmatter validation
- Progressive disclosure enforcement (500 line limit)
- Structured thinking requirements
- Multiple priority levels (CRITICAL, IMPORTANT, SUGGESTED, OPTIONAL)
- Summary comment format

---

### [Example 2: CLAUDE.md Review - Duplication Issue](./example-claude-md-review.md)

**Use when:** Reviewing CLAUDE.md files (project or global)

**Demonstrates:**
- Detecting documentation duplication
- Reference-based approach vs copying content
- Token efficiency improvements
- Decision-making guidance patterns

---

### [Example 3: Settings Review - Security Issues](./example-settings-review.md)

**Use when:** Reviewing settings.json or settings.local.json

**Demonstrates:**
- Security-first approach
- Permission scoping validation
- Sensitive path detection
- Dangerous command auto-approval issues
- CRITICAL security issue handling

---

### [Example 4: Prompts Review - Quality Improvements](./example-prompts-review.md)

**Use when:** Reviewing .claude/prompts/*.md or .claude/commands/*.md files

**Demonstrates:**
- Purpose clarity requirements
- Session context optimization
- Skill reference patterns
- Quality improvements without critical issues
- Feature documentation standards

---

## Loading Strategy

**Efficient approach:**
1. Detect file type being reviewed (Step 1 in skill.md)
2. Load only the relevant example for that file type
3. Use example as template for feedback format

**Avoid:**
- Loading all examples upfront
- Copying example text verbatim (adapt to specific context)

---

## Example Format

All examples follow this structure:

```
## Example N: [Type] Review - [Issue Category]

**Context:** Brief description of what's being reviewed

### Review Comments

**[file:line]** - PRIORITY: Issue description

[Specific fix with code example]

[Rationale]

---

### Summary Comment

**Overall Assessment:** APPROVE / REQUEST CHANGES

[Summary of findings grouped by priority]
```

---

## Summary: Review Best Practices

Extracted from the example reviews:

### Inline Comment Structure
1. **File and line reference** - Precise location
2. **Priority level** - CRITICAL, IMPORTANT, SUGGESTED, OPTIONAL
3. **Issue description** - Clear, specific problem statement
4. **Specific fix** - Actionable solution with code example
5. **Rationale** - Why this matters (impact, research, standards)
6. **Reference** - Documentation link when applicable

### Priority Usage
- **CRITICAL** - Prevents functionality, security vulnerabilities
- **IMPORTANT** - Significant quality/maintainability impact
- **SUGGESTED** - Nice-to-have improvements
- **OPTIONAL** - Personal preferences, alternatives

### Summary Comment
- Group findings by priority level
- Be specific about what must vs should vs could change
- Acknowledge strengths, not just problems
- Clear APPROVE or REQUEST CHANGES recommendation

### Tone Guidelines
- Constructive and specific, never dismissive
- Explain rationale (the "why"), not just "what"
- Provide actionable fixes, not just problem identification
- Focus on code/config, not people
- Acknowledge complexity and trade-offs

---

**Version:** 1.0.0
**Last Updated:** 2025-10-30
