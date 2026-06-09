# Known Bitwarden States and Flows

Curated reference of validated, reusable test states and UI flows for the Bitwarden web application. Both catalogs are consumed by `exploring-application-context` (entries are copied verbatim) and drive `build-test-cases`. State slugs are referenced across both catalogs; consistency is enforced by the `exploring-application-context` skill's self-review checks.

---

## Known States

Reusable, pre-grounded setup states, written in the exact `## States` schema the `exploring-application-context` skill emits — so the skill copies an entry **verbatim** into its output (no transform, no re-grounding). Each route and verification point was derived from real source at authoring time (cited in `Source:`). When a cited element moves in the codebase, update the entry here once.

---

### state:authenticated-free-user

**State type:** setup

**Produced by:**
- flow:create-new-user-and-login

**Reachable by playwright:** yes

**UI projection:**
- Route: https://localhost:8080/#/vault
- Verification points:
  - Selector: heading "All vaults"
    - Selector type: role
    - Expectation: visible
    - Source: clients/apps/web/src/app/vault/individual-vault/vault-header/vault-header.component.ts:187 (default title from the `allVaults` i18n key, rendered as the page `<h1>` via clients/libs/components/src/header/header.component.html:7)

### state:authenticated-premium-user

**State type:** setup

**Produced by:**
- flow:purchase-premium-subscription

**Reachable by playwright:** yes

**UI projection:**
- Route: https://localhost:8080/#/settings/subscription/user-subscription
- Verification points:
  - Selector: heading "You have Premium"
    - Selector type: role
    - Expectation: visible
    - Source: clients/apps/web/src/app/billing/individual/subscription/cloud-hosted-account-subscription.component.html:16 (the `youHavePremium` i18n key rendered as the page `<h1>`)

### state:authenticated-with-paid-org

**State type:** setup

**Produced by:**
- flow:create-paid-org
- flow:complete-trial-signup-existing-user

**Reachable by playwright:** yes

**UI projection:**
- Route: https://localhost:8080/#/organizations/:organizationId/vault  (org-scoped dynamic URL; `/organizations/:organizationId` redirects to the `vault` child — clients/apps/web/src/app/admin-console/organizations/organization-routing.module.ts:79-81)
- Verification points:
  - Selector: link "Admin Console"
    - Selector type: role
    - Expectation: visible
    - Source: clients/apps/web/src/app/admin-console/organizations/layouts/organization-layout.component.html:3 (org side-nav logo `<bit-nav-logo [label]="'adminConsole' | i18n">` — an org-name-independent `aria-label` rendered via clients/libs/components/src/navigation/nav-logo.component.html:11)

### state:admin-portal-authenticated

**State type:** setup

**Produced by:**
- flow:authenticate-admin-portal

**Reachable by playwright:** yes

**UI projection:**
- Route: http://localhost:62911
- Verification points:
  - Selector: heading "Dashboard"
    - Selector type: role
    - Expectation: visible
    - Source: server/src/Admin/Views/Home/Index.cshtml:55 (static `<h1>Dashboard</h1>` on the authenticated Admin home, served by server/src/Admin/Controllers/HomeController.cs:30)

### state:trialing-org-with-payment

**State type:** setup

**Produced by:**
- flow:complete-trial-signup-with-payment

**Reachable by playwright:** yes

**UI projection:**
- Route: https://localhost:8080/#/organizations/:organizationId/vault  (the producer flow ends on the `/#/trial-initiation` "Confirmation Details" step — clients/apps/web/src/app/billing/trial-initiation/complete-trial-initiation/complete-trial-initiation.component.html:55 — whose "Get started" button routes to the org vault — same file:67-70)
- Verification points:
  - Selector: link "Admin Console"
    - Selector type: role
    - Expectation: visible
    - Source: clients/apps/web/src/app/admin-console/organizations/layouts/organization-layout.component.html:3 (org side-nav logo, org-name-independent `aria-label` rendered via clients/libs/components/src/navigation/nav-logo.component.html:11)

### state:trialing-org-without-payment

**State type:** setup

