# Changelog

All notable changes to the `bitwarden-delivery-tools` plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.0] - 2026-06-06

### Added

- `choosing-collaboration-model` skill — evaluates a proposed cross-team change and recommends a collaboration model from the three Bitwarden-adopted patterns (File a Ticket, Internal Open-Source, Embedded Expert) drawn from Pete Hodgson's cross-team collaboration patterns. Anchors the trigger for "what counts as a cross-team change" in `CODEOWNERS`-based file ownership (any affected path matching an `@<other-team>` entry) rather than a fuzzy "domain boundary," and covers the edge cases (shared files with multiple owners, orphan files, read-only consumption, tests/fixtures). Walks a multi-step flow: (1) interrogates whether the change should cross the boundary at all (escape hatches for stale boundaries and missing platform capabilities); (2) evaluates change shape across six inputs (whose code changes, domain-overlap depth, codebase familiarity, repetition shape, capacity, and **owning-team domain velocity**); (3) recommends a model with reasoning, a runner-up, the velocity findings, and the owning-team confirmation step. Documents the Internal Open-Source vs. owning-team-development split with Bitwarden-specific examples and makes explicit that File a Ticket transfers planning load (the owning team writes its own breakdown if the change warrants one) and that the model is a joint decision (driving team proposes; owning team confirms during signoff). Includes `references/scanning-for-owning-team-work.md` with the operational procedure for scanning the owning team's in-flight breakdowns (under their folder in `bitwarden/tech-breakdowns`) and open PRs in the affected repos, plus how the findings shift the model recommendation (active work → File a Ticket over Internal Open-Source; two-sided in-flight work → escalate to initiative owner / EMs). Invoked from `coordinating-cross-team-breakdown` per impact, and referenced from `navigating-the-initiative-funnel` and `running-work-transitions` for cross-team work in their phases.
- `coordinating-cross-team-breakdown` — added a `Collaboration Models` section that delegates per-impact model selection to `Skill(choosing-collaboration-model)`. The three cross-team engagement subsections now require a named model per impact (with pure consumption of an unchanged API as the one exception); the signoff table's `Interface` cell carries the proposed model and brief reasoning, transitioning to confirmed once signoff lands. Added rules that File a Ticket transfers planning load (owning team writes its own breakdown if warranted) and that the model is a joint decision (driving team proposes; owning team confirms or counter-proposes during signoff). Updated `examples/signoff-table.md` to annotate every row with its model, reasoning that traces to change shape (Internal Open-Source vs. File a Ticket distinction made explicit), and added Common Mistakes covering unilateral model selection, treating File a Ticket as low-cost for the driving team, and omitting the model.
- `writing-tech-breakdowns` (Tasks section) — added a task-count nudge with explicit thresholds (5–15 healthy, 15–25 watch, >25 split, <5 likely-not-a-breakdown). When a Tasks decomposition grows past the refinable, release-date-predictable size, the skill prompts for split candidates along natural seams (sequential phases, independently-shippable subsets, interface boundaries) rather than letting an oversized breakdown carry forward. Added a Common Mistake about deferring the split into refinement.

### Fixed

