# Example Prompts Review

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

