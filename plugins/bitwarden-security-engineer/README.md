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

## References

External resources that informed each skill. Useful for maintainers updating skill content when upstream sources change.

### threat-modeling

- [Security Definitions](https://contributing.bitwarden.com/architecture/security/definitions) — Official vocabulary and terminology
- [Security Principles](https://contributing.bitwarden.com/architecture/security/principles/) — P01-P06 foundation principles
- [Security Requirements](https://contributing.bitwarden.com/architecture/security/requirements) — VD/EK/AT/SC/TC requirement categories
- [Threat Modeling Manifesto](https://www.threatmodelingmanifesto.org/)
- [Threat Modeling Guide for Software Teams](https://martinfowler.com/articles/agile-threat-modelling.html)
- [OWASP Threat Modeling Process](https://owasp.org/www-community/Threat_Modeling_Process)

### triaging-security-findings

- [Checkmarx Triage Documentation](https://docs.checkmarx.com/)
- [SonarCloud Documentation](https://docs.sonarsource.com/sonarqube-cloud/)
- [GitHub Code Scanning API](https://docs.github.com/en/rest/code-scanning)
- [GitHub Dependabot API](https://docs.github.com/en/rest/dependabot)

### analyzing-code-security

- [OWASP Top Ten](https://owasp.org/www-project-top-ten/)
- [OWASP API Security Top 10](https://owasp.org/API-Security/editions/2023/en/0x11-t10/)
- [OWASP Mobile Top 10 2024](https://owasp.org/www-project-mobile-top-10/)
- [CWE Top 25 Most Dangerous Software Weaknesses](https://cwe.mitre.org/top25/archive/2024/2024_cwe_top25.html)
- [OWASP Code Review Guide](https://owasp.org/www-project-code-review-guide/)

### reviewing-dependencies

- [GitHub Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
- [Grype GitHub Repository](https://github.com/anchore/grype)
- [OWASP Dependency-Check](https://owasp.org/www-project-dependency-check/)
- [npm Security Best Practices](https://docs.npmjs.com/packages-and-modules/securing-your-code)

### detecting-secrets

- [GitHub Secret Scanning Documentation](https://docs.github.com/en/code-security/secret-scanning)
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [git-filter-repo Documentation](https://github.com/newren/git-filter-repo)

### reviewing-security-architecture

- [OWASP Application Security Verification Standard (ASVS)](https://owasp.org/www-project-application-security-verification-standard/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [Bitwarden Security Whitepaper](https://bitwarden.com/help/bitwarden-security-white-paper/)
- [NIST Cryptographic Standards](https://csrc.nist.gov/projects/cryptographic-standards-and-guidelines)