**Produced by:**
- flow:complete-trial-signup-without-payment

**Reachable by playwright:** yes

**UI projection:**
- Route: https://localhost:8080/#/organizations/:organizationId/vault  (same landing as the with-payment variant — only the billing step is skipped; the "Confirmation Details" step's "Get started" button routes to the org vault — clients/apps/web/src/app/billing/trial-initiation/complete-trial-initiation/complete-trial-initiation.component.html:67-70)
- Verification points:
  - Selector: link "Admin Console"
    - Selector type: role
    - Expectation: visible
    - Source: clients/apps/web/src/app/admin-console/organizations/layouts/organization-layout.component.html:3 (org side-nav logo, org-name-independent `aria-label` rendered via clients/libs/components/src/navigation/nav-logo.component.html:11)

### state:trial-verification-email-received

**State type:** setup

**Produced by:**
- flow:trigger-trial-verification-email

**Reachable by playwright:** no
**If no — why:** non-UI intermediate state — verified by reading the trial-initiation email from Mailcatcher, not by a rendered page. The check is automated (a script), not a human step.
**Reach via:**
- Run flow:trigger-trial-verification-email (its external-trigger curl sends the verification email).
- Run `${CLAUDE_PLUGIN_ROOT}/skills/reading-mailcatcher-api/scripts/read-mailcatcher.sh --recipient <email> --pattern "Verify"`; a trial-initiation URL printed on stdout confirms the state (exit 1 / `NO_MATCH` means the email has not arrived yet).

**UI projection:**
- Route: n/a
- Verification points:
  - Selector: trial-initiation URL on stdout from `read-mailcatcher.sh --recipient <email> --pattern "Verify"`
    - Selector type: text
    - Expectation: stdout contains a `https://localhost:8080/#/trial-initiation?...` URL
    - Source: ${CLAUDE_PLUGIN_ROOT}/skills/reading-mailcatcher-api/scripts/read-mailcatcher.sh

---

## Known Flows

Each flow can be used by `build-test-cases` either as a precondition-producing setup flow (referenced by name) or as the action sequence a test exercises (composed inline with assertions).

Entry schema:

- **Use when:** high-level summary of the situations this flow fits
- **Parameters:** comma-separated placeholder names (e.g., `email`, `password`, `orgName`), or "none"
- **Precondition state:** `state:<slug>` that must hold before running this flow — or "none"
- **Steps:** numbered atomic UI actions with selectors and values; each step that produces a visible response carries an inline `- Feedback:` sub-item describing it (toast, redirect, modal, element enters/leaves the DOM)
- **Post-condition state(s):**
  - `Default: state:<slug>` — the terminal state the flow produces by default
  - `When <condition>: state:<slug>` — branch states when the post-condition diverges (e.g., feature-flag-gated behavior)

### flow:create-new-user-and-login

- **Use when:** Any test that requires a fresh authenticated user account with no prior subscription or organization state.
- **Parameters:** `email`, `password`
- **Precondition state:** none
- **Steps:**
  1. Navigate to `https://localhost:8080/#/signup`
  2. Fill the Email field with `<email>`
  3. (Optional) Fill the Name field
  4. Click Continue
     - Feedback: "Check your email" confirmation state appears
  5. Run `read-mailcatcher.sh --recipient <email> --pattern "Verify"` to fetch the verification email; stdout is the magic-link URL
  6. Navigate to the magic-link URL (it targets `https://localhost:8080/#/finish-signup?...`)
     - Feedback: finish-signup form appears
  7. Fill the Master Password field with `<password>` (must be ≥12 characters)
  8. Fill the Confirm Master Password field with `<password>`
  9. Click Create Account
     - Feedback: redirect to the vault
- **Post-condition state(s):**
  - Default: state:authenticated-free-user

---

### flow:purchase-premium-subscription

