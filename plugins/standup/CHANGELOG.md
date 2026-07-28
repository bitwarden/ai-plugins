# Changelog

All notable changes to the standup plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.9.0] - 2026-09-15

### Changed

- `synthesize-standup-report` skill: Updated to consume `involvement_tier` signals emitted by gather.py v1.8.0+. `AUTHORED` items are standup-worthy by default; `SUBSTANTIVE_REVIEW` items are standup-worthy when the PR was merged or has pending decisions; `LIGHT_REVIEW` items are included only when `user_merged_pr`, an unusual PR state, or linked ticket context is present. The existing `own_comment_count >= 8` rule is now a fallback for older gather.py output.
- `synthesize-standup-report` skill: Confluence edits now use `is_page_creator` to lead with "Created" vs. "Updated/Edited" — these are meaningfully different standup bullets.
- `synthesize-standup-report` skill: Jira done/created items with `user_comment_count >= 3` are now characterized as tickets Addison actively engaged with (framing: "Drove resolution on...", "Resolved after driving the thread on...").
- `synthesize-standup-report` skill: Input Contract updated to document all involvement depth signals introduced in v1.8.0 (`involvement_tier`, `review_states`, `user_merged_pr`, `user_comment_count`, `is_page_creator`, `field_counts`, `issues_touched`).

## [1.8.0] - 2026-09-15

### Added

