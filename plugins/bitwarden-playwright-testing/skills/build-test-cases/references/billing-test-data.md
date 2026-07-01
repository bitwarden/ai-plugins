# Billing Test Data Reference

## Stripe Reference Data

### Stripe Test Mode

The local dev environment is configured with a **Stripe test mode API key** (`server/dev/secrets.json`). This means:

- The web vault payment form renders live Stripe Elements iframes that accept Stripe test card numbers
- Submitting the form makes real Stripe API calls in test mode — no actual charges occur
- A successful subscription purchase produces a real Stripe Customer and Subscription in test mode

### Stripe Test Card Numbers

| Card Number | Brand | Use |
|---|---|---|
| `4242 4242 4242 4242` | Visa | **Default — always succeeds** |
| `5555 5555 5555 4444` | Mastercard | Alternative success |

For all test cards: any future expiry (e.g., `12/29`), any 3-digit CVC (e.g., `123`), postal code `12345`.

Do NOT use decline-trigger cards (e.g., `4000 0000 0000 0002`) for setup — those are for testing failure paths, not creating a working subscription.

### Payment Form Iframe Selectors

> **Critical**: Stripe Elements payment fields are iframes embedded within the page. Use Playwright's `frameLocator` to target them — `fill()` on the outer page will not reach the Stripe input fields.

- Card number: `frameLocator('[title="Secure card number input frame"]')`
- Expiry: `frameLocator('[title="Secure expiration date input frame"]')`
- CVC: `frameLocator('[title="Secure CVC input frame"]')`

---

## Billing Policies

### How Personal Discounts Work

Personal subscription discounts are **Stripe coupons** that have been imported into the Bitwarden application. The checkout flow reads available discounts from the database and automatically applies any coupon the user is eligible for when the subscription is created — no manual application is needed or allowed.

Discounts apply to Premium personal subscriptions and Families organization plans only (not Teams, Enterprise, or other org tiers).

**Critical:** Discounts are never added to a Stripe customer or subscription directly via the Stripe API, the Admin portal, or any other mechanism. The only supported path is:
1. A coupon exists in Stripe (created there)
2. The coupon is imported into the Admin application for use in the Bitwarden discounts system
3. The user is eligible for that discount
4. The checkout flow applies it automatically during subscription creation

Never generate test steps that call the Stripe API to attach a coupon to a customer or subscription — that is not how the application works and would produce test state that does not reflect production behavior. To test discount display, read the coupon ID from Stripe (Category 4 — read-only) to ensure it is imported into the Admin application, then complete the premium purchase flow through the web UI; the discount will appear if the user is eligible.
