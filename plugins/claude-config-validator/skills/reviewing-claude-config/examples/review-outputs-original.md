# Review Output Examples

Sample reviews demonstrating proper feedback format, priority classification, and constructive tone for Claude configuration reviews.

---

## Example 1: Skill Review - Multiple Issues

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

## Example 2: CLAUDE.md Review - Duplication Issue

**Context:** Reviewing CLAUDE.md that duplicates architecture documentation.

### Review Comments

**`.claude/CLAUDE.md:50-250`** - IMPORTANT: Duplicates docs/ARCHITECTURE.md content

This section copies 200 lines of MVVM patterns, Hilt DI setup, and module organization from `docs/ARCHITECTURE.md`.

Replace with reference:

```markdown
## Core Directives

1. **Adhere to Architecture**: All code MUST follow patterns in `docs/ARCHITECTURE.md`
2. **Follow Code Style**: ALWAYS follow `docs/STYLE_AND_BEST_PRACTICES.md`
3. **Error Handling**: Use Result types and sealed classes per architecture guidelines

## Reference Documentation

Critical resources:
- `docs/ARCHITECTURE.md` - Architecture patterns and principles
- `docs/STYLE_AND_BEST_PRACTICES.md` - Code style guidelines

**Do not duplicate information from these files - reference them instead.**
```

Rationale: CLAUDE.md should provide high-level directives and references, not duplicate detailed specs. This:
- Reduces token usage (200 lines → 10 lines)
- Prevents documentation drift (single source of truth)
- Improves maintainability

Reference: Progressive disclosure, DRY principle

---

**`.claude/CLAUDE.md:300`** - SUGGESTED: Add decision-making guidance

Consider adding clear guidance on when to ask vs proceed autonomously:

```markdown
## Decision-Making

Defer to user for high-impact decisions:
- Architecture/module changes
- Public API modifications
- Security mechanism changes

Proceed autonomously for:
- Implementation details within established patterns
- Test additions
- Bug fixes following existing patterns
```

This helps Claude make appropriate judgment calls without over-asking or under-asking.

---

### Summary Comment

**Overall Assessment:** REQUEST CHANGES

**Must Fix (IMPORTANT):**
- Remove duplicated architecture content, replace with references

This reduces token usage by ~80% while improving maintainability. The rest of the file is well-structured.

---

## Example 3: Settings Review - Security Issues

**Context:** Reviewing settings.json with multiple security concerns.

### Review Comments

**`.claude/settings.json:5`** - CRITICAL: Overly broad file permissions

Current:
```json
"autoApprovedTools": [
  "Read://*"
]
```

Change to project-scoped:
```json
"autoApprovedTools": [
  "Read://Users/username/projects/myproject/**"
]
```

`Read://*` grants read access to entire filesystem including:
- `~/.ssh/` (SSH keys)
- `~/.aws/` (AWS credentials)
- `/etc/` (system config)
- All user documents and personal files

Scope to project directory only per principle of least privilege.

Reference: Security best practices - Permission scoping

---

**`.claude/settings.json:8`** - CRITICAL: Dangerous command auto-approved

Current:
```json
"Bash:rm -rf:*"
```

**REMOVE THIS IMMEDIATELY**

`rm -rf` performs recursive deletion without confirmation. Auto-approving this command creates risk of accidental data loss.

If file deletion is needed frequently, scope to specific safe directories:
```json
"Bash:rm -rf /tmp/project-build-cache:*"
```

Or require manual approval for all rm commands.

Reference: Security best practices - Dangerous commands

---

**`.claude/settings.json:12`** - IMPORTANT: Permissions reference sensitive directory

Current:
```json
"Read://Users/username/.ssh/**"
```

Remove access to `.ssh` directory containing private keys.

If SSH config reading is required (rare), scope to specific config file:
```json
"Read://Users/username/.ssh/config"
```

Never grant blanket access to directories containing credentials.

---

### Summary Comment

**Overall Assessment:** BLOCK - Critical Security Issues

**CRITICAL issues must be fixed immediately:**
- Overly broad `Read://*` permission
- Auto-approved `rm -rf` command
- Access to `.ssh` directory

These issues expose significant security risks:
- Potential data loss from dangerous commands
- Exposure of SSH private keys and credentials
- Access to sensitive system files

**Cannot approve until all CRITICAL issues are resolved.**

After fixes, re-review the scoped permissions to ensure they follow principle of least privilege.

---

## Example 4: Prompts Review - Quality Improvements

**Context:** Reviewing a new slash command prompt.

### Review Comments

**`.claude/commands/review-feature.md:1`** - IMPORTANT: Missing usage information

Add usage format and example after description:

```markdown
# review-feature

Reviews a feature implementation for architectural compliance and code quality.

**Usage:** /review-feature <feature-name>

**Example:** /review-feature user-authentication

This command analyzes all files related to the specified feature.
```

