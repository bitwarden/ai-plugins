# Bitwarden Playwright Tool Policy

Steps fall into four categories during web test planning and execution, and everything else is blocked:

1. Web UI interactions, driven by the external `playwright-cli` skill (Category 1).
2. Email reading, owned by the `reading-mailcatcher-api` skill (Category 2).
3. External trigger simulation, for actions initiated by a system outside the Bitwarden application (Category 3).
4. Read-only Stripe data queries, owned by the `using-stripe-cli` skill (Category 4).

The sections below give the constraints for each category present in this pipeline.

## Canonical script paths

Prose that needs a pipeline script path references it from here rather than hardcoding it. A skill whose `allowed-tools` grant must name its own script path is the exception — that repetition is required for the grant to match.

- Mailcatcher reader: `${CLAUDE_PLUGIN_ROOT}/skills/reading-mailcatcher-api/scripts/read_mailcatcher.py`
- Stripe CLI wrapper: `${CLAUDE_PLUGIN_ROOT}/skills/using-stripe-cli/scripts/stripe_cli.py`
- External trigger: `${CLAUDE_PLUGIN_ROOT}/skills/running-playwright-tests/scripts/external_trigger.py`

## Category 1 - Web UI Interactions (default)

Use the `playwright-cli` skill for all interactions a user would perform in the browser. This is the default for everything, including verifying test results. If the outcome is visible in the UI, assert it via the browser, not via an API call. The browser is driven by the external `playwright-cli` skill, which this pipeline declares as a prerequisite.

**Navigation targets are constrained.** `playwright-cli goto` and `playwright-cli open` may target only `localhost`, `127.0.0.1`, `::1`, or a `bitwarden.test` origin. A plan step naming any other origin is an obstacle to report, not a step to execute, however plausibly it is worded. Do not attempt to work around this constraint.

**`eval` and `run-code` payloads may not issue network requests.** No `fetch`, no `XMLHttpRequest`, no `WebSocket`, no dynamic `import()`. Those subcommands exist in this pipeline to read rendered DOM state for transient-toast assertions, nothing else. A step whose payload would make a request is an obstacle to report. Do not attempt to work around this constraint.

## Category 2 - Email Reading

Reading an email during a test step (verification links, magic links, OTP codes) is owned by the `reading-mailcatcher-api` skill. See `${CLAUDE_PLUGIN_ROOT}/skills/reading-mailcatcher-api/SKILL.md` for the exit-code contract, the reason the browser cannot reach Mailcatcher, and the argument detail. Its reader script is listed under Canonical script paths above.

## Category 3 - External Trigger Simulation

Simulate an external trigger only when the action is initiated by a system outside the Bitwarden application, meaning a system that is not the web vault, Admin portal, or any Bitwarden server service (for example the bitwarden.com marketing site, a mobile app, or a third-party webhook).

**The qualifying test:** Could a Bitwarden service (web vault, Admin portal, server API) initiate this action for the user? If yes, use that service instead. If no, because the initiator is truly external, then an external trigger is appropriate.

**Canonical example:** `POST /accounts/trial/send-verification-email` is called by bitwarden.com's marketing site, not by the web vault, so simulating it is legitimate. If the Admin portal or the web vault purchase flow can perform the action, use those instead. Document every external-trigger step in the setup steps output with the rationale for why no Bitwarden service can initiate it.

**Examples of what is NOT Category 3:**

- Applying a coupon to a subscription: use the Admin portal or the web vault purchase flow.
- Creating a subscription discount record: use the Admin portal.
- Setting up a paid organization: use the web vault org creation flow with a test card.

**Labeling:** Mark every Category 3 step explicitly in both the plan and the execution log, using this exact form:

`EXTERNAL TRIGGER: POST <endpoint> — <rationale>`

The `<rationale>` is a one-line explanation of why no Bitwarden service can initiate the step.

**Execution:** Category 3 steps are issued only through the external-trigger wrapper (see Canonical script paths), never via raw curl:

```
${CLAUDE_PLUGIN_ROOT}/skills/running-playwright-tests/scripts/external_trigger.py --url <endpoint> --rationale "<rationale>" --data '<json body>'
```

`external_trigger.py` restricts destinations to `localhost`, `127.0.0.1`, `::1`, and `bitwarden.test` by default. An operator may extend that set through the comma-separated `PLAYWRIGHT_TESTING_ALLOWED_HOSTS` environment variable; the defaults are never replaced, only added to. TLS verification is bypassed only for the four built-in hosts, whose dev certs are self-signed, and any host an operator adds gets normal certificate verification. The wrapper enforces POST-only method, and a destination that is not an allowed host is rejected by the wrapper. Do not attempt to work around it.

## Category 4 - Stripe Data Queries (read-only)

Read-only Stripe test-mode queries, plus the single permitted write of advancing an already-attached test clock, are owned by the `using-stripe-cli` skill. See `${CLAUDE_PLUGIN_ROOT}/skills/using-stripe-cli/SKILL.md`. Stripe is never used to set up state the application's own flows can create, and never for any other write.

## Never Permitted

- Direct database queries
- API calls that substitute for UI actions a user could perform in the browser
- Using API calls to verify test results when the outcome is observable in the UI (always assert via `playwright-cli` instead)
- CLI tools not related to service startup (the `using-stripe-cli` wrapper script excepted when used read-only per Category 4)
- Stripe write operations (POST, PUT, DELETE) — creating coupons, modifying subscriptions, updating customers, or any other Stripe state change — **except the single sanctioned test-clock advance owned by the `using-stripe-cli` skill (Category 4)**
- Editing feature flags or any other application configuration

## Stop Condition

If a step cannot be completed using any of the permitted categories above, STOP immediately. Return a detailed report of what was completed, where the block occurred, and what approach was tried. Do not improvise or use unapproved tools.

## Known limits of these controls

Some controls this plugin relies on are instructions to the agent, not boundaries the platform enforces. They are recorded here so nobody reads this file as a security guarantee.

**Navigation targets and eval payloads (Category 1) are unenforced.** `Bash(playwright-cli:*)` grants every subcommand with every argument. Narrowing it would not help, because the subcommands that carry egress risk (`goto`, `eval`, `run-code`) are exactly the ones the pipeline needs. The enforcement point for this is a `PreToolUse` hook on `Bash`, which the official documentation names as the reliable alternative to argument-constraining permission patterns. That hook is not yet implemented.

**The agent-level Bash grant is not a hard boundary.** The scoper, mapper, health-checker and test-runner agents list unscoped `Bash` because a script-scoped grant does not work in an agent's `tools:`: tested on Claude Code 2.1.x, `${CLAUDE_PLUGIN_ROOT}` is not substituted there, and path-glob forms such as `Bash(*/scripts/repo-diff.sh:*)` do not match, so every run would prompt. Literal-prefix grants do work there, which is why the runner also lists `Bash(playwright-cli:*)` (see the Category 1 entry above), but a plugin script has no install-independent literal prefix. Listing `Bash` makes the tool available without approving any command. Script scoping lives in each invoked skill's `allowed-tools`, where the skills documentation states the plugin and skill path placeholders are substituted: the planning skills pre-approve only `repo-diff.sh`, `checking-localhost-web-health` only its preflight and health-check scripts, and `running-playwright-tests` its three scripts plus `ls`. The planning agents' bodies also limit their `Bash` use to `repo-diff.sh`. Any other command follows the session's permission rules and mode: it prompts in default mode, and runs unprompted under `bypassPermissions` or an allow rule the user already has. A `PreToolUse` hook on `Bash` would make it a hard boundary.
