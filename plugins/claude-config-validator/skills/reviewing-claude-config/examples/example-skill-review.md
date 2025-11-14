# Example Skill Review

**Context:** Reviewing a new skill with structural and quality issues.

### Review Comments

**`.claude/skills/my-new-skill/skill.md:1`** - CRITICAL: Missing YAML frontmatter

Skills require YAML frontmatter to be discoverable by Claude Code:

```yaml
---
name: my-new-skill
description: Clear description with activation triggers. Use when [specific scenario].
version: 1.0.0
---
```

Without frontmatter, the skill won't be recognized by Claude Code and will never be invoked.

Reference: Anthropic Skills Documentation - YAML Requirements

---

**`.claude/skills/my-new-skill/skill.md:1-650`** - IMPORTANT: File exceeds 500 line limit

Main skill file is 650 lines, exceeding Anthropic's 500-line progressive disclosure recommendation.

Suggested structure:
```
my-new-skill/
├── skill.md (≤500 lines - routing logic only)
├── checklists/
│   ├── type-a.md
│   └── type-b.md
└── reference/
    └── detailed-guidance.md
```

Move detailed checklists and reference material to supporting files, load on-demand.

Rationale: Improves token efficiency, reduces context loading, enables better organization.

Reference: Progressive disclosure best practices

---

**`.claude/skills/my-new-skill/skill.md:45`** - IMPORTANT: Missing structured thinking blocks

Add `<thinking>` blocks before major decision points:

```markdown
### Step 1: Detect Type

<thinking>
Key questions to determine type:
1. What files were modified?
2. What does the title indicate?
3. What's the scope of changes?
</thinking>

Analyze the changeset...
```

Research shows structured thinking reduces logic errors by 40% (Anthropic Chain of Thought study).

Reference: Anthropic Prompt Engineering - Structured Thinking

---

**`.claude/skills/my-new-skill/skill.md:120`** - SUGGESTED: Add concrete examples

This section describes the expected comment format but doesn't show an example. Consider adding:

```markdown
**Example inline comment:**

\```
**file.kt:123** - CRITICAL: Issue description

[Specific fix with code]

[Rationale]
\```
```

Examples improve clarity significantly, especially for complex output formats.

---

**`.claude/skills/my-new-skill/skill.md:200`** - OPTIONAL: Alternative phrasing

Current: "You should check for these patterns..."

Alternative: "Check for these patterns..."

More direct phrasing slightly improves token efficiency, but current version is perfectly functional.

---

### Summary Comment

**Overall Assessment:** REQUEST CHANGES

This skill has strong potential but requires fixes before approval:

**Must Fix (CRITICAL):**
- Add YAML frontmatter (blocks recognition)

**Should Fix (IMPORTANT):**
- Reduce main file to ≤500 lines via progressive disclosure
- Add structured thinking blocks for key decisions

**Nice to Have (SUGGESTED):**
- Add concrete examples for output formats

Once the critical frontmatter is added and the file is restructured with progressive disclosure, this will be ready for approval. The core logic and approach are solid.

---

