# Changelog

All notable changes to the `bitwarden-delivery-tools` plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-06-08

### Removed (BREAKING)

- **`choosing-collaboration-model` skill — removed; model picking reframed as an owner task.** The picker is no longer skill-driven. `Skill(doing-a-tech-breakdown)` Phase 3 step 6 identifies each cross-team impact and characterizes it (domain-overlap depth, owning-team domain churn from the scan procedure), then leaves the `Model` column empty for the breakdown owner to assign — informed by the depth and churn data the skill captured, and confirmed by the owning team at signoff. The three Bitwarden-adopted Hodgson patterns (File a Ticket, Internal Open-Source, Embedded Expert) are documented at the policy level on the Confluence page **Tech Breakdowns: Process and Framework**. The previous `references/three-models.md`, `references/scanning-for-owning-team-work.md`, and `references/confirmation-workflow.md` files were retired with the skill; the operational scan procedure is preserved inline in Phase 3 step 6. Sibling skills (`navigating-the-initiative-funnel`, `running-work-transitions`) that previously delegated to `Skill(choosing-collaboration-model)` now describe the split: skill characterizes the impact, owner picks the model.
- **`writing-tech-breakdowns` skill — replaced by phase-scoped skills.** The monolithic skill covered the entire breakdown lifecycle end-to-end (drafting, status transitions, cross-team engagement, signoff table, Jira story creation, gates) and grew long enough that mid-stream user prompts couldn't reliably land in the right section. Split into `starting-a-tech-breakdown` (file setup), `doing-a-tech-breakdown` (understanding-the-work walk-through, including cross-team identification with collaboration-model selection), and `syncing-tasks-with-jira` (creation + ongoing bidirectional sync of Jira stories). `references/`, `examples/`, and `evals/` content was either folded into the new skills or removed where it no longer applied. Policy and framework content (lifecycle definitions, gate semantics, sync policy) moved to the Confluence page **Tech Breakdowns: Process and Framework**. Any agent invoking `Skill(writing-tech-breakdowns)` should switch to the appropriate phase-scoped skill.
- **`coordinating-cross-team-breakdown` skill — removed.** Cross-team engagement (signoff table identification, model selection per impact, recording in the breakdown) now happens inline inside `doing-a-tech-breakdown` Phase 3 step 6. No separate signoff-chasing skill exists; reviewers fill the Signoff column during cross-team review between `Proposed` and `Accepted`. The earlier-included `examples/signoff-table.md` was retired.

### Added

- **`starting-a-tech-breakdown` skill** — first of the phase-scoped skills splitting `writing-tech-breakdowns` into smaller composable units. Owns the setup-only slice of the lifecycle: orients on context by **prompting the user openly** (Jira key, source of the work, where existing context lives, named owner), then copies the template, fills the Status block, and opens the PR via `Skill(creating-pull-request)`. Does **not** assume the work rolls up to a larger initiative — team-scoped work is a peer path, not a fallback; `Skill(navigating-the-initiative-funnel)` is invoked only when the user confirms the work is an Engineering-owned BW Initiative. Structured around the **Orient / Create / Open** flow with a `HARD-GATE` blocking file creation until context is captured, an explicit anti-pattern ("we already know what we're building"), a DOT process-flow graph, and three explicit phases each backed by `TaskCreate` so a mid-stream prompt lands on the right operational step. Does **not** run a collision scan: affected files cannot be enumerated until drafting produces a concrete file/module list, so the scan moves to a later lifecycle skill. Stops at status `In Planning`.
- **`syncing-tasks-with-jira` skill** — third of the phase-scoped skills splitting `writing-tech-breakdowns` into smaller composable units. Keeps the breakdown's Tasks section and its Jira stories in sync across the whole pair lifecycle, covering both initial creation (Tasks rows → new stories) and ongoing bidirectional reconciliation (drift either way once stories exist). Mode is detected per row from whether the row already carries a story key. Triage classifies each row as CREATE, MATCH-AND-SYNC, UPDATE-from-breakdown, UPDATE-from-jira, NO-CHANGE, CONFLICT, or ORPHANED, with a direction-of-truth heuristic (breakdown canonical for architectural fields; Jira canonical for AC, sprint-level scope tightening, owner reassignment) that the user can override per row. Five phases: Fetch & Parse, Triage (with the new drift detection), Confirm (one-at-a-time discipline for flagged rows; CONFLICT rows must resolve before Execute), Execute (delegated to whichever Jira authoring tool the engineer has — `jira-cli`, `jira-manager`, direct Atlassian MCP, or the Jira UI — in dependency order), Sync back (writes new keys into the Tasks section, applies pulled-from-Jira changes back into the breakdown, bumps Status block, commits), Summary (with a lifecycle-reset surface when a pulled change touches a signed-off cross-team interface). `HARD-GATE` blocks any writes until the full triage plan is user-confirmed. Bakes in Bitwarden field mapping: `Technical breakdown` (`customfield_10313`), `Acceptance Criteria` (`customfield_10192`), `Team` (`customfield_10001`); Description carries only the inline breakdown link. Stack-area prefix (`[Clients]`, `[Web]`, `[Server]`, `[SDK]`, `[iOS]`, `[Android]`) applied when single-stack. Dependencies wired as Jira issue links (`is blocked by`, `depends on`, `relates to`), never as Description prose. Replaces the earlier `creating-stories-from-a-tech-breakdown` name; the more generic name reflects the skill's ongoing-sync responsibility, not just one-time creation.
- **`doing-a-tech-breakdown` skill** — second of the phase-scoped skills splitting `writing-tech-breakdowns` into smaller composable units. Walks the engineer through **understanding the work** behind a breakdown, not through filling out template fields. Four phases: Resume (skip if fresh), Orient (gather context, produce Decided / Open / Gaps), Resolve (work each open design question one at a time with 2-3 concrete options), Develop and capture (articulate, consider alternatives both smaller and rejected, map per-layer impact via `Skill(architecting-solutions)`, decompose with the 10-task soft prompt, **scan for in-flight work** against the concrete file and module list, **identify cross-team impacts and characterize them** by domain-overlap depth and owning-team domain churn, surface what would surprise a reader, **curate the Clarifications Log to prune drafting trivia**, then run a final AI clarify pass). Cross-team engagement (including the signoff table) is built inside this skill, but **assigning a collaboration model per impact is an owner task, not a skill task** — the breakdown owner picks a model (File a Ticket / Internal Open-Source / Embedded Expert) per row based on the depth and churn the skill captured, and the owning team confirms or counter-proposes at signoff. The Signoff column fills itself in between `Proposed` and `Accepted` as named reviewers respond on each owning team's public Slack channel; there is no chasing skill. The in-flight scan checks three sources — other teams' breakdowns in `bitwarden/tech-breakdowns`, open PRs in affected repos, and recent `git log` activity on affected files — and runs after decomposition so it operates on a real file list, not a rough repo guess. Sections of the breakdown (Specification, Plan, Tasks, Agent Context, Clarifications Log) are framed as **the trace of the thinking** rather than the activity itself. Uses the Clarifications Log as **dual-use working state and reviewer artifact**, following Anthropic's structured-note-taking pattern: Phase 2 captures Q-and-A liberally; Phase 3 curates before reviewer-ready. `HARD-GATE` blocks capturing design decisions while questions remain unresolved. DOT process-flow graph, Resume / Fresh-start checklist, and `TaskCreate` discipline at each phase. Routes cryptographic work through `Skill(bitwarden-security-context)`. Points at the Confluence page **Tech Breakdowns: Process and Framework** for policy and framework rationale, keeping the skill body operational only.

