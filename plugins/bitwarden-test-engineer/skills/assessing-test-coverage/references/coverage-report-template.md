# Coverage report template (markdown)

The **inventory** report: what is already tested for a change, per platform, every cited test a
stable GitHub permalink. The report is a single self-contained **markdown** file you author with
`Write` — no build step, no stylesheet. Writing it is mechanical formatting, not reasoning; the
reasoning (what's covered, at what layer, the gaps) is already done by the time you render.

## Output file

Write to `test-engineer-report-<slug>-<date>/coverage.md`:

- `<slug>` — a kebab-case slug for the change (from the ticket key, PR number, or feature name).
- `<date>` — today's date as `YYYY-MM-DD`, **supplied by the caller** (skills can't read the clock).
- The directory is deterministic, so re-running on the same change and date refreshes the report in
  place. Create the directory if it doesn't exist.

## Content rules

- **Tables over prose** for the data sections and evidence — they're meant to be scanned and acted on.
- **Hyperlink every GitHub or Atlassian source the report names** — never bare text. The **Tests
  (linked)** column is binding: render each behavior's 1–3 representative tests as GitHub permalinks
  `[<path>#L<start>-L<end>](<permalink>)`, or the plain-text unlinkable form when a test genuinely
  cannot be linked — never a fabricated URL. The permalink-production rules and the unlinkable
  fallback are owned by `finding-coverage.md` → _Citing tests as GitHub permalinks_ and _When a test
  cannot be linked_. Jira items and Jira-sourced behaviors follow `input-sources.md` → _Citing Jira
  issues as links_.
- **Mark observed vs. assumed.** Tag every unverifiable claim **`unverified`** (e.g. E2E coverage
  claimed without the `test` repo checked out) and every inference **`assumption`**, so grounded
  calls are distinguishable from inferred ones. Never present assumed coverage as verified.

## Sections (in order)

A top `# <title> — <change>` heading, then a one-line meta line (`ticket/PR · status · team · date`),
then the sections below in order.

- **`## Overview`** — a short top-of-report synthesis a reader sees first: 2–4 sentences recapping
  **how well covered the change is per platform** (where observed tests concentrate, which layers are
  bare), then the **top 3 coverage gaps** the reader should know about (drawn from _Coverage gaps_).
  State in one line that this report **describes** existing coverage — it does not recommend new tests
  or assign cheapest-sufficient layers. Write this section yourself.
- **`## Summary — observed coverage shape`** — 2–4 sentences, then a per-platform bullet list of the
  **observed** layer counts (not recommended counts), one line per platform; a platform with no
  observed coverage still gets a line, shown as empty. For example:
  - `bitwarden/server` — 3 unit, 11 integration, 0 E2E observed
  - `bitwarden/clients` — 0 observed
- **`## Evidence & sources`** — a table of which inputs were used and, explicitly, **what was missing
  or unverifiable** (e.g. "`test` repo not checked out — existing E2E coverage unverified"). For PR
  inputs include the captured **head SHA** and **`owner/repo`** so the per-test permalinks elsewhere
  can be audited against the same commit.
- **`## Coverage`** — per-platform tables, **one row per behavior** (not per test):

  | Behavior / surface | Layer | Tests (linked) | Count | Source | Notes |
  | ------------------ | ----- | -------------- | ----- | ------ | ----- |
  - **Tests (linked)** — the behavior's 1–3 representative tests as markdown permalinks (or the
    plain-text `path — unlinkable: <reason>` form).
  - **Count** — the approximate number of tests covering that behavior at that layer; breadth without
    enumerating every test. Do not expand a well-covered behavior into dozens of rows.
  - **Layer** — `unit` / `integration` / `E2E`, per `test-layers-and-repos.md`.
  - **Source** — `PR` (tests shipped in a linked/merged PR) or `pre-existing` (found by the targeted
    lookup) — keep the observed-vs-assumed distinction visible.

- **`## Coverage gaps`** — behaviors/surfaces in the change with **no observed test**, each tagged
  **`unverified`** with a one-line reason (no PR-observed test and no targeted hit; or `test` repo
  unavailable). The honest record of what is _not_ known to be covered — not a recommendation to add
  tests.