- `writing-tech-breakdowns/evals/evals.json` — renamed the per-case `assertions` field to `expectations` to match the skill-creator grader schema. With the old field name the grader found zero expectations to evaluate and vacuously passed all 5 cases.
- `writing-tech-breakdowns` — dropped `search_confluence` and `search_confluence_cql` from `allowed-tools`. The skill's body has no Confluence-search step after the 1.4.0 re-anchor to `bitwarden/tech-breakdowns`; the companion skill already dropped these. Removes dead tool surface.
- `navigating-the-initiative-funnel` — updated the Phase 4 Tech Breakdown pointer and the related-skills block to the new template structure introduced in 1.4.0. Replaced `Parts 1, 2, 4, 5, 6` / `specification child pages` / all-caps lifecycle / `Part 3 signoffs` / `completion-communication checklist` with the named sections (Specification, Clarifications Log, Plan, Tasks, Agent Context), Title Case lifecycle, Cross-team engagement section, and `stakeholder-communication checklist`. Engineers entering the breakdown workflow via the funnel skill no longer hit contradictory guidance.
- `coordinating-cross-team-breakdown` — fixed the frontmatter `description` to match the body. The trigger phrase advertised "running the completion-communication checklist before Complete," contradicting the skill body (which relocates the checklist to the `Proposed → Accepted` transition and lists running it at `Complete` as a Common Mistake). Now reads "running the stakeholder-communication checklist at the Proposed → Accepted transition."
- `coordinating-cross-team-breakdown` and `writing-tech-breakdowns` — normalized references to the post-`Accepted` checklist on `stakeholder-communication checklist`. The intro paragraphs of both skills previously called it the `completion-communication checklist`, conflicting with the section heading and the rest of the body.
- `writing-tech-breakdowns` — fixed the frontmatter `description` to reference current template vocabulary. Replaced the leftover "filling in the scope checklist" trigger phrase (no longer a concept in the body) with "walking the Plan section's per-layer subsections, drafting the Tasks section."
- `coordinating-cross-team-breakdown` (`The Cross-team Signoff Table`) — normalized the path to `examples/signoff-table.md` to use a bare skill-relative reference, matching the convention used elsewhere for skill-local files. Previously used a `${CLAUDE_PLUGIN_ROOT}/skills/.../` absolute form that diverged from sibling skills.
- `coordinating-cross-team-breakdown` (`Stakeholder-Communication Checklist`, item 4) — collapsed the inline Jira field-mapping paragraph to a pointer at `Skill(writing-tech-breakdowns)`'s `references/jira-story-mechanics.md`. The detail was duplicated content owned by that reference; keeping it inline risks drift between the two surfaces.
- `writing-tech-breakdowns` (`Check for Collisions in the Same Codebase`) — dropped the redundant "(or ripgrep)" parenthetical from the Grep tool call-out. Grep is already in `allowed-tools`; the parenthetical added nothing.

### Security

- `writing-tech-breakdowns` and `coordinating-cross-team-breakdown` — added an untrusted-input boundary callout to the Canonical source section of each skill. Engineer-authored markdown in `bitwarden/tech-breakdowns`, PR titles, and branch names are now explicitly framed as data under analysis rather than instructions to execute. Addresses CWE-1427 exposure introduced when the 1.4.0 `allowed-tools` expansion gave both skills `Bash`/`Write`/`Edit` access while they read engineer-authored repo content.

### Changed

- `writing-tech-breakdowns` and `coordinating-cross-team-breakdown` — distinguished Engineering-owned BW Initiatives (routed through the Software Initiative Funnel) from Product-owned BW Initiatives (which do not use the funnel). `Skill(navigating-the-initiative-funnel)` references are now qualified as applying only to Engineering-owned initiatives; for Product-owned initiatives, the skills point at the linked PRD and the named Product owner for the equivalent context and escalation paths.

## [1.4.0] - 2026-06-04

### Changed