- **Use when:** Any test that requires the user to already hold an active Premium subscription — subscription management page, premium-feature access, discount badge display (any eligible Stripe coupon imported to Admin portal applies automatically at checkout; see `build-test-cases/references/billing-test-data.md`), etc.
- **Parameters:** none (uses defaults documented in `build-test-cases/references/billing-test-data.md`)
- **Precondition state:** state:authenticated-free-user
- **Steps:**
  1. Navigate to `https://localhost:8080/#/settings/subscription/premium`
     - Feedback: two pricing cards (Premium and Families) visible
  2. Click the "Upgrade to Premium" button on the Premium pricing card
  3. In the Payment Method section, fill the Stripe card number iframe (`frameLocator('[title="Secure card number input frame"]')`): `4242424242424242`
  4. Fill the expiry iframe (`frameLocator('[title="Secure expiration date input frame"]')`): `12/29`
  5. Fill the CVC iframe (`frameLocator('[title="Secure CVC input frame"]')`): `123`
  6. In the Billing Address section, set Country to `United States` and fill the Postal Code field with `12345`
  7. Click the "Upgrade" button
     - Feedback: dialog closes; redirect to `https://localhost:8080/#/settings/subscription/user-subscription`; the subscription management view is visible
- **Post-condition state(s):**
  - Default: state:authenticated-premium-user

---

### flow:create-paid-org

- **Use when:** Testing features that require a paid organization (Teams, Enterprise, Families, etc.) — including discount badge display on a Families organization (any eligible Stripe coupon imported to Admin portal applies automatically at checkout; see `build-test-cases/references/billing-test-data.md` for the discount mechanism).
- **Parameters:** `orgName`, `billingEmail`, `planTier`
- **Precondition state:** state:authenticated-free-user
- **Steps:**
  1. Navigate to `https://localhost:8080/#/create-organization`
  2. Select `<planTier>` (lowest plan tier that supports the features being tested)
  3. Fill in Organization Name with `<orgName>` and Billing Email with `<billingEmail>`
  4. In the Payment Information section, select Credit Card
  5. Fill the card number iframe (`frameLocator('[title="Secure card number input frame"]')`): `4242424242424242`
  6. Fill the expiry iframe (`frameLocator('[title="Secure expiration date input frame"]')`): `12/29`
  7. Fill the CVC iframe (`frameLocator('[title="Secure CVC input frame"]')`): `123`
  8. Set Country to `United States` and fill the Postal Code field with `12345`
  9. Submit the form
     - Feedback: success redirect to the new org's vault or settings page
- **Post-condition state(s):**
  - Default: state:authenticated-with-paid-org

---

### flow:trigger-trial-verification-email

- **Use when:** Setting up the first stage of any trial-initiation flow (with or without payment, new or existing user) — produces the verification email and retrieves the trial-initiation URL.
- **Parameters:** `email`, `productTier`, `products`, `trialLength`, `paymentOptional`
- **Precondition state:** none
- **Steps:**
  1. **EXTERNAL TRIGGER** — simulate the marketing site call with curl:
     ```bash
     curl -s -X POST http://localhost:33656/accounts/trial/send-verification-email \
       -H "Content-Type: application/json" \
       -d '{
         "email": "<email>",
         "name": "Test User",
         "receiveMarketingEmails": false,
         "productTier": <productTier>,
         "products": <products>,
         "trialLength": <trialLength>,
         "paymentOptional": <paymentOptional>
       }'
     ```
     Reference values — `productTier`: `0` = Free, `1` = Teams, `2` = Enterprise, `3` = Families. `products`: `1` = PasswordManager, `2` = SecretsManager. `paymentOptional`: `true` skips the payment step in the downstream completion flow; `false` requires payment.
  2. Run `read-mailcatcher.sh --recipient <email> --pattern "Verify"` to read the verification email; stdout is the trial-initiation URL — capture it for the next flow.
     - Feedback: trial-initiation URL is available on stdout
- **Post-condition state(s):**
  - Default: state:trial-verification-email-received

---

### flow:complete-trial-signup-with-payment

