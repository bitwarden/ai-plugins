---
name: reviewing-dependencies
description: This skill should be used when the user asks to "review Dependabot alerts", "check for vulnerable dependencies", "audit third-party packages", "assess supply chain risk", "run Grype scan", or needs to evaluate dependency health, transitive risk, or supply chain security.
---

## Dependency Vulnerability Workflow

### Step 1: Gather Alerts

```bash
# List ALL open Dependabot alerts, sorted by severity. Notes on why this is
# shaped the way it is — each of these is a trap worth avoiding:
#   - --paginate is required: a single page caps at 100 and silently drops the
#     rest. Page order is not severity-ranked, so a critical can be on page 2.
#   - --slurp merges pages into one array so the sort is global, not per-page.
#     gh rejects --slurp together with --jq, so pipe to jq instead.
#   - The API cannot sort by severity (sort= takes only created, updated,
#     epss_percentage), so sort in jq.
#   - scope tells you development (build/CI only) vs runtime (ships to users).
#     This usually decides the triage outcome — see Step 2 and Step 3.
#   - cvss_v3.score returns 0 rather than null when an advisory carries no v3
#     vector, so it is guarded; unguarded it reads 0 on high-severity findings.
gh api --paginate --slurp "/repos/{owner}/{repo}/dependabot/alerts?state=open&per_page=100" \
| jq '
  [ .[][]
    | (.security_advisory.cvss_severities // {}) as $c
    | { number,
        severity: .security_vulnerability.severity,
        package: .dependency.package.name,
        ecosystem: .dependency.package.ecosystem,
        scope: .dependency.scope,
        manifest: .dependency.manifest_path,
        vulnerable_range: .security_vulnerability.vulnerable_version_range,
        first_patched: .security_vulnerability.first_patched_version.identifier,
        cvss_v3_vector: $c.cvss_v3.vector_string,
        cvss_v3_score: (if $c.cvss_v3.vector_string then $c.cvss_v3.score else null end),
        cvss_v4_vector: $c.cvss_v4.vector_string,
        summary: .security_advisory.summary }
  ]
  | sort_by({ critical: 0, high: 1, medium: 2, low: 3 }[.severity])
  | .[]'

# Filter by severity
gh api "/repos/{owner}/{repo}/dependabot/alerts?severity=critical&state=open"

# Get full details for a specific alert
gh api /repos/{owner}/{repo}/dependabot/alerts/{alert_number}
```

### Step 2: Assess Impact

For each alert, determine:

1. **Does the dependency ship, or is it build-time only?** — Start here; it usually decides the outcome. `scope` on the alert reports `development` or `runtime`. Treat `development` as a strong signal, not proof: confirm the package is absent from every shipped artifact (extension, desktop, web vault, CLI, server image) before relying on it, because some build-time packages inline code into published output. A build-time-only package has no live process in production for an attacker to reach.
2. **Is the vulnerable code path reachable?** — Does the application actually use the vulnerable function/feature of the dependency?
3. **Is it a direct or transitive dependency?** — Transitive vulnerabilities may be harder to fix but still pose real risk. Identify the parent that pins it (`npm ls <package>`), because when a parent pins a vulnerable version the fix may not be available to you directly.
4. **What is the CVSS score and exploit availability?** — Score in **CVSS v3.0**, Bitwarden's standard for reporting and triage of vulnerabilities. GitHub publishes v3.1 vectors for recent advisories (v3.0 appears only on older imported CVEs), so transcribe `cvss_severities.cvss_v3.vector_string` into a v3.0 calculator — v3.0 and v3.1 share the same base metrics, so the vector maps directly. Some advisories carry a v4.0 vector only, or no vector at all; v4.0 metrics do not map onto v3.0, so score those by hand from the advisory details rather than reusing the v4.0 number. A high CVSS with a public exploit needs immediate action. A medium CVSS with no known exploit can be scheduled.
5. **What versions are affected and what versions fix it?** — `vulnerable_range` and `first_patched` on the alert give both. Check whether reaching `first_patched` is a minor bump, a breaking change, or blocked behind a parent package that pins the vulnerable version.

### Step 3: Decide on Action

Resolve scope first. A package that never reaches a shipped artifact cannot be attacked in production, and treating it as though it can produces pointless urgency and risky churn.

| Scope                                                                    | Action                                                                                                                                                                                  |
| ------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `development`, confirmed absent from every shipped artifact              | Declare **Not Affected / Informational**. Record the reachability reasoning explicitly, then track the bump with the next routine upgrade of the parent tooling rather than as a hotfix |
| `development`, but the package or its output lands in a shipped artifact | Treat as `runtime` and use the table below                                                                                                                                              |
| `runtime`                                                                | Use the table below                                                                                                                                                                     |

A `development` finding still needs the declaration written down. "It's a devDependency" is not by itself an assessment — state which artifacts were checked and why the code path cannot be reached in production.

For `runtime` findings, and for `development` findings that turned out to ship:

| Situation                                            | Action                                                                                                                                                                                            |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Fix available, minor version bump                    | Update immediately                                                                                                                                                                                |
| Fix available, major version bump                    | Evaluate breaking changes, schedule update                                                                                                                                                        |
| No fix available, code path reachable                | Implement workaround or replace dependency                                                                                                                                                        |
| No fix available, code path not reachable            | Document and monitor, set review date                                                                                                                                                             |
| Transitive, and the fixed version is installable     | Use overrides/resolutions to pin the fixed version                                                                                                                                                |
| Transitive, but a parent pins the vulnerable version | Overriding the parent's pin can break it. Prefer waiting for a parent release that bumps its own pin, and track it; override only when the finding is runtime-reachable and the risk justifies it |

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

# Show only vulnerabilities that have a fix available
grype <image> --only-fixed

# Exit non-zero (code 2) if anything at or above the given severity is found.
# This sets the exit code for CI gating; it does not filter the output.
grype <image> --fail-on high
```

**Interpreting Grype output:**

- Table columns (grype 0.116.x) are `NAME`, `INSTALLED`, `FIXED IN`, `TYPE`, `VULNERABILITY`, `SEVERITY`, `EPSS`, `RISK`
- The column set is dynamic: `FIXED IN` is omitted entirely when no finding has a fix available. When present, a blank cell means that particular vulnerability has no fix
- Use `--only-fixed` to focus on actionable items (vulnerabilities with available fixes). For scripting, read `.matches[].vulnerability.fix.state` from `-o json` (`fixed`, `not-fixed`, `wont-fix`, `unknown`) rather than parsing the table

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
