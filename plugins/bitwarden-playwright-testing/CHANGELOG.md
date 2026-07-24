# Changelog

All notable changes to bitwarden-playwright-testing will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-28

### Added

- Initial release of the `bitwarden-playwright-testing` plugin
- `test-web-changes` skill orchestrating a full UI test pipeline from Jira ticket or feature description to HTML report
- Seven-agent team: `context-gatherer`, `code-explorer`, `service-mapper`, `test-planner`, `service-manager`, `test-runner`, `report-compiler`
- Skills: `exploring-application-context`, `determining-required-services`, `verifying-environment-health`, `build-test-cases`, `executing-web-tests`, `reading-mailcatcher-api`, `compiling-test-report`
- Scoped `using-stripe-cli` skill for querying Stripe test-clock and subscription data (read-only), wired into `test-runner`.

### Security

- Replaced the `test-runner` `Bash(curl:*)` grant with a path-scoped `external-trigger.sh` wrapper that enforces localhost-only destinations and POST-only method, closing an SSRF/exfiltration surface and removing the reachable arbitrary Mailcatcher delete path.
- Added untrusted-content preambles to the source-ingesting agents to reduce Jira/Confluence prompt-injection risk, including `report-compiler` and `test-runner`.
- Stopped persisting the resolved dev admin email into run artifacts; it is now resolved at execution time only. The artifacts directory is git-ignored via a generated `.gitignore`.
- Required HTML-escaping of every interpolated report value (test case names, step text, notes, issue descriptions, and template tokens) before insertion into the compiled report, closing an injection surface from untrusted Jira/Confluence and observed page content.
- Removed the tool-policy clause instructing agents to prefer a plan-supplied external-trigger parameter value over a conflicting code-derived enum value, closing a path for untrusted plan content to override a verified value.
- Scoped the `test-runner` `ls` grant to `*/screenshots/*` instead of an unrestricted `ls *`.

### Fixed

- `read-mailcatcher.sh` now reports Mailcatcher-unreachable (exit 3), URL-filter/non-local-host misses, and genuine no-message cases distinctly, and no longer retries non-retryable failures.
- `test-web-changes` Task 5 now correctly depends on Tasks 3 and 4; subsequent-pause checkpoint appends use Bash append instead of the overwriting Write tool; the multi-pause SUMMARY merge instruction is unambiguous.
- `test-runner` Step 3 no longer contradicts the pause-response shape.
- `preflight-check.sh` Mailcatcher detection no longer false-positives on unrelated mail containers.
- `report-template.html` uses Prettier-parseable brace tokens instead of angle-bracket placeholders.
- `service-mapper` is granted `Bash(git diff *)`, needed for the diff review it already performs.
- Split the setup-failure halt in `executing-web-tests`: a setup failure now fails only that test case and `test-runner` continues to the next, while a failure before any test case has started aborts the whole run with a distinct `=== TEST RUN ABORTED: setup failure before test cases — <reason> ===` marker.
- Added an errored count to the run-complete marker, the `SUMMARY:` line, and the report summary table (`N total, N passed, N passed (adaptive), N failed, N errored`).
- `read-mailcatcher.sh` now guards `--recipient`/`--pattern`/`--link-filter` against a missing argument value and extends, rather than replaces, its local-host allowlist via the `PLAYWRIGHT_TESTING_ALLOWED_HOSTS` environment variable.
- `service-manager` now declares the `playwright-cli` skill it already required.
- Scoped the `test-web-changes` team-lead's `Bash` grant to `Bash(mkdir *)` and `Bash(printf *)` instead of an unrestricted `Bash`.
- Corrected the garbled report-persistence fence-stripping instruction in `test-web-changes`.
- Corrected remaining `invoke-stripe-api` references to `using-stripe-cli` in `references/tool-policy.md` and `exploring-application-context`.

### Changed

- Centralized script paths in `references/tool-policy.md`; split the `known-flows` catalog into `auth`/`billing`/`admin` references; documented the self-signed-cert TLS bypasses; trimmed `executing-web-tests` and `build-test-cases` for conciseness; aligned agent skill namespaces to convention.
