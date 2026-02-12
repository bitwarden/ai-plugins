# Changelog

All notable changes to the `bitwarden-security-engineer` plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-12

### Added

- `bitwarden-security-engineer` agent for coordinating security engineering tasks
- `triaging-security-findings` skill for Checkmarx, SonarCloud, and Grype findings triage via GitHub Advanced Security API
- `threat-modeling` skill for STRIDE-based threat modeling with Bitwarden's engagement model and security definitions
- `analyzing-code-security` skill for code analysis against OWASP Top 10, API Top 10, Mobile Top 10, and CWE Top 25
- `reviewing-dependencies` skill for supply chain security, Dependabot triage, and dependency governance
- `detecting-secrets` skill for hardcoded credential detection, secret scanning, and remediation workflows
- `reviewing-security-architecture` skill for authentication, authorization, encryption, and trust boundary review
