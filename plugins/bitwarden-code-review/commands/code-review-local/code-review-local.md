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
   - For local changes: Skip thread detection (step 2), analyze uncommitted and committed changes on the current branch

2. **Detect Existing Threads** (PR reviews only - skip for local changes):

   Fetch existing review threads to prevent duplicate comments. Capture BOTH comment sources:

   ```bash
   # General PR comments
   gh pr view <PR_NUMBER> --json comments

   # Inline review threads (resolved + open)
   gh api graphql -f query='
   query($owner: String!, $repo: String!, $pr: Int!) {
     repository(owner: $owner, name: $repo) {
       pullRequest(number: $pr) {
         reviewThreads(first: 100) {
           nodes {
             id
             isResolved
             isOutdated
             path
             line
             startLine
             diffSide
             comments(first: 10) {
               nodes {
                 id
                 body
                 author { login }
                 createdAt
               }
             }
           }
         }
       }
     }
   }
   ' -f owner="<OWNER>" -f repo="<REPO>" -F pr="<PR_NUMBER>"
   ```

   **Thread Matching Logic** - Before creating any new comment, check for matches:

   | Match Type   | Criteria                   | Action              |
   | ------------ | -------------------------- | ------------------- |
   | **Exact**    | Same file + same line      | Use existing thread |
   | **Nearby**   | Same file + line within ±5 | Use existing thread |
   | **Content**  | Body similarity >70%       | Use existing thread |
   | **No match** | None of above              | Create new comment  |

3. **Local Review Mode**: Writing to local files instead of GitHub. Invoke `Skill(posting-review-summary)` with local output context.

4. **Output Destination**: Write to local files:
   - `review-summary.md` - Summary (via `Skill(posting-review-summary)` in local mode)
   - `review-inline-comments.md` - Inline comments (same format as GitHub)

5. **Format Exactly As PR Comments**: Both files MUST contain exactly what would be posted to GitHub
   - If no inline comments would be left, leave `review-inline-comments.md` blank.

6. **No GitHub Posting**: Do NOT use `gh pr review --comment` or `gh pr comment` to post anything. Only READ from GitHub, WRITE to local files.

7. **Include All Standard Review Elements**:
   - Pre-review protocol (read existing comments, understand changes, assess PR metadata)
   - All finding categories (❌ ⚠️ ♻️ 🎨 ❓)
   - Proper `<details>` sections for each finding
   - Final summary with overall assessment

**Note**: The output formats below mirror the standard GitHub review formats documented in your AGENT.md file, adapted for local file output instead of direct GitHub posting.

**File 1: `review-summary.md`**

Uses same format as `Skill(posting-review-summary)`:

```markdown
**Overall Assessment:** APPROVE / REQUEST CHANGES

[1-2 neutral sentence describing what was reviewed]

<details>
<summary>Code Review Details</summary>

- [emoji] **[SEVERITY]**: [One-line description]
  - `filename.ts:42`

</details>
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
