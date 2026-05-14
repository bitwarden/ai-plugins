# Changelog

All notable changes to the `bitwarden-delivery-tools` plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-05-20

### Changed

- `creating-pull-request` skill: hardened workflow into six ordered steps with a mandatory pre-submission preview block (title, type prefix, label, body) so reviewers and label automation no longer silently miss the PR template or the AI-review label, addressing a recurring user-reported failure where PRs landed without the template applied or without the chosen label
- `creating-pull-request` skill: Step 5 confirmation now uses the `AskUserQuestion` tool with structured options (Submit / Edit title or body / Change ai-review label / Cancel) instead of a free-text question, mirroring Step 4's pattern and removing parse ambiguity
- `creating-pull-request` skill: rewrote description to cover natural-language phrasings ("package this up into a PR", "ship a draft", "send it up for review", "get this in front of reviewers", "wrap this branch", "throw together a PR") and assert precedence over `labeling-changes` when the user is in a PR-creation context, while explicitly excluding conceptual/educational and existing-PR-management queries. Split the long single-field text into `description` (what the skill does) and `when_to_use` (when to invoke it) per the Claude Code skills frontmatter reference, trimming combined listing chars from ~1,485 to ~1,137 (cap 1,536). Validated at 100% trigger reliability by threshold (20-query test set, 3 runs each, claude-opus-4-7)

### Added

- `creating-pull-request/evals/` directory containing the trigger eval set (`trigger-eval.json`), a custom runner (`run_real_eval.py`) that works around an upstream skill-creator harness false-negative when the skill under test is already plugin-registered, and a passing baseline (`baseline.json`) for diff-based regression checks on future description changes

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