- `involvement_tier` field on `authored_prs` items (constant: `"AUTHORED"`)
- `involvement_tier` field on `reviews_given` items (`"SUBSTANTIVE_REVIEW"` or `"LIGHT_REVIEW"`)
- `review_states` field on `reviews_given` items (list of review state strings from user's reviews)
- `user_merged_pr` field on `reviews_given` items (bool: true if user merged the PR)
- `user_comment_count` field on `jira_done` and `jira_created` items (count of user's own comments on the ticket)
- `is_page_creator` field on `confluence_edits` items (bool: true if user authored version 1 of the page)
- `field_counts` dict to `jira_grooming.summary` (field name → event count)
- `issues_touched` int to `jira_grooming.summary` (total distinct issues groomed)

## [1.7.0] - 2026-09-15

### Added

- `synthesize-standup-report` skill: Added Mechanism-Disclosure Rule. When a bullet's mechanism was deliberately chosen over a rejected alternative, a parenthetical disclosing the trade-off rationale is permitted and encouraged. Format: `[outcome] by [mechanism] ([trade-off rationale])`. The parenthetical must be grounded in the ticket description, PR body, or comment thread — never invented. Kept to one brief clause (~10 words or fewer).

### Changed

- `synthesize-standup-report` skill and `default-output-example.md`: Raised bullet length ceiling from `<= 12 words` to `<= 30 words` to allow causal narrative (mechanism + trade-off parenthetical). The previous 12-word cap was too tight to accommodate the `[outcome] by [mechanism] ([rationale])` pattern. Updated `~/.claude/standup/preferences.md` to match.

## [1.6.1] - 2026-09-14

### Fixed

- `collect_github.py`: Bare PR approvals (reviews where the user left no substantive comments and did not merge the PR) are now excluded from `reviews_given`. Previously, a one-click approval on any PR surfaced as a standup bullet. After this fix, a review only appears if `own_comment_count > 0` or `merged_by_login == github_user`. Renovate/bot PR approvals that the user merges are retained; rubber-stamp approvals on human PRs are filtered out. Also adds `mergedBy { login }` to both GraphQL queries to support the merge-author check.

## [1.6.0] - 2026-09-14

### Changed

- Added cross-week consistency step (Step 1: Historical Report Context) to `synthesize-standup-report` skill. Before drafting, the synthesizer now reads the 3 most recent files from `~/.claude/standup/reports/` (sorted by filename timestamp) and extracts recurring language patterns, verb choices, ongoing narratives, and carried items. This context informs voice and framing throughout synthesis — consistent idiom and narrative continuity across weeks, without copying prior content. Existing steps renumbered 2–8. Rationale: each synthesis run previously started cold with no awareness of recent report history, causing inconsistent language, random verb rotation, and re-introduction of ongoing initiatives as if new.

## [1.5.0] - 2026-09-14

### Changed

- Added outcome-intention verb discipline rule to `synthesize-standup-report` skill Step 4 (This Week section). The rule enforces outcome-intention openers (Land, Ship, Close, Deliver, Finalize, Complete, Resolve, Merge) and bans activity-framed openers ("In Progress on", "Iterating on", "Working on", "Continuing", "Making progress on"). Rationale: This Week answers "what do you intend to complete this cycle?" — a forward prediction, not an activity report. Activity openers are a persistent D6 audience-calibration failure under rubric v3.0 that preferences instructions alone cannot close.

## [1.4.1] - 2026-09-14

### Changed

- Updated `default-output-example.md` with the winning Mode A output format from Cycle 3 eval loop (composite 90.0/100). The new format adds three instructions absent from the prior version: explicit artifact-state hedging for non-terminal items (D4), earned hedge type preservation (D4), and blocker actionability with impediment + unblock path (D8).

## [1.4.0] - 2026-09-11

### Changed

- Updated plugin framing for Mode A across all user-facing copy (SKILL.md description and output contract, standup-report-generator agent description, and README intro). The output of the synthesize skill is now described as a terse Mode A draft scaffold intended to be rewritten through the user's voice — not a finished, publishable deliverable. This makes the plugin's confirmed product role (Mode A: human finishing expected) explicit to both users and agents.

## [1.3.0] - 2026-09-02

### Added

- Refining-question step (Step 0) in `synthesize-standup-report` skill. When run interactively, the synthesizer now asks one research-grounded question before drafting — "How would you characterize this week in one sentence?" — to elicit the categorically un-scrapeable BLUF signal: the author's subjective workload self-read, pacing characterization, and social standing. The answer is placed near-verbatim as the BLUF summary line; the RAG color remains data-derived. Up to two conditional Tier-2 follow-ups fire based on the Tier-1 answer (teammate credit signal, path-uncertainty signal). The step skips gracefully in non-interactive contexts (eval loop, CI). Total question cap: 1 default, 3 maximum.
- Durable context persistence in Step 0. When a refining-question answer reveals a durable recurring fact (standing ticketless commitment, ongoing narrative, framing preference), the synthesizer now directs the calling agent to write it to the appropriate subheading of `## Durable Context` in `~/.claude/standup/preferences.md` so it need not be re-elicited in future sessions.

## [1.2.0] - 2026-09-01

### Added

- Added durable-context support to synthesize-standup-report skill. The synthesizer now reads the `## Durable Context` section from preferences (`### Priorities`, `### Ongoing Narratives`, `### How I Frame Things`) and applies it as framing context before drafting. Absent or empty sections are treated as not set.

## [1.1.0] - 2026-09-01

### Added

- Team identity preference: `/standup:init` now asks for the user's team name (optional) and stores it in `~/.claude/standup/preferences.md` as a new `## Team` section. The team value is used by the synthesize skill for cross-team detection.
- Cross-team credit derivation: `generate-standup-report` now fetches the Jira Team field (`customfield_10001`) for all Jira items and for Jira tickets linked in PR descriptions. When the synthesize skill detects a `linked_ticket.team` that differs from the user's team (from preferences), it annotates the bullet to credit the cross-team collaboration — surfacing contributor credit without any per-run human input.

## [1.0.4] - 2026-08-25

### Changed

- Documented why `Bash(python3:*)` in `generate-standup-report`'s `allowed-tools` and `standup-report-generator`'s `tools` field cannot be restricted to `gather.py` by path: `${CLAUDE_PLUGIN_ROOT}` does not expand in permission specifiers, so a path-specific pattern cannot be expressed. Added inline comments on each entry noting the preflight hook as the scope boundary.

## [1.0.3] - 2026-08-25

### Changed

- Clarified in `standup-report-generator` (Step 2 - Preflight) and `generate-standup-report` skill (Environment Variables section) that `JIRA_API_TOKEN` is verified for presence only by the preflight hook — neither the hook nor Claude ever reads the token value. The Python collector reads it directly from `os.environ` and uses it only as an HTTP Basic auth header.

## [1.0.2] - 2026-08-25

### Fixed

- Renumbered agent workflow steps in `standup-report-generator` to start at Step 1 instead of Step 0.

## [1.0.1] - 2026-08-25

### Fixed

- Pruned two unused entries from the repo-level `.cspell.json` dictionary that were added alongside the plugin introduction but do not appear in any plugin file. <!-- cspell:ignore roam retargeted -->

## [1.0.0] - 2026-08-25

### Added

- `/standup:generate` command: generates a standup report by collecting real activity from GitHub, Jira, and Confluence, synthesizing it into a structured report, and delivering it to the configured destination.
- `/standup:init` command: interactive guided setup that captures identity, workspace, and output preferences and writes them to `~/.claude/standup/preferences.md` (a dedicated, load-on-demand file — never auto-loaded). Includes diff preview, timestamped backup, and explicit Apply confirmation.
- `edit-standup-preferences` skill: performs in-place section edits that `/standup:init` deliberately refuses (init only creates or fully replaces). Edits a single `##` section of the preferences file with the same diff preview and backup safety flow.
- `generate-standup-report` skill: Python activity collectors (`gather.py`, `collect_github.py`, `collect_jira.py`, `collect_confluence.py`, `lib/`) that fetch real data and emit structured JSON with semantic category keys (`authored_prs`, `reviews_given`, `jira_done`, `jira_created`, `jira_comments`, `confluence_edits`, `jira_grooming`, `in_progress`, `blocked`).
- `synthesize-standup-report` skill: synthesizes the collected activity into a report using a RAG-status heuristic, select→enrich→collapse pipeline, and a built-in default output format. The user's preferences file (if present) overrides the built-in defaults wholesale.
- `deliver-standup-report` skill: routes the finished report to the first available destination (local markdown file or stdout), with optional voice-correction gating driven by the user's output preferences.
- `standup-report-generator` agent: thin orchestrator that chains the generate → synthesize → deliver pipeline and reminds users of the `edit-standup-preferences` skill after delivering a report.
- Preflight credential hook (`hooks/hooks.json` + `hooks/preflight-credentials.sh`): a `PreToolUse` gate that verifies `JIRA_API_TOKEN` is set and `gh auth status` succeeds before the collector runs. Blocks with a targeted error message if either prerequisite is missing; never reads or prints any token value.
- `templates/user/` preference modules (`identity.md`, `destination.md`, `output-format.md`, `recurring-responsibilities.md`) that `/standup:init` renders into the preferences file.

<!-- cspell:ignore alovelace firstinitiallastname firstname -->
