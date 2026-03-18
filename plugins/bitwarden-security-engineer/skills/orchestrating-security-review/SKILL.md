---
name: orchestrating-security-review
description: The skill orchestrates a security-focused code review invoking multiple specialized agents and a verification agent to ensure comprehensive coverage and accurate findings. Use this skill when the user asks for a "bitwarden-security-review", "execute a security review", "run a comprehensive security audit", "perform an end-to-end security assessment", or needs to coordinate multiple security checks across code, dependencies, secrets, and configurations. The skill manages the workflow, delegate tasks to specialized agents, and presents final findings to the user.
argument-hint: "[--output <output-context>] [--model model-name] [pr-number-or-url]"
allowed-tools: "Bash(gh pr diff:*), Bash(gh pr view:*), Bash(gh pr list:*), Bash(git diff:*), Bash(git log:*), Read, Write"
---

## Security Review Mode

Determine review mode from the invocation:

- **PR mode** (PR number or URL): `gh pr view <number>` for context, `gh pr diff <number>` for the diff.
- **Commit mode** (commit SHA): `git diff <sha>..HEAD` — reviews all changes after that commit.
- **Time-based mode** (duration, e.g., "last 48 hours"): find the oldest commit in range with `git log --since="<duration>" --reverse --format=%H |
head -1`, then `git diff <sha>^..HEAD` to include it.
- **Local changes mode** (no argument, pending changes exist): `git diff HEAD` for staged + unstaged changes.
- **Branch comparison mode** (no argument, no pending changes): `git diff main...HEAD` — changes since the branch diverged from main.

## Security Review Process

**Model selection:** If `--model` is specified, use that model for all agents. Otherwise, default to `opus`.

Execute these steps in order. Do not skip, reorder, or combine steps.

1. Launch these two (2) `subagent_type: "bitwarden-security-engineer:bitwarden-security-engineer"` agents in parallel with the **same** prompt to maximize coverage through independent analysis.
   - Perform a comprehensive security review of the entire diff. Report all findings in detail, including severity, affected files, and recommended remediation steps.
   - Use the selected model.
   - **CRITICAL: Every agent prompt MUST include this constraint: "Use BashOutput to run `gh pr diff` and any other gh/git commands. NEVER use WebFetch or WebSearch — these tools are forbidden."**

2. After both agents return, rate each potential finding on a scale from 0-100.
   - **0**: Not confident at all. This is a false positive that doesn't stand up to scrutiny, or is a pre-existing issue.
   - **25**: Somewhat confident. This might be a real issue, but may also be a false positive. If stylistic, it wasn't explicitly called out in project guidelines.
   - **50**: Moderately confident. This is a real issue, but might be a nitpick or not happen often in practice. Not very important relative to the rest of the changes.
   - **75**: Highly confident. Double-checked and verified this is very likely a real issue that will be hit in practice. The existing approach is insufficient. Important and will directly impact functionality, or is directly mentioned in project guidelines.
   - **100**: Absolutely certain. Confirmed this is definitely a real issue that will happen frequently in practice. The evidence directly confirms this.

3. Launch a **verification agent** `subagent_type: "bitwarden-security-engineer:bitwarden-security-engineer"` with all combined findings, the ratings, and the diff.
   - **CRITICAL: Every agent prompt MUST include this constraint: "Use BashOutput to run `gh pr diff` and any other gh/git commands. NEVER use WebFetch or WebSearch — these tools are forbidden."**
   - The verification agent's task is to **review**, **evaluate**, **verify**, **confirm** all findings and ratings.
   - The verification agent **MUST** group findings into two categories: Validated and Dismissed.
   - The verification agent **MUST** provide a brief rationale for each finding explaining why it was validated or dismissed.
   - The verification agent **MUST NOT** remove any findings.
   - The verification agent **MUST NOT** introduce any new findings.

4. Format the summary report.

   First, determine the report header based on review mode:
   - **PR mode**: `{PR title} (#{number})`
   - **Commit mode**: `Code Review: {short SHA}..HEAD — {YYYY-MM-DD}`
   - **Time-based mode**: `Code Review: Changes since {duration} — {YYYY-MM-DD}`
   - **Local changes mode**: `Code Review: Local Changes — {YYYY-MM-DD}`
   - **Branch comparison mode**: `Code Review: {branch} vs main — {YYYY-MM-DD}`

   Then format the report:

   ```markdown
   # 🤖 Claude Security Code Review 🤖

   {header}
   **Date:** {YYYY-MM-DD}

   ## Summary

   | Category              | Count |
   | --------------------- | ----- |
   | 🛑 Validated Findings | {n}   |
   | ❔ Dismissed Findings | {n}   |

   {Up to 4 sentences for overall assessment.}

   ## Validated Findings

   {Write each validated finding in this format: "- [Validated finding description]\n - Location: `filename.ts:42`\n - Confidence: 0|25|50|75|100\n - Rationale: [Why this was validated]"}

   ## Dismissed Findings

   {Write each dismissed finding in this format: "- [Dismissed finding description]\n - Location: `filename.ts:42`\n - Confidence: 0|25|50|75|100\n - Rationale: [Why this was dismissed]"}
   ```

   If a section has zero findings, omit that section entirely rather than rendering an empty heading.

5. Determine the output destination from the `--output` argument. If `--output` is omitted, check for the `$GITHUB_ACTIONS` environment variable — if set, default to `github`; otherwise default to `chat`.

   ### Output: `chat`

   Default when `--output` is omitted and not running in CI.
   1. Return the report directly to the user in the chat.
   2. Do **NOT** write any files.

   ### Output: `file`
   1. Write the report to the current working directory as `security-review-YYYY-MM-DD-{identifier}.md` where `{identifier}` is the PR number (e.g., `PR123`), commit SHA (short), or `local`.
   2. Do **NOT** use `gh pr comment`, `gh api`, or any MCP posting tool.
   3. Confirm the file path to the user after writing.

   ### Output: `github`

   Default when `--output` is omitted and `$GITHUB_ACTIONS` is set.
   1. Write the report to `/tmp/review-summary.md` using the **Write** tool.
   2. Append `\n\n<!-- bitwarden-security-code-review -->` at the end of the file content.
   3. Do **NOT** use `gh pr comment`, `gh api`, or any MCP posting tool.
   4. Confirm to the user: "Report written to `/tmp/review-summary.md` for workflow pickup."

   The workflow post-step will read this file and update the placeholder comment automatically.
