# Supported Stripe Resources (read-only)

Only read operations are listed. Creating, updating, deleting, attaching, detaching, paying, voiding, finalizing, cancelling, refunding, or closing any resource is out of scope for this read-only skill. The one permitted write, advancing an already-attached test clock, is documented in the skill body, not here.

> **Substitute the plugin root before running.** These commands use the `${CLAUDE_PLUGIN_ROOT}/` placeholder for readability. When the skill runs, `${CLAUDE_PLUGIN_ROOT}` is already set in its environment and the shell expands it for you, and it is the same variable the skill's `allowed-tools` grant is written against, so an expanded invocation auto-approves without a prompt. (`${CLAUDE_SKILL_DIR}` is deliberately not used here: it is not currently substituted inside `allowed-tools` permission matchers, so a grant written against it would prompt on every call.) If you run one by hand from a plain shell where the variable is not set, resolve it first with `printenv CLAUDE_PLUGIN_ROOT` (or set it to this plugin's absolute directory) and invoke the script by that absolute path; a relative path would not match the grant.

Every operation below is a `${CLAUDE_PLUGIN_ROOT}/skills/using-stripe-cli/scripts/stripe_cli.py read --path <path>` call. The base path retrieves or lists depending on whether an ID is appended; append `/search` for search, and append `/<id>/<sub-resource>` for a nested list such as a customer's payment methods.

Search paths (`.../search`) require a `query` parameter, for example `${CLAUDE_PLUGIN_ROOT}/skills/using-stripe-cli/scripts/stripe_cli.py read --path /v1/customers/search --param query="email:'qa@example.com'"`.

## customers

- **Base path**: `/v1/customers` (append `/<id>` to retrieve, `/search` to search, `/<id>/payment_methods` to list payment methods)
- **Read operations**: retrieve, list, search, list_payment_methods
- **Key fields**: id, email, name, invoice_settings.default_payment_method, subscriptions, balance, metadata, created
- **Common queries**: "Does this customer have a default payment method?", "What subscriptions does this customer have?", "Look up customer by email"

## subscriptions

- **Base path**: `/v1/subscriptions` (append `/<id>` to retrieve, `/search` to search)
- **Read operations**: retrieve, list, search
- **Key fields**: id, customer, status, items (each with current_period_start, current_period_end), default_payment_method, cancel_at_period_end, canceled_at, latest_invoice, test_clock, metadata
- **Common queries**: "What's the status of this subscription?", "When does it renew?", "What plan/price is on this subscription?", "Is a test clock attached?"

## invoices

- **Base path**: `/v1/invoices` (append `/<id>` to retrieve, `/search` to search)
- **Read operations**: retrieve, list, search
- **Key fields**: id, customer, parent.subscription_details.subscription (the related subscription; the top-level `subscription` field was removed in `2025-03-31.basil`), status, amount_due, amount_paid, amount_remaining, due_date, lines, payments (list; the top-level `payment_intent` field was removed in `2025-03-31.basil` — a payment intent is now reached at `payments.data.payment.payment_intent`), hosted_invoice_url, metadata
- **Common queries**: "Show me recent invoices for this customer", "What's the payment status?"

## payment_intents

- **Base path**: `/v1/payment_intents` (append `/<id>` to retrieve, `/search` to search)
- **Read operations**: retrieve, list, search
- **Key fields**: id, amount, currency, status, customer, payment_method, last_payment_error, latest_charge (the `charges` list was replaced by this singular field in API `2022-11-15`), metadata, created
- **Common queries**: "Why did this payment fail?", "What's the status of this payment?"

## payment_methods

- **Base path**: `/v1/payment_methods` (append `/<id>` to retrieve)
- **Read operations**: retrieve, list
- **Key fields**: id, type, card (last4, brand, exp_month, exp_year), customer, billing_details, created
- **Common queries**: "What payment methods does this customer have?", "Is this card expired?"

## events

- **Base path**: `/v1/events` (append `/<id>` to retrieve)
- **Read operations**: retrieve, list
- **Key fields**: id, type, data.object, created, request
- **Common queries**: "What events happened for this subscription?", "What triggered this change?"

## charges

- **Base path**: `/v1/charges` (append `/<id>` to retrieve, `/search` to search)
- **Read operations**: retrieve, list, search
- **Key fields**: id, amount, currency, status, customer, payment_intent, failure_code, failure_message, outcome, refunded, metadata
- **Common queries**: "Why was this charge declined?", "Show me the outcome details"

## prices

- **Base path**: `/v1/prices` (append `/<id>` to retrieve, `/search` to search)
- **Read operations**: retrieve, list, search
- **Key fields**: id, product, unit_amount, currency, recurring (interval, interval_count), active, type, metadata
- **Common queries**: "What's the price on this product?", "Show me all recurring prices"

## products

- **Base path**: `/v1/products` (append `/<id>` to retrieve, `/search` to search)
- **Read operations**: retrieve, list, search
- **Key fields**: id, name, description, active, default_price, metadata, created
- **Common queries**: "What products do we have?", "Is this product active?"

## coupons

- **Base path**: `/v1/coupons` (append `/<id>` to retrieve)
- **Read operations**: retrieve, list
- **Key fields**: id, name, percent_off, amount_off, currency, duration, duration_in_months, max_redemptions, times_redeemed, valid, metadata, created
- **Common queries**: "List the coupon IDs in our Stripe test account for the Admin portal import", "Is this coupon still valid?", "What discount does this coupon apply?"

## promotion_codes

- **Base path**: `/v1/promotion_codes` (append `/<id>` to retrieve)
- **Read operations**: retrieve, list
- **Key fields**: id, code, coupon, active, customer, expires_at, max_redemptions, times_redeemed, restrictions, metadata, created
- **Common queries**: "What promotion codes map to this coupon?", "Is this promo code active?"

## subscription_schedules

- **Base path**: `/v1/subscription_schedules` (append `/<id>` to retrieve)
- **Read operations**: retrieve, list
- **Key fields**: id, customer, subscription, status, current_phase, phases (items, start_date, end_date), end_behavior, metadata, created
- **Common queries**: "Does this subscription have a schedule?", "What phases are on this schedule?", "When does the next phase start?"
