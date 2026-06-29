# Changelog

All notable changes to the `bitwarden-delivery-tools` plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-06-19

### Added

- **`completing-breakdown` skill** — marks a breakdown `Complete` and moves the breakdown folder into the team's `complete/` subfolder.

## [2.0.0] - 2026-06-19

### Added

- **`decomposing-into-tasks` skill** — decomposes a breakdown Plan into a `tasks.md` document with one entry per future Jira work item. Supports resumption against a partly-drafted task list.

### Removed

- **BREAKING:** `writing-tech-breakdowns` skill removed. Superseded by `starting-breakdown`, `developing-breakdown-spec`, `developing-breakdown-plan`, and `decomposing-into-tasks`. The skill was deprecated in 1.4.0.
- **BREAKING:** `coordinating-cross-team-breakdown` skill removed.

### Changed

- `navigating-the-initiative-funnel`: cross-references to the removed skills replaced with pointers to `starting-breakdown`, `developing-breakdown-spec`, `developing-breakdown-plan`, and `decomposing-into-tasks`.

## [1.5.0] - 2026-06-17

### Added

- **`developing-breakdown-plan` skill** — develops the Plan section of a Tech Breakdown after the Specification is filled, with an optional follow-on step to open a draft prototype PR across affected repos for the team to evaluate alongside the design.

## [1.4.0] - 2026-06-09

### Added

- **`starting-breakdown` skill** — sets up a new Tech Breakdown file in `bitwarden/tech-breakdowns`.
- **`developing-breakdown-spec` skill** — defines the scope and boundaries of a breakdown effort, then captures the change into the Specification section.

### Changed

- `writing-tech-breakdowns` marked **obsolete** in the README and via a deprecation banner at the top of its `SKILL.md` so the deprecation surfaces at activation time. Superseded by `starting-breakdown` and `developing-breakdown-spec`; the skill remains available but future work will fold remaining pieces into successor skills referencing the `bitwarden/tech-breakdowns` document.

## [1.3.0] - 2026-05-20

### Changed

- `creating-pull-request`: hardened workflow into six ordered steps with `AskUserQuestion`-driven preflight, label selection, and a mandatory pre-submission preview (title, type prefix, label, body) so the PR template and `ai-review` label are no longer silently dropped. Rewrote the description to trigger on natural-language PR phrasings and split it into `description` and `when_to_use` per the Claude Code skills frontmatter reference.

### Added

- `creating-pull-request/evals/` — trigger eval set, custom runner, and baseline for diff-based regression checks on future description changes.

## [1.2.0] - 2026-05-13

### Added

- `writing-tech-breakdowns` skill — drafting Parts 1, 2, 4, 5, 6 of Bitwarden's Tech Breakdown Template (problem overview, breakdown scope checklist, specification artifacts, open questions, AI context) plus the full status lifecycle (IN PLANNING → IN PROGRESS → PROPOSED → ACCEPTED → COMPLETE, with REJECTED as the terminal alternative).
- `coordinating-cross-team-breakdown` skill — Part 3 signoff table, cross-team checklist (mobile changes, components outside the team's domain, dependencies on other teams' services, APIs built for other teams), and the completion-communication checklist that closes a breakdown.

### Changed

- `navigating-the-initiative-funnel` — added pointers to the new tech-breakdown skills at the Scoping & Commitment phase and in the related-skills block so the funnel ↔ breakdown linkage is bidirectional.
- Plugin description, README, and keywords extended to cover tech breakdowns and cross-team signoffs alongside the existing lifecycle and mechanics concerns.

## [1.1.0] - 2026-05-07

### Added

- `navigating-the-initiative-funnel` skill — phase-by-phase tech-lead participation across Bitwarden's Software Initiative Funnel
- `running-work-transitions` skill — both-sides playbook for receiving or originating ownership transitions

### Changed

- Plugin description and README reframed to "delivery lifecycle" to encompass initiative routing and team handoffs alongside the existing commit/PR mechanics
- Added `lifecycle`, `initiative-funnel`, and `work-transition` to plugin keywords

## [1.0.0] - 2026-04-08

### Added

- Generic `committing-changes` skill for commit message format and staging workflow
- Generic `creating-pull-request` skill for PR creation and draft workflow
- Generic `labeling-changes` skill for conventional commit type keywords and label mapping
- Generic `perform-preflight` skill for pre-commit quality gate checklist
- All skills are platform-agnostic and reference the repo's CLAUDE.md for platform-specific details
