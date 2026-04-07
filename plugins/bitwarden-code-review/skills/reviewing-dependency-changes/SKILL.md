---
name: reviewing-dependency-changes
description: Use this skill when a PR diff contains changes to dependency manifest files (package.json, .csproj, Cargo.toml, go.mod, requirements.txt, etc.) or when reviewing Renovate/Dependabot bot PRs. Evaluates new dependencies for AppSec approval process compliance, major version bump significance, lock file hygiene, and dependency removal completeness. Does NOT perform deep security or license analysis — that is handled by the bitwarden-security-engineer plugin's reviewing-dependencies skill.
---

# Reviewing Dependency Changes

## Manifest File Detection

Flag this skill when any of these files appear in the diff:

- `package.json`, `package-lock.json`
- `*.csproj`, `Directory.Packages.props`, `packages.lock.json`
- `Cargo.toml`, `Cargo.lock`
- `go.mod`, `go.sum`
- `requirements.txt`, `pyproject.toml`, `poetry.lock`
- `Gemfile`, `Gemfile.lock`

## Area 1: New Dependencies

When a PR adds a dependency that was not previously in the codebase, Bitwarden's Dependency Review and Approval process requires AppSec review and approval before integration. This applies to **all** new dependencies — production, dev, and test.

The submitter must provide the package name/version, ecosystem, justification, scope, affected products, and what it replaces. A security engineer creates a VULN task in Jira and evaluates the dependency across security (known CVEs, exploitability), license compatibility (permissive licenses like MIT/Apache-2.0 are acceptable; copyleft licenses like GPL/AGPL are flagged), maintenance health (active maintainers, recent releases, security policy), supply chain risk (typosquatting, ownership changes, obfuscated install scripts), and transitive dependencies before rendering an approval decision.

### What to Check

1. Is this a **net-new** dependency (not already present in the codebase)?
2. Does the PR description contain an **approval signal** indicating the process was followed?

### Approval Signals

Evidence that the dependency approval process was followed:

- PR description references a **VULN task** (e.g., `VULN-1234`)
- PR description explicitly mentions **AppSec approval** or the dependency review process

### Severity

- **No approval signal found** → ⚠️ **IMPORTANT**: New dependency `<package>` added. Bitwarden requires AppSec approval before introducing new dependencies. The submitter should reach out to the AppSec team to initiate the dependency review and approval process.
- **Unclear whether approval was obtained** → ❓ **QUESTION**: Was AppSec approval obtained for the new `<package>` dependency?

### What NOT to Flag

- Dependencies that already exist in the codebase (version updates are not new dependencies)
- Dependencies added by Renovate/Dependabot as transitive dependency updates (these are part of Stage 5 monitoring for existing approved dependencies)

## Area 2: Major Version Bumps

A major version bump (e.g., v2 → v3) may introduce breaking changes that affect Bitwarden's codebase.

### What to Check

1. Is this a **SemVer major** version change?
2. Does the PR description discuss **breaking changes** or **migration steps**?

### Severity

- Major bump without migration discussion → ❓ **QUESTION**: This bumps `<package>` from v`X` to v`Y` (major). Were breaking changes evaluated?
- Version downgrade → ⚠️ **IMPORTANT**: `<package>` is being downgraded from v`X` to v`Y`. This is unusual and may reintroduce resolved vulnerabilities.

## Area 3: Lock File Hygiene

Lock files ensure reproducible builds. Inconsistencies between manifests and lock files are a build reliability and security concern.

### What to Check

| Scenario                                | Finding                                                                                                                    |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Manifest changed, lock file not updated | ⚠️ **IMPORTANT**: Lock file not updated to reflect manifest changes                                                        |
| Lock file changed, no manifest change   | ❓ **QUESTION**: Lock file changed without a corresponding manifest change — was this intentional (e.g., `npm audit fix`)? |
| Lock file deleted                       | ⚠️ **IMPORTANT**: Lock file removal breaks reproducible builds                                                             |

### What NOT to Flag

- Large lock file diffs from a small manifest change — this is normal behavior. Lock files can change significantly from a single dependency addition or version bump.
- Lock file-only changes that accompany a clear manifest change in the same PR.

## Area 4: Automated Dependency PRs

Renovate and Dependabot PRs are part of Bitwarden's Stage 5 (Monitoring) process. These automated updates to **existing** approved dependencies require different review treatment.

### How to Detect

- PR author: `renovate[bot]`, `dependabot[bot]`, or similar bot accounts
- PR title pattern: "Update ...", "Bump ...", "chore(deps): ..."

### Review Guidance

| Scenario                                  | Action                                                                                |
| ----------------------------------------- | ------------------------------------------------------------------------------------- |
| Minor/patch update to existing dependency | No approval-process finding needed. Focus on lock file hygiene and CI status.         |
| Major version bump from bot               | Flag per Area 2 — major bumps warrant human review regardless of source.              |
| Bot PR introduces a net-new dependency    | Flag per Area 1 — new dependencies require the approval process regardless of source. |

## Area 5: Dependency Removal

When a dependency is removed from a manifest, verify the removal is complete.

### What to Check

1. Are there remaining code references to the removed package?
   - **JavaScript/TypeScript**: `import ... from '<package>'`, `require('<package>')`
   - **C#/.NET**: `using <namespace>`, references in other `.csproj` files
   - **Rust**: `use <crate>::`, `extern crate <crate>`
   - **Python**: `import <package>`, `from <package> import`
2. Are there references in build or infrastructure files?
   - `Dockerfile`, `docker-compose.yml`
   - CI workflow files (`.github/workflows/*.yml`)
   - Build scripts, `Makefile`, task runners

### Severity

- Dead imports or references remain → ♻️ **DEBT**: `<package>` removed from manifest but still referenced in code.
