---
name: triaging-security-findings
description: This skill should be used when the user asks to "triage security findings", "fix a Checkmarx finding", "review SonarCloud results", "dismiss a false positive", "check code scanning alerts", or needs to work with GitHub Advanced Security alerts, scanner annotations on PRs, or Grype vulnerability results.
---

## Scanner Landscape

Bitwarden uses three scanners, all triggered by the `scan.yml` GitHub Actions workflow in each repository:

**Checkmarx One** — SAST (static analysis) and IaC (infrastructure as code) scanning. Dedicated cloud tenant named "bitwarden". Results upload to GitHub Advanced Security via SARIF format and post as PR annotations. Checkmarx understands branch differences, so PR results show only what changed. Access the Checkmarx webapp at the AST WebApp (tenant: "bitwarden") or via the Workspace Directory.

**SonarCloud** — Quality and security hotspot scanning. Free public cloud offering (not licensed for private repos). Uses quality profiles and gates for customized results. Posts PR annotations. Results also propagate to GitHub's security section. Configure via `sonar-config` input: `default`, `dotnet`, or `maven`.

**Grype** — Container image and filesystem vulnerability scanner. CVE-focused. Used for supply chain and dependency vulnerability detection.

## GitHub Advanced Security API

Use these `gh api` commands to query and manage security findings:

### Code Scanning Alerts (Checkmarx, SonarCloud)

```bash
# List all open code scanning alerts
gh api /repos/{owner}/{repo}/code-scanning/alerts --jq '.[] | {number, state, rule: .rule.id, severity: .rule.security_severity_level, path: .most_recent_instance.location.path}'

# Get details for a specific alert
gh api /repos/{owner}/{repo}/code-scanning/alerts/{alert_number}

# Filter alerts by path (useful for file-specific triage)
gh api "/repos/{owner}/{repo}/code-scanning/alerts?ref={branch}&state=open" --jq '.[] | select(.most_recent_instance.location.path | startswith("src/Api"))'

# Filter by tool (separate Checkmarx from SonarCloud results)
gh api "/repos/{owner}/{repo}/code-scanning/alerts?tool_name=Checkmarx&state=open"
gh api "/repos/{owner}/{repo}/code-scanning/alerts?tool_name=SonarQube&state=open"

# Dismiss an alert as false positive
gh api -X PATCH /repos/{owner}/{repo}/code-scanning/alerts/{alert_number} \
  -f state=dismissed \
  -f dismissed_reason=false\ positive \
  -f dismissed_comment="Rationale for dismissal"

# Dismiss as won't fix
gh api -X PATCH /repos/{owner}/{repo}/code-scanning/alerts/{alert_number} \
  -f state=dismissed \
  -f dismissed_reason=won\'t\ fix \
  -f dismissed_comment="Rationale"
```

### Dependabot Alerts

```bash
# List open Dependabot alerts
gh api /repos/{owner}/{repo}/dependabot/alerts --jq '.[] | {number, state, severity: .security_vulnerability.severity, package: .security_vulnerability.package.name, ecosystem: .security_vulnerability.package.ecosystem}'

# Get specific alert details
gh api /repos/{owner}/{repo}/dependabot/alerts/{alert_number}
```

### Secret Scanning Alerts

```bash
# List secret scanning alerts
gh api /repos/{owner}/{repo}/secret-scanning/alerts --jq '.[] | {number, state, secret_type, created_at}'
```

## Checkmarx Finding States

These are the states available in Checkmarx for managing findings. Getting the state right matters — it affects whether the finding reappears in future scans.

| State                        | When to Use                                                                | Effect                                                    |
| ---------------------------- | -------------------------------------------------------------------------- | --------------------------------------------------------- |
| **Not Exploitable**          | CERTAIN there is no potential risk at ANY point in the product's lifecycle | Finding stops appearing in subsequent scans               |
| **Proposed Not Exploitable** | Suspected false positive, needs team verification                          | Flags for review; requires manager approval for promotion |
| **Confirmed**                | Vulnerability poses a real risk to be addressed during development         | Tracked as known issue                                    |
| **Urgent**                   | Acute risk requiring immediate attention                                   | Escalated priority                                        |

### Critical Rules for State Changes

- **Never mark as Not Exploitable** just because the app isn't in production yet, or because it's currently on a local server. Consider the full product lifecycle — if deploying to cloud or going to production would make it exploitable, it IS exploitable.
- **Validation is not sufficient.** Checkmarx does not consider adding validation steps as a foolproof solution because they leave threatening input values in place. Sanitizers (which replace threatening values) are preferred. Do not mark a finding as Not Exploitable solely on the basis of a validation step.
- **When uncertain, use Proposed Not Exploitable** and discuss with the team or #team-eng-appsec.
- **Document the rationale** — every state change should include a clear explanation of why.

## SonarCloud Finding Management

SonarCloud categorizes findings as **issues** (code quality and bugs) and **security hotspots** (code that needs manual security review).

- Issues have severity levels and can be resolved, confirmed, or marked as won't fix
- Security hotspots require review to determine if they are actually vulnerable
- Quality gates enforce thresholds — a failing quality gate blocks the PR
- Results depend on the base branch quality; until initial triage is complete, PR results may be noisy

## False Positive Protocol

Before dismissing any finding, follow this decision tree:

1. **Trace the data flow.** Can untrusted input actually reach the flagged sink? Follow the data from entry point through all transformations to the flagged location.
2. **Check for existing sanitization.** Is there encoding, escaping, or sanitization in the data path? Remember: validation alone is insufficient for Checkmarx findings.
3. **Consider the full lifecycle.** Even if the code isn't deployed to a risky environment today, will it be? Private repos may go public. Local deployments may move to cloud.
4. **Document the rationale.** Every dismissal must include a clear, reviewable explanation of why the finding is not exploitable.

If any step is uncertain, mark as **Proposed Not Exploitable** rather than **Not Exploitable**.

## Fix Implementation Patterns

Common remediation patterns by vulnerability type:

| Vulnerability            | Wrong                                        | Right                                              |
| ------------------------ | -------------------------------------------- | -------------------------------------------------- |
| SQL Injection            | String concatenation in queries              | Parameterized queries / stored procedures          |
| XSS                      | Raw interpolation in HTML                    | Output encoding / framework auto-escaping          |
| Path Traversal           | Direct use of user-supplied paths            | Canonicalize + validate against allowed base path  |
| SSRF                     | Direct use of user-supplied URLs             | Allowlist of permitted hosts/schemes               |
| Insecure Deserialization | Deserializing untrusted input with type info | Use safe serializers, avoid `TypeNameHandling.All` |
| Hardcoded Secrets        | Credentials in source code                   | Environment variables / Azure Key Vault            |
| XXE                      | Default XML parser settings                  | Disable DTD processing and external entities       |

## Private Repository Notes

- **SARIF upload** to GitHub Advanced Security will fail for private repos (GitHub billing limitation). Disable by passing `upload-sarif: false` to the Checkmarx reusable workflow.
- **SonarCloud** is not licensed for private repos. Remove the `quality` job from `scan.yml` entirely for private repos.
- When a private repo goes public, re-enable both.

## Further Reading

- [Checkmarx Triage Documentation](https://docs.checkmarx.com/)
- [SonarCloud Documentation](https://docs.sonarsource.com/sonarqube-cloud/)
- [GitHub Code Scanning API](https://docs.github.com/en/rest/code-scanning)
- [GitHub Dependabot API](https://docs.github.com/en/rest/dependabot)
