# Changelog

All notable changes to the `bitwarden-shepherd` plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2026-07-10

### Changed

- Repointed all `architecting-solutions` cross-plugin references from `bitwarden-tech-lead` to `bitwarden-delivery-tools` following the skill's move in `bitwarden-tech-lead` 3.0.0 / `bitwarden-delivery-tools` 2.1.0.

## [1.0.0] - 2026-05-13

### Added

- Initial release. `bitwarden-shepherd` is a champion-of-a-technical-strategy agent that complements `bitwarden-tech-lead`. The shepherd's role spans two connected acts: shepherding a Technical Strategy Idea through Architecture's evaluation into the Software Initiative Funnel, then driving the resulting initiative across all five funnel phases (Identification, Research, Proof of Concept, Scoping & Commitment, Implementation) to durable adoption.
- `bitwarden-shepherd` agent with explicit ownership boundaries between shepherd and each receiving team's tech lead.
- Seven skills:
  - `championing-a-strategy-idea` — Primary-Owner playbook for the pre-funnel arc; canonical home for the Stakeholder & Engagement Map and the Adoption Retrospective at Implementation handoff.
  - `shepherding-an-initiative` — umbrella playbook for the five funnel phases.
  - `running-an-architectural-assessment` — Phase 2 (Research) deep dive.
  - `running-a-proof-of-concept` — Phase 3 (PoC) deep dive, including ADR placement and Bitwarden's close-to-code vs. centralized documentation patterns.
  - `scoping-and-handing-off-to-teams` — Phase 4 (Scoping & Commitment) deep dive. Composes `running-work-transitions` for the originating side of the Work Transition Playbook.
  - `coordinating-implementation-across-teams` — Phase 5 (Implementation) deep dive. Composes `running-work-transitions` for the support period through closure.
  - `curating-the-strategy-ideas-backlog` — Peer-Reviewer and portfolio-curator side of the TSI Shepherding Model.
- Cross-plugin integration with `bitwarden-delivery-tools` (funnel and work-transition skills are composed, not duplicated), `bitwarden-tech-lead` (team-side counterpart), `bitwarden-security-engineer`, and `bitwarden-atlassian-tools`.
