# Changelog

All notable changes to the bitwarden-feature-flag-unwinder plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-10-20

### Added

- Initial release. One agent (`feature-flag-unwinder`) scoped to a single repo per invocation. The agent reads a Jira cleanup task (`customfield_12076` for the flag key; `flagged-logic-removal` or `server-flag-removal` label for the step), executes the step inside the current working directory, verifies with `Skill(perform-preflight)`, and opens one draft PR against the current repo. Step 1 removes flagged logic plus the per-repo flag definition in clients, server, ios, or android; Step 2 removes the key from server `FeatureFlagKeys` after a backward-compat gate check delegated to `Skill(computing-backward-compatibility)` (±2 month window, safe server release = last-client-with-flag.month + 3). Step 3 (LaunchDarkly archival) is manual and intentionally un-labelled; the agent never picks it up.
- `examples/per-repo-workflow.yml` — the per-repo workflow template. Copies into each of `bitwarden/clients`, `bitwarden/server`, `bitwarden/ios`, and `bitwarden/android` at `.github/workflows/feature-flag-unwinder.yml`. Triggers on `repository_dispatch: feature-flag-unwinder`. Follows the pattern of `bitwarden/clients/sdk-update.yml`: Azure Key Vault token minting, GH App installation token for commits, `bw-ghapp[bot]` identity, reusable `flag-cleanup/<flag>-step-<N>` branch guarded against human edits (tip-author check + `stop-cleanup` label check). The server workflow additionally mounts a read-only sidecar checkout of `bitwarden/clients` so Step 2 can run the compat gate.
- `examples/conductor-workflow.yml` — the biweekly dispatcher. Lives in an ops repo, runs every other Wednesday at 15:00 UTC (even ISO weeks), queries Jira for `labels = "ready-for-cleanup" AND (labels = "flagged-logic-removal" OR labels = "server-flag-removal") AND statusCategory != Done`, splits results by step label, and fans out `repository_dispatch` events. Step 1 dispatches to all four target repos; Step 2 dispatches to server only. The conductor never touches target-repo code — all cleanup happens inside each target repo's own workflow.
- Branch guards against clobbering human work: if the flag-cleanup branch already exists on the remote with a tip commit not authored by `bw-ghapp[bot]`, or if the open PR carries a `stop-cleanup` label, the agent aborts and links the existing PR on Jira rather than overwriting.
- Build and tests must pass before any PR is opened. The agent runs the target repo's canonical build + test commands (deferring to its `CLAUDE.md`) on the edited branch before committing, iterates on fixes within a bounded budget if the removal left stragglers, and aborts if verification can't be made green.
- The agent posts one Jira comment per run — one URL per PR as each per-repo workflow completes. For Step 1, the Jira ticket collects four comments as clients, server, ios, and android finish independently. For Step 2, one comment with the per-platform compat-gate data from the backward-compat verdict.
