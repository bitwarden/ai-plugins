---
name: triaging-security-findings
description: This skill should be used when the user asks to "triage security findings", "fix an Aikido finding", "review Aikido issues", "dismiss a false positive", "check SAST/IaC alerts", or needs to work with Aikido feed issues, GitHub Dependabot alerts, or GitHub secret scanning alerts.
---

## Scanner Landscape

Bitwarden uses **Aikido** as its unified security platform. Aikido continuously scans connected repositories and surfaces findings across SAST, IaC, SCA (open source), secrets, cloud, container, malware, EOL, and license categories in a single feed.

Findings are queried and triaged via the `aikido:issues` skill (`aikido_issues_list`), not through GitHub code-scanning alerts — Aikido triage does not flow through GitHub Advanced Security. See that skill for the full list of scope filters, `issue_types`, and SLA filters (`out_of_sla`, `sla_due_soon`).

## GitHub-Native Alerts (Dependabot, Secret Scanning)

Dependabot and GitHub secret scanning are unaffected by the Aikido transition — they remain GitHub-native and are queried separately from the Aikido feed.

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

## Triaging Aikido Findings

Aikido triage is handled through Jira, not through Aikido's own dismissal states or GitHub Advanced Security. Ticket sourcing (`Source = Aikido` tickets parented under epic `VULN-560`, excluding SCA/dependency findings which are handled separately under `VULN-564`), the five-label comment format (`Finding / Declaration / Effective severity / Status / Action`), the Team/Severity/CVSS-base-score field rules, the CVSS **v3.0** scoring convention for this flow, and the `New` → `In Review` transition are documented as the methodology of record on **[VULN-665](https://bitwarden.atlassian.net/browse/VULN-665)**. Treat that ticket as the source of truth for the Jira mechanics and triage rubric — use `Skill(bitwarden-atlassian-tools:researching-jira-issues)` to read it.

### Comment Format

Write the Jira triage comment as five labeled paragraphs, in this exact order, not open prose:

- **Finding:** what was flagged — source (Aikido/Renovate/SAST/CVE/GHSA/CWE), the specific file/line or package/version, and what was reviewed to write this (repo checkout, decompiled assembly, advisory DB, etc).
- **Declaration:** the verdict word first (`AFFECTED` / `NOT AFFECTED` / `unable to determine`), then the technical reasoning/evidence for it — reachability, code path, config, mitigating controls.
- **Effective severity:** the severity after analysis, using **CVSS v3.0** with the full vector string, called out against the raw feed severity if it changed, with a one-line reason for any adjustment. Include a clickable GitHub blob+line link to the flagged code.
- **Status:** current remediation state — merged/unmerged, released/unreleased, what's verified vs. still a gap.
- **Action:** concrete next step and ownership/team routing (or "no fix needed").

When one ticket bundles multiple distinct findings (e.g. several XSS sites), use a condensed markdown table with columns `Finding | Declaration | Severity/CWE | Owner | Action required` instead of repeating the five paragraphs per row.

### False Positive Protocol

Before writing a `NOT AFFECTED` **Declaration**, verify:

1. **Trace the data flow.** Can untrusted input actually reach the flagged sink? Follow it from entry point through every transformation to the flagged location.
2. **Check for existing sanitization.** Validation alone is insufficient — sanitizers (which replace threatening values) are preferred over encoding/escaping-free validators (which leave the original value in place). Don't declare `NOT AFFECTED` on the basis of a validation step alone.
3. **Consider the full lifecycle.** Even if the code isn't deployed to a risky environment today, will it be? Private repos may go public. Local deployments may move to cloud. If deploying to production would make it exploitable, treat it as exploitable now.
4. **Document the rationale in the Declaration paragraph.** Every `NOT AFFECTED` verdict needs a clear, reviewable explanation.

If any step is uncertain, declare `unable to determine` rather than `NOT AFFECTED`, and route it through the **Action** field for team review.

### Severity Mapping (Jira → Aikido)

The Jira `Severity` field (Informative, Low, Medium, High, Critical) has one more value than Aikido's own severity scale (Critical, High, Medium, Low). When syncing a ticket's severity back to the Aikido issue:

| Jira `Severity` | Aikido     |
| --------------- | ---------- |
| Critical        | Critical   |
| High            | High       |
| Medium          | Medium     |
| Low             | Low        |
| Informative     | **Ignore** |

`Informative` has no Aikido severity equivalent — set the finding's status to **Ignore** in Aikido rather than assigning a severity.

### Group-Scoped Actions

Aikido findings are organized into **issue groups** (one group per package or per rule, spanning every repo and occurrence it appears in). A severity-filtered `aikido_issues_list` pull, or the set of repos named in a Jira ticket, is often only a _sample_ of a group's true membership — not the whole group.

Before recommending or approving any group-level action (adjusting severity, ignoring, snoozing), use `aikido_issues_list` with no severity or SLA filter to pull the group's full unfiltered membership and diff it against whatever scope prompted the action. If that shows repos or occurrences beyond what was actually verified, either verify those too before acting, or scope the action to the individual verified occurrences rather than the whole group, so unverified occurrences are left untouched. A group-level action is only safe once the unfiltered pull confirms the group's true membership matches what was checked — otherwise it silently mis-triages the unverified occurrences alongside the real ones. This skill only has read access to Aikido (`aikido_issues_list`); applying the action itself happens in the Aikido dashboard — this step is about verifying scope before that happens, not about calling an API to do it directly.

### Ticket Scope Is Pinned at Creation

A group's membership is not static — a later Aikido scan can add new occurrences to a group after its Jira ticket already exists. Don't fold newly-arrived occurrences into an existing ticket's scope. Scope a ticket to the group's membership **as of the ticket's creation time**; the engineering team may already be working the ticket as originally scoped, and silently widening it moves the ground under them mid-fix.

When a later scan surfaces occurrences beyond an existing ticket's original scope, file a **new** ticket for those occurrences rather than reopening or expanding the old one. This applies even if it's the same underlying group/package/rule — same group, new ticket, if the new occurrences postdate the original ticket.

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
