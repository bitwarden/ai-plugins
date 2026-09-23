# Reach via conventions

Conventions for writing `Reach via:` recipes and `[HUMAN]` verification points in the Application Context that `scoping-playwright-application-context` produces.

For states with `Reachable by playwright: no`, the `Reach via:` recipe documents how the test executor or a human can drive the application into the state using tools beyond playwright-cli. Free-form prose with these conventions:

- **Reference flows by slug:** `Run flow:create-paid-org with orgName=…`
- **Reference skills by name:** `Use the using-stripe-cli skill to advance the test clock 8 days (two 4-day batches).`
- **Mark human steps explicitly:** `[HUMAN] Attach a Stripe test clock to the subscription.` The bracketed `[HUMAN]` prefix is a structural marker — downstream consumers detect it deterministically.
- **Mark `[HUMAN]` verification points the same way:** when confirming a state requires a check the tool policy (`${CLAUDE_PLUGIN_ROOT}/references/playwright-tool-policy.md`) disallows (a database-field inspection, or any verification playwright cannot perform), record it as a verification point prefixed with `[HUMAN]`.
