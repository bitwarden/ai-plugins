# Changelog

All notable changes to the `bitwarden-security-engineer` plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2026-05-05

### Changed

- `threat-modeling` skill: revised based on AppSec review feedback on a real-world generated security definition document. Changes address noise, mis-scoped attacker assumptions, and missing rationale that surfaced when the skill was used to produce SDs for an unlock-flow feature.
  - Skill now requires every Security Goal to carry a **Rationale** (principle → asset → user-visible harm); goals without rationale are treated as claims, not requirements.
  - New guidance to prune **Dominated Threats** (SDs whose residual risk collapses to an already out-of-scope higher-privilege threat) and to add **Passive Observer** SDs wherever secrets cross into external services (LLM providers, log aggregators, analytics, training pipelines).
  - New rule to reality-check goals against runtime — "cleared from memory" / "zeroized" / "not retained" are flagged as unenforceable in GC'd, string-interned runtimes (JavaScript, .NET, JVM, Python).
  - New rule to prefer stdin or file-descriptor handoff over env/argv when a goal forbids secret exposure to `process.env` or `argv`.
  - New rule to verify "attacker does not have X" limitations against every supported OS (common pitfall: assuming kernel privileges are required for reading another process's environment).
  - Accepted Goal Status rationales of "brief" or "short-lived" now require a quantified **Exposure Window**.
  - Each SD must carry a **Criticality** tag (Critical / High / Medium / Low) and the document must be ordered by Criticality descending.

### Added

- `references/writing-quality-sds.md`: six named anti-patterns (dominated threat, adversarial-only attacker, unenforceable goal, aspirational limitation, shell-quoting SD, "brief exposure" trap), a prioritization heuristic, and a five-question self-consistency checklist.
- `references/bitwarden-vocabulary.md`: added **Passive Observer**, **Dominated Threat**, and **Exposure Window** to the standard terminology.
- `examples/security-definition-document.md`: template extended with **Criticality** field per SD, **Rationale** line per Security Goal, and a quantified-exposure-window reminder for accepted status.

## [1.0.1] - 2026-04-08

### Changed

- Simplified credential-storage and encryption-at-rest guidance in `reviewing-security-architecture` skill.

## [1.0.0] - 2026-03-18

### Added

- Raising to version 1.0.0 because we are implementing a skill that leverages the skills and agents in the plugin to strengthen our security posture.
- `perform-security-review` skill: performs a multi-agent security code review with 4 specialized agents (code security, secrets & dependencies, security architecture, threat perspective), two-axis Severity × Confidence scoring, GitHub Advanced Security scan evidence gathering, and flexible output routing (chat, local file, or GitHub Actions workflow); supports `--output-dir <path>` for report placement
- `references/security-review-rubric.md`: OWASP Top 10 2025 checklist, severity × confidence threshold table, and Bitwarden-specific security invariants for agent grounding; includes security researcher framing in agent prompts and explicit P05 coverage for user-joined organization access paths

## [0.2.0] - 2026-02-23

### Added

- `bitwarden-security-context` skill: lightweight quick-reference for security principles (P01-P06), vocabulary, and data classification standards
- Cross-plugin skill awareness: agent now invokes software engineer skills (`writing-server-code`, `writing-database-queries`, `writing-client-code`) to ground remediation recommendations in Bitwarden's actual conventions when the `bitwarden-software-engineer` plugin is installed alongside

## [0.1.0] - 2026-02-12

### Added

- `bitwarden-security-engineer` agent for coordinating security engineering tasks
- `triaging-security-findings` skill for Checkmarx, SonarCloud, and Grype findings triage via GitHub Advanced Security API
- `threat-modeling` skill for STRIDE-based threat modeling with Bitwarden's engagement model and security definitions
- `analyzing-code-security` skill for code analysis against OWASP Top 10, API Top 10, Mobile Top 10, and CWE Top 25
- `reviewing-dependencies` skill for supply chain security, Dependabot triage, and dependency governance
- `detecting-secrets` skill for hardcoded credential detection, secret scanning, and remediation workflows
- `reviewing-security-architecture` skill for authentication, authorization, encryption, and trust boundary review
