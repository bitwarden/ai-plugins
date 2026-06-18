# Ingesting evidence sources

Inputs are additive — handle any combination, and record in the report which sources were
present and which were missing. Never block on a missing source.

## Jira ticket

Preferred: if the `bitwarden-atlassian-tools` plugin is installed, invoke
`Skill(bitwarden-atlassian-tools:researching-jira-issues)` for a deep, link-following read.

Otherwise use the MCP tools directly:

- `mcp__bitwarden-atlassian__get_issue` — the issue itself (summary, description,
  acceptance criteria, custom fields).
- `mcp__bitwarden-atlassian__get_issue_comments` — clarifications and edge cases raised in
  discussion.
- `mcp__bitwarden-atlassian__get_issue_remote_links` — linked Confluence pages and PRs.
- `mcp__bitwarden-atlassian__get_confluence_page` — linked requirements/design docs.

Extract: discrete **testable behaviors**, **acceptance criteria**, and the **platforms/
components** named. If the MCP is unavailable, ask the user to paste the requirements.

Also capture, for every issue you read, its **key and browse URL** (prefer the URL the MCP/skill
returns; otherwise construct `https://bitwarden.atlassian.net/browse/<KEY>`), and **carry the
originating issue key with each behavior you extract**. The report links every behavior back to
the Jira item it came from — see _Citing Jira issues as links_ below — so provenance must survive
intake. A behavior that traces to no Jira item (e.g. found only in a PR diff) simply carries no
source issue.

