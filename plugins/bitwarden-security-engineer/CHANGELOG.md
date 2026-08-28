# Changelog

All notable changes to the `bitwarden-security-engineer` plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2026-08-25

### Added

- `auditing-hackerone-vulns` skill: new action tokens 🆕 **Create VULN Ticket** (open report with no linked VULN) and 🟣 **Close HackerOne Report** (VULN reached a terminal status while the report stayed open).
- `auditing-hackerone-vulns` skill: new 🏁 **Close Out** token. `Verified` is no longer excluded from the audit query, so VULNs whose fix is confirmed in production but whose Jira ticket was never moved to `Closed` stop dropping out of the report. These skip the child-item and GitHub steps entirely.
- `auditing-hackerone-vulns` skill: new **Blocked** child-status category, so an `On Hold` child is tracked separately from one that simply has not been picked up and is called out as stalled in both the child-status cell and the summary. `Ready for Dev` and `In QA` were also added to the status categories.
- `auditing-hackerone-vulns` skill: new Step 7 reconciliation sweep and 🗂️ Orphaned VULNs section, catching open Jira tickets whose HackerOne report was already closed, which a HackerOne-first traversal would otherwise miss. VULNs with no report reference at all are excluded rather than filed as orphans, since they came from another source and this audit has no jurisdiction over them.
- `auditing-hackerone-vulns` skill: new edge cases for half-remediated VULNs (an SRE child Done ahead of the PM code fix), duplicate-report clusters on one root cause, and work blocked on an upstream third-party fix.
- `auditing-hackerone-vulns` skill: tool-usage guardrails against interpreter pipes, file writes and heredocs, shell scripting to orchestrate the audit, `2>/dev/null` error suppression, and fetching release note body text.
- Plugin README now carries a Requirements section naming the operator-configured HackerOne MCP server and the `bitwarden-atlassian-tools` dependency, both of which `auditing-hackerone-vulns` hard-requires. The skill itself now says what to do when the HackerOne tools are unavailable instead of failing opaquely on the first call.

### Changed

- `auditing-hackerone-vulns` skill: inverted the source of truth from Jira to HackerOne. The audit now enumerates open reports across **both** programs via the HackerOne MCP (`bitwarden` VDP and `bitwarden-bbp` Bug Bounty) and correlates outward to VULN tickets, child engineering items, fix PRs, and release state, rather than starting from a `project = VULN` JQL sweep. Reports that never got a VULN ticket created are no longer invisible to the audit.
- `auditing-hackerone-vulns` skill: output tables are keyed on the HackerOne report, carry program (VDP/BBP), submission date, and HackerOne severity, and sort oldest-first so aging reports surface at the top.
- `auditing-hackerone-vulns` skill: release-inclusion checking reworked. The candidate release is now the earliest whose `publishedAt` postdates the PR merge, confirmed by matching the PR number against the tag-to-tag commit range. A missing cherry-pick is reported as 🔵 Monitor with an engineering flag rather than being counted as shipped, and Jira's `Fix Version` "(Released)" annotation is explicitly called out as untrustworthy.
- `auditing-hackerone-vulns` skill: `allowed-tools` tightened. `Bash(base64 *)` narrowed to `Bash(base64 -d)`, because the wildcard form also permitted reading an arbitrary file in a skill whose own rules forbid touching the filesystem. Unused `Bash(gh search prs *)` and `mcp__hackerone__get_current_user` grants were dropped, and `gh release list` was replaced with the Releases API. Commit-message matching moved from a `grep` pipe into the `gh api --jq` expression, so no `grep` grant is needed.
- `auditing-hackerone-vulns` skill: documented API constraints hit in practice. `search_reports` requires `program_handles` and returns HTTP 500 for the `open` and `needs-more-info` states, report IDs are base64 GIDs needing decode, the Jira reference lives in `get_report_activities` and not in `get_report`, Jira `search_issues` silently drops the `issuelinks` field so `linkedIssues()` is required, and VULN-project `status not in (Done, Verified)` fails to exclude `Rejected` or `Closed`. The audit query exclusion list widened to `(Done, Closed, Rejected, Resolved, Canceled)`, and the 🟣 branch now names the same five statuses the queries exclude.

### Fixed

- `auditing-hackerone-vulns` skill: the PR search `--jq` filter now reads `.pull_request.merged_at`. The Search Issues API returns no `mergedAt` field, so the previous filter reported every PR as unmerged.
- `auditing-hackerone-vulns` skill: cherry-pick verification no longer trusts a truncated commit range. GitHub's compare endpoint caps `.commits` at 250 and reports no error when it truncates, which a normal `clients` release range exceeds, so a fix shipped in the tail was reported as a missed cherry-pick. The check now compares `total_commits` against the returned count, paginates the remainder, and treats an unmatched truncated range as inconclusive rather than as proof the fix never shipped.
- `auditing-hackerone-vulns` skill: restored `mergeCommit` to the `gh pr view` field list and made that call unconditional for direct-push repos. Dropping it left no step returning a commit SHA, so release state for `bitwarden/sm-action` and similar repos could not be determined at all.
- `auditing-hackerone-vulns` skill: the Step 2 activity-thread fallback no longer dead-ends when it succeeds. Finding a Jira reference now routes to extracting the VULN key and continuing at Step 3, where previously only the negative case was handled and a VULN whose description had been reformatted could be silently dropped.

## [1.3.0] - 2026-07-21

### Added

- `bitwarden-security-context`, `reviewing-security-architecture`, and `threat-modeling` skills now check alignment against Bitwarden's [Architecture Decision Records](https://contributing.bitwarden.com/architecture/adr/) as part of security assessments. Conflicts with an accepted ADR are treated as findings, significant undocumented architectural decisions are flagged as gaps, and ADR status is verified (not superseded/deprecated) before being cited.

## [1.2.0] - 2026-05-08

### Added

- `auditing-hackerone-vulns` skill: audits all open HackerOne-sourced VULN Jira tickets and their linked engineering child items to produce a prioritized action table. Correlates VULN status against child item progress and merged PRs, determines whether fixes are included in a shipped release (using tag-range commit search to handle cherry-pick workflows), and emits per-ticket action tokens (🔴 Update Status / 🟡 Mark Remediated / 🟢 Verify & Close / 🔵 Monitor / ⚪ Waiting / ➖ No Child Item) sorted by urgency.

## [1.1.1] - 2026-05-07

### Fixed

- Added `Skill` to the agent's `tools:` frontmatter so the agent can dispatch the six skills declared in its `skills:` block (`triaging-security-findings`, `threat-modeling`, `analyzing-code-security`, `reviewing-dependencies`, `detecting-secrets`, `reviewing-security-architecture`). Previously these declared skills could not be invoked.

## [1.1.0] - 2026-05-05

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
