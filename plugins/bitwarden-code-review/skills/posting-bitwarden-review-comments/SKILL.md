---
name: posting-bitwarden-review-comments
description: Formats and posts GitHub PR review comments following Bitwarden engineering standards. Use when posting code review findings, inline comments, or summary assessments on pull requests. Also use when Claude Code creates a sticky comment for PR reviews.
---

# Posting Bitwarden Review Comments

## GitHub Comment Posting Protocol

1. **MUST** Analyze all changes before posting anything
2. **MUST** Use inline comments for code-specific findings
3. **MUST** Use the Bitwarden finding format
4. **FORBIDDEN**: Do NOT add "Strengths", "Highlights", or positive observations sections.
5. **FORBIDDEN** Do NOT post praise-only inline comments

## Finding Format

**CRITICAL: Never use # followed by numbers** - GitHub will autolink it to unrelated issues/PRs.

1. Writing "#1" creates a clickable link to issue/PR #1 (not your finding)
2. "Issue" is also wrong terminology (use "Finding")
3. Use "Finding" + space + number (no # symbol); aim for under 30 words in sentence

**CORRECT FORMAT:**

- Finding 1: Memory leak detected
- Finding 2: Missing error handling

**WRONG (DO NOT USE):**

- ❌ Issue #1 (wrong term + autolink)
- ❌ #1 (autolink only)
- ❌ Issue 1 (wrong term only)

## Inline Comments

**Every inline comment MUST:**

1. Reference specific line(s)
2. State the problem - what breaks or what's the risk?
3. Provide actionable fix (for ❌ and ⚠️)
4. Be brief yet clear
5. Use collapsed sections for comments over 5 lines
6. Include both opening `<details>` AND closing `</details>` tags

**Visibility Rule:** Only severity + one-line description visible; everything else inside `<details>` tags.

### Template for long comments

```
[emoji] **[SEVERITY]**: [One-line issue description]

<details>
<summary>Details and fix</summary>

[Code example or specific fix]

[Rationale explaining why]

Reference: [docs link if applicable]
</details>
```

## Summary Comments

**Every summary comment MUST:**

1. Be concise - list only finding summaries with file:line references
2. Not repeat details from inline comments
3. Limit praise to one or two sentences

### Template for PRs with actionable issues

```
**Overall Assessment:** APPROVE / REQUEST CHANGES

**Critical Issues** (if any):
- [One-line summary with file:line reference]

See inline comments for details.
```

### Template for PRs without actionable issues

```
**Overall Assessment:** APPROVE

[One neutral sentence describing what was reviewed]
```
