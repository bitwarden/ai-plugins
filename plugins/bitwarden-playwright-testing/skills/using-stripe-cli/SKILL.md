---
name: using-stripe-cli
description: Query read-only Stripe test data and advance an already-attached test clock using the Stripe CLI. Invoked by the test-runner during Category 4 steps of the Bitwarden web test pipeline when data cannot be obtained through the web UI (for example listing coupon IDs for an Admin portal import). Read-only, except the single permitted write of advancing an existing test clock.
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/stripe_cli.py *)
---

# Using the Stripe CLI

Translate a Category 4 data need into a wrapper call, run it, and interpret the JSON. This skill is read-only, with one exception: advancing an already-attached test clock. Everything else that creates, updates, or deletes Stripe state is forbidden by `references/tool-policy.md` and is out of scope here.

## Test mode only

All Stripe access goes through the co-located wrapper:

```
${CLAUDE_SKILL_DIR}/scripts/stripe_cli.py read --path /v1/<resource> [--param k=v ...]
${CLAUDE_SKILL_DIR}/scripts/stripe_cli.py advance-clock --clock <clock_id> --days <n>
```

The wrapper builds every command from scratch and never forwards a caller-supplied flag, so `--live` cannot appear in anything it issues. The CLI defaults to test mode without that flag. This is enforcement in code, not an instruction. Do not invoke `stripe` directly; the test-runner holds no grant for it.

Nothing needs to be configured beyond `stripe login`. The wrapper uses the CLI's own test mode credentials.

If a step would require live data, STOP and report it as an obstacle.

If the wrapper exits 21, the environment has `STRIPE_API_KEY` set to a live key, which the Stripe CLI reads in preference to its own configuration. Report that as an obstacle rather than working around it. If it exits 1 with a "not installed" message, report that the Stripe CLI needs installing and `stripe login`.

## How the CLI works (read queries)

Every read is a `read --path` call against a `/v1/` resource:

```bash
${CLAUDE_SKILL_DIR}/scripts/stripe_cli.py read --path /v1/customers/cus_abc123
${CLAUDE_SKILL_DIR}/scripts/stripe_cli.py read --path /v1/subscriptions --param customer=cus_abc123 --param limit=10
${CLAUDE_SKILL_DIR}/scripts/stripe_cli.py read --path /v1/events --param type=customer.subscription.updated --param limit=5
```

Key `--param` values:

- `limit=N`: number of results (default 10, max 100)
- `expand[]=field`: inline a nested object (repeatable)
- `nested[param]=value`: set a nested parameter
- `starting_after=id` / `ending_before=id`: paginate

Expand nested objects when the question needs them rather than making extra round trips:

```bash
${CLAUDE_SKILL_DIR}/scripts/stripe_cli.py read --path /v1/subscriptions/sub_abc123 --param expand[]=default_payment_method
${CLAUDE_SKILL_DIR}/scripts/stripe_cli.py read --path /v1/invoices/in_abc123 --param expand[]=charge --param expand[]=subscription
```

See `references/resources.md` for the read operations and key fields of the resources you will most often query.

## Interpreting responses

- Lead with the direct answer; include the relevant IDs so the user can cross-reference in the Dashboard.
- Amounts are in the smallest currency unit, so divide by 100 for most currencies (1250 USD = `$12.50`); zero-decimal currencies like JPY use the value as-is. Always check the `currency` field.
- Timestamps are Unix epochs, so convert them to human-readable dates.
- Explain a status if it is not self-evident (for example `past_due` means the latest invoice payment failed and Stripe is retrying).
- Do not dump raw JSON unless explicitly asked; report the fields that answer the question.

## Read-only debugging patterns

- **Payment failures:** check the payment intent's `last_payment_error` and the charge's `outcome` / `failure_message` (expand the charge on the payment intent).
- **Subscription issues:** check `status`, the expanded `latest_invoice`, and recent `customer.subscription.*` events.
- **Event tracing:** `/v1/events` filters by type, not object ID; list by type and filter client-side. Events carry the object snapshot at event time.
- **Customer state:** expand `subscriptions` and use `list_payment_methods` for the full picture.

## The one permitted write: advancing an already-attached test clock

You may advance a test clock that is already attached to the subscription. You may NOT attach a clock. Attaching is a `[HUMAN]` step, not a CLI action available to you.

Advance a clock by N days with a single wrapper call; it waits for the clock to return to `ready` between each internal step so you do not have to:

```bash
${CLAUDE_SKILL_DIR}/scripts/stripe_cli.py advance-clock --clock <clock_id> --days 8
```

Eight days is the number that matters for driving a subscription to `unpaid`: Stripe's smart retry policy fires one payment retry per simulated day, and after eight failed attempts the subscription transitions to `unpaid` and fires `customer.subscription.updated`. Advancing fewer days will not reach that state.

The wrapper is the only granted path to this operation; the test-runner holds no grant for the `stripe` binary itself.
