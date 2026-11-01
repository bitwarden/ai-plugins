# Changelog

All notable changes to the bitwarden-owning-team-review plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-10-31

### Added

- `owning-team-classifier` agent. Classifies whether each changed file outside domain critical paths needs review from its owning team, or whether any engineer can approve it. It assigns a change kind from the global policy, checks the change against the module's `INTENT.md` from the base commit, fails shut when no signal supports "any engineer," and prints a JSON result. Each required entry carries an explanation and a next step for the author, and a review focus for the owning-team reviewer, which the enforcing workflow renders into a PR comment. The agent has only `Read`, `Grep`, and `Glob`: no shell, no write access, and no GitHub access. Ownership comes from `CODEOWNERS`, which the workflow reads.
- `prepare-context.sh` script. Every caller runs it before the agent. It fetches the diff, changed files, base and head CODEOWNERS, and an export of the base commit into a context directory, validates the PR number, repository, base ref, and commit SHAs, and never fetches the PR title or body.
- `inject-intent.sh` hook. Attaches the governing `INTENT.md` to the first Read of a file in a module, so it arrives before any edit. When an edit comes first, it pauses that one edit with the intent as the reason. It never pauses a second edit in the same module. It ignores a symlinked `INTENT.md`.
- Local mode. `prepare-context.sh local` builds a context for the current branch against its merge base, so the classifier runs before a PR exists.
- Owner grouping. Result entries carry `owners` and never mix files with different owners, so each team's section of the PR comment holds only that team's review focus. A file the base commit gives no owner takes the owner the PR's own `CODEOWNERS` change assigns.
- The cross-owner import indicator fires only for an owner a file did not import from before. Moving a call site to a replacement the same PR adds, from the same owner, is `pattern-following`.
- `classify-owning-team-review` skill. Runs the agent on the current branch (`local`) or on one or more PRs and reports a table, for checking an open PR or backtesting a module's INTENT.md against merged PRs.
- Feedback loop design in the README. The PR comment ends with checkboxes that owning-team reviewers tick to label the classification. The enforcing workflow records each label with the classifier version, model, and base commit, and a tick never changes the status.
- `change-kinds.md` reference. Defines eight change kinds in three families (`fix`, `pattern-following`, `debt-extending`, `pattern-breaking`, `special-case`, `structural`, `api-additive`, `api-breaking`), the mechanical indicators that set a minimum kind, and clients and server examples for each.
- Classification evals in `evals/`. 23 synthetic pull requests, one per change kind, signal, and security guard, and 15 real `bitwarden/clients` pull requests replayed with a draft Platform `INTENT.md`, scored deterministically. Runs use a `gh` stub for the synthetic set and never post to GitHub. False negatives are counted separately and gate every change.
- `render-comment.sh` script. Renders the classifier's result as the evaluation-mode PR comment, with a section per owning team, feedback checkboxes, evidence links at the head commit, and the workflow's reviewer request check. It escapes the agent's text, and renders a missing, unparseable, or stale result as no verdict.
- `extract-result.sh` script. Parses the result JSON from the agent's final message, for the workflow and the evals.
- `intent-format.md` reference. Defines `INTENT.md`: purpose, direction, boundaries, and patterns, plus optional review exceptions. Intent only raises a change to the owning team.
