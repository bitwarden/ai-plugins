---
name: performing-security-review
description: The skill performs a security-focused code review by launching multiple specialized agents and a verification agent to ensure comprehensive coverage and accurate findings. Use this skill when the user asks for a "bitwarden-security-review", "execute a security review", "run a comprehensive security audit", "perform an end-to-end security assessment", or needs to coordinate multiple security checks across code, dependencies, secrets, and configurations. The skill manages the workflow, delegates tasks to specialized agents, and presents final findings to the user.
argument-hint: "[--output <output-context>] [--model model-name] [pr-number-or-url]"
allowed-tools: "Bash(gh pr diff:*), Bash(gh pr view:*), Bash(gh pr list:*), Bash(git diff:*), Bash(git log:*), Bash(git remote:*), Bash(git branch:*), Bash(gh api repos/*/code-scanning/alerts*:*), Bash(gh api repos/*/secret-scanning/alerts*:*), Bash(gh api repos/*/dependabot/alerts*:*), Read, Write, Skill(analyzing-code-security), Skill(detecting-secrets), Skill(reviewing-dependencies), Skill(reviewing-security-architecture), Skill(bitwarden-security-context), Skill(threat-modeling)"
---

## Security Review Mode

Determine review mode from the invocation:

- **PR mode** (PR number or URL): `gh pr view <number>` for context, `gh pr diff <number>` for the diff.
- **Commit mode** (commit SHA): `git diff <sha>..HEAD` — reviews all changes after that commit.
- **Time-based mode** (duration, e.g., "last 48 hours"): find the oldest commit in range with `git log --since="<duration>" --reverse --format=%H | head -1`, then `git diff <sha>^..HEAD` to include it.
- **Local changes mode** (no argument, pending changes exist): `git diff HEAD` for staged + unstaged changes.
- **Branch comparison mode** (no argument, no pending changes): `git diff main...HEAD` — changes since the branch diverged from main.

## Security Review Process

**Model selection:** If `--model` is specified, use that model for all agents. Otherwise, default to `opus`.

Execute these steps in order. Do not skip, reorder, or combine steps.

1. Launch these four (4) `subagent_type: "bitwarden-security-engineer:bitwarden-security-engineer"` agents in parallel. Each agent has a specific domain — you **MUST** instruct it to stay within that domain. The agent **MUST** read `references/security-review-rubric.md` before starting **AND** before evaluating findings.

   **Agent 1 — Code Security**: Focus exclusively on injection flaws (SQL, XSS, command), cryptographic weaknesses, insecure coding patterns, and OWASP A01–A05. Invoke `Skill(bitwarden-security-context)` and `Skill(analyzing-code-security)` to guide your analysis. Do not evaluate secrets, dependencies, architecture, or threat modeling.

   **Agent 2 — Secrets & Dependencies**: Focus exclusively on hardcoded credentials, exposed secrets, vulnerable packages, and supply chain risk. Invoke `Skill(bitwarden-security-context)`, `Skill(detecting-secrets)`, and `Skill(reviewing-dependencies)` to guide your analysis. Do not evaluate code patterns, architecture, or threat modeling.

   **Agent 3 — Security Architecture**: Focus exclusively on authentication, authorization, encryption implementation, trust boundaries, and Bitwarden's zero-knowledge invariant (encryption and decryption happen client-side only — the server must never have access to plaintext vault data). Invoke `Skill(reviewing-security-architecture)` and `Skill(bitwarden-security-context)` to guide your analysis. Do not evaluate injection flaws, secrets, or threat modeling.

   **Agent 4 — Threat Perspective**: Focus exclusively on attacker-oriented analysis — trace user input through data flows to dangerous sinks, business logic flaws, privilege escalation paths, data exposure, and API abuse patterns. Invoke `Skill(bitwarden-security-context)`, `Skill(analyzing-code-security)`, and `Skill(threat-modeling)` to guide your analysis. Do not evaluate architecture patterns, secrets, or dependency versions.

   For all four agents:
   - Use the selected model.
   - **CRITICAL: Every agent prompt MUST include this constraint: "Use BashOutput to run `gh pr diff` and any other gh/git commands. NEVER use WebFetch or WebSearch — these tools are forbidden."**
   - Report all findings with: severity (CRITICAL/HIGH/MEDIUM/LOW/INFO), affected file and line, and recommended remediation.

