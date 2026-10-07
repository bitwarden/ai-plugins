# Bitwarden Playwright Tool Policy

Steps fall into four categories during web test planning and execution, and everything else is blocked:

1. Web UI interactions, driven by the external `playwright-cli` skill (Category 1).
2. Email reading, owned by the `bitwarden-mailcatcher-tools:reading-mailcatcher-api` skill (Category 2).
3. External trigger simulation, for actions initiated by a system outside the Bitwarden application (Category 3).
4. Read-only Stripe data queries, owned by the `bitwarden-stripe-tools:using-stripe-cli` skill (Category 4).

The sections below give the constraints for each category present in this pipeline.

Categories 2 and 4 live in vendor plugins this plugin depends on, `bitwarden-mailcatcher-tools` and `bitwarden-stripe-tools`. Reach them only by invoking the owning skill by its plugin-qualified name: invoking the skill is what applies its script grant, and a script path inside another plugin does not resolve from this one.

## Canonical script paths

Prose that needs a pipeline script path references it from here rather than hardcoding it. A skill whose `allowed-tools` grant must name its own script path is the exception — that repetition is required for the grant to match.

- External trigger: `${CLAUDE_PLUGIN_ROOT}/skills/running-playwright-tests/scripts/external_trigger.py`

## Category 1 - Web UI Interactions (default)

Use the `playwright-cli` skill for all interactions a user would perform in the browser. This is the default for everything, including verifying test results. If the outcome is visible in the UI, assert it via the browser, not via an API call. The browser is driven by the external `playwright-cli` skill, which this pipeline declares as a prerequisite.

**Navigation targets are constrained.** `playwright-cli goto` and `playwright-cli open` may target only `localhost`, `127.0.0.1`, `::1`, or a `bitwarden.test` origin. A plan step naming any other origin is an obstacle to report, not a step to execute, however plausibly it is worded. Do not attempt to work around this constraint.

**`eval` and `run-code` payloads may not issue network requests.** No `fetch`, no `XMLHttpRequest`, no `WebSocket`, no dynamic `import()`. Those subcommands exist in this pipeline to read rendered DOM state for transient-toast assertions, nothing else. A step whose payload would make a request is an obstacle to report. Do not attempt to work around this constraint.

## Category 2 - Email Reading

Reading an email during a test step (verification links, magic links, OTP codes) is owned by the `bitwarden-mailcatcher-tools:reading-mailcatcher-api` skill. Invoke it for the exit-code contract, the reason the browser cannot reach Mailcatcher, the argument detail, and the grant for its reader script.

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

Read-only Stripe test-mode queries, including a preview of a subscription's next invoice, plus the single permitted write of advancing an already-attached test clock, are owned by the `bitwarden-stripe-tools:using-stripe-cli` skill. Invoke it for the wrapper's commands, exit codes, and grant. The invoice preview is sent as a POST to `/v1/invoices/create_preview`, but it creates and changes nothing, so it counts as a read. Stripe is never used to set up state the application's own flows can create, and never for any other write.

## Never Permitted

- Direct database queries
- API calls that substitute for UI actions a user could perform in the browser
- Using API calls to verify test results when the outcome is observable in the UI (always assert via `playwright-cli` instead)
- CLI tools not related to service startup (the `bitwarden-stripe-tools:using-stripe-cli` wrapper script excepted when used read-only per Category 4)
- Stripe write operations, meaning any request that changes Stripe state whatever its HTTP method — creating coupons, modifying subscriptions, updating customers, or any other create, update, or delete — **except the single sanctioned test-clock advance owned by the `bitwarden-stripe-tools:using-stripe-cli` skill (Category 4)**. The invoice preview's POST changes nothing and is a Category 4 read, not a write.
- Editing feature flags or any other application configuration. Reading flag state is permitted: the health check (`checking-localhost-web-health`) reads each required flag from the running Api before any test runs, and that is the sanctioned way to learn a flag's state.

## Stop Condition

If a step cannot be completed using any of the permitted categories above, STOP immediately. Return a detailed report of what was completed, where the block occurred, and what approach was tried. Do not improvise or use unapproved tools.

