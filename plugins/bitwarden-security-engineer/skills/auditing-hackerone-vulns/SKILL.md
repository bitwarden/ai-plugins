---
name: auditing-hackerone-vulns
description: Audit every open HackerOne report across Bitwarden's VDP and Bug Bounty programs, correlate each to its VULN Jira ticket and linked engineering child items, and identify what needs action. Use this skill whenever the user wants to: list open HackerOne reports, check VULN ticket status, see which HackerOne findings need status updates, identify vulnerabilities ready to verify or close, run a remediation audit, check "what do I need to do on my VULN tickets today", or get a prioritized view of open vulnerabilities. HackerOne is the source of truth for what is open, while Jira and GitHub supply remediation state. Outputs a sorted action table with emoji tokens. Always use this skill for HackerOne/VULN remediation tracking and status correlation tasks — don't try to do it from scratch.
allowed-tools: mcp__hackerone__list_programs, mcp__hackerone__search_reports, mcp__hackerone__get_report, mcp__hackerone__get_report_activities, mcp__hackerone__get_current_user, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_issues, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_remote_links, Bash(base64 *), Bash(gh api --method GET *), Bash(gh pr view *), Bash(gh api repos/bitwarden/*/compare/*), Bash(gh search prs *)
---

## Direction of traversal

**HackerOne is the source of truth.** Start from the open report list on both programs, then walk outward to Jira for remediation state and to GitHub for release state. Do not start from a `project = VULN` JQL sweep — a Jira-first query drifts from what is actually open on the programs and silently misses reports that never got a VULN ticket created.

```
HackerOne open reports  →  VULN Jira ticket  →  engineering child items  →  fix PR  →  release
   (Step 1)                  (Step 2)             (Step 3-4)                 (Step 5)
```

---

## Tool usage rules — read before executing any step

- **Only use tools listed in `allowed-tools`.** Do not use `curl`, `wget`, `python3`, `node`, or any interpreter or HTTP client not in the list.
- **Do not write files.** Do not write to `/tmp/`, to any file path, or use heredocs (`cat > FILE << 'EOF'`). Hold all data in-memory between steps.
- **Do not write shell scripts to orchestrate the audit.** No `&` background processes, no `wait`, no associative arrays, no multi-step bash loops over tickets. When this skill says "in parallel", it means issue multiple **Claude tool calls** in the same response turn, not shell concurrency.
- **No shell expansion.** Do not use `$VAR`, `$(...)`, backticks, or `for`/`while` loops in any Bash command. The harness cannot pre-validate a command whose text is built at runtime, so every one of them stops the audit on an approval prompt. Write inert literal commands instead, even when that means a longer command string.
- **No `sed`, `awk`, or other tools that can write or execute.** They stop the audit on an approval prompt even for a read-only substitution, because the harness cannot prove from the command text that no write or execute subcommand is present. Prefer no post-processing at all, and reach for `grep`/`jq` when you genuinely need to reshape output.
- **No interpreter pipes.** Do not pipe command output to `python3`, `node`, `ruby`, or any interpreter. Use `--jq` or standalone `jq` for JSON.
- **No error suppression.** Do not add `2>/dev/null` to any command. Silent failures are indistinguishable from empty results and waste follow-up calls.
- **Never fetch release note body text.** Do not call `repos/bitwarden/REPO/releases/tags/TAG` and read the `.body` field. Release note bodies run to hundreds of lines of markdown and will flood the context window.

---

## Action tokens (sorted order in output)

| Token | Label                      | When it applies                                                                                        |
| ----- | -------------------------- | ------------------------------------------------------------------------------------------------------ |
| 🆕    | **Create VULN Ticket**     | HackerOne report is open but has no linked VULN Jira ticket at all                                     |
| 🟣    | **Close HackerOne Report** | VULN is Closed/Rejected/Done but the HackerOne report is still open — the report needs a resolution    |
| 🔴    | **Update VULN Status**     | Child item has progressed (In Progress/Review) but VULN is still at a lower status                     |
| 🟡    | **Mark Remediated**        | Child item is Done — set Remediation Date to merged PR date and move VULN to Remediated                |
| 🟢    | **Verify & Close**         | Fix is in a release that has already shipped — verify in prod, add Confirmation Date, close HackerOne  |
| 🏁    | **Close Out**              | VULN is already Verified (fix confirmed in prod) — close the report and move the Jira ticket to Closed |
| 🔵    | **Monitor**                | Work is actively in progress or in a pending release; no action needed yet                             |
| ⚪    | **Waiting**                | Child item exists but hasn't started                                                                   |
| ➖    | **No Child Item**          | VULN exists and is Ready for Resolution but no engineering ticket linked yet                           |

---

## Step 1 — Enumerate open HackerOne reports across both programs

Resolve program handles first rather than hardcoding them:

```
list_programs()
```

Bitwarden runs two programs, and **both must be audited**:

| Handle          | Name          | Type                           |
| --------------- | ------------- | ------------------------------ |
| `bitwarden`     | Bitwarden     | Vulnerability Disclosure (VDP) |
| `bitwarden-bbp` | Bitwarden BBP | Bug Bounty                     |

Pass both handles in a single call so reports interleave by date:

```
search_reports(
  program_handles=["bitwarden", "bitwarden-bbp"],
  states=["new", "triaged"],
  sort="created_at",
  page_size=100
)
```

**API constraints — do not deviate:**

- `program_handles` is **required**. Omitting it errors.
- `states=["new", "triaged"]` is the working "open" filter. The values `open` and `needs-more-info` cause the API to return **HTTP 500** — do not pass them. `new` plus `triaged` covers everything actionable, and `duplicate`, `informative`, `not-applicable`, and `resolved` are terminal and correctly excluded.
- `sort="created_at"` gives oldest-first, which is the useful ordering for an audit. Prefix with `-` for newest-first.
- Paginate on `meta.has_next_page` using `page_number` until exhausted.

**Report IDs come back as base64 GIDs**, not numbers. Decode them to get the numeric IDs needed for report URLs and for `get_report` / `get_report_activities`.

Decode the whole batch in **one** call, passing the GIDs as a newline-separated literal exactly as the API returned them, and do **not** post-process the output:

```bash
echo 'Z2lkOi8vaGFja2Vyb25lL1JlcG9ydC8yODY1MDQ4
Z2lkOi8vaGFja2Vyb25lL1JlcG9ydC8zNTcyMDg2
Z2lkOi8vaGFja2Vyb25lL1JlcG9ydC8zOTY5MzYy' | base64 -d
```

```
gid://hackerone/Report/2865048gid://hackerone/Report/3572086gid://hackerone/Report/3969362
```

Read the IDs straight out of that string. They are delimited by the constant `gid://hackerone/Report/` prefix, so no splitting step is required.

**Keep the pipeline to `echo` and `base64` only.** Piping into `sed` triggers an approval prompt, because `sed` supports write and execute subcommands and the harness cannot rule those out from the command text alone. `grep -oE '[0-9]+'` gives tidier one-per-line output and is usually permitted, but it is an optional convenience — if it prompts, drop it and parse the raw string.

```bash
# Optional, only if it runs unprompted here
echo 'Z2lkOi8vaGFja2Vyb25lL1JlcG9ydC8yODY1MDQ4
Z2lkOi8vaGFja2Vyb25lL1JlcG9ydC8zNTcyMDg2' | base64 -d | LC_ALL=C grep -oE '[0-9]+'
```

**Do not write a `for` loop over the GIDs.** A loop needs a shell variable (`for s in ...; do echo "$s" | base64 -d; done`), and that variable expansion cannot be pre-validated by the harness, so it triggers an approval prompt on every audit run. The single-call form above is an inert literal with no expansion of any kind, so it runs unprompted.

Why the batch decode is valid: each payload is `gid://hackerone/Report/` (23 bytes) plus a 7-digit ID, which is exactly 30 bytes. Because 30 is a multiple of 3, every GID encodes to an unpadded 40-character string, so concatenating them stays valid base64. `base64 -d` also ignores whitespace between the GIDs, which is what removes the need to join the list by hand and makes indentation from a wrapped paste harmless.

- **Check that the count of decoded IDs matches the number of GIDs passed in.** A mistyped or truncated GID corrupts the stream from that point onward and surfaces as visible garbage in the middle of the output. If the counts disagree, decode the offending entries individually with `echo 'GID' | base64 -d`.
- If HackerOne report IDs ever reach 8 digits the payload becomes 31 bytes, padding appears, and concatenation breaks. Decode per-entry if that happens.
- `LC_ALL=C` on the optional `grep` guards against it aborting with `illegal byte sequence` when a byte in the stream is malformed.

Record for each report: numeric ID, title, program handle, `severity.rating`, `state`/`substate`, and `created_at`.

---

## Step 2 — Correlate each report to its VULN Jira ticket

Every VULN ticket embeds its HackerOne URL on the first line of the description (`HackerOne Report: https://hackerone.com/reports/NNNNNNN`). Exploit that to build the whole mapping in **one** Jira call instead of one call per report.

```
project = VULN AND status not in (Done, Closed, Rejected, Resolved, Canceled) ORDER BY created ASC
```

Request fields: `summary`, `status`, `description`, `priority`, `created`, `updated`

Parse the report ID out of each description and build a `report ID → VULN key` map, then join against the Step 1 list.

> **`Verified` is intentionally not excluded.** A Verified VULN has had its fix confirmed in production but the Jira ticket has not yet been moved to `Closed`. These surface under the 🏁 Close Out token so the remaining status flip doesn't get forgotten. They need no child-item or GitHub lookups — skip Steps 3 through 5 for them and route straight to 🏁 in Step 6.

**Critical JQL gotcha:** in the VULN project, `status not in (Done, Verified)` does **not** exclude `Rejected` or `Closed` — those are distinct statuses and will flood the result set with terminal tickets. Use the full exclusion list above.

**For any open report with no match in that map**, resolve it individually before concluding no ticket exists:

1. Check whether the VULN exists but is already terminal:

   ```
   project = VULN AND description ~ "NNNNNNN"
   ```

   A hit here means the VULN was closed or rejected while the HackerOne report stayed open → token 🟣.

   Treat a miss here as inconclusive, not as proof. Jira's `~` operator is a tokenized full-text match, so a bare report ID embedded inside a URL may not register as its own search term. Always fall through to the activity thread below before concluding no ticket exists.

2. Confirm against the report's own activity thread:

   ```
   get_report_activities(report_id="NNNNNNN", page_size=100)
   ```

   The Jira link lives in the activity timeline, **not** in the `get_report` payload. Look for an `ActivitiesReferenceIdAdded` entry, followed by `ActivitiesComment` entries reading `The [Jira issue](https://bitwarden.atlassian.net/browse/VULN-NNN) associated with this report was modified.` Those comments are `is_internal: true`, so program access is required to see them.

3. No `ActivitiesReferenceIdAdded` anywhere in the thread means no ticket was ever created → token 🆕.

The activity thread is also the best place to recover **why** something stalled — it carries the internal engineering discussion and the full history of Jira status transitions. Pull it for anything old or blocked before writing the summary.

---

## Step 3 — Find child engineering items for each VULN

For each VULN key, run:

```
issue in linkedIssues("VULN-XXX")
```

Request fields: `summary`, `status`, `fixVersions`, `project`

**MCP gotcha:** requesting `issuelinks` on `search_issues` does not work — the formatter silently drops the field and returns issues with no link data, which reads as "no children" when children exist. `get_issue` does not return linked issues either. `linkedIssues()` is the only reliable path, and it needs one call per VULN. Issue several as parallel tool calls in one turn rather than waiting on each.

- A VULN may have **multiple** child items. Collect them all.
- Ignore items in the same VULN project (those are sibling or related VULNs, not engineering tickets) — but note them, since a cluster of linked VULNs usually means duplicate reports of one root cause worth calling out.
- Child items with `[VULN]` in the summary are the primary engineering tracking items. Some are further split per team, e.g. `[VULN] [Platform Team] ...` and `[VULN] [Desktop Native Team] ...`.
- Children can land in any project (`PM`, `SRE`, and others). An `SRE` child being Done while the `PM` code fix is still in backlog is a common half-remediated shape — do not read one Done child as the whole fix.
- Some VULNs (especially fresh "Ready for Resolution") may have no child items yet → token ➖.

---

## Step 4 — Classify child item statuses

Map Jira statuses to these categories:

| Category        | Example statuses                                                       |
| --------------- | ---------------------------------------------------------------------- |
| **Not Started** | To Do, Backlog, In Backlog, Open, New, In Analysis, Ready for Dev      |
| **In Progress** | In Progress, In Development, In Review, Code Review, In Testing, In QA |
| **Done**        | Done, Closed, Resolved, Completed                                      |
| **Blocked**     | On Hold, Blocked                                                       |
| **Abandoned**   | Abandoned, Won't Fix, Duplicate, Canceled, Rejected                    |

For VULNs with multiple children: the **highest-priority active child** drives the action token. "In Progress" outranks "Not Started", and "Done" only counts if all non-abandoned children are Done.

**Blocked** is distinct from Not Started and must not be collapsed into it. An `On Hold` child means the work has actively stopped rather than merely queued, so surface it explicitly in the summary instead of letting it sit quietly under ⚪ Waiting.

---

## Step 5 — Search GitHub for PRs linked to child items

**Only execute this step for child items classified as Done in Step 4.** If every child item for a VULN is Not Started, In Progress, Blocked, or Abandoned, skip directly to Step 6 for that VULN — there is no PR to find yet and no GitHub call is needed.

**Do not trust Jira's `Fix Version` "(Released)" annotation as evidence of deployment.** The field is set aspirationally when the engineering ticket is resolved and is not corrected when the cherry-pick into the release branch is missed. The release tag's actual commit log is the only source of truth.

**PR search** — Use the GitHub Search API to find PRs. You may issue multiple independent search tool calls in the same response turn, one per child item key.

```bash
gh api --method GET "search/issues?q=CHILD-KEY+type:pr+org:bitwarden&per_page=10" \
  --jq '.items[] | {number,title,state,mergedAt:.pull_request.merged_at,url:.html_url}'
```

Note the field mapping: the Search Issues API returns `pull_request.merged_at`, not `mergedAt`. Always use `.pull_request.merged_at` in the `--jq` filter — otherwise `mergedAt` will be null for every result.

Search on the **child item key** (`PM-40120`), never on the HackerOne report ID. Public PR titles and branches reference the engineering ticket only, because HackerOne report IDs are deliberately kept out of public GitHub artifacts.

**Two-attempt cap on PR searches.** If the first search (by child item key) returns no results, try one more search using the VULN key (e.g. `VULN-529+type:pr+org:bitwarden`). If that also returns no results, mark "No PR found" and move on. Do not try keyword searches, repo-scoped retries, or other fallback queries — they rarely succeed and waste significant time.

**Skip `gh pr view` when the merge date is already known.** Only call `gh pr view PR_URL --json state,mergedAt,baseRefName,title` if the search returned `mergedAt: null`. If `gh pr view` also returns `mergedAt: null`, the PR was not merged — record it as closed-without-merge and move on.

**Listing releases** — `gh release list` is blocked by this skill's `allowed-tools`. Use the Releases API instead:

```bash
gh api --method GET "repos/bitwarden/REPO/releases?per_page=20" \
  --jq '.[] | select(.draft == false and .prerelease == false) | {tagName: .tag_name, publishedAt: .published_at}'
```

**Determining release inclusion** — Bitwarden uses two release strategies. Use the correct method per repo.

**`bitwarden/server` and `bitwarden/clients` (cherry-pick workflow)** — release branches are cut from `main` and fixes must be **explicitly cherry-picked** to ship. A PR merged before a release was published is **not** automatically in it, because the cherry-pick may have slipped. Merge-date inference produces false positives here.

Verify cherry-pick presence by searching the release range's commit messages for the PR number. Bitwarden cherry-pick commits preserve the original `(#NNNN)` suffix from the source PR:

```bash
gh api --method GET "repos/bitwarden/REPO/compare/PREV_TAG...CANDIDATE_TAG" \
  --jq '.commits[].commit.message' | grep -E "\(#PR_NUMBER\)"
```

1. From the release list, identify the **earliest release where `publishedAt > PR.mergedAt`** — that is the **candidate** release, not yet confirmed.
2. Run the compare-and-grep above against `PREV_TAG...CANDIDATE_TAG`.
   - Match found → fix is in that release ✅
   - No match → cherry-pick was missed and the fix is on `main` only → mark 🔵 Monitor and flag for engineering follow-up
3. If `PR.mergedAt` is after the latest release's `publishedAt` → not yet released → mark 🔵 Monitor.

> Tag-to-tag `compare` is the right tool here. The thing to avoid is `MERGE_COMMIT_SHA...TAG`, which returns "diverged" for cherry-picked commits because the SHA is rewritten. Tag-to-tag comparison lists what shipped between two releases regardless of SHA rewrites.

**clients monorepo tags** — only use the tag type relevant to the affected client: `web-vYYYY.M.P`, `browser-vYYYY.M.P`, `desktop-vYYYY.M.P`, `cli-vYYYY.M.P`. A fix in `web-v2026.4.2` does **not** mean the browser extension has it. Do not check all four types for every PR.

**Picking the right repo** — derive it from the affected product, not from the child item's project. `clients` covers web, browser, desktop, and CLI; `ios` and `android` are standalone repos; `server` covers API/Identity/Admin. A report against the browser extension is a `clients` fix even though its ticket is a `PM` item.

**Direct-push repos** (e.g. `bitwarden/sm-action`) — commits push directly to release branches without cherry-picks, so `compare/COMMIT_SHA...TAG` is usable. GitHub's `status` field describes head relative to base, so a TAG that contains the commit plus later work reports `ahead`, and a TAG pointing at exactly that commit reports `identical`. Treat `ahead` or `identical` as in-release and `diverged` as not. Check `total_commits` first and skip the compare if it is 500 or more.

To confirm a release has been **deployed to production**, check the `publishedAt` date from the releases API response. If it is in the past and the release is not draft or prerelease, it is live.

---

## Step 6 — Determine action token for each report

Apply this decision tree to every **open HackerOne report**, using the correlation from Step 2, child statuses from Step 4, and PR/release data from Step 5:

```
No VULN ticket found at all?                                   → 🆕 Create VULN Ticket
VULN exists but is Closed / Rejected / Done?                   → 🟣 Close HackerOne Report

VULN status "Verified":
  → Fix already confirmed in prod                              → 🏁 Close report + move VULN to Closed

VULN status "New" or "Ready for Resolution":
  → No child items linked?                                     → ➖ No Child Item
  → Child item exists, status Not Started?                     → ⚪ Waiting
  → Child item Blocked (On Hold)?                              → ⚪ Waiting (flag as stalled)
  → Child item In Progress?                                    → 🔴 Update VULN to In Progress
  → All child items Done?                                      → 🟡 Mark Remediated

VULN status "In Progress" or "In Review":
  → Child item(s) still In Progress?                           → 🔵 Monitor
  → All non-abandoned child items Done, PR not yet found?      → 🟡 Mark Remediated (investigate date)
  → All non-abandoned child items Done, PR merged?             → 🟡 Mark Remediated (use PR merge date)

VULN status "Remediated":
  → Cannot determine release?                                  → 🔵 Monitor
  → PR in an upcoming/unreleased version?                      → 🔵 Monitor (release pending)
  → Cherry-pick missed, fix on main only?                      → 🔵 Monitor (flag for engineering)
  → PR in a released, deployed version
    (verified by commit-presence check, not Jira Fix Version)? → 🟢 Verify & Close
```

The **Remediation Date** should be the date the fix PR was merged to the default branch.

---

## Step 7 — Reconciliation sweep

Traversing from HackerOne catches everything open on the programs, but it cannot see a VULN that is still open in Jira while its HackerOne report was already closed. Those tickets represent real unfinished work, so close the loop:

```
project = VULN AND status not in (Done, Closed, Rejected, Resolved, Canceled) ORDER BY created ASC
```

This is the same result set already fetched in Step 2. Any VULN in it whose report ID did **not** appear in the Step 1 open list is an orphan: engineering work still tracked in Jira against an already-resolved report. List these in a separate section and do not fold them into the main token counts, because HackerOne has nothing left to action on them.

---

## Step 8 — Format the output report

Use this template. Omit any section (including `<details>` blocks) that has zero items — do not render empty headings or empty tables.

```markdown
# 🤖 HackerOne VULN Audit — {YYYY-MM-DD}

## Summary

| Token | Category                 | Count |
| ----- | ------------------------ | ----- |
| 🆕    | Needs VULN Ticket        | {n}   |
| 🟣    | Close HackerOne Report   | {n}   |
| 🔴    | Need Status Update       | {n}   |
| 🟡    | Ready to Mark Remediated | {n}   |
| 🟢    | Ready to Verify & Close  | {n}   |
| 🏁    | Ready to Close Out       | {n}   |
| 🔵    | Monitoring               | {n}   |
| ⚪    | Waiting                  | {n}   |
| ➖    | Missing Child Item       | {n}   |

{n} open reports total, {n} on `bitwarden` (VDP) and {n} on `bitwarden-bbp` (BBP).

{2–4 bullets: overall remediation health, anything overdue or stalled, patterns worth noting, any reports with incomplete data that need manual follow-up}

## 🆕 Create VULN Ticket

| HackerOne       | Program | Submitted  | Sev | Title                        | Action                                     |
| --------------- | ------- | ---------- | --- | ---------------------------- | ------------------------------------------ |
| [#3968639](...) | VDP     | 2026-08-25 | Low | Title truncated to ~60 chars | Create VULN ticket and link to this report |

## 🟣 Close HackerOne Report

| HackerOne       | Program | Submitted  | Sev  | Title                        | VULN            | VULN Status | Action                                  |
| --------------- | ------- | ---------- | ---- | ---------------------------- | --------------- | ----------- | --------------------------------------- |
| [#3673748](...) | BBP     | 2026-04-11 | High | Title truncated to ~60 chars | [VULN-529](...) | Rejected    | Close report as Informative / Duplicate |

## 🔴 Update VULN Status

| HackerOne       | Program | Submitted  | Sev  | Title                        | VULN            | VULN Status          | Child Item(s)   | Child Status | Action                   |
| --------------- | ------- | ---------- | ---- | ---------------------------- | --------------- | -------------------- | --------------- | ------------ | ------------------------ |
| [#3673748](...) | BBP     | 2026-04-11 | High | Title truncated to ~60 chars | [VULN-529](...) | Ready for Resolution | [PM-35250](...) | In Progress  | Move VULN to In Progress |

## 🟡 Mark Remediated

| HackerOne       | Program | Submitted  | Sev  | Title                        | VULN            | Child Item(s)   | PR / Merged                    | Action                                        |
| --------------- | ------- | ---------- | ---- | ---------------------------- | --------------- | --------------- | ------------------------------ | --------------------------------------------- |
| [#3673748](...) | BBP     | 2026-04-11 | High | Title truncated to ~60 chars | [VULN-529](...) | [PM-35250](...) | [#1234](...) merged 2026-04-30 | Set Remediated + Remediation Date: 2026-04-30 |

## 🟢 Verify & Close

| HackerOne       | Program | Submitted  | Sev  | Title                        | VULN            | Child Item(s)   | PR / Release                         | Action                                                              |
| --------------- | ------- | ---------- | ---- | ---------------------------- | --------------- | --------------- | ------------------------------------ | ------------------------------------------------------------------- |
| [#3673748](...) | BBP     | 2026-04-11 | High | Title truncated to ~60 chars | [VULN-529](...) | [PM-35250](...) | [#1234](...) → v2026.4.0 ✅ deployed | Verify fix in prod, add Confirmation Date, close HackerOne #3673748 |

## 🏁 Close Out

| HackerOne       | Program | Submitted  | Sev    | Title                        | VULN            | VULN Status | Action                                                           |
| --------------- | ------- | ---------- | ------ | ---------------------------- | --------------- | ----------- | ---------------------------------------------------------------- |
| [#3673748](...) | VDP     | 2026-03-02 | Medium | Title truncated to ~60 chars | [VULN-442](...) | Verified    | Close HackerOne report and move VULN to Closed (already in prod) |

<details>
<summary>🔵 Monitoring ({n} items — no action needed yet)</summary>

| HackerOne       | Program | Submitted  | Sev  | Title                        | VULN            | Child Item(s)   | Child Status | PR / Release                        |
| --------------- | ------- | ---------- | ---- | ---------------------------- | --------------- | --------------- | ------------ | ----------------------------------- |
| [#3673748](...) | BBP     | 2026-04-11 | High | Title truncated to ~60 chars | [VULN-529](...) | [PM-35250](...) | In Progress  | [#1234](...) → v2026.9.0 ⏳ pending |

</details>

<details>
<summary>⚪ Waiting ({n} items — not yet started)</summary>

| HackerOne       | Program | Submitted  | Sev    | Title                        | VULN            | VULN Status          | Child Item(s)   | Child Status |
| --------------- | ------- | ---------- | ------ | ---------------------------- | --------------- | -------------------- | --------------- | ------------ |
| [#3673748](...) | VDP     | 2026-04-11 | Medium | Title truncated to ~60 chars | [VULN-529](...) | Ready for Resolution | [PM-35250](...) | On Hold      |

</details>

<details>
<summary>➖ Missing Child Item ({n} items — needs engineering ticket)</summary>

| HackerOne       | Program | Submitted  | Sev | Title                        | VULN            | VULN Status          |
| --------------- | ------- | ---------- | --- | ---------------------------- | --------------- | -------------------- |
| [#3673748](...) | VDP     | 2026-03-15 | Low | Title truncated to ~60 chars | [VULN-529](...) | Ready for Resolution |

</details>

<details>
<summary>🗂️ Orphaned VULNs ({n} items — HackerOne report already closed)</summary>

| VULN            | VULN Status | Summary                        | HackerOne       | H1 State  | Child Item(s)   | Child Status |
| --------------- | ----------- | ------------------------------ | --------------- | --------- | --------------- | ------------ |
| [VULN-529](...) | In Progress | Summary truncated to ~60 chars | [#3673748](...) | duplicate | [PM-35250](...) | In Backlog   |

</details>
```

**Formatting notes:**

- **HackerOne**: `[#3673748](https://hackerone.com/reports/3673748)`, using the decoded numeric ID from Step 1.
- **Program**: `VDP` for `bitwarden`, `BBP` for `bitwarden-bbp`. Always show it — bounty obligations and response expectations differ between the two.
- **Submitted**: report `created_at` as `YYYY-MM-DD`. Sort every table oldest-first so aging reports surface at the top.
- **Sev**: HackerOne `severity.rating`, not the Jira priority. Show `none` when the report carries no rating.
- **VULN**: Jira link, e.g. `[VULN-529](https://bitwarden.atlassian.net/browse/VULN-529)`
- **Child Item(s)**: Jira link(s), e.g. `[PM-35250](https://bitwarden.atlassian.net/browse/PM-35250)`. If multiple, list each on its own line within the cell.
- **PR / Release**: e.g. `[#1234](PR_URL) → v2026.8.0 ✅ deployed`, `[#1234](PR_URL) → v2026.9.0 ⏳ pending`, `[#1234](PR_URL) → cherry-pick missed ⚠️`, or `No PR found`
- **Action**: One-line plain-English instruction specific to the token, e.g. "Move to In Progress", "Set Remediated + Remediation Date: 2026-04-30", or "Verify fix in prod, add Confirmation Date, close HackerOne #3673748"
- Truncate long titles to ~60 chars

---

## Edge cases

- **Report open on both programs**: the same researcher sometimes files to VDP and BBP. Treat them as separate rows but note the pairing, since only one needs an engineering fix.
- **VULN with 3+ child items** (e.g. one abandoned, one done, one in progress): the in-progress one drives the token. Show all children in the table.
- **Child item abandoned / Won't Fix / Rejected**: Skip it for status purposes. If all children are abandoned, flag the report with 🔵 and note "all child items abandoned — review needed." A primary `[VULN]` child that was abandoned while smaller follow-ups remain open usually means the fix approach changed — read the activity thread and say what replaced it.
- **Blocked on an upstream dependency**: when the remaining children only track a third-party fix (a Chromium bug, a vendor patch), say so explicitly rather than reporting it as ordinary backlog. These need a reporter update, not a status change.
- **Cluster of duplicate reports**: several open reports mapping to linked sibling VULNs on one root cause. Call the cluster out once in the summary rather than repeating the analysis per row, and note that unfixed root causes keep generating new reports.
- **Half-remediated VULN**: one child Done, another still open (commonly an `SRE` config change done ahead of the `PM` code fix). This is **not** 🟡 — it stays 🔵 Monitor until every non-abandoned child is Done.
- **Cherry-pick missed**: child Done and PR merged, but the PR number is absent from every release range. This is the case Jira's Fix Version field will misreport as released. Mark 🔵 Monitor and flag it, because the fix is not actually in customers' hands.
- **PR search returns no results**: Note "No PR found" in the table and still apply the decision tree using child item status alone.
- **Fix version "vNext-full" or similar placeholder**: Treat as "unreleased" until a real version number appears.
- **`get_report_activities` age restriction**: the HackerOne MCP applies a 10-minute age filter. A report filed moments ago may return an incomplete timeline; note it rather than concluding no ticket exists.
- **No assignee filter**: `search_reports` cannot filter by assignee, so the audit is always program-wide. State this in the summary whenever the user asked for "my" reports.
