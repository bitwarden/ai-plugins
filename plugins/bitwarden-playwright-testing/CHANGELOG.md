# Changelog

All notable changes to bitwarden-playwright-testing will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-28

### Added

- Initial release of the `bitwarden-playwright-testing` plugin: an automated UI testing framework for Bitwarden web changes, accepting a Jira ticket key, a Jira browse URL, an implementation plan path, or a feature description.
- `test-web-changes` orchestrator driving a six-agent pipeline (`context-gatherer`, `code-explorer`, `service-mapper`, `test-planner`, `service-manager`, `test-runner`) from context-gathering through test execution to an HTML report.
- Nine skills: `exploring-application-context`, `determining-required-services`, `verifying-environment-health`, `build-test-cases`, `executing-web-tests`, `reading-mailcatcher-api`, `compiling-test-report`, `test-web-changes`, and `using-stripe-cli`, a scoped skill for read-only Stripe test-clock and subscription queries via `scripts/stripe_cli.py`, wired into `test-runner`.
- `references/tool-policy.md` at the plugin root governs four categories of permitted test steps: web UI interaction via `playwright-cli`, Mailcatcher email reading, external-trigger simulation, and read-only Stripe queries.
- `external_trigger.py` and `read_admin_email.py` under `skills/executing-web-tests/scripts/`, and `read_mailcatcher.py` under `skills/reading-mailcatcher-api/scripts/`, back the email-reading and external-trigger categories. `external_trigger.py` restricts destinations to `localhost`, `127.0.0.1`, `::1`, and `bitwarden.test` by default, extendable by the operator via the `PLAYWRIGHT_TESTING_ALLOWED_HOSTS` environment variable, and enforces POST-only requests. `read_admin_email.py` resolves the dev admin email at execution time from the developer's local `server/dev/secrets.json` rather than embedding it in plugin content.
- Test results are a JSON contract end to end: `test-runner` emits a results object per segment (complete, paused, or aborted), `merge_results.py` (under `skills/compiling-test-report/scripts/`) assembles segments and derives totals, and `render_report.py` renders the HTML report from the `templates/report.html` and `templates/test-case.html` templates, HTML-escaping every interpolated value. The canonical results artifact is `test-results-<timestamp>.json`, documented in `skills/compiling-test-report/references/results-schema.md`.
