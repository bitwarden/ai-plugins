# Bitwarden Playwright Tool Policy

Steps fall into four categories during web test planning and execution, and everything else is blocked:

1. Web UI interactions, driven by the external `playwright-cli` skill (Category 1).
2. Email reading, owned by the `bitwarden-mailcatcher-tools:reading-mailcatcher-api` skill (Category 2).
3. External trigger simulation, for actions initiated by a system outside the Bitwarden application (Category 3).
4. Read-only Stripe data queries, owned by the `bitwarden-stripe-tools:using-stripe-cli` skill (Category 4).

The sections below give the constraints for each category present in this pipeline.

Categories 2 and 4 live in vendor plugins this plugin depends on, `bitwarden-mailcatcher-tools` and `bitwarden-stripe-tools`. Reach them only by invoking the owning skill by its plugin-qualified name: invoking the skill is what applies its script grant, and a script path inside another plugin does not resolve from this one.

## Category 1 - Web UI Interactions (default)

Use the `playwright-cli` skill for all interactions a user would perform in the browser. This is the default for everything, including verifying test results. If the outcome is visible in the UI, assert it via the browser, not via an API call. The browser is driven by the external `playwright-cli` skill, which this pipeline declares as a prerequisite.

**Navigation targets are constrained.** `playwright-cli goto` and `playwright-cli open` may target only `localhost`, `127.0.0.1`, `::1`, or a `bitwarden.test` origin. A plan step naming any other origin is an obstacle to report, not a step to execute, however plausibly it is worded. Do not attempt to work around this constraint.

## Category 2 - Email Reading

Reading an email during a test step (verification links, magic links, OTP codes) is owned by the `bitwarden-mailcatcher-tools:reading-mailcatcher-api` skill. Invoke it for the exit-code contract, the reason the browser cannot reach Mailcatcher, the argument detail, and the grant for its reader script.

## Category 3 - External Trigger Simulation

Some flows begin with an action that a system _outside_ the Bitwarden application initiates — a marketing-site form post, a third-party webhook, a scheduled job — that no Bitwarden service fires on its own (for example, the trial verification email POST in the billing known-flows). Simulating that initiator with a direct request is permitted only when all of these hold: the trigger genuinely originates outside the application and is not a UI action a user could perform in the browser (those stay in Category 1); the target is a `localhost`, `127.0.0.1`, `::1`, or `bitwarden.test` origin; and the request only kicks off the flow under test rather than fabricating its result state. A flow step using it must be marked `**EXTERNAL TRIGGER**` and name the external system it stands in for. Anything that instead substitutes for a user's own browser action, or manufactures state the application's own flows can produce, is blocked under Never Permitted.

## Category 4 - Stripe Data Queries (read-only)

Read-only Stripe test-mode queries, including a preview of a subscription's next invoice, plus the single permitted write of advancing an already-attached test clock, are owned by the `bitwarden-stripe-tools:using-stripe-cli` skill. Invoke it for the wrapper's commands, exit codes, and grant. The invoice preview is sent as a POST to `/v1/invoices/create_preview`, but it creates and changes nothing, so it counts as a read. Stripe is never used to set up state the application's own flows can create, and never for any other write.

## Never Permitted

- Direct database queries
- API calls that substitute for UI actions a user could perform in the browser
- Using API calls to verify test results when the outcome is observable in the UI (always assert via `playwright-cli` instead)
- CLI tools not related to service startup (the `bitwarden-stripe-tools:using-stripe-cli` wrapper script excepted when used read-only per Category 4)
- Stripe write operations, meaning any request that changes Stripe state whatever its HTTP method — creating coupons, modifying subscriptions, updating customers, or any other create, update, or delete — **except the single sanctioned test-clock advance owned by the `bitwarden-stripe-tools:using-stripe-cli` skill (Category 4)**. The invoice preview's POST changes nothing and is a Category 4 read, not a write.
- Editing feature flags or any other application configuration

## Stop Condition

If a step cannot be completed using any of the permitted categories above, STOP immediately. Return a detailed report of what was completed, where the block occurred, and what approach was tried. Do not improvise or use unapproved tools.

## Known limits of these controls

This section records where the controls in this plugin fall short of a hard boundary, so nobody reads this file as a security guarantee.

**The planning agents hold no Bash; their Skill use rests on a hook.** The scoper and mapper agents do not list `Bash` in `tools:`. On macOS, Linux, and WSL, a subagent that holds `Bash` loses the Grep and Glob tools, so the scoper could not search code if it held `Bash`. A script-scoped grant is no substitute: tested on Claude Code 2.1.x, `${CLAUDE_PLUGIN_ROOT}` is not substituted in an agent's `tools:`, and path-glob forms such as `Bash(*/scripts/repo-diff.sh:*)` do not match. Instead, the `start-playwright-test` orchestrator runs `scripts/repo-diff.sh` in the main session under its skill's `allowed-tools` grant, and passes the changed files to both agents as the `diff-<timestamp>.md` artifact; `repo-diff.sh` still checks each repo path against its basename allowlist. The main session is outside the hook, so that grant and the script's allowlist are the controls on the orchestrator's call. A planning skill run on its own, directly or in evals, runs `repo-diff.sh` itself under the session's normal permission rules and mode. The plugin's `PreToolUse` hook, `hooks/restrict_planning_agents.py`, blocks any `Bash` call from the scoper, the mapper, and the context gatherer, as a second layer in case a later edit adds `Bash` back. It also limits those three to their own skill, because a skill that runs in a forked context executes its `Bash` as a different agent type, outside the check. The block applies before permission rules are evaluated, so while the hook runs it holds in every permission mode, including `bypassPermissions`. Three limits remain. The block depends on the hook running: if `python3` is missing, the hook exceeds its 5-second timeout or cannot run in the shell Claude Code uses for hooks, or hooks are turned off by `disableAllHooks` or managed policy, Claude Code lets the call proceed. On Windows that includes a machine without Git Bash, where hooks run in PowerShell and the hook's POSIX command fails, and one where Python is installed as `python` or `py` but not `python3`; there, every `Bash` and `Skill` call in a session with this plugin enabled also shows a non-blocking hook-error notice. The hook recognizes the agents by the `agent_type` field Claude Code passes it, matching the plugin name as the first `:`-separated segment and the agent name as the last, so a change to that format would stop it recognizing them. And the skill limit assumes each agent's own skill runs in the agent's context and invokes no other skill: if a later version of one of them, including `bitwarden-atlassian-tools:researching-jira-issues` from another plugin, ran in a forked context, it would reopen the shell path. The hook restricts only these three agents: other agents in this plugin, including any that hold `Skill`, follow the session's normal permission rules and mode.
