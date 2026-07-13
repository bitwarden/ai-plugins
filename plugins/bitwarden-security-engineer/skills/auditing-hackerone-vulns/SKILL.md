---
name: auditing-hackerone-vulns
description: Audit all open HackerOne-sourced VULN Jira tickets and their linked engineering child items to identify what needs action. Use this skill whenever the user wants to: check VULN ticket status, see which HackerOne findings need status updates, identify vulnerabilities ready to verify or close, run a remediation audit, check "what do I need to do on my VULN tickets today", or get a prioritized view of open vulnerabilities. Outputs a sorted action table with emoji tokens. Always use this skill for HackerOne/VULN remediation tracking and status correlation tasks — don't try to do it from scratch.
allowed-tools: mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_issues, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_remote_links, Bash(gh api --method GET *), Bash(gh pr view *), Bash(gh api repos/bitwarden/*/compare/*), Bash(gh search prs *)
---

## Action tokens (sorted order in output)

| Token | Label                  | When it applies                                                                                       |
| ----- | ---------------------- | ----------------------------------------------------------------------------------------------------- |
| 🔴    | **Update VULN Status** | Child item has progressed (In Progress/Review) but VULN is still at a lower status                    |
| 🟡    | **Mark Remediated**    | Child item is Done — set Remediation Date to merged PR date and move VULN to Remediated               |
| 🟢    | **Verify & Close**     | Fix is in a release that has already shipped — verify in prod, add Confirmation Date, close HackerOne |
| 🏁    | **Close Out**          | VULN is already Verified (fix confirmed in prod) — move the Jira ticket to Closed                     |
| 🔵    | **Monitor**            | Work is actively in progress or in a pending release; no action needed yet                            |
| ⚪    | **Waiting**            | Child item exists but hasn't started                                                                  |
| ➖    | **No Child Item**      | VULN is Ready for Resolution but no engineering ticket linked yet                                     |

---

## Tool usage rules — read before executing any step

- **Only use tools listed in `allowed-tools`.** Do not use `curl`, `wget`, `python3`, `node`, or any interpreter or HTTP client not in the list.
- **Do not write files.** Do not write to `/tmp/`, to any file path, or use heredocs (`cat > FILE << 'EOF'`). Hold all data in-memory between steps.
- **Do not use shell parallelism.** Do not use `&` background processes, `wait`, `declare -A` / `typeset -A` associative arrays, or multi-step bash/zsh scripts. When this skill says "in parallel", it means issue multiple **Claude tool calls** in the same response turn — not shell concurrency.
- **No interpreter pipes.** Do not pipe command output to `python3`, `node`, `ruby`, or any interpreter. Use `--jq` or standalone `jq` for JSON.
- **No error suppression.** Do not add `2>/dev/null` to any command. Silent failures are indistinguishable from empty results and waste follow-up calls.

---

## Step 1 — Query open VULN issues

Use `search_issues` with this JQL:

```
project = VULN AND status not in (Done, Closed, Rejected, Resolved, Canceled) AND "Source" = "HackerOne" ORDER BY priority DESC, updated DESC
```

Request fields: `summary`, `status`, `description`, `priority`, `created`, `updated`, `issuelinks`

Paginate if needed (default max 50; use `nextPageToken` to get all).

> **Note**: `Verified` is intentionally **not** excluded. A Verified VULN has had its fix confirmed in production but the Jira ticket has not yet been moved to `Closed`. These surface under the 🏁 Close Out token so the remaining status flip doesn't get forgotten. They need no child-item or GitHub lookups — skip Steps 2–4 for them and route straight to 🏁 in Step 5.

---

## Step 2 — Collect and batch-fetch child engineering items

**Do not loop over VULNs one at a time.** Instead:

1. **Extract child keys from `issuelinks`** already returned in Step 1. For each VULN, scan its `issuelinks` array and collect the keys of linked issues that are NOT in the VULN project (those are engineering tickets, not sibling VULNs).

2. **Deduplicate** the collected keys into a single list.

3. **Batch-fetch all child items in one JQL call** (split into pages of 50 if needed):

   ```
   issue in (KEY1, KEY2, KEY3, ...)
   ```

   Request fields: `summary`, `status`, `fixVersions`, `project`

4. Build a lookup map: `VULN key → [child item objects]`.

5. VULNs whose `issuelinks` array is empty or has only VULN-project siblings have no child items yet → token ➖.

> **Why**: fetching `issuelinks` in Step 1 and batching child lookups reduces N+1 sequential Jira calls to 2–3 total calls regardless of how many VULNs are open.

**Fallback**: If `issuelinks` is not populated in the Step 1 response (some Jira configurations omit it), use a batched JQL with parallel tool calls (10–15 VULNs at a time):

```
issue in linkedIssues("VULN-1") OR issue in linkedIssues("VULN-2") OR issue in linkedIssues("VULN-3") ...
```

**Do NOT call `get_issue` to look up `issuelinks`** — it does not return linked issues either. Skip straight to the batched JQL above.

- A VULN may have **multiple** child items. Collect them all.
- Ignore items in the same VULN project (those are sibling VULNs, not engineering tickets).
- Child items with `[VULN]` in the summary are the primary engineering tracking items.

---

## Step 3 — Classify child item statuses

Map Jira statuses to these categories:

| Category        | Example statuses                                                       |
| --------------- | ---------------------------------------------------------------------- |
| **Not Started** | To Do, Backlog, Open, New, In Analysis, Ready for Dev                  |
| **In Progress** | In Progress, In Development, In Review, Code Review, In Testing, In QA |
| **Done**        | Done, Closed, Resolved, Completed                                      |
| **Abandoned**   | Abandoned, Won't Fix, Duplicate, Canceled                              |

For VULNs with multiple children: the **highest-priority active child** drives the action token. "In Progress" outranks "Not Started"; "Done" only counts if all non-abandoned children are Done.

---

## Step 4 — Search GitHub for PRs linked to child items

**Only execute this step for child items classified as Done in Step 3.** If every child item for a VULN is Not Started, In Progress, or Abandoned, skip directly to Step 5 for that VULN — there is no PR to find yet and no GitHub call is needed. This gate eliminates the majority of GitHub lookups.

**Do not trust Jira's `Fix Version` "(Released)" annotation as evidence of deployment.** The field is set aspirationally when the engineering ticket is resolved and is not corrected when the cherry-pick into the release branch is missed. The release tag's actual commit log is the only source of truth.

**Never fetch release note body text.** Do not call `repos/bitwarden/REPO/releases/tags/TAG` and read the `.body` field. Release note bodies are hundreds of lines of markdown and will flood the context window.

**JSON parsing rule** — Always use `gh`'s built-in `--jq` flag or standalone `jq` for JSON parsing. Never pipe to `python3` or any other interpreter — Python is not in this skill's `allowed-tools` and will trigger a permission prompt. Do not add `2>/dev/null` to any calls — silent failures look identical to empty results.

```bash
# Correct — use --jq, not a separate pipe to python3
gh api --method GET "search/issues?q=PM-12345+type:pr+org:bitwarden&per_page=10" \
  --jq '.items[] | {number,title,state,mergedAt:.pull_request.merged_at,url:.html_url}'
```

**PR search** — Use the GitHub Search API to find PRs. You may issue multiple independent search tool calls in the same response turn — one per child item key — rather than one at a time. Do not write a shell script to batch them.

```bash
gh api --method GET "search/issues?q=CHILD-KEY+type:pr+org:bitwarden&per_page=10" \
  --jq '.items[] | {number,title,state,mergedAt:.pull_request.merged_at,url:.html_url}'
```

Note the field mapping: the Search Issues API returns `pull_request.merged_at`, not `mergedAt`. Always use `.pull_request.merged_at` in the `--jq` filter — otherwise `mergedAt` will be null for every result.

**Two-attempt cap on PR searches.** If the first search (by child item key) returns no results, try one more search using the VULN key (e.g., `VULN-529+type:pr+org:bitwarden`). If that also returns no results, mark "No PR found" and move on. Do not try keyword searches, repo-scoped retries, or other fallback queries — they rarely succeed and waste significant time.

**Skip `gh pr view` when merge date is already known.** Only call `gh pr view PR_URL --json state,mergedAt,baseRefName,title` if the search returned `mergedAt: null`. If the search already returned a non-null merge date, you have what you need — do not make a redundant follow-up call. If `gh pr view` also returns `mergedAt: null`, the PR was not merged — record it as closed-without-merge and move on; do not search further.

**Release list caching** — Fetch releases **once per repo** and reuse the result for all PRs in that repo. Do not re-fetch for each PR.

```bash
# Note: gh release list is blocked — use the Releases API directly
gh api --method GET "repos/bitwarden/REPO/releases?per_page=20" \
  --jq '.[] | select(.draft == false and .prerelease == false) | {tagName: .tag_name, publishedAt: .published_at}'
```

**Determining release inclusion** — Bitwarden uses two release strategies. Use the correct method per repo:

**`bitwarden/server` and `bitwarden/clients` (cherry-pick workflow)** — release branches are cut from `main` and fixes must be **explicitly cherry-picked** to ship. A PR merged before a release was published is **not** automatically in it — the cherry-pick may have slipped. Merge-date inference produces false positives here.

Verify cherry-pick presence by searching the release range's commit messages for the PR number. Bitwarden cherry-pick commits preserve the original `(#NNNN)` suffix from the source PR:

```bash
gh api --method GET "repos/bitwarden/REPO/compare/PREV_TAG...CANDIDATE_TAG" \
  --jq '.commits[].commit.message' | grep -E "\(#PR_NUMBER\)"
```

1. From the cached release list, identify the **earliest release where `publishedAt > PR.mergedAt`** — that is the **candidate** release (not yet confirmed).
2. Run the compare-and-grep above against `PREV_TAG...CANDIDATE_TAG`.
   - Match found → fix is in that release ✅
   - No match → cherry-pick was missed; fix is on `main` only → mark 🔵 Monitor and flag for engineering follow-up
3. If `PR.mergedAt` is after the latest release's `publishedAt` → not yet released → mark 🔵 Monitor.

> The earlier "Do not use `compare` for these repos" guidance referred to `MERGE_COMMIT_SHA...TAG` comparisons (which return "diverged" for cherry-picked commits with different SHAs). Tag-to-tag `compare` is fine — it lists what shipped between two releases regardless of cherry-pick SHA rewrites — and is the correct tool here.

**clients monorepo tags** — only use the tag type relevant to the affected client: `web-vYYYY.M.P`, `browser-vYYYY.M.P`, `desktop-vYYYY.M.P`, `cli-vYYYY.M.P`. Do not check all four types for every PR.

**Direct-push repos** (e.g., `bitwarden/sm-action`) — commits push directly to release branches without cherry-picks. For these, use `compare/COMMIT_SHA...TAG`: if status is `"behind"` or `"identical"`, the commit is in the release. First check commit count; skip compare if `total_commits >= 500`.

**Never repeat an API call.** Before issuing any `releases` or `search` call, confirm you have not already received a response for that exact endpoint and parameters in this session. If you have, use the cached result.

To confirm a release has been **deployed to production**, check the `publishedAt` date from the releases API response. If it is in the past and the release is not draft/prerelease, it is live.

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
  → PR in a released, deployed version
    (verified by commit-presence check, not Jira Fix Version)? → 🟢 Verify & Close

VULN status "Verified":
  → Fix already confirmed in prod; ticket just needs closing   → 🏁 Move to Closed
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
| 🏁    | Ready to Close Out       | {n}   |
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

## 🏁 Close Out

| VULN            | Priority | Summary                        | HackerOne       | VULN Status | Action                                             |
| --------------- | -------- | ------------------------------ | --------------- | ----------- | -------------------------------------------------- |
| [VULN-442](...) | Medium   | Summary truncated to ~60 chars | [#3673748](...) | Verified    | Move VULN to Closed (fix already verified in prod) |

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
