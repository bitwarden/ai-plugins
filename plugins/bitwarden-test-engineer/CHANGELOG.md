# Changelog

All notable changes to the Bitwarden Test Engineer Plugin will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-15

### Added

- Initial release of the `bitwarden-test-engineer` plugin.
- `bitwarden-test-engineer` agent: classifies the inputs for a change (Jira ticket,
  GitHub PR, technical breakdown document, exported test-case CSV, plain-language
  description), fans out subagents to gather evidence — including a dedicated **breakdown
  reader** subagent (`sonnet`) that mines a tech breakdown for testable behaviors and its
  status — then runs the analyst skill and presents its recommendation. When
  inspecting a checked-out repo, subagents read its Claude config (root `CLAUDE.md`,
  `.claude/`, nested `CLAUDE.md`) for test conventions before opening test files, and
  establish existing coverage PR-first (tests in linked/merged PRs) with a targeted lookup
  for pre-existing tests — never a repo-wide grep. The agent runs a dedicated **assess
  existing coverage** step (per-repo coverage scouts applying `assessing-test-coverage`)
  after evidence gathering and before invoking `analyzing-test-stack`, passing the merged
  coverage inventory into the recommendation.
- `assessing-test-coverage` skill: a backward-looking inventory of what a change is
  **already tested** by. Scoped to the change surface (PR-first, then a targeted lookup —
  never a repo-wide sweep), it discovers each repo's test conventions config-first, buckets
  every observed test by layer, cites it as a stable GitHub permalink (commit SHA, not
  branch), records untested behaviors as `unverified` gaps, and writes its own self-contained
  HTML **coverage report** (`test-coverage-report-<slug>-<date>.html`) following
  `references/coverage-report-template.md`. Usable standalone to audit current coverage, and
  consumed by `analyzing-test-stack`. Owns convention discovery, existing-test finding, and
  the GitHub permalink citation rules (in `references/finding-coverage.md`) — concerns kept
  separate from the trophy recommendation.
- Plugin-level shared `references/`: `input-sources.md` (evidence-source ingestion, used by
  both skills and the agent) and `report-style-tokens.md` (the single off-brand data-report
  styling system both the coverage report and the test-stack report inline verbatim, so the
  two read as one instrument).
- `analyzing-test-stack` skill: consumes the coverage inventory from `assessing-test-coverage`,
  then maps a change's testable behaviors to the cheapest
  sufficient Testing Trophy layer (static, unit, integration, E2E) per platform and emits
  a self-contained HTML report to the current working directory. Accepts a **technical
  breakdown document** (a Bitwarden Tech Breakdown Confluence page, the artifact produced by
  the `bitwarden-delivery-tools:writing-tech-breakdowns` skill) as an additive evidence
  source alongside Jira, PR, CSV, and plain-language inputs — mining its Part 2 scope
  checklist for the surfaces and platforms touched, its Part 4 specification child pages for
  the interfaces to test against, and its Part 5 open questions for untestable-requirement
  risk. The report surfaces coverage gaps and trophy-wrong shapes (ice-cream-cone,
  over-testing, missing platform layers), recording ungrounded findings as `unverified`
  gaps. Includes references for the Testing Trophy model, the repo/stack
  layer→repo map, evidence-source ingestion, and the HTML report
  template. The Atlassian `search_confluence` / `search_confluence_cql` tools back locating a
  breakdown by feature/team name when only a name (not a page ID) is given.
- Top-of-report `#overview` synthesis section, written by the analyst: a 2–4 sentence recap
  of the recommended shape per platform, the top 3 open risks (drawn from
  `#gaps`), and anchor links into the detail sections, so readers see the bottom line without
  scrolling. The overview is additive — per-behavior detail stays in `#recommendations`/`#gaps`.
- Per-layer model governance to optimize token spend: the agent runs on Opus
  (its context drives the analysis and the recommendation), while the fan-out
  evidence subagents are assigned explicitly — `sonnet` for sources that read a diff, ticket,
  or repo, `haiku` for pure CSV parsing — rather than inheriting Opus.
