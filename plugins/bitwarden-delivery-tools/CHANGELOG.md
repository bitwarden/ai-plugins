# Changelog

All notable changes to the `bitwarden-delivery-tools` plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2026-06-04

### Changed

- `writing-tech-breakdowns` — re-anchored to the markdown-based [`bitwarden/tech-breakdowns`](https://github.com/bitwarden/tech-breakdowns) repo template (single self-contained file in `<team>/`, no child pages), replacing references to the Confluence template page. Dropped "Part 1–6" numbering for the new named sections: Specification, Clarifications Log, Plan (with Current State, Architecture + Out of Scope + Known Limitations, Prototypes, and per-layer subsections), Tasks, Agent Context. Lowercased lifecycle states (`In Planning / In Progress / Proposed / Accepted / Rejected / Complete`) and rewrote workflow mechanics around git PRs and CODEOWNERS rather than Confluence edits. Added guidance for the new Tasks decomposition format and the structured Agent Context block (Repos affected with `CLAUDE.md` pointers, Existing patterns, External references, Things an agent should not assume). Added AI-clarify-pass guidance before circulating the Clarifications Log. Removed engineer-vs-tech-lead role split — anyone on the team drafts a breakdown.
- `coordinating-cross-team-breakdown` — updated for the new Cross-team engagement structure with three explicit subsections (Consuming other teams' APIs, Changes required in other teams' code, Cross-team sequencing & ordering) plus a free-form Coordination notes subsection. Updated signoff table column names (`Describe interface` → `Interface`, `Associated Other Team Breakdown` → `Associated breakdown`). Re-anchored references from the Confluence template page to the markdown template in the breakdowns repo. Added note that files under `**/complete/**` are point-in-time records, not source of truth. Re-staged the template's stakeholder-communication checklist (signoff verification, `#team-eng-tech-breakdowns` post, QA contact, refinement-facilitator handoff) from the post-implementation `Complete` transition to the `Proposed → Accepted` transition, matching the template's "when complete" preamble intent (the breakdown document is complete, not the implementation). Left only the file move at `Complete`. Added team-refinement engagement to the `Proposed` status in `writing-tech-breakdowns` so refinement-pass feedback can flow back into the Tasks section before signoff. Trimmed `allowed-tools` to drop the heavier Confluence search surface (`search_confluence`, `search_confluence_cql`) that this skill doesn't exercise.
- Aligned `writing-tech-breakdowns` to use "owner" for the initiative-funnel role, matching the convention already in `coordinating-cross-team-breakdown` (which renamed `Shepherd-Mediated Escalation` → `Owner-Mediated Escalation` in this PR). The upstream `Skill(navigating-the-initiative-funnel)` and `Skill(running-work-transitions)` still use "shepherd" — vocabulary alignment across those skills remains a follow-up.
- `writing-tech-breakdowns` (Tasks section) — added guidance for creating Jira stories at the `Proposed → Accepted` transition (one story per Tasks row, carrying the Ticket Shape) and updating the Tasks section with a link back to each story for bidirectional linkage. Extracted the detailed field-by-field Jira mapping, the `is blocked by` / `depends on` / `relates to` linkage rules, and the trivial/substantive/significant sync taxonomy into `references/jira-story-mechanics.md`; extracted the Ticket Shape appendix into `references/ticket-shape.md`. SKILL.md now points at those references and keeps the lifecycle/timing/shape guidance inline. Added Common Mistakes for acceptance-criteria-in-Description and skipped issue links. Mechanics-level Jira writes are intentionally not in `allowed-tools` — delegated to whichever Jira authoring tooling the engineer has available (a `jira-manager` / `jira-cli` skill if installed, direct Atlassian MCP write calls, or the Jira UI). `coordinating-cross-team-breakdown` checklist gains a corresponding "Create Jira stories" step between QA contact and refinement handoff, pointing at the new `references/jira-story-mechanics.md`.
- `coordinating-cross-team-breakdown/examples/signoff-table.md` — updated column names and lifecycle status capitalization to match the new template.
- Plugin `allowed-tools` extended to include local filesystem tools (`Read`, `Edit`, `Write`, `Bash`, `Glob`, `Grep`) for working with the breakdowns repo. Atlassian tools retained for pulling Jira/Confluence context referenced from a breakdown.
- README skill catalog rows for `writing-tech-breakdowns` and `coordinating-cross-team-breakdown` updated to reflect the new template section naming (Specification / Clarifications Log / Plan / Tasks / Agent Context) and lowercase Title Case lifecycle states.
- `writing-tech-breakdowns` — replaced raw `grep -ri` guidance in the collision scan with "use the Grep tool (or ripgrep)" to match the in-repo agent-on-pattern guidance.

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
