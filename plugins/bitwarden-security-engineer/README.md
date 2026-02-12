# Bitwarden Security Engineer Plugin

Claude Code skills for application security at Bitwarden. Generic AI coding assistance doesn't know our scanner toolchain, triage workflows, or threat modeling practices. These skills keep Claude focused on how we secure software here.

## Skills

| Skill                             | What It Does                                                                                                                                                |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `triaging-security-findings`      | Triage Checkmarx, SonarCloud, and Grype findings via GitHub Advanced Security API. Includes finding state rules, false positive protocol, and fix patterns. |
| `threat-modeling`                 | Generate security definitions, data flow diagrams, and threat catalogs using STRIDE. Follows Bitwarden's 4-phase AppSec engagement model.                   |
| `analyzing-code-security`         | Security code review against OWASP Web/API/Mobile Top 10, CWE Top 25. Step-by-step review workflow with adversarial mindset guidance.                       |
| `reviewing-dependencies`          | Dependabot triage, Grype scanning, transitive dependency risk analysis. NuGet and npm platform-specific guidance.                                           |
| `detecting-secrets`               | Hardcoded credential detection with context-aware analysis. GitHub secret scanning integration, Azure Key Vault remediation.                                |
| `reviewing-security-architecture` | Architecture-level review for authentication, authorization, encryption, trust boundaries, and cryptographic patterns.                                      |

## Usage

Install the plugin and invoke the agent:

```
Use the bitwarden-security-engineer agent to triage the open Checkmarx findings on this PR.
```

```
Use the bitwarden-security-engineer agent to create a threat model for the new Send feature.
```

```
Use the bitwarden-security-engineer agent to review this code for OWASP Top 10 vulnerabilities.
```
