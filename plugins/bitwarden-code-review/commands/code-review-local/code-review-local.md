---
argument-hint: [PR#] | [PR URL]
description: Review a GitHub pull request or local changes and write the review to local files instead of posting
---

You must invoke the bitwarden-code-reviewer agent to perform a comprehensive code review of a GitHub pull request or local changes.

**CRITICAL INSTRUCTIONS FOR THE AGENT:**

1. **Pull Request Information**:
   - If arguments are provided ($ARGUMENTS), extract the numeric PR number:
     - Direct number: "123" → PR number is 123
     - PR URL: "https://github.com/org/repo/pull/456" → PR number is 456
     - Text reference: "PR #789" → PR number is 789
   - If no arguments provided, ask the user if there is a related PR number or URL
   - If user indicates no PR or requests local changes review, review the current git branch changes using `git diff` and `git status`
   - For PRs: Use the extracted PR number when executing thread detection and fetching PR data with `gh pr view` commands
   - For local changes: Skip thread detection, analyze uncommitted and committed changes on the current branch

2. **Local Review Mode**: You are performing a code review, and writing output to LOCAL FILES instead of posting to GitHub

3. **Output Destination**: Write review findings to TWO separate files:
   - `review-summary.md` - The overall summary comment (what would be posted with `gh pr comment`)
   - `review-inline-comments.md` - All inline review comments (what would be posted with `gh pr review --comment`)

4. **Format Exactly As PR Comments**: Both files MUST contain exactly what would be posted to GitHub
   - If no inline comments would be left, leave `review-inline-comments.md` blank.

5. **No GitHub Posting**: Do NOT use `gh pr review --comment` or `gh pr comment` to post anything. Only READ from GitHub, WRITE to local files.

6. **Include All Standard Review Elements**:
   - Pre-review protocol (read existing comments, understand changes, assess PR metadata)
   - All finding categories (❌ ⚠️ ♻️ 🎨 ❓)
   - Proper `<details>` sections for each finding
   - Final summary with overall assessment

**Note**: The output formats below mirror the standard GitHub review formats documented in your AGENT.md file, adapted for local file output instead of direct GitHub posting.

**File 1: `review-summary.md`**

Contains the overall summary comment (same format as would be posted with `gh pr comment` in standard GitHub reviews, but written to local file). Format:

```markdown
**Overall Assessment:** APPROVE / REQUEST CHANGES

**Critical Issues** (if any):

- [file:line] - [brief description]

See inline comments for details.
```

Or for clean PRs:

```markdown
**Overall Assessment:** APPROVE

[One neutral sentence describing what was reviewed]
```

**File 2: `review-inline-comments.md`**

Contains all inline review comments with file and line references (same format as would be posted with `gh pr review --comment` in standard GitHub reviews, but written to local file). Format:

```markdown
## [file-path]:[line-number]

[Emoji] **[SEVERITY]**: [One-line description]

<details>
<summary>Details and fix</summary>

[Full details, code examples, rationale]

</details>

---

## [next-file]:[next-line]

[Next comment...]

---
```

Invoke the bitwarden-code-reviewer agent now with these instructions.