Users need clear invocation syntax. Without it, they may guess incorrectly or not use the command at all.

---

**`.claude/commands/review-feature.md:10`** - IMPORTANT: Vague instructions

Current: "Look at the code and check for issues."

Change to specific criteria:

```markdown
Analyze feature implementation for:

1. **Architecture Compliance**
   - MVVM pattern adherence
   - Proper dependency injection
   - Module boundaries respected

2. **Code Quality**
   - Error handling (Result types)
   - Null safety
   - KDoc documentation on public APIs

3. **Testing**
   - Unit tests for business logic
   - UI tests for user flows
   - Edge cases covered
```

Specific criteria ensure consistent, thorough reviews.

Reference: Prompt engineering - Specificity

---

**`.claude/commands/review-feature.md:25`** - SUGGESTED: Add expected output format

Show reviewers what the output should look like:

```markdown
**Expected Output Format:**

\```
## Feature: [name]

### Architecture: ✅ Pass / ❌ Issues Found
[Details]

### Code Quality: ✅ Pass / ❌ Issues Found
[Details]

### Testing: ✅ Pass / ❌ Issues Found
[Details]
\```
```

Explicit output format improves consistency and clarity.

---

**`.claude/commands/review-feature.md:30`** - SUGGESTED: Reference existing skill

If a `reviewing-changes` skill exists, consider referencing it:

```markdown
## Implementation

Use the `reviewing-changes` skill with feature-addition checklist:
1. Identify all files in feature scope
2. Apply feature-addition review checklist
3. Document findings in structured format above
```

Reusing existing skills improves consistency and reduces duplication.

---

### Summary Comment

**Overall Assessment:** REQUEST CHANGES

**Must Fix (IMPORTANT):**
- Add usage syntax and example
- Replace vague instructions with specific criteria

**Nice to Have (SUGGESTED):**
- Add expected output format example
- Reference existing reviewing-changes skill if applicable

The core concept is good - this command would be very useful once the instructions are clarified and the usage format is documented.

---

## Anti-Patterns to Avoid

### ❌ One Large Summary Comment

**DON'T DO THIS:**
```
**Overall Review**

I found these issues:
1. Missing YAML frontmatter on line 1
2. File too long (line 1-650)
3. No structured thinking (line 45)
4. Missing examples (line 120)
...
```

**Why this is bad:**
- All feedback in one comment, no specific line references
- Harder to track what's been addressed
- Loses context for each issue
- Doesn't retain history if comment is edited

**DO THIS INSTEAD:**
Create separate inline comment for EACH issue on the specific line.

---

### ❌ Blame Language

**DON'T DO THIS:**
```
**file.kt:50** - You clearly don't understand MVVM. This is completely wrong.
```

**Why this is bad:**
- Attacks person, not code
- Discourages learning
- Creates defensive responses
- Unprofessional tone

**DO THIS INSTEAD:**
```
**file.kt:50** - IMPORTANT: Exposes mutable state

ViewModels should expose StateFlow, not MutableStateFlow:

[code example]

This prevents external mutation, enforcing unidirectional data flow.

Reference: docs/ARCHITECTURE.md#mvvm-pattern
```

Focus on code, provide rationale, offer solution.

---

### ❌ Vague Feedback

**DON'T DO THIS:**
```
**file.kt:100** - This could be better.
```

**Why this is bad:**
- No actionable guidance
- Unclear what "better" means
- Author doesn't know what to change

**DO THIS INSTEAD:**
```
**file.kt:100** - SUGGESTED: Extract complex logic to separate function

Current function is 50 lines with nested conditions. Consider extracting validation logic:

[before/after code example]

Improves readability and testability.
```

Specific issue, concrete solution, clear rationale.

---

### ❌ Missing Priority

**DON'T DO THIS:**
```
**settings.json:5** - Overly broad permissions.
```

**Why this is bad:**
- Unclear if this blocks approval
- Author doesn't know urgency
- May skip critical security fix

**DO THIS INSTEAD:**
```
**settings.json:5** - CRITICAL: Overly broad permissions

[specific fix]

[security rationale]

This must be fixed before approval.
```

Clear priority, specific fix, explicit blocking status.

---

## Summary: Review Best Practices

**DO:**
- ✅ Create separate inline comment for each issue
- ✅ Include specific line references (file:line)
- ✅ Provide concrete code examples for fixes
- ✅ Explain rationale (why it matters)
- ✅ Use clear priority levels (CRITICAL, IMPORTANT, SUGGESTED, OPTIONAL)
- ✅ Focus on code, not people
- ✅ Be constructive and actionable

**DON'T:**
- ❌ Create one large summary comment with all issues
- ❌ Use vague feedback without specific guidance
- ❌ Blame or use judgmental language
- ❌ Omit priority classification
- ❌ Skip rationale or code examples
- ❌ Update existing comments (create new ones)

These examples demonstrate the full range of review scenarios, priorities, and communication patterns for Claude configuration reviews.
