# Changelog

All notable changes to the `bitwarden-shepherd` plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-12

### Added

- Initial release of the `bitwarden-shepherd` plugin — a champion-of-a-technical-strategy agent that complements `bitwarden-tech-lead`. The shepherd's role spans two connected acts: (1) shepherding a Technical Strategy Idea through Architecture's evaluation until it earns funnel intake, and (2) shepherding the resulting initiative across all five funnel phases (Identification, Research, Proof of Concept, Scoping & Commitment, Implementation) to durable adoption.
- `bitwarden-shepherd` agent — leads with the strategy-champion framing; the funnel mechanics are positioned as how a thesis becomes reality, not what the agent is. Explicit ownership boundaries between shepherd and each receiving team's tech lead are preserved throughout.
- `championing-a-strategy-idea` skill — Primary-Owner playbook for the pre-funnel arc: taking accountability for a specific TSI, pairing with a peer reviewer, completing the Stakeholder & Engagement Map (especially Known Friction Points), refining the Problem Statement through Research, presenting at Architecture Council, navigating quarterly prioritization, and running the Adoption Retrospective at Implementation handoff (the canonical home for the influence-effectiveness retro).
- `shepherding-an-initiative` skill — umbrella playbook covering all five funnel phases with effort budgets, decision gates, and dispatch into the phase-deep skills. Picks up after Architecture has approved an idea for funnel intake.
- `running-an-architectural-assessment` skill — Phase 2 (Research) deep dive: stakeholder interviews, current-state analysis, 2–4 solution options, the Architectural Assessment template, Architecture Council preview.
- `running-a-proof-of-concept` skill — Phase 3 (PoC) deep dive: PoC area selection, framework build, Architecture Council walkthrough, drafting the ADR.
- `scoping-and-handing-off-to-teams` skill — Phase 4 (Scoping & Commitment) deep dive: High-Level Architecture Plan, child epics, per-team handoff meeting, leadership commitment, operational prioritization. Composes `running-work-transitions` (originating side, Phases 1–2 of the Work Transition Playbook).
- `coordinating-implementation-across-teams` skill — Phase 5 (Implementation) deep dive: communication channels, kickoff, review-for-consistency, drift detection, progress reporting cadence, knowledge transfer, retrospective, post-implementation impact measurement. Composes `running-work-transitions` (originating side, Phases 3–6 of the Work Transition Playbook).
- `curating-the-strategy-ideas-backlog` skill — Peer-Reviewer and portfolio-curator side of the TSI Shepherding Model: serving as constructive challenge function for someone else's idea, weekly triage, monthly score updates, mid-quarter backlog management, quarterly prioritization with engineering leadership, and the transition from approved idea to BW Initiative.
- ADR placement and documentation patterns grounded in [Documentation Patterns](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/1774977070): ADRs land in the centralized `bitwarden/contributing-docs` repository under `docs/architecture/adr/` (not per-repo); close-to-code documentation (framework `README.md`, folder notes, JSDoc/XML/`rustdoc`, CLAUDE.md updates) ships alongside the code. `running-a-proof-of-concept` carries the deep guidance on both homes; `coordinating-implementation-across-teams` carries the Implementation-phase documentation cadence; `shepherding-an-initiative` cross-references both at Phase 3.
- Agent description now includes four `<example>` blocks (championing a new TSI pre-funnel, driving an approved initiative through Phase 3 PoC, peer-reviewing another engineer's idea, running per-team Phase 4 handoff meetings) so the orchestrator can route on concrete triggering scenarios rather than prose alone. Adopts Anthropic's documented standard for agent description fields.
- `scoping-and-handing-off-to-teams` skill: the `## What You Produce` wrapper is replaced by a short intro listing the eight Phase 4 deliverables, with each deliverable promoted from H3 to its own H2 for cleaner TOC navigation and progressive scanning.
- Cross-plugin integration with `bitwarden-delivery-tools` (load-bearing — funnel and work-transition skills are composed, not duplicated), `bitwarden-tech-lead` (team-side counterpart), `bitwarden-security-engineer`, and `bitwarden-atlassian-tools`.
