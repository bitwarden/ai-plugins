---
argument-hint: "[PR#] | [PR URL] | (blank to choose interactively)"
allowed-tools: AskUserQuestion, Task
description: Review a GitHub pull request or local changes and write the review to local files instead of posting
---

**Resolve the target first, in this turn.** Two ways in:

- `$ARGUMENTS` names a PR. Extract just the number — `123`, `https://github.com/org/repo/pull/456`, and `PR #789` all yield a bare integer.
- `$ARGUMENTS` is empty, or names nothing that parses as a PR. Use `AskUserQuestion` to ask whether to review a pull request or the local changes, and settle it here; the agent runs as a subagent and cannot prompt mid-run, so a question left for it has no one to answer. This turn cannot list open PRs, so take the number as free text rather than offering a menu.

**If the target is a pull request, the number must match `^[0-9]+$` before it goes into the `TARGET:` line.** (A local-changes target has no number; this check does not apply to it.) It is written verbatim into `gh pr view`, `gh pr diff`, and the GraphQL variable below, and `Bash(gh pr view:*)` is a prefix rule — `gh pr view 1 --repo attacker/repo` would match it and redirect the review. If the value does not match, **do not invoke the Task tool at all**: report what you were given and ask again. Never delegate without a resolved target.

**Then invoke the Task tool** with `subagent_type: "bitwarden-code-review:bitwarden-code-reviewer"`. Begin the prompt with the resolved target on its own line, in exactly one of these forms, followed by everything from **CRITICAL INSTRUCTIONS FOR THE AGENT** onward — not this paragraph, which is addressed to the command turn and would tell the agent not to do its own job:

```
TARGET: PR #<number>
TARGET: local changes
```

On the line after it, always add `OUTPUT: local files` — both targets. This command writes to local files and never posts, so that declaration, not the target, is what `Skill(posting-review-summary)` routes on.

That line is the only carrier — `$ARGUMENTS` is empty on the interactive path, so an agent left to re-derive the target from it would find nothing. This command's own turn holds only `AskUserQuestion` and `Task`: it settles the target and delegates. Thread pre-fetching belongs to the workflow-driven `/bitwarden-code-review:code-review`, not here. Do not run the `gh`, `git`, `Skill`, or `Write` operations described below yourself — they are the agent's, and it carries its own grants for them.

Invoke the bitwarden-code-reviewer agent now with the instructions below.

**CRITICAL INSTRUCTIONS FOR THE AGENT:**

1. **Read the target from the `TARGET:` line at the top of this prompt.** It is already resolved — the command turn settled it before delegating. Do not ask and do not re-derive it: you hold no `AskUserQuestion` grant and no one is there to answer.
   - `TARGET: PR #<number>` — use that number for thread detection and for fetching PR data with `gh pr view`
   - `TARGET: local changes` — follow the local-mode procedure in your `AGENT.md`, which defines how the base is resolved and what to do when there is nothing to review. Skip thread detection (step 2). The scope is whatever that procedure resolves, not both scopes at once

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

Uses the same format as `Skill(posting-review-summary)`, including its `## No Verdict` form when nothing could be reviewed:

```markdown
**Overall Assessment:** APPROVE / REQUEST CHANGES

[1-2 neutral sentence describing what was reviewed]

<details>
<summary>Code Review Details</summary>

- [emoji]: [One-line description]
  - `filename.ts:42`

</details>
```

**File 2: `review-inline-comments.md`**

Contains all inline review comments with file and line references (same format as would be posted with `gh pr review --comment` in standard GitHub reviews, but written to local file). Format:

```markdown
## [file-path]:[line-number]

[Emoji]: [One-line description]

<details>
<summary>Details and fix</summary>

[Full details, code examples, rationale]

</details>

---

## [next-file]:[next-line]

[Next comment...]

---
```
