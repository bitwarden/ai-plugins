# Prompts and Commands Review Checklist

Review checklist for changes to `.claude/prompts/*.md` and `.claude/commands/*.md` files.

---

## Multi-Pass Review Strategy

### First Pass: Purpose and Activation

<thinking>
Purpose clarity:
1. Is it clear what this prompt/command does?
2. When should it be invoked?
3. What input does it expect?
4. What output will it produce?
</thinking>

**Clear Purpose Statement:**
Every prompt/command file should answer these questions in first 1-3 lines:

```markdown
# Command Name

Brief description of what this does and when to use it.
```

**Examples:**

✅ **GOOD - Clear purpose:**
```markdown
# review-pr

Reviews a GitHub pull request by number. Use when analyzing PR changes before merge.

Usage: /review-pr <pr-number>
```

❌ **BAD - Vague purpose:**
```markdown
# review-pr

Does PR stuff.
```

---

### Second Pass: Completeness

<thinking>
Completeness check:
1. Does the prompt provide all necessary context?
2. Are expected outputs clearly defined?
3. Are examples provided where helpful?
4. Is the prompt self-contained or properly referencing skills?
</thinking>

**Complete Prompt Elements:**

- [ ] Clear description of task
- [ ] Expected input format (if applicable)
- [ ] Expected output format
- [ ] Examples (if task is complex)
- [ ] References to relevant skills or documentation

**Self-Contained vs Skill Reference:**

✅ **GOOD - Simple task, self-contained:**
```markdown
# format-commit

Generate a conventional commit message from staged changes.

Format: `type(scope): description`

Types: feat, fix, docs, style, refactor, test, chore
```

✅ **GOOD - Complex task, reference skill:**
```markdown
# review-changes

Review current git changes for code quality and architectural compliance.

Use the `reviewing-changes` skill to perform comprehensive review based on change type.
```

❌ **BAD - Complex task without guidance:**
```markdown
# review-changes

Review the code.
```

---

### Third Pass: Prompt Engineering Quality

<thinking>
Quality considerations:
1. Is the language clear and specific?
2. Are instructions structured logically?
3. Are examples provided for complex concepts?
4. Does it use appropriate emphasis?
</thinking>

**Clarity and Specificity:**

❌ **VAGUE:** "Look at the files and find problems"
✅ **SPECIFIC:** "Analyze modified Kotlin files for MVVM violations: mutable state exposure, improper dependency injection, missing error handling"

**Logical Structure:**

✅ **GOOD - Step-by-step:**
```markdown
1. Read the PR description and changed files
2. Identify the change type (feature, bug fix, refactor)
3. Apply appropriate review checklist
4. Document findings with inline comments
```

**Examples for Complex Tasks:**

✅ **GOOD - Shows expected format:**
```markdown
Expected output format:

\```
**file.kt:123** - CRITICAL: Exposes mutable state

Change MutableStateFlow to StateFlow:
...
\```
```

---

### Fourth Pass: Session Context

<thinking>
Session context considerations:
1. Does this prompt make assumptions about session state?
2. Does it require files to be read first?
3. Does it handle missing context gracefully?
4. Is it clear what the user needs to provide?
</thinking>

**Context Requirements:**

✅ **GOOD - Explicit about requirements:**
```markdown
# review-file

Reviews a specific file for quality issues.

**Usage:** /review-file path/to/file.kt

This command will read the file and analyze it against project standards.
```

❌ **BAD - Assumes context without stating:**
```markdown
# review-file

Reviews the file.
```

**Graceful Handling:**

✅ **GOOD - Handles missing info:**
```markdown
If no PR number provided, analyze current git diff.
If no files changed, report clean working directory.
```

---

### Fifth Pass: Skill References

<thinking>
Skill reference check:
1. If this references a skill, does the skill exist?
2. Is the skill name correct?
3. Is it clear when to use command vs skill directly?
4. Is the relationship between command and skill logical?
</thinking>

**Proper Skill References:**

✅ **GOOD - Clear skill invocation:**
```markdown
# review-changes

Use the `reviewing-changes` skill to perform comprehensive code review.

This command is equivalent to directly invoking the skill but provides
a convenient shorthand for PR and commit reviews.
```

**Verify:**
- [ ] Referenced skill exists in `.claude/skills/`
- [ ] Skill name matches exactly (case-sensitive)
- [ ] Command adds value beyond just calling skill
- [ ] Command purpose is distinct from skill purpose

---

## Priority Classification

Classify findings using `reference/priority-framework.md`:
- **CRITICAL** - Prevents functionality or exposes security vulnerabilities
- **IMPORTANT** - Significantly impacts quality or maintainability
- **SUGGESTED** - Improvements that aren't essential
- **OPTIONAL** - Personal preferences

---
