# Changelog

All notable changes to the `bitwarden-shepherd` plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-11

### Added

- Initial release of the `bitwarden-shepherd` plugin — the Staff+-engineer initiative shepherd counterpart to `bitwarden-tech-lead`. Covers the Software Initiative Funnel from the shepherd-originating side and the upstream Technical Strategy Ideas backlog from the Architecture-curator side.
- `bitwarden-shepherd` agent — drives a single cross-cutting initiative end-to-end (Identification through Implementation), with explicit ownership boundaries between shepherd and each receiving team's tech lead.
- `shepherding-an-initiative` skill — umbrella playbook spanning all five funnel phases with effort budgets, decision gates, and dispatch into the phase-deep skills.
- `running-an-architectural-assessment` skill — Phase 2 (Research) deep dive: stakeholder interviews, current-state analysis, 2–4 solution options, the Architectural Assessment template, Architecture Council preview.
- `running-a-proof-of-concept` skill — Phase 3 (PoC) deep dive: PoC area selection, framework build, Architecture Council walkthrough, drafting the ADR.
- `scoping-and-handing-off-to-teams` skill — Phase 4 (Scoping & Commitment) deep dive: High-Level Architecture Plan, child epics, per-team handoff meeting, leadership commitment, operational prioritization. Composes `running-work-transitions` (originating side, Phases 1–2 of the Work Transition Playbook).
- `coordinating-implementation-across-teams` skill — Phase 5 (Implementation) deep dive: communication channels, kickoff, review-for-consistency, drift detection, progress reporting cadence, knowledge transfer, retrospective, post-implementation impact measurement. Composes `running-work-transitions` (originating side, Phases 3–6 of the Work Transition Playbook).
- `curating-the-strategy-ideas-backlog` skill — Architecture-group-curator side of the TSI backlog: primary-owner / peer-reviewer pairing, the Stakeholder & Engagement Map as a Research gate, RICE scoring, quarterly prioritization, the transition from approved idea to BW Initiative at the funnel's Identification phase.
- Cross-plugin integration with `bitwarden-delivery-tools` (load-bearing — funnel and work-transition skills are composed, not duplicated), `bitwarden-tech-lead` (team-side counterpart), `bitwarden-security-engineer`, and `bitwarden-atlassian-tools`.
