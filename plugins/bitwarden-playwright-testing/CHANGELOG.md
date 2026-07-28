# Changelog

All notable changes to bitwarden-playwright-testing will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-28

### Added

- Initial release of the `bitwarden-playwright-testing` plugin
- `test-web-changes` skill orchestrating a full UI test pipeline to HTML report, accepting a Jira ticket key, a Jira browse URL, an implementation plan path, or a feature description
- Six-agent pipeline: `context-gatherer`, `code-explorer`, `service-mapper`, `test-planner`, `service-manager`, `test-runner`
- Skills: `exploring-application-context`, `determining-required-services`, `verifying-environment-health`, `build-test-cases`, `executing-web-tests`, `reading-mailcatcher-api`, `compiling-test-report`
- Scoped `using-stripe-cli` skill for querying Stripe test-clock and subscription data (read-only), wired into `test-runner`.

### Security

- Replaced the `test-runner` `Bash(curl:*)` grant with a path-scoped `external_trigger.py` wrapper that enforces localhost-only destinations and POST-only method, closing an SSRF/exfiltration surface and removing the reachable arbitrary Mailcatcher delete path.
- Added untrusted-content preambles to the source-ingesting agents to reduce Jira/Confluence prompt-injection risk, including `test-runner`.
- The dev admin email is never embedded in committed plugin content; it is resolved at execution time from the developer's local `server/dev/secrets.json`.
- HTML-escaping of every interpolated report value (test case names, step text, notes, issue descriptions, and template tokens) is now performed inherently by `render_report.py` via the stdlib `html.escape`, rather than by prose instruction to an LLM, closing an injection surface from untrusted Jira/Confluence and observed page content.
- Removed the tool-policy clause instructing agents to prefer a plan-supplied external-trigger parameter value over a conflicting code-derived enum value, closing a path for untrusted plan content to override a verified value.
- Scoped the `test-runner` `ls` grant to `*/screenshots/*` instead of an unrestricted `ls *`.

### Fixed

- `read_mailcatcher.py` now reports Mailcatcher-unreachable (exit 3), URL-filter/non-local-host misses, and genuine no-message cases distinctly, and no longer retries non-retryable failures.
- `test-web-changes` Task 5 now correctly depends on Tasks 3 and 4; subsequent-pause checkpoint appends use Bash append instead of the overwriting Write tool; the multi-pause SUMMARY merge instruction is unambiguous.
- `test-runner` Step 3 no longer contradicts the pause-response shape.
- `preflight-check.sh` Mailcatcher detection no longer false-positives on unrelated mail containers.
- `report-template.html` uses Prettier-parseable brace tokens instead of angle-bracket placeholders.
- `service-mapper` is granted `Bash(git diff *)`, needed for the diff review it already performs.
- Split the setup-failure halt in `executing-web-tests`: a setup failure now fails only that test case and `test-runner` continues to the next, while a failure before any test case has started aborts the whole run with a distinct `=== TEST RUN ABORTED: setup failure before test cases (<reason>) ===` marker.
- Added an errored count to the run-complete marker, the `SUMMARY:` line, and the report summary table (`N total, N passed, N passed (adaptive), N failed, N errored`).
- `read_mailcatcher.py` now guards `--recipient`/`--pattern`/`--link-filter` against a missing argument value and extends, rather than replaces, its local-host allowlist via the `PLAYWRIGHT_TESTING_ALLOWED_HOSTS` environment variable.
- `service-manager` now declares the `playwright-cli` skill it already required.
- Narrowed the `test-web-changes` orchestrator's pre-approved `Bash` commands from an unrestricted `Bash` to `Bash(mkdir *)` plus the two report scripts, so fewer commands run without a permission prompt. Note that `allowed-tools` pre-approves rather than restricts.
- Corrected the garbled report-persistence fence-stripping instruction in `test-web-changes`.
- Corrected remaining `invoke-stripe-api` references to `using-stripe-cli` in `references/tool-policy.md` and `exploring-application-context`.

### Changed

- Centralized script paths in `references/tool-policy.md`; split the `known-flows` catalog into `auth`/`billing`/`admin` references; documented the self-signed-cert TLS bypasses; trimmed `executing-web-tests` and `build-test-cases` for conciseness; aligned agent skill namespaces to convention.
- The test-run results contract is now JSON end to end. The `test-runner` emits a results object (complete, paused, or aborted); the orchestrator assembles segments and derives totals with `merge_results.py` (removing the hand-merge and its per-segment SUMMARY summing), then renders `report-<timestamp>.html` with `render_report.py`. The canonical results artifact is now `test-results-<timestamp>.json`.
- The `external-trigger` wrapper and the Mailcatcher reader are now Python (`external_trigger.py`, `read_mailcatcher.py`) with unit tests covering the host allowlist, the scheme and method guards, and the documented exit codes. Both were already bash wrappers around inline `python3` for URL parsing and JSON. Every documented invocation of all four plugin scripts is now a bare absolute path under `${CLAUDE_PLUGIN_ROOT}`, which is the form the path-scoped `Bash(...)` grants actually match.
