# Bitwarden Web Test Tool Policy

Four categories of steps are permitted during web test planning and execution. Everything else is blocked.

## Canonical script paths

Reference these scripts by these exact paths; do not duplicate the paths elsewhere in prose.

- Mailcatcher reader: `${CLAUDE_PLUGIN_ROOT}/skills/reading-mailcatcher-api/scripts/read_mailcatcher.py`
- External trigger: `${CLAUDE_PLUGIN_ROOT}/scripts/external_trigger.py`

## Category 1 — Web UI Interactions (default)

Use the `playwright-cli` skill for all interactions a user would perform in the browser. This is the default for everything, including verifying test results — if the outcome is visible in the UI, assert it via the browser, not via an API call.

## Category 2 — Email Reading

When a test step requires reading an email (verification links, magic links, OTP codes), use the mailcatcher reader script via Bash. The script accepts `--recipient` and `--pattern` arguments, returns the extracted URL on stdout, retries once on no-match, and exits non-zero if the email never arrives. Do not navigate to `http://localhost:1080` via playwright-cli (CORS blocks browser access).

## Category 3 — External Trigger Simulation

Use the external-trigger wrapper (see Canonical script paths) only when the action is initiated by a system external to the Bitwarden application — meaning a system that is not the web vault, Admin portal, or any Bitwarden server service (e.g., the bitwarden.com marketing site, a mobile app, a third-party webhook).

**The qualifying test:** Could a Bitwarden service (web vault, Admin portal, server API) initiate this action for the user? If yes, use that service instead. If no — because the initiator is truly external — then the wrapper is appropriate.

**Canonical example:** `POST /accounts/trial/send-verification-email` is called by bitwarden.com's marketing site, not by the web vault — simulating it with the wrapper is legitimate. If the Admin portal or the web vault purchase flow can perform the action, use those instead. Document every external-trigger call in the setup steps output with the rationale for why no Bitwarden service can initiate this step.

**Examples of what is NOT Category 3:**

- Applying a coupon to a subscription — use the Admin portal or the web vault purchase flow
- Creating a subscription discount record — use the Admin portal
- Setting up a paid organization — use the web vault org creation flow with a test card

**Labeling:** Mark every Category 3 step explicitly in both the plan and the execution log:
EXTERNAL TRIGGER: POST <endpoint> — <one-line rationale for why no Bitwarden service can initiate this>

**Execution:** Category 3 steps are issued ONLY through the external-trigger wrapper (see Canonical script paths), never via raw curl:
${CLAUDE_PLUGIN_ROOT}/scripts/external_trigger.py --url <endpoint> --rationale "<rationale>" --data '<json body>'
The wrapper enforces localhost-only destinations and POST-only method. A destination that is not a local dev host is rejected by the wrapper; do not attempt to work around it.

## Category 4 — Stripe Data Queries (read-only)

Use the `using-stripe-cli` skill (or fall back to direct `stripe get` CLI commands) only to query Stripe data that cannot be obtained through the web UI — for example, listing coupon IDs needed for an Admin portal import flow. Check your available skills list first: if `using-stripe-cli` is present, use it. If not, use `stripe get` via Bash for GET/read-only queries only.

Do not use Stripe calls to set up state that the application's own flows can create.

Never use Stripe for write operations (POST, PUT, DELETE) — no creating coupons, modifying subscriptions, updating customers, or any other state changes. The one exception is advancing test clocks. All other Stripe access is strictly read-only.

## Never Permitted

- Direct database queries
- API calls that substitute for UI actions a user could perform in the browser
- Using API calls to verify test results when the outcome is observable in the UI (always assert via playwright-cli instead)
- CLI tools not related to service startup (Stripe CLI excepted when used as read-only per Category 4)
- Stripe write operations (POST, PUT, DELETE — creating coupons, modifying subscriptions, updating customers, or any other Stripe state changes)
- Editing feature flags or any other application configuration

## Stop Condition

If a step cannot be completed using any of the four permitted categories above, STOP immediately. Return a detailed report of what was completed, where the block occurred, and what approach was tried. Do not improvise or use unapproved tools.
