---
name: posting-review-summary
description: Use this skill when posting the final summary comment after all inline comments are posted. Apply as the LAST step of code review after all findings are classified and inline comments are complete. Detects context (agent mode sticky comment, GitHub Actions MCP tool, or local file) and routes output accordingly.
---

# Posting Review Summary

## Context Detection

Check contexts **in this order** — use the first match:

| Context                   | How to Detect                                                                                    | Action                                            |
| ------------------------- | ------------------------------------------------------------------------------------------------ | ------------------------------------------------- |
| **Agent Mode**            | Sticky comment context provided in prompt (comment ID + `<!-- bitwarden-code-review -->` marker) | Write summary to `/tmp/review-summary.md`         |
| GitHub Actions (tag mode) | `mcp__github_comment__update_claude_comment` available AND no sticky comment context             | Update sticky comment via MCP tool                |
| Local review              | Neither agent mode context nor MCP tool available                                                | Write to `review-summary.md` in working directory |

**FORBIDDEN:** Do not use `gh pr comment` to create summary comments.

## PR Metadata Assessment

If PR title, description, or test plan is genuinely deficient, add as a finding in the Code Review Details collapsible section.

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
## 🤖 Bitwarden Claude Code Review

**Overall Assessment:** APPROVE / REQUEST CHANGES

[Up to 4 neutral sentences describing what was reviewed]

<details>
<summary>Code Review Details</summary>

[Findings grouped by severity - see ordering below]

[Optional PR Metadata Assessment - only for truly deficient metadata]

</details>
```

## Findings in Details Section

**Ordering:** Group findings by severity in this exact order:

1. ❌ : CRITICAL
2. ⚠️ : IMPORTANT
3. ♻️ : DEBT
4. 🎨 : SUGGESTED
5. ❓ : QUESTION

**Omit empty categories entirely.**

**Format per finding:**

```markdown
- [emoji]: [One-line description]
  - `filename.ts:42`
```

**Example:**

```markdown
<details>
<summary>Code Review Details</summary>

- ❌ : SQL injection in user query builder
  - `src/auth/queries.ts:87`
- ⚠️ : Missing null check on optional config
  - `src/config/loader.ts:23`

</details>
```

## Output Execution

### Agent Mode (Sticky Comment)

When sticky comment context is provided in the prompt (comment ID + marker):

1. Write the summary to `/tmp/review-summary.md` using the **Write** tool
2. Append `\n\n<!-- bitwarden-code-review -->` at the end of the file content
3. Do **NOT** use `mcp__github_comment__update_claude_comment`
4. Do **NOT** use `gh pr comment` or `gh api`

The workflow post-step will read this file and update the placeholder comment automatically.

### GitHub Actions (Tag Mode)

```
Use mcp__github_comment__update_claude_comment to update the sticky comment with the summary.
```

### Local

```
Write summary to review-summary.md in working directory.
```
