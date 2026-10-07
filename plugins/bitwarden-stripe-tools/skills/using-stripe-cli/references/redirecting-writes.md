# Redirecting Stripe write requests

Route each request that would create, update, cancel, or delete Stripe state — or manufacture test state some other way — to the sanctioned flow that produces the same result. The read-only rule and the no-shortcuts rule that decide _when_ to redirect, and the canonical permitted case of reading Stripe data to _drive_ one of these flows, live in the skill body under "When to refuse"; this table is the _where_.

| The request                                                         | Where it belongs                                                                                                             |
| ------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Create a coupon, or apply a discount to a subscription              | Admin portal, or the web vault purchase flow                                                                                 |
| Create a paid organization or subscription                          | web vault organization creation flow, using a test card                                                                      |
| Cancel a subscription                                               | web vault or Admin portal cancellation flow                                                                                  |
| Make an org "look subscribed"                                       | the application's own purchase flow — never a direct database row edit or a feature-flag flip                                |
| Attach a test clock to an existing subscription                     | the Stripe Dashboard's "Run simulation" on that subscription, a manual step the user takes                                   |
| Any other Stripe write, such as a refund or a payment method update | the web vault or Admin portal flow that performs it; if no product flow does, report the request to the user as out of scope |
