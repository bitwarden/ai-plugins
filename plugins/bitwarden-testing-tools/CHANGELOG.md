# Changelog

All notable changes to the Bitwarden Testing Tools Plugin will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-08-27

### Added

- `reading-mailcatcher-api`, reading Bitwarden emails through the Mailcatcher REST API for verification links, magic links, and tokens, directly invocable outside a test run. Includes a trigger eval recorded as an on-demand prose reading.
- `using-stripe-cli`, read-only Stripe test-mode data queries plus the single permitted write of advancing an already-attached test clock, through the `stripe_cli.py` wrapper. Includes a trigger eval and advice-only behavior evals, both recorded as on-demand prose readings.
- `scripts/eval_harness.py`, a shared trigger-eval runner that per-skill eval scripts configure rather than copy.

### Fixed

- Addressed the PR #209 validation review before merge: made the `email-patterns.md` command paths self-substituting (the `${CLAUDE_SKILL_DIR}` placeholder is not expanded in a reference file), enumerated the covered email types and surfaced the `get_admin_email.py` helper in `reading-mailcatcher-api`, documented the generic Stripe CLI failure exit code and reframed the eight-day dunning note in `using-stripe-cli`, made per-skill eval runners stop reporting a misleading pass/fail exit status, added `stripe`/`billing`/`email`/`mailcatcher` marketplace keywords, and corrected assorted path, quoting, and documentation details.
- Addressed the PR #209 code review before merge: fixed the Mailcatcher endpoint at `http://localhost:1080` and removed the base-URL override entirely (the `--mailcatcher-url`/`--allowed-host` flags and the `MAILCATCHER_URL` env var), so a granted `read_mailcatcher.py` call can never be pointed at an arbitrary host; the operator-supplied `PLAYWRIGHT_TESTING_ALLOWED_HOSTS` env var still extends the extracted-URL allowlist.
- Corrected every skill's Bash tool grant from the non-matching `Bash(<script> *)` form to the working `Bash(<script>:*)` prefix form, and added the `Read` tool grant the skills rely on so their reference-file reads are auto-approved rather than prompting on every open.
- Addressed a second PR #209 validation review before merge, in `reading-mailcatcher-api`: `read_mailcatcher.py` now walks every filter-matching URL and returns the first that is also a local dev host, so an external footer link that matches the link filter (a marketing or help link, say) no longer masks the real local action link; the HTML-body fallback unescapes entities such as `&amp;` so multi-parameter links are no longer corrupted after the first parameter; the `SKILL.md` exit-code table splits the filter-miss and non-local-host causes and points the latter at `PLAYWRIGHT_TESTING_ALLOWED_HOSTS`; the `get_admin_email.py` current-directory-relative default, `--secrets-file` override, and exit 3 are documented; the admin-email recipe is now two separate Bash calls rather than a `$(...)` command substitution that always prompts; `manual-api-walkthrough.md` uses a self-contained `<message-id>` placeholder in every block; the unused `Grep`/`Glob` tool grants were dropped and `argument-hint` quoted for consistency; and the password-reset trigger-eval query was removed since the skill documents no password-reset pattern.
- Addressed a second PR #209 validation review before merge, in `using-stripe-cli`: the `references/resources.md` examples carry the `${CLAUDE_SKILL_DIR}/scripts/` prefix (and a placeholder-substitution note) so a copied command matches the grant; the Stripe field references were corrected to the current Basil-era shapes (`payment_intents.latest_charge` in place of the removed `charges` list, and `invoices.parent.subscription_details.subscription` plus the `invoices.payments` list in place of the removed top-level `subscription` and `payment_intent`), with the invoice expand example updated to match; the `advance-clock --days 8` call is documented as long-running with an extended-Bash-timeout guidance and partial-advance recovery note; and `advance_clock` now reports how many days completed and the last attempted `frozen_time` when an advance fails partway through.
- Addressed a third PR #209 validation review before merge, across both skills: switched every `allowed-tools` Bash grant and every in-body and reference-file script invocation from `${CLAUDE_SKILL_DIR}` to `${CLAUDE_PLUGIN_ROOT}/skills/<skill-name>/...`, because `${CLAUDE_SKILL_DIR}` is not substituted inside `allowed-tools` permission matchers and so a grant written against it never auto-approved a granted call; and quoted the `allowed-tools` scalar to match the plugin's other skills.
- Addressed a third PR #209 validation review before merge, in `using-stripe-cli`: added a "When to refuse, and what to redirect to" section that names the sanctioned alternatives (the Admin portal and the web vault purchase, organization-creation, and cancellation flows) and the database and feature-flag shortcuts to refuse, so the behavior-eval subordination cases are grounded in the skill body rather than ambient model behavior; converted the failure-handling paragraph to an exit-code table that carves the interrupted-`advance-clock` resume case out of the generic exit-1 "report and stop" rule it previously contradicted; corrected the long-running-advance guidance to the Bash tool's `600000` ms timeout ceiling with four-day batching, since no single value can guarantee an eight-day advance completes; documented obtaining the clock id from the subscription's `test_clock` field; fixed the smallest-currency-unit example (`amount` `1250` with `currency: usd` is `$12.50`); trimmed the description below the length guideline; and updated behavior-eval case 2 to expect the batched advance.
- Addressed a third PR #209 validation review before merge, in `reading-mailcatcher-api`: `read_mailcatcher.py` now surfaces a Mailcatcher outage that strikes during the message-body fetch as exit 3 (unreachable) instead of mislabeling it exit 1 (link-filter miss), and its non-local-host diagnostic reports the count and every distinct rejected hostname rather than only the first URL; renamed the `PLAYWRIGHT_TESTING_ALLOWED_HOSTS` env var to `MAILCATCHER_ALLOWED_HOSTS` so the name matches the Mailcatcher allowlist it governs; documented the `--link-filter` default and the `get_admin_email.py --all` flag; removed the happy-path pointer into the debugging-only `manual-api-walkthrough.md`; folded the redundant "User invocation" section into the quick reference; and trimmed the description.

## [1.1.0] - 2026-08-12

### Added

- `writing-manual-test-cases` skill: authors new manual Gherkin test cases from a Jira ticket, PR, or feature description and delivers a paired `.txt` and Testmo-importable `.csv` under `${CLAUDE_PLUGIN_DATA}/writing-manual-test-cases/`, keeping generated files out of the repo under test so they cannot be committed by accident. Ported from the `bitwarden/test` repository so it is available org-wide rather than only to that repo's contributors. See the plugin README for details.

### Changed

- Ported skill standardizes the Automation Type for `Functional` cases on `Not Automating`. The original skill named both `None` and `Not Automating` in different sections, which produced inconsistent CSV exports between runs.

## [1.0.0] - 2026-07-24

### Added

- Initial release of the `bitwarden-testing-tools` plugin.
- `assessing-test-coverage` skill: an evidence-grounded inventory of what a change is already tested by. See the plugin README for details.
