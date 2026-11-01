# Changelog

All notable changes to the bitwarden-owning-team-review plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-10-31

### Added

- `owning-team-classifier` agent. Classifies whether each changed file outside domain critical paths needs review from its owning team, or whether any engineer can approve it. It assigns a change kind from the global policy, checks the change against the module's `INTENT.md` from the PR's base commit, fails shut when no signal supports "any engineer," and writes `owning-team-review-<PR>.json`. Each required entry carries an explanation and a next step for the author, and a review focus for the owning-team reviewer, which the enforcing workflow renders into a PR comment. Read-only on GitHub. Ownership comes from `CODEOWNERS`, which the workflow reads.
- `inject-intent.sh` hook. Attaches the governing `INTENT.md` to the first Read of a file in a module, so it arrives before any edit. When an edit comes first, it pauses that one edit with the intent as the reason. It never pauses a second edit in the same module.
- Local mode. `TARGET: local changes` classifies the current branch against its merge base, before a PR exists, and prints the result without writing a file.
- Owner grouping. Result entries carry `owners` and never mix files with different owners, so each team's section of the PR comment holds only that team's review focus. A file the base commit gives no owner takes the owner the PR's own `CODEOWNERS` change assigns.
- The cross-owner import indicator fires only for an owner a file did not import from before. Moving a call site to a replacement the same PR adds, from the same owner, is `pattern-following`.
- `classify-owning-team-review` skill. Runs the agent on the current branch (`local`) or on one or more PRs and reports a table, for checking an open PR or backtesting a module's INTENT.md against merged PRs.
- Feedback loop design in the README. The PR comment ends with checkboxes that owning-team reviewers tick to label the classification. The enforcing workflow records each label with the classifier version, model, and base commit, and a tick never changes the status.
- `change-kinds.md` reference. Defines eight change kinds in three families (`fix`, `pattern-following`, `debt-extending`, `pattern-breaking`, `special-case`, `structural`, `api-additive`, `api-breaking`), the mechanical indicators that set a minimum kind, and clients and server examples for each.
- Classification evals in `evals/`. 22 synthetic pull requests, one per change kind, signal, and security guard, scored deterministically. Runs use a `gh` stub and never reach GitHub. False negatives are counted separately and gate every change.
- `intent-format.md` reference. Defines `INTENT.md`: purpose, direction, boundaries, and patterns, plus optional review exceptions. Intent only raises a change to the owning team.
