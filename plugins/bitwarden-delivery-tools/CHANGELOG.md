# Changelog

All notable changes to the `bitwarden-delivery-tools` plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.2.0] - 2026-09-04

### Added

- **`stacking-pull-requests` skill** — Bitwarden's per-PR conventions across a chain of dependent pull requests: layer planning, per-layer gates, a stack-level submission preview, lower-layer feedback, and merging. `gh stack` mechanics are delegated to GitHub's `gh-stack` skill and extension, with an availability check and a single-branch fallback
- `references/submitting-a-stack.md` — the two paths that carry a title, body, and `t:` label onto every layer; `gh stack link` is passed `--base` so the bottom layer's base is not silently rewritten to the repository default branch
- **`applying-pr-conventions` skill** — the title, template body, and `ai-review` label a Bitwarden pull request needs, composed for one PR and returning those three values only. `creating-pull-request`, `stacking-pull-requests`, and `force-multiplier` all invoke it instead of reaching into each other: the stack path calls it per layer, the fan-out once at its pilot
- `references/installing-gh-stack.md`, holding the install detail out of the always-loaded file
- `skills/stacking-pull-requests/evals/` — 20-case trigger eval, runner, and README. The runner denies the mutating tools, loads no MCP servers, and runs each subprocess in a temp directory, since the query set is imperative. No baseline is committed
- `perform-preflight`: Stacked Branches section covering the current layer, with its own stack-detection test; a skipped section is reported rather than passing silently. It stops when the layer already has an open pull request, since that fix belongs to `stacking-pull-requests` Step 5 — the check sits here because `committing-changes` runs this checklist before staging, so a direct commit onto a lower layer passes through it
- `stacking-pull-requests` Step 1 registers the planned layers with `gh stack init`, so submission does not fail after every layer has been gated and previewed
- `stacking-pull-requests` Step 5 confirms before rebasing layers above a fix, and Step 6 confirms before both the draft flip and the merge
- `perform-preflight`: a failed rebase checkbox on a layer with an open pull request is reported rather than auto-fixed, since the fix force-pushes every layer above; before submission it is fixed in place, rebasing the layer and restacking the layers above it

### Changed

- `creating-pull-request`: routes to `stacking-pull-requests` on the user's intent to open a chain, and never when that skill is the caller. Its title, body, and label steps moved to `applying-pr-conventions`, so the workflow is now gate → conventions → preview → submit and its steps renumber 1–6 to 1–4
- `creating-pull-request`: Step 1b names the base ref instead of hardcoding `origin/HEAD`, and keys it on the same trunk-or-release-branch distinction its push step uses for `--base`, so a branch cut from `rc` is not reviewed against trunk with every already-merged release commit in the diff. Only the `Substantial` path can be scoped to one layer, or to an explicit range on a release-cut branch
- `creating-pull-request`: the review gate has no exemption left. `force-multiplier` was the only caller that skipped it and no longer enters this workflow at all, so the gate runs on every entry; the single remaining caller edge is `stacking-pull-requests` running Step 1b alone, per layer
- `creating-pull-request`: its push step passes `--base <branch>` for a branch cut from `rc`, `hotfix-rc`, or another release branch, which `gh pr create` would otherwise point at the repository default branch
- `force-multiplier`: collects conventions from `applying-pr-conventions` at its pilot target rather than walking `creating-pull-request`, so there is no per-PR preview, no `gh pr create`, and no review gate to suppress mid-campaign
- `committing-changes`: `description` gains a stack boundary so stack-level requests route to `stacking-pull-requests`. The body stays stack-agnostic — a layer is a branch, so the existing "first commit on a branch" rule already applies per layer — and the open-pull-request guard lives in `perform-preflight`, which this skill already runs before staging
- Stack detection reads `gh stack view --json`'s exit code and requires a payload naming the current branch; `stacking-pull-requests` Step 0 owns what each status means
- `creating-pull-request`: stack exclusion added to `description`; its eval baseline is stale and must be re-recorded after this version ships, since that runner takes no `--plugin-dir` and loads the installed cache
- `committing-changes` gains a single-layer eval case guarding its new description boundary. The stack boundary cannot be measured from these skills' own eval sets — correct routing goes to `stacking-pull-requests`, which then invokes them per layer, and the runner matches its token anywhere in the response — so it is measured from `stacking-pull-requests/evals/` only. Its runner requires `--plugin-dir`, so that baseline can be recorded from the branch; the `committing-changes` and `creating-pull-request` baselines take no such flag and must wait until after this version ships
- `stacking-pull-requests`: the stack root is `<stack base>` rather than `<trunk>` in `gh stack init`, the Step 4 preview, and both commands in `submitting-a-stack.md`, so a stack rooted on `rc` or a release branch is not registered and submitted against the default branch
- `stacking-pull-requests` Step 0 gates on whether the tooling is usable in this run rather than on install status: a skill installed mid-session is on disk but unresolvable until Claude Code restarts, so that outcome reports the install and takes the single-branch fallback instead of continuing into the stack path
- `creating-pull-request` no longer detects which skill is calling it. The three-signal protocol and the six-row caller table collapse to two documented edges on the review gate — run only that step (`stacking-pull-requests`, per layer) or skip it on a named caller that owns the review (`force-multiplier`) — plus the reverse-direction handoff when the stack path is unavailable for a run, which now covers a mid-session install as well as a decline. `references/caller-integration.md` is deleted
- `stacking-pull-requests` Step 2 walks the layers bottom to top, the order under which a lower layer's rebase is re-gated on every layer above it
- `plugin.json`: description and `stacked-pull-requests` keyword added; marketplace and README catalog entries follow

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
