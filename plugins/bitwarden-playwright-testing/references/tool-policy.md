# Bitwarden Web Test Tool Policy

Four categories of steps are permitted during web test planning and execution. Everything else is blocked.

## Category 1 — Web UI Interactions (default)

Use the `playwright-cli` skill for all interactions a user would perform in the browser. This is the default for everything, including verifying test results — if the outcome is visible in the UI, assert it via the browser, not via an API call.

## Category 2 — Email Reading

When a test step requires reading an email (verification links, magic links, OTP codes), use the mailcatcher reader script via Bash. The script accepts `--recipient` and `--pattern` arguments, returns the extracted URL on stdout, retries once on no-match, and exits non-zero if the email never arrives. Do not navigate to `http://localhost:1080` via playwright-cli (CORS blocks browser access).

## Category 3 — External Trigger Simulation

Use direct API calls (curl via Bash) only when the action is initiated by a system external to the Bitwarden application — meaning a system that is not the web vault, Admin portal, or any Bitwarden server service (e.g., the bitwarden.com marketing site, a mobile app, a third-party webhook).

**The qualifying test:** Could a Bitwarden service (web vault, Admin portal, server API) initiate this action for the user? If yes, use that service instead. If no — because the initiator is truly external — then curl is appropriate.

**Canonical example:** `POST /accounts/trial/send-verification-email` is called by bitwarden.com's marketing site, not by the web vault — simulating it with curl is legitimate. If the Admin portal or the web vault purchase flow can perform the action, use those instead. Document every curl call in the setup steps output with the rationale for why no Bitwarden service can initiate this step.

**Examples of what is NOT Category 3:**
- Applying a coupon to a subscription — use the Admin portal or the web vault purchase flow
- Creating a subscription discount record — use the Admin portal
- Setting up a paid organization — use the web vault org creation flow with a test card

**Authoritative source for external trigger parameter values:** When the plan or Jira synthesis contains explicit parameter values for an external trigger request body (productTier, products, trialLength, paymentOptional, etc.), copy them verbatim. Do not substitute values derived from enum definitions found in the codebase. If your code reading conflicts with the plan value, use the plan value and annotate it: `Note: plan specifies productTier: 2. Code enum shows Teams=2, Families=1. Using plan value.`

**Labeling:** Mark every Category 3 step explicitly in both the plan and the execution log:
  EXTERNAL TRIGGER: <METHOD> <endpoint> — <one-line rationale for why no Bitwarden service can initiate this>

## Category 4 — Stripe Data Queries (read-only)

Use the `invoke-stripe-api` skill (or fall back to direct `stripe get` CLI commands) only to query Stripe data that cannot be obtained through the web UI — for example, listing coupon IDs needed for an Admin portal import flow. Check your available skills list first: if `invoke-stripe-api` is present, use it. If not, use `stripe get` via Bash for GET/read-only queries only.

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
