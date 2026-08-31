# Redirecting Stripe write requests

This skill is read-only apart from advancing an already-attached test clock. When a request would create, update, cancel, or delete Stripe state — or would manufacture test state some other way — route it to the sanctioned flow instead of doing it through Stripe. Two rules bound this, and both resolve to "route the work elsewhere," never "do it through Stripe":

- **No Stripe writes** — the sole exception is advancing an already-attached test clock. Refuse to create, update, cancel, or delete any Stripe object, and give the read-only rule as the reason, not a capability limit. Never offer a raw `stripe` call as a workaround.
- **No shortcuts around the application's own flows** — even setting the write rule aside, do not use Stripe, a direct database edit, or a feature-flag flip to manufacture state that Bitwarden's own product flows produce. "It's faster" is not a reason to bypass this. Driving the real flow is also the more faithful test, since it exercises the code under review.

Redirect to the sanctioned path instead:

| The request                                            | Where it belongs                                                                              |
| ------------------------------------------------------ | --------------------------------------------------------------------------------------------- |
| Create a coupon, or apply a discount to a subscription | Admin portal, or the web vault purchase flow                                                  |
| Create a paid organization or subscription             | web vault organization creation flow, using a test card                                       |
| Cancel a subscription                                  | web vault or Admin portal cancellation flow                                                   |
| Make an org "look subscribed"                          | the application's own purchase flow — never a direct database row edit or a feature-flag flip |

Reading Stripe data to _drive_ one of those flows is the canonical permitted case — for example, listing the coupon ids that already exist in the test account so the Admin portal import has real values to use.
