---
name: using-stripe-cli
description: Query read-only Stripe test data and advance an already-attached test clock using the Stripe CLI. Invoked by the test-runner during Category 4 steps of the Bitwarden web test pipeline when data cannot be obtained through the web UI (for example listing coupon IDs for an Admin portal import). Read-only, except the single permitted write of advancing an existing test clock.
---

# Using the Stripe CLI

Translate a Category 4 data need into Stripe CLI commands, run them, and interpret the JSON. This skill is read-only, with one exception: advancing an already-attached test clock. Everything else that creates, updates, or deletes Stripe state is forbidden by `references/tool-policy.md` and is out of scope here.

## Test mode only

The Stripe CLI defaults to test mode but is NOT test-mode-only: a per-command `--live` flag exists, and `stripe login` provisions a live-mode key alongside the sandbox key. Therefore:

- Never pass `--live` to any command.
- Never pass `--api-key` with a live secret key (`sk_live_…`).

The `Bash(stripe get:*)` grant's wildcard matches any arguments, so it cannot block `--live` or a live key. This instruction is the only control. If a step would require live data, STOP and report it as an obstacle instead of running it.

If `stripe` fails with "command not found" or an authentication error, report that the Stripe CLI needs to be installed and authenticated (`stripe login`); do not improvise another data source.

## How the CLI works (read queries)

Two ways to read:

```bash
# Resource commands
stripe customers retrieve cus_abc123
stripe subscriptions list --customer=cus_abc123 --limit=10
stripe events list --type=customer.subscription.updated --limit=5

# Raw API (for endpoints without a resource command)
stripe get /v1/customers/cus_abc123
```

Key flags:

- `--limit=N`: number of results (default 10, max 100)
- `--expand=field`: inline a nested object (repeatable). For raw `stripe get`, use `-d 'expand[]=field'`
- `-d "nested[param]=value"`: set a nested parameter
- `--starting-after=id` / `--ending-before=id`: paginate

Expand nested objects when the question needs them rather than making extra round trips:

```bash
stripe subscriptions retrieve sub_abc123 --expand=default_payment_method
stripe invoices retrieve in_abc123 --expand=charge --expand=subscription
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
- **Event tracing:** `stripe events list` filters by type, not object ID; list by type and filter client-side. Events carry the object snapshot at event time.
- **Customer state:** expand `subscriptions` and use `list_payment_methods` for the full picture.

## The one permitted write: advancing an already-attached test clock

You may advance a test clock that is already attached to the subscription. You may NOT attach a clock. Attaching is a `[HUMAN]` step, not a CLI action available to you.

Advance a clock by N days, waiting for it to return to `ready` before each subsequent advance:

```bash
CLOCK_ID="clock_xxxxx"   # from the subscription's test_clock field
DAYS=8
for i in $(seq 1 "$DAYS"); do
  CURRENT=$(stripe get /v1/test_helpers/test_clocks/$CLOCK_ID | python3 -c "import sys,json; print(json.load(sys.stdin)['frozen_time'])")
  NEW_TIME=$((CURRENT + 86400))
  stripe post /v1/test_helpers/test_clocks/$CLOCK_ID/advance -d "frozen_time=$NEW_TIME" > /dev/null
  while true; do
    STATUS=$(stripe get /v1/test_helpers/test_clocks/$CLOCK_ID | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])")
    [ "$STATUS" = "ready" ] && break
    sleep 2
  done
done
```

This uses only `stripe get` (read) and `stripe post /v1/test_helpers/test_clocks/<id>/advance` (the sole permitted write), which are the grants the test-runner holds.
