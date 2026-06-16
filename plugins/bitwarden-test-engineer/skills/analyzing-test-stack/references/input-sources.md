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

## GitHub PR

- `gh pr view <pr>` — title, body, linked issues, files changed, checks.
- `gh pr diff <pr>` — the actual change surface.

Extract: the public API / behavior touched, the diff paths (→ which repos/platforms), and
**any tests already included in the PR** (so you assess incremental, not absolute, gaps).

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
  to cross-link any Jira/PR inputs, not as a behavior source on its own.
- **Part 2 — Breakdown scope checklist**: the core of the mining. Each answered item names a
  surface the change touches and therefore a place tests are needed — **Database changes**
  (migration/backwards-compat behaviors, EDD phasing), **API changes** (endpoint contracts,
  V±2 compatibility, any unauthenticated endpoint), **UI components** (shared/base components),
  **SDK changes**, **Services touched**, **Hosting** (Self-Hosted vs Cloud paths),
  **Feature flagging** (flag-on/flag-off states to cover), and **Security considerations**
  (crypto, threat-model-relevant behaviors). The **Testing considerations** item is the team's
  own stated test intent — treat it as a claim to assess against the trophy, not as ground truth
  to copy.
- **Part 4 — Specification artifacts**: linked child pages defining concrete interfaces (API
  contracts, schemas, component APIs, crypto schemes). Fetch the relevant ones with
  `get_confluence_page`; their public interfaces and edge cases are exactly what integration and
  unit tests pin down.
- **Part 5 — Open questions**: unresolved questions are untestable-requirement risk — a behavior
  can't be reliably tested until its question is answered. Surface them in the report's gaps.

Extract: discrete **testable behaviors** per platform, the **surfaces** each touches (→ repos via
`monorepo-layout.md`), and the team's **stated testing intent** (to evaluate, not echo). Where the
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

Map rows to behaviors and bucket each by apparent layer using `testing-trophy.md`:

- A case that drives the full UI through a complete journey → likely **E2E** (target the
  dedicated `test` repo).
- A case asserting one service/component's behavior through its collaborators →
  **integration**.
- A case pinning a single function's logic or an edge case → **unit**.

Flag cases that are currently manual but cheaply automatable at a lower layer, and cases
slated for E2E that would be better as integration. If a column's meaning is ambiguous,
state the interpretation you used rather than guessing silently.
