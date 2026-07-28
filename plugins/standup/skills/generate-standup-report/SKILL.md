---
name: generate-standup-report
description: |
  Gathers a user's activity across GitHub PRs, Jira tickets, Jira comments,
  Confluence edits, and Jira grooming edits over a configurable time window and
  emits a single combined JSON document. Used by standup-report-agent. All
  operations are read-only -- never performs writes against any API.
allowed-tools: Bash(python3:*)
---

# generate-standup-report Skill

This skill bundles Python scripts that collect activity data from GitHub and Atlassian APIs and emit a single combined JSON document for LLM synthesis.

## Prerequisites

- JIRA_API_TOKEN environment variable set (Atlassian API token)
- JIRA_EMAIL environment variable set (Atlassian account email; required for live mode; no default)
- JIRA_BASE_URL environment variable set (Atlassian base URL; required for live mode; no default)
- STANDUP_TZ environment variable (optional; timezone for date calculations; default: UTC)
- gh CLI authenticated (gh auth status must succeed)
- Python 3.11+ (stdlib only; no pip installs required)

A runner supplies identity and workspace values either via args+env directly or (for an agent runner) from the user's preferences file. Per the preferences contract, a runner Reads `~/.claude/standup/preferences.md` at run start (load-on-demand; that file is never auto-loaded), extracts identity and workspace from its `## Identity & workspace` section to supply this skill's `--jira-user` / `--github-user` args and the `JIRA_EMAIL` / `JIRA_BASE_URL` / `STANDUP_TZ` environment variables, and applies the `## Output format` and `## Output style` knobs when synthesizing and rendering the report. The report-generation runner itself lands in a later plugin release, but this preferences contract is defined now.

## Invocation

python3 ${CLAUDE_PLUGIN_ROOT}/skills/generate-standup-report/gather.py \
  --timeline "last 1 week" \
  --jira-user "Your Display Name" \
  --github-user your-github-login \
  [--out /path/to/output.json] \
  [--dry-run]

Both --jira-user and --github-user are REQUIRED (no defaults).

--dry-run and --help are fully network-free and do NOT require JIRA_EMAIL,
JIRA_BASE_URL, or JIRA_API_TOKEN. Only a real (non-dry-run) collection
requires those environment variables.

## Timeline Syntax

Relative: "last 1 day", "last 1 week", "last 2 weeks"
Absolute: "2026-04-14 - 2026-06-20"

## Environment Variables

| Variable        | Required         | Default  | Notes                                             |
|-----------------|------------------|----------|---------------------------------------------------|
| JIRA_API_TOKEN  | Live mode only   | --       | Not needed for --dry-run or --help                |
| JIRA_EMAIL      | Live mode only   | --       | No default; must be set explicitly                |
| JIRA_BASE_URL   | Live mode only   | --       | No default; must be set explicitly                |
| STANDUP_TZ      | No               | UTC      | IANA timezone name (e.g. America/Chicago)         |

JIRA_EMAIL, JIRA_BASE_URL, and JIRA_API_TOKEN are checked only when an actual
network call is attempted. --dry-run and --help remain fully network-free and
work with none of these set.

## Output Schema Top-Level Keys

- schema_version: "1.0"
- generated_at: ISO-8601 timestamp
- dry_run: boolean
- window: {start, end, input_timeline}
- identity: {atlassian: {account_id, display_name, email, input_name}, github: {login, input_login}}
- categories: {cat1_authored_prs, cat2_reviews_given, cat3_jira_done, cat4_jira_created,
               cat5_jira_comments, cat6_confluence_edits, cat7_jira_grooming,
               cat8_in_progress, cat9_blocked}

Each category: {status: "ok"|"error", count: int, items: [...], error: str|null}

Items in cat3_jira_done, cat4_jira_created, cat8_in_progress, and cat9_blocked carry
a comments field with the full ticket comment thread:
  comments: [{"author": str, "created": ISO-8601, "excerpt": str (<=500 chars, "..." if truncated)}, ...]
  comments_truncated: true  -- present only when the ticket has >50 comments; absent otherwise.
