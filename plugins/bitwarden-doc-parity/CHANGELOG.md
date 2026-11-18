# Changelog

All notable changes to the bitwarden-doc-parity plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-11-18

### Changed

- Stop-hook tripwire ignores package-manager lock files in Bitwarden's stack (`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `*packages.lock.json`, `Cargo.lock`). Prevents false-positive fires when an IDE's background restore rewrites dozens of lock files the agent never touched. Generated source files are still treated as code.
- Skill report rules in Step 4 condensed: when nothing drifted, the report is a single line (`Documentation parity: verified current, no changes required.`); when updates were made, the report lists only the Update lines with their reasons and omits Attest scopes. The internal walk still covers every documented scope. Addresses feedback that the per-scope enumeration flooded terminals in large repos.
- Step 4 forbids naming attested scopes in prose as well as in lists, and requires every Step 3 judgment to finish before the report shape is chosen. One sentence confirming the user's own documentation edits is still allowed, and in a review, out-of-repo callouts are always reported alongside the one-line or Update-only report. Eval runs on 1.1.0 had emitted the one-line report followed by a sentence listing the checked scopes.
- Step 2 adds a repo search for text outside the ancestor chain that restates a value or name the change altered, such as another file's doc comments, a schema `description`, or CLI help text. Eval runs had missed a changed percentage split restated in three such places.
- Behavior eval 10: the PR title now names the `organization` → `org-preset` rename the fixture performs.
- Behavior eval 1 uses a new scenario: a ninth username category, which makes the "8 username patterns" line in `util/Seeder/Data/README.md` stale. The previous scenario (a new generator class) caused no drift, because that README does not list generators. The case also grades the update to a restated percentage in `OrganizationVaultOptions.cs`.
- Behavior eval 6 is renamed `xml-docs-do-not-discharge-readme` and uses a new scenario: `attachmentVersion` becomes optional with an inferred default. The previous scenario (a `v3` attachment scheme) produced attachments that clients could not decrypt and duplicated v1. The new scenario drifts `util/Seeder/README.md` and `Seeds/schemas/cipher.schema.json`, and the case now grades report shape.

### Notes

- Re-recorded the behavior baseline (`skills/verifying-doc-parity/evals/behavior-baseline.json`) against the updated expectations: 3 runs per case per configuration, with-skill pass rate 98% vs. 63% without the skill.

## [1.0.1] - 2026-10-12

### Changed

- README Layer 4 no longer says `bitwarden-code-review` integration is planned, since `bitwarden-code-review` 2.4.0 now implements it.

## [1.0.0] - 2026-08-04

### Added

- Initial release of the `bitwarden-doc-parity` plugin, enforcing the documentation standard's base obligations to monitor for drift between code and documentation. Operates within-repo only when fired as a stop-hook and includes out-of-repo validation against contributing-docs when being executed in a PR review.
- Behavior evals for `verifying-doc-parity` against the bitwarden/server Seeder subsystem as the first ground-truth corpus.
