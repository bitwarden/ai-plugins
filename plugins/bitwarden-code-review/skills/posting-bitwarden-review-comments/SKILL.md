---
name: posting-bitwarden-review-comments
description: Use this skill when posting inline comments to GitHub pull requests. Apply when formatting comments following Bitwarden engineering standards with severity emojis, clear explanations, and actionable suggestions. Use after findings are classified and ready to post. DO NOT USE when posting summary comments.
---

# Posting Bitwarden Review Comments

## GitHub Comment Posting Protocol

1. **MUST** Analyze all changes before posting anything
2. **MUST** Use inline comments for code-specific findings
3. **MUST** Use the Bitwarden finding format
4. **FORBIDDEN**: Do NOT add "Strengths", "Highlights", or positive observations sections.
5. **FORBIDDEN** Do NOT post praise-only inline comments
6. **FORBIDDEN**: Do NOT post PR metadata issues (title, description, test plan) as inline comments. These go in the summary only.

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

## Summary Output

Invoke `Skill(posting-review-summary)` for all summary formatting and posting.
