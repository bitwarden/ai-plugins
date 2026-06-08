# Changelog

All notable changes to the `bitwarden-delivery-tools` plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-06-07

### Removed (BREAKING)

- **`coordinating-cross-team-breakdown` skill — merged into `writing-tech-breakdowns`.** The Tech Breakdown is one artifact with one lifecycle, so two peer skills forced unnecessary context-switching. `writing-tech-breakdowns` now owns the full lifecycle end-to-end: drafting the engineering content, the status lifecycle, cross-team engagement, building and chasing the signoff table, owner-mediated escalation, the `Proposed → Accepted` gates, the stakeholder-communication checklist, moving to `Complete`, and the `Rejected` terminal state. Any agent invoking `Skill(coordinating-cross-team-breakdown)` should switch to `Skill(writing-tech-breakdowns)`. `examples/signoff-table.md` moved into `writing-tech-breakdowns/examples/`.

### Added

- **`choosing-collaboration-model` skill** — evaluates a proposed cross-team change and recommends a collaboration model from the three Bitwarden-adopted patterns (File a Ticket, Internal Open-Source, Embedded Expert) drawn from Pete Hodgson's cross-team collaboration patterns. Anchors "what counts as a cross-team change" in `CODEOWNERS`-based file ownership, covers the edge cases (shared files, orphan files, read-only consumption, tests/fixtures), and walks: (1) escape-hatch interrogation of whether the crossing should happen at all; (2) change-shape evaluation across six inputs including **owning-team domain velocity**; (3) recommendation with reasoning, runner-up, velocity findings, and the owning-team confirmation step. Makes explicit that File a Ticket transfers planning load (not just execution) and is **not** "file and forget" — the driving team stays engaged on alignment, refinement, and review. Includes `references/three-models.md` (per-model deep dive plus the Internal Open-Source vs. owning-team development comparison table), `references/scanning-for-owning-team-work.md` (operational scan procedure for in-flight owning-team work), and `references/confirmation-workflow.md` (joint-decision flow at signoff). Invoked from `writing-tech-breakdowns` per impact and referenced from `navigating-the-initiative-funnel` and `running-work-transitions`.
- `writing-tech-breakdowns/evals/evals.json` — 5-case eval set covering the most-likely user prompts: starting a breakdown from an initiative handoff, drafting the Plan section, the `Proposed → Accepted` transition, Tasks-and-Jira-stories sync timing, and handling a same-codebase collision with another team. Each case has expectations for objectively-checkable behaviors (correct lifecycle casing, cross-skill delegation to `architecting-solutions` / `bitwarden-security-context`, no inlining of content that belongs in `references/`).

### Changed

