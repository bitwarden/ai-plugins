# Changelog

All notable changes to the bitwarden-devops-engineer plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-08-17

### Added

- New `managing-workflow-secrets` reference and authoring skill documenting Bitwarden's Azure Key Vault (AKV) + OIDC secret pattern for GitHub Actions workflows. Covers the `azure-login` → `get-keyvault-secrets` → `azure-logout` lifecycle via the centralized `bitwarden/gh-actions` composite actions, the golden invariants (internal actions on `@main` while third-party actions are SHA-pinned, `id-token: write` on any logging-in job, matched login/logout conditions), the house conventions for the retrieval step (`id: secrets`, a folded block scalar for three or more secrets), an authoring procedure, and a secret-hygiene checklist (step-scoped `env:` consumption, no logging, retrieve only what the job uses). Treats preventing secret exposure as the overriding priority: a "Secret exposure is the overriding concern" gate requires every edit, fix, or suggestion to be evaluated against the hygiene checklist before it is offered. The Key Vault name and secret names are always provided per task and never inferred from the repository or workflow content — the skill uses the placeholders `KEY-VAULT` and `SECRET-NAME-1`/`SECRET-NAME-2` and flags to the user when a real name is unknown. Explains how a secret reaches beyond the job that retrieved it — same-job step outputs, per-job re-retrieval, a short-lived GitHub App token minted from AKV, and reusable-workflow credential hand-off as a two-sided change (`secrets: inherit` same-repo vs explicit `secrets:` cross-repo, matched to the callee's `on.workflow_call.secrets:` declarations with `id-token: write` on each logging-in job) — while never passing a raw value through a job `outputs:`, since the runner redacts masked values out of job outputs and the value arrives empty downstream. Advanced patterns (fork-PR access gates, multiple vaults in one job, dynamic identity selection, matrix logins, and raw `az` CLI for certificates and secret write-back) are out of scope. Ships one reference, `references/actions.md` (input/output contracts for the three actions, the OIDC client-identity conventions, and how vault and secret names are supplied). Defers to `bitwarden-workflow-linter-rules` for all linted rules. Listed in the plugin README alongside the existing reference skills.

## [0.2.0] - 2026-08-10

### Added

- New `auditing-workflow-conventions` reference skill documenting the GitHub Actions naming standards `bwwl` does not enforce: job IDs (`kebab-case`), step names (Sentence case with a leading imperative verb), and workflow file names (`kebab-case.yml`, `_` prefix for exclusively reusable workflows). Includes an ownership table that defers to `bitwarden-workflow-linter-rules` for every linted rule so findings are not double-reported, reference-sweep procedures for the two rename types that are not display-only, and an advisory canonical step-name glossary. Listed in the plugin README alongside the existing linter-rules reference.

## [0.1.5] - 2026-07-28

### Changed

- Added `Overview` and `Usage` sections to the plugin README. The Overview documents the paired audit → remediation skill structure and the shared linter-rules reference, matching the structure used by sibling plugin READMEs and clearing both `validate-plugin-structure.sh` content warnings. No skill behavior changed.

## [0.1.4] - 2026-06-23

### Security

- Removed the `Bash(git add .github/:*)`, `Bash(git commit:*)`, and `Bash(git push:*)` permissions from the `action-remediate` and `workflow-fix` skills so these mutating git operations are run manually by the user instead of auto-approved. The skills now present the commands and resume to create the draft PR after the user confirms the push. Read-only `git diff`/`git status`, branch setup via `git checkout`, and `gh pr create` are retained.

## [0.1.3] - 2026-05-08

### Changed

- Updated `action-audit` skill to apply Bitwarden's two-tier pin compliance model: internal `bitwarden/` actions must be pinned to `@main`; third-party actions must be pinned to a full 40-char SHA with an inline version comment. Previously the skill treated all non-hash refs as non-compliant, which incorrectly flagged valid internal action references.

### Fixed

- Updated `bitwarden-workflow-linter-rules` skill to correctly document the `step_pinned` rule with its two-tier model: internal `bitwarden/` actions must pin to `@main` (with a `bitwarden/sm-action` exception that allows any ref), external actions must pin to a full 40-char SHA with an inline version comment. Previously the rule described `@main` as non-compliant, contradicting `action-audit`.
- Updated `action-audit` skill to reference `bitwarden-workflow-linter-rules` as the single source of truth via `${CLAUDE_PLUGIN_ROOT}` path, eliminating both cross-skill drift and a runtime path-resolution failure in marketplace deployments.
- Updated `action-audit` skill to restore the incident mode replacement-action branch in Step 4, which was incorrectly dropped — a compromised-action response that names a replacement now routes to SHA resolution for the replacement rather than the compromised action.
- Updated `action-audit` skill to treat SHA-pinned internal actions as informational rather than non-compliant, requiring user confirmation before recommending a change to `@main`.
- Updated `action-remediate` skill to add a **pin to main** remediation path for internal `bitwarden/` actions, closing a gap where following the documented audit→remediate flow would incorrectly SHA-pin internal actions.

## [0.1.1] - 2026-04-15

### Changed

- Apply prettier formatting to markdown files

## [0.1.0] - 2026-04-14

### Added

- Initial release of the bitwarden-devops-engineer plugin
- Workflow linting audit and fix skills
- Org-wide GitHub Actions action usage auditing and remediation skills
- Linter rules reference covering all 10 bwwl rules
