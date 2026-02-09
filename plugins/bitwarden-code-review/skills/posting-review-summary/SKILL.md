---
name: posting-review-summary
description: Use this skill when posting the final summary comment after all inline comments are posted. Apply as the LAST step of code review after all findings are classified and inline comments are complete. Detects context (GitHub sticky comment, new comment, or local file) and routes output accordingly.
---

# Posting Review Summary

## When to Use

Invoke this skill **ONCE** per review, **AFTER** all inline comments are posted.
The summary **MUST** be scannable and brief because engineers read summaries first.

## Context Detection

| Context        | How to Detect                                          | Action                       |
| -------------- | ------------------------------------------------------ | ---------------------------- |
| GitHub Actions | `mcp__github_comment__update_claude_comment` available | Update sticky comment        |
| Local review   | Tool not available OR explicit local mode              | Write to `review-summary.md` |

**FORBIDDEN:** Do not use `gh pr comment` to create summary comments.

## PR Metadata Assessment

If PR title, description, or test plan is genuinely deficient, add as ❓ finding in the Code Review Details collapsible section.

### Rules

- **DO NOT** comment on minor improvements
- **DO NOT** comment on adequate-but-imperfect metadata
- **NEVER** add as an inline comment
- **DO NOT** exceed 3 lines of feedback on the PR Metadata Assessment

### Examples

**Genuinely deficient means:**

- Title is literally "fix bug", "update", "changes", or single word
- Description is empty or just "See Jira"
- UI changes with zero screenshots
- No test plan **AND** changes are testable

**Adequate (DO NOT flag):**

- Title describes the change even if imperfect: "Fix login issue for SSO users"
- Description exists and explains the change, even briefly
- Test plan references Jira task with testing details

### Format

```markdown
- ❓ **QUESTION**: PR title could be more specific
  - Suggested: "Fix null check in UserService.getProfile"
```

## Summary Format

```markdown
**Overall Assessment:** APPROVE / REQUEST CHANGES

[1-2 neutral sentence describing what was reviewed]

<details>
<summary>Code Review Details</summary>

[Findings grouped by severity - see ordering below]

[Optional PR Metadata Assessment - only for truly deficient metadata]

</details>
```

## Findings in Details Section

**Ordering:** Group findings by severity in this exact order:

1. ❌ **CRITICAL** (first)
2. ⚠️ **IMPORTANT**
3. ♻️ **DEBT**
4. 🎨 **SUGGESTED**
5. ❓ **QUESTION**

**Omit empty categories entirely.**

**Format per finding:**

```markdown
- [emoji] **[SEVERITY]**: [One-line description]
  - `filename.ts:42`
```

**Example:**

```markdown
<details>
<summary>Code Review Details</summary>

- ❌ **CRITICAL**: SQL injection in user query builder
  - `src/auth/queries.ts:87`
- ⚠️ **IMPORTANT**: Missing null check on optional config
  - `src/config/loader.ts:23`

</details>
```

## Output Execution

**GitHub Actions:**

```
Use mcp__github_comment__update_claude_comment to update the sticky comment with the summary.
```

**Local:**

```
Write summary to review-summary.md in working directory.
```
