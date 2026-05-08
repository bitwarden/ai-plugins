---
name: auditing-hackerone-vulns
description: Audit all open HackerOne-sourced VULN Jira tickets and their linked engineering child items to identify what needs action. Use this skill whenever the user wants to: check VULN ticket status, see which HackerOne findings need status updates, identify vulnerabilities ready to verify or close, run a remediation audit, check "what do I need to do on my VULN tickets today", or get a prioritized view of open vulnerabilities. Outputs a sorted action table with emoji tokens. Always use this skill for HackerOne/VULN remediation tracking and status correlation tasks — don't try to do it from scratch.
allowed-tools: mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_issues, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_remote_links, Bash(gh api --method GET *), Bash(gh pr view *), Bash(gh release list *), Bash(gh api repos/bitwarden/*/compare/*)
---

## Action tokens (sorted order in output)

| Token | Label                  | When it applies                                                                                       |
| ----- | ---------------------- | ----------------------------------------------------------------------------------------------------- |
| 🔴    | **Update VULN Status** | Child item has progressed (In Progress/Review) but VULN is still at a lower status                    |
| 🟡    | **Mark Remediated**    | Child item is Done — set Remediation Date to merged PR date and move VULN to Remediated               |
| 🟢    | **Verify & Close**     | Fix is in a release that has already shipped — verify in prod, add Confirmation Date, close HackerOne |
| 🔵    | **Monitor**            | Work is actively in progress or in a pending release; no action needed yet                            |
| ⚪    | **Waiting**            | Child item exists but hasn't started                                                                  |
| ➖    | **No Child Item**      | VULN is Ready for Resolution but no engineering ticket linked yet                                     |

---

## Step 1 — Query open VULN issues

Use `search_issues` with this JQL:

```
project = VULN AND status not in (Done, Verified) AND "Source" = "HackerOne" ORDER BY priority DESC, updated DESC
```

Request fields: `summary`, `status`, `description`, `priority`, `created`, `updated`

Paginate if needed (default max 50; use `nextPageToken` to get all).

---

## Step 2 — Find child engineering items for each VULN

For each VULN key, run:

```
issue in linkedIssues("VULN-XXX")
```

Request fields: `summary`, `status`, `fixVersions`, `project`

- A VULN may have **multiple** child items. Collect them all.
- Ignore items in the same VULN project (those are sibling VULNs, not engineering tickets).
- Child items with `[VULN]` in the summary are the primary engineering tracking items.
- Some VULNs (especially fresh "Ready for Resolution") may have no child items yet → token ➖.

---

## Step 3 — Classify child item statuses

Map Jira statuses to these categories:

| Category        | Example statuses                                                |
| --------------- | --------------------------------------------------------------- |
| **Not Started** | To Do, Backlog, Open, New, In Analysis                          |
| **In Progress** | In Progress, In Development, In Review, Code Review, In Testing |
| **Done**        | Done, Closed, Resolved, Completed                               |
| **Abandoned**   | Abandoned, Won't Fix, Duplicate, Canceled                       |

For VULNs with multiple children: the **highest-priority active child** drives the action token. "In Progress" outranks "Not Started"; "Done" only counts if all non-abandoned children are Done.

---

## Step 4 — Search GitHub for PRs linked to child items

**JSON parsing rule** — Always use `gh`'s built-in `--jq` flag or standalone `jq` for JSON parsing. Never pipe to `python3` or any other interpreter — Python is not in this skill's `allowed-tools` and will trigger a permission prompt. If stderr s uppression is needed, place `2>/dev/null` _after_ the full `gh api ... --jq '...'` command, not before:

```bash
# Correct — 2>/dev/null after --jq, before the next pipe
gh api --method GET "repos/bitwarden/REPO/compare/A...B?per_page=250" \
  --jq '.commits[] | .commit.message | split("\n")[0]' 2>/dev/null \
  | grep "#PR_NUMBER"
```

**PR search** — Use `gh search prs` to find PRs. If that fails, fallback to the GitHub API with `gh api --method GET "search/"`

```bash
gh api --method GET "search/issues?q=CHILD-KEY+type:pr+org:bitwarden&per_page=10" \
  --jq '.items[] | {number,title,state,mergedAt,url:.html_url}'
```

For each PR that appears to be the correct fix (match on title/ticket key), get accurate merge details:

```bash
gh pr view PR_URL --json state,mergedAt,mergeCommit,baseRefName,title
```

**Determining release inclusion** — Bitwarden's repos (server, clients) use **release branches with cherry-picks**. The merge commit SHA on `main` gets a _new SHA_ when cherry-picked, so `compare/TAG...COMMIT_SHA` always returns "diverged" and is **unreliable**. Do not use it.

The correct method is to compare consecutive release tags and search for the PR number in commit messages (cherry-picks preserve the original PR number):

```bash
# 1. List non-draft, non-prerelease tags for the relevant repo
gh release list --repo bitwarden/REPO --limit 20 \
  --json tagName,publishedAt,isDraft,isPrerelease \
  | jq '.[] | select(.isDraft == false and .isPrerelease == false)'

# 2. Find the two consecutive tags that bracket the expected fix release
#    (e.g., v2026.4.0 and v2026.4.1)

# 3. List all commits in that range and grep for the PR number
gh api --method GET "repos/bitwarden/REPO/compare/TAG_PREV...TAG_RELEASE?per_page=250" \
  --jq '.commits[] | .commit.message | split("\n")[0]' \
  | grep "#PR_NUMBER"
```

- If the PR number **is found** → the fix is in that release ✅
- If the PR number **is NOT found** → the fix missed the RC cut and is NOT in that release ❌

**clients monorepo note**: The `bitwarden/clients` repo publishes separate release tags per client type: `web-vYYYY.M.P`, `cli-vYYYY.M.P`, `browser-vYYYY.M.P`, `desktop-vYYYY.M.P`. A fix deployed in `web-v2026.4.2` does **not** mean the browser extension has it — always check the specific product's tag if the vulnerability affects a specific client.

**Simple repos** (e.g., sm-action) use direct pushes without cherry-picks. For those, `compare/COMMIT_SHA...TAG` returning `"ahead"` means the TAG is a descendant of the commit — i.e., the commit IS in the release.

To confirm a release has been **deployed to production**, check the published date from `gh release list`. If `publishedAt` is in the past and the release is not draft/prerelease, it is live.

---

## Step 5 — Determine action token for each VULN

Apply this decision tree to every VULN, using the child item statuses classified in Step 3 and the PR/release data from Step 4:

```
VULN status "Ready for Resolution":
  → No child items linked?                                     → ➖ No Child Item
  → Child item exists, status Not Started?                     → ⚪ Waiting
  → Child item In Progress?                                    → 🔴 Update VULN to In Progress
  → All child items Done?                                      → 🟡 Mark Remediated

VULN status "In Progress" or "In Review":
  → Child item(s) still In Progress?                          → 🔵 Monitor
  → All child items Done, PR not yet found?                   → 🟡 Mark Remediated (investigate date)
  → All child items Done, PR merged?                          → 🟡 Mark Remediated (use PR merge date)

VULN status "Remediated":
  → Cannot determine release?                                  → 🔵 Monitor
  → PR in an upcoming/unreleased version?                      → 🔵 Monitor (release pending)
  → PR in a released, deployed version?                        → 🟢 Verify & Close
```

The **Remediation Date** should be the date the fix PR was merged to the default branch.

---

## Step 6 — Format the output report

Use this template. Omit any section (including `<details>` blocks) that has zero items — do not render empty headings or empty tables.

```markdown
# 🤖 HackerOne VULN Audit — {YYYY-MM-DD}

## Summary

| Token | Category                 | Count |
| ----- | ------------------------ | ----- |
| 🔴    | Need Status Update       | {n}   |
| 🟡    | Ready to Mark Remediated | {n}   |
| 🟢    | Ready to Verify & Close  | {n}   |
| 🔵    | Monitoring               | {n}   |
| ⚪    | Waiting                  | {n}   |
| ➖    | Missing Child Item       | {n}   |

{2–4 bullets: overall remediation health, anything overdue or stalled, patterns worth noting, any tickets with incomplete data that need manual follow-up}

## 🔴 Update VULN Status

| VULN            | Priority | Summary                        | HackerOne       | Child Item(s)   | Child Status | Action                   |
| --------------- | -------- | ------------------------------ | --------------- | --------------- | ------------ | ------------------------ |
| [VULN-529](...) | High     | Summary truncated to ~60 chars | [#3673748](...) | [PM-35250](...) | In Progress  | Move VULN to In Progress |

## 🟡 Mark Remediated

| VULN            | Priority | Summary                        | HackerOne       | Child Item(s)   | PR / Merged                    | Action                                        |
| --------------- | -------- | ------------------------------ | --------------- | --------------- | ------------------------------ | --------------------------------------------- |
| [VULN-529](...) | High     | Summary truncated to ~60 chars | [#3673748](...) | [PM-35250](...) | [#1234](...) merged 2026-04-30 | Set Remediated + Remediation Date: 2026-04-30 |

## 🟢 Verify & Close

| VULN            | Priority | Summary                        | HackerOne       | Child Item(s)   | PR / Release                         | Action                                                              |
| --------------- | -------- | ------------------------------ | --------------- | --------------- | ------------------------------------ | ------------------------------------------------------------------- |
| [VULN-529](...) | High     | Summary truncated to ~60 chars | [#3673748](...) | [PM-35250](...) | [#1234](...) → v2026.4.0 ✅ deployed | Verify fix in prod, add Confirmation Date, close HackerOne #3673748 |

<details>
<summary>🔵 Monitoring ({n} items — no action needed yet)</summary>

| VULN            | Priority | Summary                        | HackerOne       | Child Item(s)   | Child Status | PR / Release                        |
| --------------- | -------- | ------------------------------ | --------------- | --------------- | ------------ | ----------------------------------- |
| [VULN-529](...) | High     | Summary truncated to ~60 chars | [#3673748](...) | [PM-35250](...) | In Progress  | [#1234](...) → v2026.9.0 ⏳ pending |

</details>

<details>
<summary>⚪ Waiting ({n} items — not yet started)</summary>

| VULN            | Priority | Summary                        | HackerOne       | Child Item(s)   | VULN Status          |
| --------------- | -------- | ------------------------------ | --------------- | --------------- | -------------------- |
| [VULN-529](...) | Medium   | Summary truncated to ~60 chars | [#3673748](...) | [PM-35250](...) | Ready for Resolution |

</details>

<details>
<summary>➖ Missing Child Item ({n} items — needs engineering ticket)</summary>

| VULN            | Priority | Summary                        | HackerOne       | VULN Status          | Created    |
| --------------- | -------- | ------------------------------ | --------------- | -------------------- | ---------- |
| [VULN-529](...) | Low      | Summary truncated to ~60 chars | [#3673748](...) | Ready for Resolution | 2026-03-15 |

</details>
```

**Formatting notes:**

- **VULN**: Jira link, e.g. `[VULN-529](https://bitwarden.atlassian.net/browse/VULN-529)`
- **HackerOne**: Report link extracted from the first line of the description, e.g. `[#3673748](https://hackerone.com/reports/3673748)`. If not found, show `unknown` and flag it in the summary bullets.
- **Child Item(s)**: Jira link(s), e.g. `[PM-35250](https://bitwarden.atlassian.net/browse/PM-35250)`. If multiple, list each on its own line within the cell.
- **PR / Release**: e.g. `[#1234](PR_URL) → v2026.8.0 ✅ deployed`, `[#1234](PR_URL) → v2026.9.0 ⏳ pending`, or `No PR found`
- **Action**: One-line plain-English instruction specific to the token, e.g. "Move to In Progress", "Set Remediated + Remediation Date: 2026-04-30", or "Verify fix in prod, add Confirmation Date, close HackerOne #3673748"
- Truncate long summaries to ~60 chars

---

## Edge cases

- **VULN with 3+ child items** (e.g., one abandoned, one done, one in progress): the in-progress one drives the token. Show all children in the table.
- **Child item abandoned / Won't Fix**: Skip it for status purposes. If all children are abandoned, flag the VULN with 🔵 and note "all child items abandoned — review needed."
- **Fresh VULN with no description HackerOne URL**: Extract the report URL from the first line of the description. If not found, show "HackerOne: unknown" and flag it.
- **PR search returns no results**: Note "No PR found" in the table and still apply the decision tree using child item status alone.
- **Fix version "vNext-full" or similar placeholder**: Treat as "unreleased" until a real version number appears.
