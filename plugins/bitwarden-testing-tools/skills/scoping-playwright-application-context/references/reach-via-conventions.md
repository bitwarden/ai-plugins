# Reach via conventions

Conventions for writing `Reach via:` recipes and `[HUMAN]` verification points in the Application Context that `scoping-playwright-application-context` produces.

For states with `Reachable by playwright: no`, the `Reach via:` recipe documents how the test executor or a human can drive the application into the state using tools beyond playwright-cli. Free-form prose with these conventions:

- **Reference flows by slug:** `Run flow:create-paid-org with orgName=…`
- **Reference skills by name:** `Use the bitwarden-stripe-tools:using-stripe-cli skill to advance the test clock 8 days (two 4-day batches).`
- **Mark human steps explicitly:** `[HUMAN] Attach a Stripe test clock to the subscription.` The bracketed `[HUMAN]` prefix is a structural marker — downstream consumers detect it deterministically, and the test run stops at it until a person acts. Use it only for an action no granted tool can perform.
- **Mark `[HUMAN]` verification points the same way:** when confirming a state requires a check that no granted tool can perform (a database-field inspection, or another check the tool policy (`${CLAUDE_PLUGIN_ROOT}/references/playwright-tool-policy.md`) disallows), record it as a verification point prefixed with `[HUMAN]`.
- **Never mark a granted skill's work `[HUMAN]`:** a read through the `bitwarden-stripe-tools:using-stripe-cli` skill (Category 4) or the `bitwarden-mailcatcher-tools:reading-mailcatcher-api` skill (Category 2) is something the test executor runs itself. Write it as a step or verification point that names the skill, with no `[HUMAN]` prefix — for example `Use the bitwarden-stripe-tools:using-stripe-cli skill to read the subscription; its status is trialing`. On an out-of-band `Route: n/a` state, use the `stdout contains` verification-point form, with the Selector naming the skill's read.
- **Never write a feature-flag requirement as a step:** a flag the run depends on belongs in the `## Required Feature Flags` section, not in a `Reach via:` recipe, a `[HUMAN]` step, or a verification point.