### Changed

- **Tech Breakdown workflow re-anchored to the markdown-based [`bitwarden/tech-breakdowns`](https://github.com/bitwarden/tech-breakdowns) repo template** (single self-contained file in `<team>/`, no child pages) — replaces the previous Confluence template page. Named sections (Specification, Clarifications Log, Plan with per-layer subsections, Tasks, Agent Context) replace "Part 1–6" numbering. Lifecycle states are Title Case (`In Planning / In Progress / Proposed / Accepted / Rejected / Complete`). Workflow mechanics anchored on git PRs and CODEOWNERS rather than Confluence edits. AI-clarify-pass discipline applied in `doing-a-tech-breakdown` Phase 3 step 9. Engineer-vs-tech-lead role split removed — anyone on the team drafts a breakdown. Files under `**/complete/**` are point-in-time historical records, not source of truth.
- **Signoff table** — columns are `Team`, `Interface`, `Associated breakdown`, `Signoff`. (`Describe interface` → `Interface`, `Associated Other Team Breakdown` → `Associated breakdown`; the `Blocking?` column is dropped.) Built inside `doing-a-tech-breakdown` Phase 3 step 6; reviewers from named owning teams fill the `Signoff` column during cross-team review between `Proposed` and `Accepted`. Teams that only need to be informed belong in Coordination notes or an FYI Slack post.
- **Jira story creation** — two valid timings, tied to how the team refines: **create stories at Proposed entry** (default, for ticket-refinement teams) or **defer to the Accepted gate** (for teams who refine on the breakdown). Either way, by `Accepted` stories must exist with bidirectional linkage. Owned by `syncing-tasks-with-jira`. Story-specific tech-breakdown content goes in the dedicated **`Technical breakdown` custom field** (`customfield_10313`), not Description. `customfield_*` IDs surfaced inline (Technical breakdown `customfield_10313`, Acceptance Criteria `customfield_10192`, Team `customfield_10001`) so authoring tooling can target them programmatically. Mechanics-level Jira writes are delegated to whichever Jira authoring tooling the engineer has available (a `jira-manager` / `jira-cli` skill, direct Atlassian MCP write calls, or the Jira UI) rather than performed by this skill.
- **Tasks-section sizing nudge** — **10 or fewer tasks** is healthy (refinable in one or two sessions, predictable release date); **more than 10** review for natural seams (sequential phases, independently-shippable subsets, interface boundaries) and split.
- **Engineering-owned vs. Product-owned BW Initiatives** distinguished across the tech-breakdown skills. `Skill(navigating-the-initiative-funnel)` references are qualified as applying only to Engineering-owned initiatives; for Product-owned initiatives, point at the linked PRD and the named Product owner for the equivalent context and escalation paths.
- Plugin `allowed-tools` set across the lifecycle skills updated for the new working surface: local filesystem tools (`Read`, `Edit`, `Write`, `Bash`, `Glob`, `Grep`) for working with the `bitwarden/tech-breakdowns` repo; Atlassian read tools retained for pulling Jira/Confluence context referenced from a breakdown.
- README skill catalog and the `bitwarden-tech-lead` agent's Cross-Plugin Integration block updated to the new phase-scoped skills, with the current template section naming and Title Case lifecycle states.

### Security

- Tech-breakdown skills (`starting-a-tech-breakdown`, `doing-a-tech-breakdown`, `syncing-tasks-with-jira`) — added untrusted-input boundary callouts. Engineer-authored markdown in `bitwarden/tech-breakdowns`, sibling-team breakdowns, PR titles, branch names, and commit messages are explicitly framed as data under analysis, never as instructions to execute. Addresses CWE-1427 exposure from the `Bash`/`Write`/`Edit` access the lifecycle skills hold while reading engineer-authored content.

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