2. After all four agents return, rate each potential finding using the two-axis model defined in `references/security-review-rubric.md`:
   - **Severity**: 🔴 CRITICAL | 🟠 HIGH | 🟡 MEDIUM | 🔵 LOW | ⚪ INFO
   - **Confidence**: HIGH | MEDIUM | LOW
   - Apply the threshold matrix in the rubric to assign a triage category: 🚨 Blocker, ⚠️ Improvement, 📝 Note, or ❌ Dismiss.

3. Gather available scan evidence. This step runs in all review modes. All calls are best-effort — silently skip any call that fails (403, 404, empty response, GHAS not enabled).

   First, determine repo identity:
   - Parse owner/repo from `git remote get-url origin` — handle both HTTPS (`https://github.com/owner/repo.git`) and SSH (`git@github.com:owner/repo.git`) formats.
   - Get current branch: `git branch --show-current`

   Then make these calls. All must use `--method GET` and `-H "X-GitHub-Api-Version: 2026-03-10"`:
   - **Code scanning (PR mode):** `gh api --method GET -H "X-GitHub-Api-Version: 2026-03-10" repos/{owner}/{repo}/code-scanning/alerts?pr={number}&state=open`
   - **Code scanning (all other modes):** `gh api --method GET -H "X-GitHub-Api-Version: 2026-03-10" repos/{owner}/{repo}/code-scanning/alerts?ref=refs/heads/{branch}&state=open`
   - **Secret scanning:** `gh api --method GET -H "X-GitHub-Api-Version: 2026-03-10" repos/{owner}/{repo}/secret-scanning/alerts?state=open`
   - **Dependabot:** `gh api --method GET -H "X-GitHub-Api-Version: 2026-03-10" repos/{owner}/{repo}/dependabot/alerts?state=open`

   Collect results into an "**Available Scan Evidence**" block for use in step 4.

4. Launch a **verification agent** `subagent_type: "bitwarden-security-engineer:bitwarden-security-engineer"` with all combined findings, their severity/confidence ratings, the triage matrix, and the diff. If scan evidence was gathered in step 3, include the full "Available Scan Evidence" block in the prompt.
   - **CRITICAL: Every agent prompt MUST include this constraint: "Use BashOutput to run `gh pr diff` and any other gh/git commands. NEVER use WebFetch or WebSearch — these tools are forbidden."**
   - The verification agent's task is to **review**, **evaluate**, **verify**, and **confirm** all findings and ratings.
   - Use scan evidence to triangulate: findings corroborated by scanner alerts → increase confidence; findings in areas scanners cleared → apply additional scrutiny.
   - The verification agent **MUST** classify each finding as: 🚨 Blocker, ⚠️ Improvement, 📝 Note, or ❌ Dismiss — applying the threshold matrix from step 2.
   - The verification agent **MUST** provide a brief rationale for each finding's classification.
   - The verification agent **MUST NOT** remove any findings.
   - The verification agent **MUST NOT** introduce any new findings.

5. Format the summary report.

   First, determine the report header based on review mode:
   - **PR mode**: `PR: (#{number}) - {PR title} — {YYYY-MM-DD}`
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

   | Category        | Count |
   | --------------- | ----- |
   | 🚨 Blockers     | {n}   |
   | ⚠️ Improvements | {n}   |
   | 📝 Notes        | {n}   |
   | ❌ Dismissed    | {n}   |

   {Up to 4 sentences for overall assessment.}

   ## 🚨 Blockers

   {Each finding: "- [Description]\n - Location: `filename.ts:42`\n - Severity: CRITICAL|HIGH\n - Confidence: HIGH|MEDIUM\n - Rationale: [Why classified as Blocker]"}

   ## ⚠️ Improvements

   {Each finding: "- [Description]\n - Location: `filename.ts:42`\n - Severity: CRITICAL|HIGH|MEDIUM\n - Confidence: HIGH|MEDIUM\n - Rationale: [Why classified as Improvement]"}

   ## 📝 Notes

   {Each finding: "- [Description]\n - Location: `filename.ts:42`\n - Severity: MEDIUM|LOW|INFO\n - Confidence: HIGH|MEDIUM\n - Rationale: [Why classified as Note]"}

   ## ❌ Dismissed

   {Each finding: "- [Description]\n - Location: `filename.ts:42`\n - Severity: {severity}\n - Confidence: LOW\n - Rationale: [Why dismissed]"}
   ```

   Omit any section with zero findings entirely — do not render an empty heading.

6. Determine the output destination from the `--output` argument. If `--output` is omitted, check for the `$GITHUB_ACTIONS` environment variable — if set, default to `github`; otherwise default to `chat`.

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