- **`writing-tech-breakdowns` re-anchored to the markdown-based [`bitwarden/tech-breakdowns`](https://github.com/bitwarden/tech-breakdowns) repo template** (single self-contained file in `<team>/`, no child pages) — replaces the previous Confluence template page. New named sections (Specification, Clarifications Log, Plan with per-layer subsections, Tasks, Agent Context) replace "Part 1–6" numbering. Lifecycle states are now Title Case (`In Planning / In Progress / Proposed / Accepted / Rejected / Complete`). Workflow mechanics rewritten around git PRs and CODEOWNERS rather than Confluence edits. New Tasks decomposition format and structured Agent Context block (Repos affected with `CLAUDE.md` pointers, Existing patterns, External references, Things an agent should not assume). AI-clarify-pass guidance added before circulating the Clarifications Log. Engineer-vs-tech-lead role split removed — anyone on the team drafts a breakdown. Files under `**/complete/**` are point-in-time historical records, not source of truth.
- **`writing-tech-breakdowns` now covers the full lifecycle** (Before You Start → Drafting → Moving to Proposed → Cross-team engagement → Chasing signoffs → Moving to Accepted → Moving to Complete → Rejected), absorbing the cross-team engagement content from the removed sibling skill. The Cross-team engagement section has three explicit subsections (Consuming other teams' APIs, Changes required in other teams' code, Cross-team sequencing & ordering) plus a free-form Coordination notes subsection. The stakeholder-communication checklist runs at the **`In Progress → Proposed`** entry — its items (post to `#team-eng-tech-breakdowns`, contact QA, create Jira stories, hand off to refinement facilitator) kick off the parallel work (signoff, refinement, QA test design) that has to close before `Accepted`. The `Proposed → Accepted` transition is gate verification only: cross-team signoff captured **and** the team's refinement pass complete. Owner-Mediated Escalation replaces Shepherd-Mediated Escalation; the skill uses "owner" for the initiative-funnel role.
- **Signoff table** — columns are `Team`, `Interface`, `Associated breakdown`, `Signoff`. (`Describe interface` → `Interface`, `Associated Other Team Breakdown` → `Associated breakdown`; the `Blocking?` column is dropped.) Every row is a signoff the breakdown needs before `Accepted`. Teams that only need to be informed belong in Coordination notes or an FYI Slack post.
- **Jira story creation** — two valid timings, tied to how the team refines: **create stories at Proposed entry** (default, for ticket-refinement teams) or **defer to the Accepted gate** (for teams who refine on the breakdown). Either way, by `Accepted` stories must exist with bidirectional linkage. Story-specific tech-breakdown content goes in the dedicated **`Technical breakdown` custom field** (`customfield_10313`), not Description — refinement, QA, and reporting all key off the dedicated fields. Description's only job on a breakdown-derived ticket is to carry the inline link back to the breakdown. `customfield_*` IDs surfaced inline (Technical breakdown `customfield_10313`, Acceptance Criteria `customfield_10192`, Team `customfield_10001`) so authoring tooling can target them programmatically. Mechanics-level Jira writes are delegated to whichever Jira authoring tooling the engineer has available (a `jira-manager` / `jira-cli` skill, direct Atlassian MCP write calls, or the Jira UI) rather than performed by this skill.
- **Tasks-section sizing nudge** — **10 or fewer tasks** is healthy (refinable in one or two sessions, predictable release date); **more than 10** review for natural seams (sequential phases, independently-shippable subsets, interface boundaries) and split.
- **Engineering-owned vs. Product-owned BW Initiatives** distinguished across `writing-tech-breakdowns` and `choosing-collaboration-model`. `Skill(navigating-the-initiative-funnel)` references are qualified as applying only to Engineering-owned initiatives; for Product-owned initiatives, point at the linked PRD and the named Product owner for the equivalent context and escalation paths.
- **Progressive disclosure** — heavy content extracted to `references/` and duplicated content consolidated so each SKILL.md fits within the 3,000-word skill-content target. New/expanded references: `writing-tech-breakdowns/references/{status-lifecycle,section-drafting-guide,cross-team-engagement,jira-story-mechanics}.md`; `choosing-collaboration-model/references/{three-models,scanning-for-owning-team-work,confirmation-workflow}.md`. `running-work-transitions` consolidated its twin "From the Receiving Side" / "From the Originating Side" phase walkthroughs into one **Six Phases** walkthrough with side-specific callouts inside each phase. Each SKILL.md carries a lifecycle-spine summary plus explicit "Load `references/<file>.md` when …" directives so deep content only enters the agent context when needed.
- Plugin `allowed-tools` set across the lifecycle skills updated for the new working surface: local filesystem tools (`Read`, `Edit`, `Write`, `Bash`, `Glob`, `Grep`) for working with the `bitwarden/tech-breakdowns` repo; Atlassian read tools retained for pulling Jira/Confluence context referenced from a breakdown; Confluence search (`search_confluence`, `search_confluence_cql`) dropped from `writing-tech-breakdowns` since the workflow no longer searches Confluence.
- README skill catalog and the `bitwarden-tech-lead` agent's Cross-Plugin Integration block updated to the merged skill and the new `choosing-collaboration-model` skill, with the current template section naming and Title Case lifecycle states.

### Security

- `writing-tech-breakdowns` and `choosing-collaboration-model` — added untrusted-input boundary callouts. Engineer-authored markdown in `bitwarden/tech-breakdowns`, sibling-team breakdowns, PR titles, branch names, and commit messages are explicitly framed as data under analysis, never as instructions to execute. Addresses CWE-1427 exposure from the `Bash`/`Write`/`Edit` access the lifecycle skills hold while reading engineer-authored content.

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