Also capture **severity** — for a bug/defect ticket, read the severity assigned on the issue
(the severity field, or the QA/reporter's stated severity in the description/comments) and
carry it with the behaviors; for a feature/story without a defect, leave it to the analyst to
assess each behavior's risk severity. Severity is the impact dial the `analyzing-test-stack`
skill uses to risk-weight coverage — see that skill's `references/severity-risk.md`, mirrored
from the Defect Severity Classification Guide (Confluence page `2759229512`).

### Epic intake

A Jira key may resolve to an Epic (or, in next-gen projects, a Feature) rather than a single
story. The epic body itself rarely lists testable behaviors — those live on its children
and on the PRs the children produce. If you analyze only the epic, you will under-scope the
analysis. So when the `issuetype` on the `get_issue` response is `Epic` or `Feature`, expand
before extracting:

1. **Discover children.** Read the `subtasks` field first. If empty (common in next-gen
   projects, which use `parent` relationships rather than the legacy `subtasks` field), fall
   back to `mcp__bitwarden-atlassian__search_issues` with JQL `parent = <EPIC-KEY>`. On
   classic projects, also try `"Epic Link" = <EPIC-KEY>`. Together these cover both schemas.
2. **Bound the fan-out.** If the epic has more than ~10 children, fetch the first 10 in full
   and summarize the rest as a one-line list (key, status, summary) from the search results.
   This matches the depth-control discipline in
   `bitwarden-atlassian-tools:researching-jira-issues` (Steps 2–3) — re-use that recipe; do
   not re-derive it.
3. **Per child, gather behaviors and PRs.**
   - `mcp__bitwarden-atlassian__get_issue` for the child's description and acceptance
     criteria — these are the testable behaviors for the analysis. Capture each child's **key and
     browse URL** and carry it with the behaviors it produces, exactly as for a single-issue
     intake — a behavior sourced from a child issue links to that child, not the epic.
   - `mcp__bitwarden-atlassian__get_issue_remote_links` for PRs (grouped under "GitHub").
     Each PR URL becomes an input to the **GitHub PR** branch below: hand it off to
     `gh pr view` / `gh pr diff` so the actual change surface and any tests-in-PR feed the
     recommendation. **These merged/linked PRs are the reliable backbone for existing
     coverage** — the tests they contain are what shipped with this work, and the PR head SHA
     makes each one permalink-ready (see the `assessing-test-coverage` skill's
     `references/finding-coverage.md` → _Finding existing coverage_).
     If `gh` cannot reach a PR (private fork, not authenticated, repo not accessible), record
     the URL as evidence-not-inspected in the report rather than silently dropping it.
4. **Track epic status.** The epic's own status (`In Planning`, `In Progress`, `Done`) tells
   you how much of the work is shipped: children in `Done` with merged PRs likely already
   have tests-in-PR you can audit for shape; children still `To Do` are scope-only and your
   recommendation is necessarily prospective. Surface this distinction in the Evidence
   section of the report.
5. **Preferred path when available.** If `bitwarden-atlassian-tools` is installed, invoke
   `Skill(bitwarden-atlassian-tools:researching-jira-issues)` on the epic key — its Step 2
   already does the hierarchical-link discovery and Step 3 the depth-controlled traversal,
   and returns the children + linked Confluence pages + remote links in one synthesized read.
   Use the direct MCP calls above only when that skill is unavailable.

## GitHub PR

- `gh pr view <pr> --json url,headRefOid,baseRefName,title,body,files,state` — title,
  body, linked issues, files changed, **and the head SHA + `owner/repo`** needed for
  permalink production downstream.
- `gh pr diff <pr>` — the actual change surface.

Extract: the public API / behavior touched, the diff paths (→ which repos/platforms),
**any tests already included in the PR** (so you assess incremental, not absolute,
gaps), and the captured **`headRefOid`** + **`owner/repo`** (parsed from the PR URL).
The SHA and `owner/repo` are required — they are what makes every test cited as
existing coverage clickable in the report. Tests observed in the PR diff are primary
coverage evidence; for _pre-existing_ tests not in the diff, do a targeted lookup scoped
to the changed paths/symbols rather than a repo-wide sweep. See the
`assessing-test-coverage` skill's `references/finding-coverage.md` → _Finding existing
coverage_ and _Citing tests as GitHub permalinks_ for the link form and the fallback when
ingredients are missing.

## Technical breakdown document

A Bitwarden **Tech Breakdown** — the Confluence artifact a team produces before implementation,
authored with the `bitwarden-delivery-tools:writing-tech-breakdowns` skill. It is the richest
single input for this analysis, because a good breakdown has already done the cross-platform
scoping you would otherwise reconstruct from a diff or a ticket. Mine it; don't re-derive it.

Locate and fetch it:

- If given a page ID or URL, fetch directly with `mcp__bitwarden-atlassian__get_confluence_page`.
- If given only a feature/team name, find the page first with `mcp__bitwarden-atlassian__search_confluence`
  or `mcp__bitwarden-atlassian__search_confluence_cql` (breakdowns live in a team's "Tech Breakdown"
  folder), then fetch it.
- The breakdown's **status** matters: `IN PLANNING` / `IN PROGRESS` means the scope may still
  shift — note that the recommendation rests on a draft. `PROPOSED` / `ACCEPTED` is a stable
  basis. Record the status as part of the evidence.

Map its structure to testable evidence (the canonical template is page `2920349776`):

- **Part 1 — Problem overview**: the feature framing and linked Jira epic. Use it for scope and
  to cross-link any Jira/PR inputs, not as a behavior source on its own. **When Part 1 names an
  Epic**, treat it the same as an Epic-key intake — drill into its children and their PR remote
  links per the _Epic intake_ recipe above. A breakdown plus its epic together usually surface
  more testable behavior than either alone.
- **Part 2 — Breakdown scope checklist**: the core of the mining. Each answered item names a
  surface the change touches and therefore a place tests are needed — **Database changes**
  (migration/backwards-compat behaviors, EDD phasing), **API changes** (endpoint contracts,
  V±2 compatibility, any unauthenticated endpoint), **UI components** (shared/base components),
  **SDK changes**, **Services touched**, **Hosting** (Self-Hosted vs Cloud paths),
  **Feature flagging** (flag-on/flag-off states to cover), and **Security considerations**
  (crypto, threat-model-relevant behaviors). The **Testing considerations** item is the team's
  own stated test intent — treat it as a claim to assess, not as ground truth
  to copy.
- **Part 4 — Specification artifacts**: linked child pages defining concrete interfaces (API
  contracts, schemas, component APIs, crypto schemes). Fetch the relevant ones with
  `get_confluence_page`; their public interfaces and edge cases are exactly what integration and
  unit tests pin down.
- **Part 5 — Open questions**: unresolved questions are untestable-requirement risk — a behavior
  can't be reliably tested until its question is answered. Surface them in the report's gaps.

Extract: discrete **testable behaviors** per platform, the **surfaces** each touches (→ repos via
the `analyzing-test-stack` skill's `references/monorepo-layout.md`), and the team's **stated testing
intent** (to evaluate, not echo). Where the
breakdown's scope checklist disagrees with a diff or ticket you were also given, treat the
divergence as a finding rather than silently picking one.

## Test-case CSV export

A CSV export of existing or planned test cases. Column headers vary by tool and export
settings — **do not hardcode them**. Read the header row, then map by meaning:

- A **title / case** column — the scenario name.
- A **type** column (e.g. "Regression", "Smoke", "Functional") — hints at intended layer.
- An **automation status** column (e.g. "Ready to Automate", "Automated", "Manual") —
  what already exists vs. what's planned.
- A **steps / expected-result** column, often in Given–When–Then form — the behavior.
- Optional **team / area / tags / preconditions** columns — scope and grouping.

Map rows to behaviors and bucket each by apparent layer using the `analyzing-test-stack` skill's `references/testing-trophy.md`:

- A case that drives the full UI through a complete journey → likely **E2E** (target the
  dedicated `test` repo).
- A case asserting one service/component's behavior through its collaborators →
  **integration**.
- A case pinning a single function's logic or an edge case → **unit**.

Flag cases that are currently manual but cheaply automatable at a lower layer, and cases
slated for E2E that would be better as integration. If a column's meaning is ambiguous,
state the interpretation you used rather than guessing silently.

## Citing Jira issues as links

Every Jira item the report **names** — and every behavior the report shows that was **found from
a Jira item** — is rendered as a clickable link to that item, never as bare key text. This is the
Jira counterpart to the GitHub permalink rule for tests (the `assessing-test-coverage` skill's
`references/finding-coverage.md` → _Citing tests as GitHub permalinks_).

The link form is the issue's browse URL:

```
https://bitwarden.atlassian.net/browse/<KEY>
```

where `<KEY>` is the issue key (e.g. `PM-1234`). Prefer the URL the MCP tool or
`bitwarden-atlassian-tools:researching-jira-issues` skill returns for the issue; fall back to
constructing the browse URL from the key. The same rule covers epics and their children — link
each to its own key.

Apply it everywhere the report renders one of these:

- An **issue, epic, or child key** named in the Overview, Summary, or Evidence sections —
  anchor the key: `<a href="https://bitwarden.atlassian.net/browse/PM-1234">PM-1234</a>`.
- A **behavior row** (in the recommendations/coverage and gaps sections) whose behavior was
  extracted from a Jira item — append the linked source key to the behavior cell so a reader can
  jump to the requirement it came from. A behavior with no Jira source (PR-only) carries no key.

These are informational `<a href>` citations — text, not loaded assets — so they do not violate
the reports' self-contained / no-remote-resources constraint. Never fabricate a key or URL; if an
issue's key is unknown, name the source in plain text rather than inventing a link.
