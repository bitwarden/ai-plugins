# Changelog

All notable changes to the `bitwarden-delivery-tools` plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.3.0] - 2026-09-09

### Added

- **`stacking-pull-requests` skill** — carries Bitwarden's per-PR conventions across a chain of dependent pull requests: layer planning, per-layer gates walked bottom to top, one whole-stack submission preview, lower-layer feedback, and merging. `gh stack` mechanics are delegated to GitHub's `gh-stack` skill and extension, and Step 0 falls back to a single-branch PR whenever either is unusable for the current run.
- `perform-preflight`: a Stacked Branches section covering the current layer, with its own stack detection. It stops when a commit is about to land on a layer that already has an open pull request, since that rebase belongs to `stacking-pull-requests` Step 5.
- `committing-changes`: `description` gains a stack boundary so stack-level requests route to `stacking-pull-requests`. The body stays stack-agnostic, since a layer is a branch and the existing "first commit on a branch" rule already applies per layer.

### Changed

- `creating-pull-request`: routes chain requests to `stacking-pull-requests`, and accepts a single pull request back from it when the stack path is unavailable. Its review gate runs per layer when that skill drives it.
- `applying-pr-conventions`: invoked once per layer by the stack path.

## [3.2.0] - 2026-09-09

### Added

- **`applying-pr-conventions` skill** — composes one pull request's title, template body, resolved `t:` label, and `ai-review` label choice, and returns them. `creating-pull-request` and `force-multiplier` both invoke it instead of one reaching into the other.

### Changed

- `creating-pull-request`: title, body, and label move to `applying-pr-conventions`; steps renumber 1–6 to 1–4.
- `creating-pull-request`: the review gate no longer exempts callers.
- `creating-pull-request`: Step 1 resolves the base branch, and the push step passes `--base` for a branch cut from a release branch.
- `creating-pull-request`: `when_to_use` folded into `description`.
- `force-multiplier`: takes conventions from `applying-pr-conventions` at its pilot target.
- `creating-pull-request`: `description` broadened to cover the natural phrasings for turning a branch into a PR, and to keep the request when it also asks about the title or `t:` label. Triggering measured 9/10, up from 1/10.
- `creating-pull-request` evals: 22 cases, six should-trigger queries rewritten to drop repo fixtures, `--plugin-dir` added to the runner, baseline re-recorded.

### Security

- `references/pr-title-allowlist.md` — every path that submits a PR title validates it before the title reaches a shell. `gh` has no `--title-file`, so the generated summary would otherwise be interpolated into a double-quoted argument. Two checks, in order: refuse any title containing a line break, then match the whole string against the pattern. The line-break check is not redundant with the anchors, because `grep -qE` is line-oriented and an anchored pattern still passes a multi-line title whose second line carries the payload.
- `applying-pr-conventions` declares `allowed-tools: Read, Glob`, so its compose-and-return contract is structural rather than prose. It names the allowlist to its caller rather than running it, since running it needs a shell this skill deliberately cannot reach.
- `force-multiplier` states the `--body-file` rule where it opens each PR. It previously inherited it from `creating-pull-request`, and no longer enters that workflow.
- `applying-pr-conventions` treats the target repo's PR template as data rather than as instructions addressed to it, matching `force-multiplier`'s rule for target-repo content.

## [3.1.0] - 2026-08-19

### Added

- **`filing-breakdown-tasks` skill** — turns a breakdown's `tasks.md` into Jira ticket drafts: an epic parent plus one child story/task per entry, with acceptance criteria and mapped dependency links, then hands off to `filing-jira-tickets` to file them. Requires `bitwarden-atlassian-tools`.
- **`filing-breakdown-tasks` trigger eval** (`skills/filing-breakdown-tasks/evals/`) — a 20-query trigger eval (10 should-trigger, 10 near-miss) with a recorded baseline.

### Changed

- `plugin.json`: description and `jira` keyword added for the new skill. Marketplace description and README catalog entry follow suit.

## [3.0.0] - 2026-08-08

### Removed

- **BREAKING:** `starting-breakdown`, `developing-breakdown-spec`, `developing-breakdown-plan`, and `decomposing-into-tasks` skills. Tech Breakdown drafting now lives in the [`bitwarden/tech-breakdowns`](https://github.com/bitwarden/tech-breakdowns) repository, where the templates and per-team folder conventions are canonical.

### Changed

- `navigating-the-initiative-funnel`: Phase-4 Tech Breakdown paragraph and Related links rewritten to point at the `bitwarden/tech-breakdowns` repository instead of the removed skills.
- `README.md`: breakdown skills removed from the Technical design table; usage examples for the removed skills dropped; a pointer to `bitwarden/tech-breakdowns` added for discoverability.
- `plugin.json`: description and keywords stripped of `tech-breakdown` / `task-decomposition`. Marketplace description and README catalog entry follow suit.

## [2.4.0] - 2026-07-31

### Added

- **`committing-changes` skill** — added a branch check step. If the current branch is the repository's default branch, the user is asked for a branch before staging or committing. If the default branch cannot be resolved, the current branch is confirmed instead of assumed.
- **`committing-changes` eval set** (`skills/committing-changes/evals/`) — a 13-query trigger eval and a six-case behavior eval in the `skill-creator` schema, each with a recorded baseline.

## [2.3.0] - 2026-07-30

### Added

- `creating-pull-request`: a code-review gate in Step 1 that runs before a PR is opened, routing by change blast radius — Standard runs `code-review-local`, Substantial runs `performing-multi-agent-code-review` against the full branch diff. Deferred CRITICAL/IMPORTANT findings are recorded in the PR body and surfaced in the Step 5 preview, an optional second-model re-run (via the multi-agent skill) is available for the highest-risk changes, review output is cleaned up before pushing, and invocations from another delivery skill's workflow are exempt (wiring review into those callers is a tracked follow-up).
- `README`: documented the `bitwarden-code-review` dependency in the **Related Plugins** section.

### Changed

- `creating-pull-request`: narrowed Step 1's preflight options so the quality gate can no longer be silently skipped.

### Security

- `creating-pull-request`: submit the PR body via `--body-file` instead of `--body` so review- and model-generated text (derived from untrusted repo content) cannot be interpreted as shell during `gh pr create`.

## [2.2.0] - 2026-07-10

### Added

- **`architecting-solutions` skill** — moved in from `bitwarden-tech-lead` (last at 2.3.2) and reworked to increase security focus and remove explicit Initiative Shepherd references.

## [2.1.0] - 2026-07-01

### Added

- **`force-multiplier` skill** — fans one intent across a repo fleet or monorepo into N consistent, idempotent draft PRs, gated by a mandatory pilot and per-target isolation. Repo content is untrusted data (CWE-1427); destructive recipes require a reference-check with a `held-back` reconciliation disposition; the secrets-scan has a no-scanner fallback.
- **`force-multiplier` behavior eval set** (`skills/force-multiplier/evals/`) — seven `skill-creator`-schema cases guarding its load-bearing decisions.

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