- `writing-tech-breakdowns` — re-anchored to the markdown-based [`bitwarden/tech-breakdowns`](https://github.com/bitwarden/tech-breakdowns) repo template (single self-contained file in `<team>/`, no child pages), replacing references to the Confluence template page. Dropped "Part 1–6" numbering for the new named sections: Specification, Clarifications Log, Plan (with Current State, Architecture + Out of Scope + Known Limitations, Prototypes, and per-layer subsections), Tasks, Agent Context. Lowercased lifecycle states (`In Planning / In Progress / Proposed / Accepted / Rejected / Complete`) and rewrote workflow mechanics around git PRs and CODEOWNERS rather than Confluence edits. Added guidance for the new Tasks decomposition format and the structured Agent Context block (Repos affected with `CLAUDE.md` pointers, Existing patterns, External references, Things an agent should not assume). Added AI-clarify-pass guidance before circulating the Clarifications Log. Removed engineer-vs-tech-lead role split — anyone on the team drafts a breakdown.
- `coordinating-cross-team-breakdown` — updated for the new Cross-team engagement structure with three explicit subsections (Consuming other teams' APIs, Changes required in other teams' code, Cross-team sequencing & ordering) plus a free-form Coordination notes subsection. Updated signoff table column names (`Describe interface` → `Interface`, `Associated Other Team Breakdown` → `Associated breakdown`). Re-anchored references from the Confluence template page to the markdown template in the breakdowns repo. Added note that files under `**/complete/**` are point-in-time records, not source of truth. Re-staged the template's stakeholder-communication checklist (signoff verification, `#team-eng-tech-breakdowns` post, QA contact, refinement-facilitator handoff) from the post-implementation `Complete` transition to the `Proposed → Accepted` transition, matching the template's "when complete" preamble intent (the breakdown document is complete, not the implementation). Left only the file move at `Complete`. Added team-refinement engagement to the `Proposed` status in `writing-tech-breakdowns` so refinement-pass feedback can flow back into the Tasks section before signoff. Trimmed `allowed-tools` to drop the heavier Confluence search surface (`search_confluence`, `search_confluence_cql`) that this skill doesn't exercise.
- Aligned `writing-tech-breakdowns` to use "owner" for the initiative-funnel role, matching the convention already in `coordinating-cross-team-breakdown` (which renamed `Shepherd-Mediated Escalation` → `Owner-Mediated Escalation` in this PR). The upstream `Skill(navigating-the-initiative-funnel)` and `Skill(running-work-transitions)` still use "shepherd" — vocabulary alignment across those skills remains a follow-up.
- `writing-tech-breakdowns` (Tasks section) — added guidance for creating Jira stories at the `Proposed → Accepted` transition (one story per Tasks row, carrying the Ticket Shape) and updating the Tasks section with a link back to each story for bidirectional linkage. Extracted the detailed field-by-field Jira mapping, the `is blocked by` / `depends on` / `relates to` linkage rules, and the trivial/substantive/significant sync taxonomy into `references/jira-story-mechanics.md`; extracted the Ticket Shape appendix into `references/ticket-shape.md`.
- `writing-tech-breakdowns` — collapsed the per-section authoring enumerations (Specification subsections, Clarifications Log mechanics, Plan subsections, Tasks fields, Agent Context subsections, Ticket Shape) into a single "Drafting the sections" block that captures only the Bitwarden-specific gotchas and cross-skill delegation. The template at `templates/tech-breakdown.md` owns the section structure (including the per-layer checklists for data model, server API, `sdk-internal`, client/UI, security & cryptography, etc.); SKILL.md now owns the workflow, lifecycle, gotchas not in the template (cryptographic work routing through `Skill(bitwarden-security-context)`, V±2 client compatibility lens, Mermaid-source preference, Out-of-Scope vs Known-Limitations distinction), and pointers to references. Compressed the Status Lifecycle into a state/meaning/entry-criteria table with the transition rules underneath. Net result: ~4,864 → ~2,800 words (within the skill-quality target).
- `writing-tech-breakdowns/evals/evals.json` — added a 5-case eval set covering the most-likely user prompts: starting a breakdown from an initiative handoff, drafting the Plan section, the Proposed → Accepted transition, Tasks-and-Jira-stories sync timing, and handling a same-codebase collision with another team. Each case has assertions for objectively-checkable behaviors (correct lifecycle casing, cross-skill delegation to `coordinating-cross-team-breakdown` / `architecting-solutions` / `bitwarden-security-context`, no inlining of content that belongs in `references/`). Added Common Mistakes for acceptance-criteria-in-Description and skipped issue links. Mechanics-level Jira writes are intentionally not in `allowed-tools` — delegated to whichever Jira authoring tooling the engineer has available (a `jira-manager` / `jira-cli` skill if installed, direct Atlassian MCP write calls, or the Jira UI). `coordinating-cross-team-breakdown` checklist gains a corresponding "Create Jira stories" step between QA contact and refinement handoff, pointing at the new `references/jira-story-mechanics.md`.
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
