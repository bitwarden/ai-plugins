---
name: reviewing-dependencies
description: This skill should be used when the user asks to "review Dependabot alerts", "check for vulnerable dependencies", "audit third-party packages", "assess supply chain risk", "run Grype scan", or needs to evaluate dependency health, transitive risk, or supply chain security.
---

## Dependency Vulnerability Workflow

### Step 1: Gather Alerts

```bash
# List all open Dependabot alerts sorted by severity
gh api /repos/{owner}/{repo}/dependabot/alerts --jq '.[] | select(.state == "open") | {number, severity: .security_vulnerability.severity, package: .security_vulnerability.package.name, ecosystem: .security_vulnerability.package.ecosystem, summary: .security_advisory.summary}'

# Filter by severity
gh api "/repos/{owner}/{repo}/dependabot/alerts?severity=critical&state=open"

# Get full details for a specific alert
gh api /repos/{owner}/{repo}/dependabot/alerts/{alert_number}
```

### Step 2: Assess Impact

For each alert, determine:

1. **Is the vulnerable code path reachable?** — Does the application actually use the vulnerable function/feature of the dependency?
2. **Is it a direct or transitive dependency?** — Transitive vulnerabilities may be harder to fix but still pose real risk.
3. **What is the CVSS score and exploit availability?** — A high CVSS with a public exploit needs immediate action. A medium CVSS with no known exploit can be scheduled.
4. **What versions are affected and what versions fix it?** — Check if updating is a minor bump or a breaking change.

### Step 3: Decide on Action

| Situation                                 | Action                                         |
| ----------------------------------------- | ---------------------------------------------- |
| Fix available, minor version bump         | Update immediately                             |
| Fix available, major version bump         | Evaluate breaking changes, schedule update     |
| No fix available, code path reachable     | Implement workaround or replace dependency     |
| No fix available, code path not reachable | Document and monitor, set review date          |
| Vulnerability in transitive dependency    | Use overrides/resolutions to pin fixed version |

## Transitive Dependency Risk

Direct dependencies are visible in `package.json` or `.csproj` files, but transitive dependencies (dependencies of dependencies) make up the majority of the dependency tree and are often invisible.

**Why transitive dependencies matter:**

- A vulnerability in a deeply nested dependency is just as exploitable as one in a direct dependency
- Transitive dependencies are less likely to be actively monitored
- Updating a transitive dependency may require updating the direct dependency that pulls it in

**How to investigate:**

```bash
# npm: Show full dependency tree
npm ls --all

# npm: Find which direct dependency pulls in a vulnerable transitive
npm ls <vulnerable-package>

# .NET: List all vulnerable packages including transitive
dotnet list package --vulnerable --include-transitive

# .NET: Show dependency graph
dotnet list package --include-transitive
```

## Dependency Health Evaluation

When evaluating whether to adopt or keep a dependency, assess:

| Criterion                 | Green Flag                                | Red Flag                                     |
| ------------------------- | ----------------------------------------- | -------------------------------------------- |
| **Maintenance**           | Regular commits, responsive to issues     | No commits in 12+ months, unresponded issues |
| **Vulnerability History** | Few CVEs, quick patches                   | Repeated CVEs, slow response                 |
| **Maintainer Count**      | Multiple active maintainers               | Single maintainer, bus factor of 1           |
| **Community**             | High download count, active users         | Very low adoption for claimed scope          |
| **License**               | Compatible with project (MIT, Apache-2.0) | Restrictive or ambiguous license             |
| **Security Practices**    | Signed releases, security policy, 2FA     | No security policy, no signed releases       |

## Grype Integration

Grype scans container images and filesystems for known vulnerabilities:

```bash
# Scan a container image
grype <image>:<tag>

# Scan a directory
grype dir:/path/to/project

# Output as JSON for programmatic processing
grype <image> -o json

# Filter by severity
grype <image> --only-fixed --fail-on high
```

**Interpreting Grype output:**

- Each finding includes: CVE ID, severity, package name, installed version, fixed version
- `Fixed` column indicates whether an update is available
- Use `--only-fixed` to focus on actionable items (vulnerabilities with available fixes)

## Platform-Specific Guidance

### NuGet (.NET)

```bash
# Check for vulnerable packages
dotnet list package --vulnerable

# Include transitive dependencies
dotnet list package --vulnerable --include-transitive

# Check for outdated packages
dotnet list package --outdated
```

**NuGet-specific concerns:**

- .NET framework packages may have different vulnerability profiles than .NET Core
- `PackageReference` in `.csproj` is preferred over `packages.config` for better transitive resolution
- Use `Directory.Packages.props` for centralized version management in multi-project solutions

### npm (Node.js)

```bash
# Run security audit
npm audit

# Auto-fix where possible
npm audit fix

# Force fixes (may introduce breaking changes)
npm audit fix --force

# Check lockfile integrity
npm ci  # Installs exactly from lockfile, fails if lockfile is out of date
```

**npm-specific concerns:**

- `package-lock.json` must be committed and kept in sync
- Use `overrides` in `package.json` to force transitive dependency versions:
  ```json
  {
    "overrides": {
      "vulnerable-package": ">=2.0.0"
    }
  }
  ```
- Beware of `postinstall` scripts in dependencies — they execute arbitrary code during `npm install`

## SBOM Concepts

A Software Bill of Materials (SBOM) is an inventory of all components in a software artifact. Understanding SBOMs helps reason about supply chain risk:

- **What it contains:** Package names, versions, licenses, relationships (direct vs. transitive)
- **Why it matters:** Enables rapid response when a new CVE is published — immediately identify which projects are affected
- **Standard formats:** SPDX, CycloneDX
- **GitHub integration:** GitHub generates dependency graphs automatically; Dependabot uses this for alerting

## Critical Rules

- **Never ignore critical/high Dependabot alerts** without documented justification. Even if the vulnerable code path seems unreachable, document why.
- **Prefer updating over pinning.** Pinning a vulnerable version and adding a workaround accumulates tech debt. Update when a fix is available.
- **Evaluate the full transitive tree.** A direct dependency may be safe, but its transitive dependencies may not be.
- **Review new dependencies before adoption.** Check health criteria above before adding any new package. More dependencies = more attack surface.
- **Lock dependencies.** Always commit lockfiles (`package-lock.json`, `packages.lock.json`). Use `npm ci` in CI/CD, not `npm install`.

## Further Reading

- [GitHub Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
- [Grype GitHub Repository](https://github.com/anchore/grype)
- [OWASP Dependency-Check](https://owasp.org/www-project-dependency-check/)
- [npm Security Best Practices](https://docs.npmjs.com/packages-and-modules/securing-your-code)
