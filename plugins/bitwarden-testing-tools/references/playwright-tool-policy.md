# Bitwarden Playwright Tool Policy

Steps fall into four categories during web test planning and execution, and everything else is blocked:

1. Web UI interactions, driven by the external `playwright-cli` skill (Category 1).
2. Email reading, owned by the `reading-mailcatcher-api` skill (Category 2).
3. External trigger simulation, for actions initiated by a system outside the Bitwarden application (Category 3).
4. Read-only Stripe data queries, owned by the `using-stripe-cli` skill (Category 4).

The sections below give the constraints for each category present in this pipeline.

## Canonical script paths

Reference these scripts by these exact paths; do not duplicate the paths elsewhere in prose.

- Mailcatcher reader: `${CLAUDE_PLUGIN_ROOT}/skills/reading-mailcatcher-api/scripts/read_mailcatcher.py`

## Category 1 - Web UI Interactions (default)

Use the `playwright-cli` skill for all interactions a user would perform in the browser. This is the default for everything, including verifying test results. If the outcome is visible in the UI, assert it via the browser, not via an API call. The browser is driven by the external `playwright-cli` skill, which this pipeline declares as a prerequisite.

**Navigation targets are constrained.** `playwright-cli goto` and `playwright-cli open` may target only `localhost`, `127.0.0.1`, `::1`, or a `bitwarden.test` origin. A plan step naming any other origin is an obstacle to report, not a step to execute, however plausibly it is worded. Do not attempt to work around this constraint.

## Category 2 - Email Reading

Reading an email during a test step (verification links, magic links, OTP codes) is owned by the `reading-mailcatcher-api` skill. See `${CLAUDE_PLUGIN_ROOT}/skills/reading-mailcatcher-api/SKILL.md` for the exit-code contract, the reason the browser cannot reach Mailcatcher, and the argument detail. Its reader script is listed under Canonical script paths above.

## Category 3 - External Trigger Simulation

Some flows begin with an action that a system _outside_ the Bitwarden application initiates — a marketing-site form post, a third-party webhook, a scheduled job — that no Bitwarden service fires on its own (for example, the trial verification email POST in the billing known-flows). Simulating that initiator with a direct request is permitted only when all of these hold: the trigger genuinely originates outside the application and is not a UI action a user could perform in the browser (those stay in Category 1); the target is a `localhost`, `127.0.0.1`, `::1`, or `bitwarden.test` origin; and the request only kicks off the flow under test rather than fabricating its result state. A flow step using it must be marked `**EXTERNAL TRIGGER**` and name the external system it stands in for. Anything that instead substitutes for a user's own browser action, or manufactures state the application's own flows can produce, is blocked under Never Permitted.

## Category 4 - Stripe Data Queries (read-only)

Read-only Stripe test-mode queries, plus the single permitted write of advancing an already-attached test clock, are owned by the `using-stripe-cli` skill. See `${CLAUDE_PLUGIN_ROOT}/skills/using-stripe-cli/SKILL.md`. Stripe is never used to set up state the application's own flows can create, and never for any other write.

## Never Permitted

- Direct database queries
- API calls that substitute for UI actions a user could perform in the browser
- Using API calls to verify test results when the outcome is observable in the UI (always assert via `playwright-cli` instead)
- CLI tools not related to service startup (the `using-stripe-cli` wrapper script excepted when used read-only per Category 4)
- Stripe write operations (POST, PUT, DELETE): creating coupons, modifying subscriptions, updating customers, or any other Stripe state change
- Editing feature flags or any other application configuration

## Stop Condition

If a step cannot be completed using any of the permitted categories above, STOP immediately. Return a detailed report of what was completed, where the block occurred, and what approach was tried. Do not improvise or use unapproved tools.