- **Use when:** Completing a trial signup that requires a payment method (the marketing-site call set `paymentOptional=false`).
- **Parameters:** `password`, `orgName`, `billingEmail`, `trialInitiationUrl` (the URL captured from `flow:trigger-trial-verification-email`)
- **Precondition state:** state:trial-verification-email-received
- **Steps:**
  1. Navigate to `<trialInitiationUrl>` in the browser
     - Feedback: "Email verified" toast appears
  2. Step 1 — enter organization name (`<orgName>`) and billing email (`<billingEmail>`); click Next
  3. Step 2 — enter payment method (card iframes as in `flow:purchase-premium-subscription` steps 3–6); click Next
  4. Step 3 — set a master password to `<password>` (must be ≥12 characters); click Complete
  5. Confirm on the confirmation page
     - Feedback: redirect to the new trial organization
- **Post-condition state(s):**
  - Default: state:trialing-org-with-payment

---

### flow:complete-trial-signup-without-payment

- **Use when:** Completing a trial signup that does not require a payment method (the marketing-site call set `paymentOptional=true`).
- **Parameters:** `password`, `orgName`, `billingEmail`, `trialInitiationUrl` (the URL captured from `flow:trigger-trial-verification-email` invoked with `paymentOptional=true`)
- **Precondition state:** state:trial-verification-email-received
- **Steps:**
  1. Navigate to `<trialInitiationUrl>` in the browser
     - Feedback: "Email verified" toast appears
  2. Step 1 — enter organization name (`<orgName>`) and billing email (`<billingEmail>`); click Next
  3. Step 2 — set a master password to `<password>` (must be ≥12 characters); click Complete (the payment step is skipped because the trigger was called with `paymentOptional=true`)
  4. Confirm on the confirmation page
     - Feedback: redirect to the new trial organization
- **Post-condition state(s):**
  - Default: state:trialing-org-without-payment

---

### flow:complete-trial-signup-existing-user

- **Use when:** Completing a trial signup when the verifying email is already registered with a Bitwarden account; the verification link routes to `/create-organization` instead of `/trial-initiation`.
- **Parameters:** `orgName`, `billingEmail`, `planTier`, `trialInitiationUrl` (the URL captured from `flow:trigger-trial-verification-email`)
- **Precondition state:** state:trial-verification-email-received
- **Steps:**
  1. Navigate to `<trialInitiationUrl>` in the browser; the app routes to `https://localhost:8080/#/create-organization`
     - Feedback: routes to `/create-organization`
  2. Select `<planTier>`
  3. Fill in Organization Name with `<orgName>` and Billing Email with `<billingEmail>`
  4. In the Payment Information section, select Credit Card
  5. Fill the card number iframe (`frameLocator('[title="Secure card number input frame"]')`): `4242424242424242`
  6. Fill the expiry iframe (`frameLocator('[title="Secure expiration date input frame"]')`): `12/29`
  7. Fill the CVC iframe (`frameLocator('[title="Secure CVC input frame"]')`): `123`
  8. Set Country to `United States` and fill the Postal Code field with `12345`
  9. Submit the form
     - Feedback: success redirect to the new org's vault or settings page
- **Post-condition state(s):**
  - Default: state:authenticated-with-paid-org

**Note:** This flow assumes the user from whose mailbox the verification email was retrieved is already logged in. The trial-existing-user path requires the existing session to persist; the verification URL only works for the logged-in user matching the email.

---

### flow:authenticate-admin-portal

- **Use when:** Any test that requires administrative setup (creating discounts, managing users, verifying subscription state).
- **Parameters:** `bitwarden-portal-admin-email`
- **Precondition state:** none
- **Steps:**
  1. Navigate to `http://localhost:62911`
     - Feedback: redirect to the Admin portal login page
  2. Enter `<bitwarden-portal-admin-email>` in the login field
  3. Submit the form
     - Feedback: form clears; magic-link email sent
  4. Run `read-mailcatcher.sh --recipient <bitwarden-portal-admin-email> --pattern "Continue Logging In"` to read the magic link (subject contains "Admin" or "Continue Logging In"); stdout is the URL
  5. Navigate directly to the extracted magic-link URL
     - Feedback: Admin portal home loads, authenticated
- **Post-condition state(s):**
  - Default: state:admin-portal-authenticated
