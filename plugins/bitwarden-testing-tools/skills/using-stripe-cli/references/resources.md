# Supported Stripe Resources (read-only)

Only read operations are listed. Creating, updating, deleting, attaching, detaching, paying, voiding, finalizing, cancelling, refunding, or closing any resource is forbidden by tool-policy Category 4. The one permitted write, advancing an already-attached test clock, is documented in the skill body, not here.

Every operation below is a `stripe_cli.py read --path <path>` call. The base path retrieves or lists depending on whether an ID is appended; append `/search` for search, and append `/<id>/<sub-resource>` for a nested list such as a customer's payment methods.

## customers

- **Base path**: `/v1/customers` (append `/<id>` to retrieve, `/search` to search, `/<id>/payment_methods` to list payment methods)
- **Read operations**: retrieve, list, search, list_payment_methods
- **Key fields**: id, email, name, invoice_settings.default_payment_method, subscriptions, balance, metadata, created
- **Common queries**: "Does this customer have a default payment method?", "What subscriptions does this customer have?", "Look up customer by email"

## subscriptions

- **Base path**: `/v1/subscriptions` (append `/<id>` to retrieve, `/search` to search)
- **Read operations**: retrieve, list, search
- **Key fields**: id, customer, status, current_period_start, current_period_end, items, default_payment_method, cancel_at_period_end, canceled_at, latest_invoice, test_clock, metadata
- **Common queries**: "What's the status of this subscription?", "When does it renew?", "What plan/price is on this subscription?", "Is a test clock attached?"

## invoices

- **Base path**: `/v1/invoices` (append `/<id>` to retrieve, `/search` to search)
- **Read operations**: retrieve, list, search
- **Key fields**: id, customer, subscription, status, amount_due, amount_paid, amount_remaining, due_date, lines, payment_intent, hosted_invoice_url, metadata
- **Common queries**: "Show me recent invoices for this customer", "What's the payment status?"

## payment_intents

- **Base path**: `/v1/payment_intents` (append `/<id>` to retrieve, `/search` to search)
- **Read operations**: retrieve, list, search
- **Key fields**: id, amount, currency, status, customer, payment_method, last_payment_error, charges, metadata, created
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

## subscription_schedules

- **Base path**: `/v1/subscription_schedules` (append `/<id>` to retrieve)
- **Read operations**: retrieve, list
- **Key fields**: id, customer, subscription, status, current_phase, phases (items, start_date, end_date), end_behavior, metadata, created
- **Common queries**: "Does this subscription have a schedule?", "What phases are on this schedule?", "When does the next phase start?"