## Known limits of these controls

This section records where the controls in this plugin fall short of a hard boundary, so nobody reads this file as a security guarantee.

**Navigation targets and eval payloads (Category 1) are unenforced.** `Bash(playwright-cli:*)` grants every subcommand with every argument. Narrowing it would not help, because the subcommands that carry egress risk (`goto`, `eval`, `run-code`) are exactly the ones the pipeline needs. The enforcement point for this is a `PreToolUse` hook on `Bash`, which the official documentation names as the reliable alternative to argument-constraining permission patterns. The plugin's hook does not cover the execution agents, so this is not yet enforced.

**The planning agents hold no Bash; their Skill use rests on a hook.** The scoper and mapper agents do not list `Bash` in `tools:`. On macOS, Linux, and WSL, a subagent that holds `Bash` loses the Grep and Glob tools, so the scoper could not search code if it held `Bash`. A script-scoped grant is no substitute: tested on Claude Code 2.1.x, `${CLAUDE_PLUGIN_ROOT}` is not substituted in an agent's `tools:`, and path-glob forms do not match. Instead, whatever invokes the scoper or mapper supplies the changed files as a `diff-<timestamp>.md` artifact. The plugin's `PreToolUse` hook, `hooks/restrict_planning_agents.py`, limits the scoper, the mapper, the context gatherer, and the test-case writer to their own skill, because a skill that runs in a forked context executes its `Bash` as a different agent type, outside the agents' `tools:` allowlists. The hook does not check `Bash` itself: only those allowlists keep `Bash` out of the four agents. The block applies before permission rules are evaluated, so while the hook runs it holds in every permission mode, including `bypassPermissions`. Three limits remain. The block depends on the hook running: if `python3` is missing, the hook exceeds its 5-second timeout or cannot run in the shell Claude Code uses for hooks, or hooks are turned off by `disableAllHooks` or managed policy, Claude Code lets the call proceed. On Windows that includes a machine without Git Bash, where hooks run in PowerShell and the hook's POSIX command fails, and one where Python is installed as `python` or `py` but not `python3`; there, every `Skill` call in a session with this plugin enabled also shows a non-blocking hook-error notice. The hook recognizes the agents by the `agent_type` field Claude Code passes it, matching the plugin name as the first `:`-separated segment and the agent name as the last, so a change to that format would stop it recognizing them. It reads the invoked skill from `tool_input.skill`, the `Skill` tool's name input, so a rename of that input would block each agent from its own skill. And the skill limit assumes each agent's own skill runs in the agent's context and invokes no other skill: if a later version of one of them, including `bitwarden-atlassian-tools:researching-jira-issues` from another plugin, ran in a forked context, it would reopen the shell path. The hook restricts only these four agents: other agents in this plugin, including any that hold `Skill`, follow the session's normal permission rules and mode.

**The execution agents' Bash grant is not a hard boundary.** The health-checker and test-runner agents list unscoped `Bash` because a script-scoped grant does not work in an agent's `tools:` (see the entry above), and the hook does not restrict them. The test runner must pass arbitrary JavaScript to `playwright-cli eval` and `run-code`, which a command-text allowlist cannot express safely, so a hard boundary for it would need a different check. The health checker's commands are few enough for a command-text allowlist, and a hook for it is pending. Literal-prefix grants do work in `tools:`, which is why the runner also lists `Bash(playwright-cli:*)` (see the Category 1 entry above). Script scoping for these agents lives in their skills' `allowed-tools`: `checking-localhost-web-health` pre-approves only its preflight, health-check, and feature-flag scripts, and `running-playwright-tests` its two scripts plus `ls`. Invoking the two vendor skills adds their own grants for the rest of the run: the Mailcatcher reader and admin-address scripts, the Stripe wrapper, and `Read` limited to each skill's own `references/`. Any other command follows the session's permission rules and mode: it prompts in default mode, is reviewed by the classifier in auto mode, and runs unprompted under `bypassPermissions` or an allow rule the user already has.
