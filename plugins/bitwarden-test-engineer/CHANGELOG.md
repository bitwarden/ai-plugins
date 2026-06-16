# Changelog

All notable changes to the Bitwarden Test Engineer Plugin will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-15

### Added

- Initial release of the `bitwarden-test-engineer` plugin.
- `test-engineer-orchestrator` agent: classifies the inputs for a change (Jira ticket,
  GitHub PR, technical breakdown document, exported test-case CSV, plain-language
  description), fans out subagents to gather evidence — including a dedicated **breakdown
  reader** subagent (`sonnet`) that mines a tech breakdown for testable behaviors and its
  status — runs the analyst skill, then automatically runs the adversarial counterpart
  before presenting a consolidated result.
- `analyzing-test-stack` skill: maps a change's testable behaviors to the cheapest
  sufficient Testing Trophy layer (static, unit, integration, E2E) per platform and emits
  a self-contained HTML report to the current working directory. Accepts a **technical
  breakdown document** (a Bitwarden Tech Breakdown Confluence page, the artifact produced by
  the `bitwarden-delivery-tools:writing-tech-breakdowns` skill) as an additive evidence
  source alongside Jira, PR, CSV, and plain-language inputs — mining its Part 2 scope
  checklist for the surfaces and platforms touched, its Part 4 specification child pages for
  the interfaces to test against, and its Part 5 open questions for untestable-requirement
  risk. Includes references for the Testing Trophy model, the repo/stack layer→repo map,
  evidence-source ingestion, and the HTML report template. The Atlassian
  `search_confluence` / `search_confluence_cql` tools back locating a breakdown by
  feature/team name when only a name (not a page ID) is given.
- `challenging-test-stack-recommendations` skill: the adversarial counterpart that
  red-teams the analyst's recommendation against known anti-patterns (ice-cream-cone,
  unit-masquerading-as-integration, over-testing, untestable requirements, missing platform
  layers, flaky-E2E candidates, ungrounded coverage claims) and returns a verdict of
  endorse, revise, or reject-with-reasons.
- Per-layer model governance to optimize token spend: the orchestrator runs on Opus
  (its context drives the synthesis and adversarial reasoning), while its fan-out evidence
  subagents are assigned explicitly — `sonnet` for sources that read a diff, ticket, or repo,
  `haiku` for pure CSV parsing — rather than inheriting Opus.