Comments are ordered oldest -> newest. Capped at the 50 most-recent. Empty list [] if no
comments or on fetch failure. The same comments field appears on linked_ticket objects in
cat1_authored_prs and cat2_reviews_given items.

cat7_jira_grooming additionally includes a qualitative summary (no raw counts):
  summary: {
    fields_by_frequency: [str, ...],   // distinct field kinds groomed, most→least frequent
    top_areas: [                        // up to 6 most-groomed issues, identity only
      {key: str, summary: str, parent: {key: str, summary: str}|null},
      ...
    ]
  }
Note: issues_touched and field_counts (numeric) are NOT emitted. Ordering is
derived internally from counts, but no magnitude is exposed in the output.

### cat1_authored_prs item fields

| Field                    | Type            | Description |
|--------------------------|-----------------|-------------|
| number                   | int             | PR number |
| title                    | str             | PR title |
| url                      | str             | GitHub html URL |
| branch                   | str             | Head branch name (headRefName) |
| body_excerpt             | str\|null       | PR body as plain text, ≤500 chars; "…" suffix if truncated; null if no body |
| linked_ticket            | object\|null    | Jira ticket linked to this PR, or null if none found |
| linked_ticket.key        | str             | Jira key, e.g. "PM-40845" |
| linked_ticket.status     | str\|null       | Jira status name, e.g. "In QA"; null on resolution error |
| linked_ticket.url        | str             | https://bitwarden.atlassian.net/browse/KEY |
| linked_ticket.comments   | list            | Full comment thread (same shape as cat8/cat9 comments); [] on failure |
| linked_ticket.comments_truncated | bool   | Present and true only when ticket has >50 comments; absent otherwise |
| repo                     | str             | GitHub repo in org/name format |
| state                    | str             | OPEN / CLOSED / MERGED |
| is_draft                 | bool            | Draft PR flag |
| review_decision          | str\|null       | APPROVED / REVIEW_REQUIRED / CHANGES_REQUESTED / null |
| created_at               | str             | ISO-8601 creation timestamp |
| merged_at                | str\|null       | ISO-8601 merge timestamp or null |
| closed_at                | str\|null       | ISO-8601 close timestamp or null |
| activity_in_window       | list            | In-window timeline events |
| activity_count_in_window | int             | Count of in-window events |

### cat2_reviews_given item fields

| Field                    | Type         | Description |
|--------------------------|--------------|-------------|
| pr_number                | int          | PR number |
| pr_title                 | str          | PR title |
| url                      | str          | GitHub html URL (same value as pr_url) |
| pr_url                   | str          | GitHub html URL |
| branch                   | str          | Head branch name (headRefName) |
| body_excerpt             | str\|null    | PR body as plain text, ≤500 chars; null if no body |
| linked_ticket            | object\|null | Jira ticket linked to this PR, or null if none found (same shape as cat1, including comments) |
| repo                     | str          | GitHub repo in org/name format |
| pr_author                | str          | PR author GitHub login |
| pr_state                 | str          | OPEN / CLOSED / MERGED |
| pr_review_decision       | str\|null    | APPROVED / REVIEW_REQUIRED / CHANGES_REQUESTED / null |
| reviews_by_user          | list         | Reviews submitted by the user in-window |
| comments_by_user         | list         | Comments left by the user in-window (conversation tab) |
| own_comment_count        | int          | Total comments attributed to the user on this PR: review-submission bodies (non-empty) + inline review-thread comment nodes authored by user + conversation-tab comments_by_user. Used for "complex review" threshold (≥8). |
| own_comment_count_capped | bool         | Present and true only when inline comment pagination hit its first:100 limit; own_comment_count is then a floor, not exact. Absent (not false) when not capped. |

### cat3_jira_done and cat4_jira_created item fields

| Field               | Type      | Description |
|---------------------|-----------|-------------|
| key                 | str       | Jira issue key, e.g. "PM-40844" |
| summary             | str       | Issue title/summary |
| status              | str       | Current Jira status name |
| issuetype           | str       | Issue type (Task, Bug, Story, etc.) |
| resolution_date     | str\|null | (cat3 only) ISO-8601 resolution timestamp |
| created             | str\|null | (cat4 only) ISO-8601 creation timestamp |
| reporter            | str       | (cat4 only) Reporter display name |
| creator             | str       | (cat4 only) Creator display name |
| priority            | str       | (cat3 only) Priority name |
| description_excerpt | str\|null | Issue description flattened from ADF to plain text, ≤500 chars; null if absent |
| url                 | str       | https://bitwarden.atlassian.net/browse/KEY |

### cat6_confluence_edits item fields

| Field              | Type      | Description |
|--------------------|-----------|-------------|
| page_id            | str       | Confluence content ID |
| title              | str       | Page title |
| url                | str       | Full web URL to the page |
| space_key          | str       | Confluence space key |
| version_number     | int\|null | Current version number |
| user_edit_confirmed| bool      | Always true (only confirmed edits are included) |
| edit_date          | str       | ISO-8601 timestamp of user's edit |
| body_excerpt       | str\|null | Page body as plain text, ≤500 chars ("…" if truncated); null if fetch fails or body is empty |

### cat8_in_progress item fields

**CURRENT-STATE snapshot — NOT filtered by the report's time window.**
Returns all issues currently assigned to the user whose statusCategory is "In Progress".
This catches all status names mapping to that category (In Development, In Scoping,
In Validation, In Implementation, etc.) regardless of when the issue was last updated.

| Field           | Type         | Description |
|-----------------|--------------|-------------|
| key             | str          | Jira issue key, e.g. "PM-35087" |
| summary         | str          | Issue title/summary |
| status          | str          | Exact status name, e.g. "In Development" |
| status_category | str          | Status category name, e.g. "In Progress" |
| issuetype       | str          | Issue type (Epic, Initiative, Task, Story, Bug, etc.) |
| priority        | str          | Priority name |
| updated         | str          | ISO-8601 timestamp of last update |
| parent          | object\|null | {key: str, summary: str} if a parent issue exists, else null |
| url             | str          | https://bitwarden.atlassian.net/browse/KEY |

### cat9_blocked item fields

**CURRENT-STATE snapshot — NOT filtered by the report's time window.**
Returns all issues currently assigned to the user with status = "Blocked".
"Blocked" has statusCategory "To Do" and is intentionally separate from cat8.
On Hold and Waiting on Contributor are NOT included.

| Field           | Type         | Description |
|-----------------|--------------|-------------|
| key             | str          | Jira issue key, e.g. "PM-40563" |
| summary         | str          | Issue title/summary |
| status          | str          | "Blocked" |
| status_category | str          | "To Do" |
| issuetype       | str          | Issue type |
| priority        | str          | Priority name |
| updated         | str          | ISO-8601 timestamp of last update |
| parent          | object\|null | {key: str, summary: str} if a parent issue exists, else null |
| url             | str          | https://bitwarden.atlassian.net/browse/KEY |

## CAT7 Jira Grooming (Activity Streams Feed)

CAT7 is sourced from the Atlassian Activity Streams Atom feed at
`/plugins/servlet/streams` (site root, NOT under /rest/api/3).

**Key characteristics:**
- **Comprehensive**: covers all issues the user touched, including issues
  they do not own or report. Not self-scoped.
- **Fast**: approximately one feed call per week; a 1-month window typically
  requires ~2 feed calls (date-cursor pagination, no hang risk).
- **Feed-only**: the feed names which field was groomed (status, description,
  goals, parent, etc.) but does not include before/after values. Multiple
  rapid edits may collapse to "updated N fields".
- **Appropriate for reporting**: summarise grooming breadth qualitatively
  (fields_by_frequency, top_areas) rather than specific value deltas or raw counts.

Pagination uses date-cursor windowing: if a page returns maxResults=1000
entries and the oldest is still inside the window, the collector re-requests
with the end clamped to oldest-1ms. A safety cap of 25 pages is applied.

## No-Write Constraint

All scripts in this skill are read-only. No mutations, no POST/PUT/PATCH/DELETE.
The only POST calls are POST /rest/api/3/search/jql (a read-only search endpoint).
