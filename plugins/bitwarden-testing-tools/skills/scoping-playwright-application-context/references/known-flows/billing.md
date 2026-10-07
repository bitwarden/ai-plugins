# Known Bitwarden States and Flows — Billing

<!-- cspell:ignore Inititaion -->

Curated reference of reusable test states and UI flows for Bitwarden billing, subscriptions, and organizations. `scoping-playwright-application-context` copies these entries as written once their cited literals check out, dropping the catalog-only fields below, and the downstream test-case authoring step consumes them.

## Catalog conventions

- **Citations.** A citation is `` `<workspace path>` (`<literal>`) ``. The path is relative to the bitwarden root (`clients/…`, `server/…`). Each literal in backticks is an exact substring of that file that encodes the fact, searched as plain text (many contain regex metacharacters). When several literals end with `in order`, they appear in that order in the file. States cite on each verification point's `Source:` line; flows cite in a `**Sources:**` block.
- **`**Select only when:**`** (flows only; catalog-only). The scoper uses the flow only when the context's feature description or acceptance criteria, or the user's extra instructions, meet the condition. A condition names the explicit call for that kind of trial and the requirements only that flow can meet; anything a normal paid-org signup can already do (a card, a cadence, a seat count, a trial length) never counts. Dropped on copy.
- **`**Sources:**`** (flows only; catalog-only). One bullet per cited fact: the citation, then the fact it grounds. Dropped on copy.
- Card iframe titles (`Secure card number input frame` and the like) are rendered by Stripe, not Bitwarden code, so they are not cited.

---

## Known States

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
    - Source: `clients/apps/web/src/app/billing/individual/subscription/cloud-hosted-account-subscription.component.html` (`{{ "youHavePremium" | i18n }}`) — the page `<h1>`

### state:trialing-paid-org

**State type:** setup

**Produced by:**

- flow:create-paid-org

**Reachable by playwright:** yes

**UI projection:**

- Route: https://localhost:8080/#/organizations/:organizationId/vault (org-scoped dynamic URL; `/organizations/:organizationId` redirects to the `vault` child. An org just created by `flow:create-paid-org` is in its 7-day trial: a paid-org signup never sets `skipTrial`, so the server applies the plan's trial period)
- Verification points:
  - Selector: link "Admin Console"
    - Selector type: role
    - Expectation: visible
    - Source: `clients/apps/web/src/app/admin-console/organizations/layouts/organization-layout.component.html` (`[label]="'adminConsole' | i18n"`) — the org side-nav logo's org-name-independent `aria-label`, rendered by `bit-nav-logo`

### state:trialing-org-marketing-with-payment

**State type:** setup

**Produced by:**

- flow:complete-marketing-trial-signup-with-payment
- flow:complete-marketing-trial-signup-existing-user

**Reachable by playwright:** yes

**UI projection:**

- Route: https://localhost:8080/#/organizations/:organizationId/vault (a marketing-initiated trial with a payment method on file; the new-user flow ends on the "Confirmation Details" step, whose "Get Started" button routes here, and the existing-user flow lands on the new org after "Submit")
- Verification points:
  - Selector: link "Admin Console"
    - Selector type: role
    - Expectation: visible
    - Source: `clients/apps/web/src/app/admin-console/organizations/layouts/organization-layout.component.html` (`[label]="'adminConsole' | i18n"`) — the org side-nav logo's org-name-independent `aria-label`, rendered by `bit-nav-logo`

### state:trialing-org-marketing-without-payment

**State type:** setup

**Produced by:**

- flow:complete-marketing-trial-signup-without-payment

**Reachable by playwright:** yes

**UI projection:**

- Route: https://localhost:8080/#/organizations/:organizationId/vault (a marketing-initiated trial with no payment method, always on an annual plan; the "Confirmation Details" step's "Get Started" button routes here)
- Verification points:
  - Selector: link "Admin Console"
    - Selector type: role
    - Expectation: visible
    - Source: `clients/apps/web/src/app/admin-console/organizations/layouts/organization-layout.component.html` (`[label]="'adminConsole' | i18n"`) — the org side-nav logo's org-name-independent `aria-label`, rendered by `bit-nav-logo`

### state:trialing-org-sales-assisted

**State type:** setup

**Produced by:**

- flow:complete-sales-assisted-trial-signup

**Reachable by playwright:** yes

**UI projection:**

- Route: https://localhost:8080/#/organizations/:organizationId/vault (a sales-assisted trial sent from the Admin portal, with no payment method, always on an annual plan; the "Confirmation Details" step's "Get Started" button routes here)
- Verification points:
  - Selector: link "Admin Console"
    - Selector type: role
    - Expectation: visible
    - Source: `clients/apps/web/src/app/admin-console/organizations/layouts/organization-layout.component.html` (`[label]="'adminConsole' | i18n"`) — the org side-nav logo's org-name-independent `aria-label`, rendered by `bit-nav-logo`

### state:marketing-trial-verification-email-received

**State type:** setup

**Produced by:**

- flow:trigger-marketing-trial-verification-email

**Reachable by playwright:** no
**If no — why:** non-UI intermediate state — verified by reading the trial-initiation email from Mailcatcher, not by a rendered page. The check is automated (a script), not a human step.
**Reach via:**

- Run flow:trigger-marketing-trial-verification-email (its external-trigger step sends the verification email).
- Use the `reading-mailcatcher-api` skill (`--recipient <email> --pattern "Verify"`); a trial-initiation URL printed on stdout confirms the state (exit 1 / `NO_MATCH` means the email has not arrived yet).

**UI projection:**

- Route: n/a
- Verification points:
  - Selector: trial-initiation URL on stdout from the `reading-mailcatcher-api` skill (`--recipient <email> --pattern "Verify"`)
    - Selector type: text
    - Expectation: stdout contains "#/trial-initiation?"
    - Source: `server/src/Core/Billing/Models/Mail/TrialInititaionVerifyEmail.cs` (`? "trial-initiation"`) — the emailed link's route for a new user's Password Manager trial

### state:sales-assisted-trial-invitation-received

**State type:** setup

**Produced by:**

- flow:send-sales-assisted-trial-invitation

**Reachable by playwright:** no
**If no — why:** non-UI intermediate state — verified by reading the invitation email from Mailcatcher, not by a rendered page. The check is automated (a script), not a human step.
**Reach via:**

- Run flow:send-sales-assisted-trial-invitation (its last step reads the invitation email).
- Use the `reading-mailcatcher-api` skill (`--recipient <email> --pattern "invited to try Bitwarden"`); a trial-initiation URL carrying `salesAssistedToken` on stdout confirms the state.

**UI projection:**

- Route: n/a
- Verification points:
  - Selector: invitation URL on stdout from the `reading-mailcatcher-api` skill (`--recipient <email> --pattern "invited to try Bitwarden"`)
    - Selector type: text
    - Expectation: stdout contains "salesAssistedToken="
    - Source: `server/src/Core/Billing/Models/Mail/Mailer/SalesAssistedTrialInvitationEmailView.cs` (`&salesAssistedToken={WebUtility.UrlEncode(Token)}`, `"&paymentOptional=true&fromEmail=true"`; in order) — the invitation link's query parameters

---

## Known Flows

### flow:purchase-premium-subscription

**Use when:** Any test that requires the user to already hold an active Premium subscription — subscription management page, premium-feature access, discount badge display (any eligible Stripe coupon imported to Admin portal applies automatically at checkout), etc.

**Parameters:** none (uses default billing values)

**Precondition state:** state:authenticated-free-user

**Steps:**

1. Navigate to `https://localhost:8080/#/settings/subscription/premium`
   - Feedback: two pricing cards (Premium and Families) visible
2. Click the "Upgrade to Premium" button on the Premium pricing card
3. In the Payment Method section, fill the Stripe card number iframe (`frameLocator('[title="Secure card number input frame"]')`): `4242424242424242`
4. Fill the expiry iframe (`frameLocator('[title="Secure expiration date input frame"]')`): `12/29`
5. Fill the CVC iframe (`frameLocator('[title="Secure CVC input frame"]')`): `123`
6. In the Billing Address section, set Country to `United States` and fill the Postal Code field with `12345`
7. Click the "Upgrade" button
   - Feedback: dialog closes; redirect to `https://localhost:8080/#/settings/subscription/user-subscription`; the subscription management view is visible

**Post-condition state(s):**

- Default: state:authenticated-premium-user

**Sources:**

- `clients/apps/web/src/app/billing/individual/individual-billing-routing.module.ts` (`path: "user-subscription",`, `path: "premium",`; in order) — the routes in steps 1 and 7
- `clients/apps/web/src/app/billing/individual/premium/cloud-hosted-premium.component.html` (`text: ('upgradeToPremium' | i18n)`) — step 2's button

---

### flow:create-paid-org

**Use when:** The default way to get a paid organization (Families, Teams, or Enterprise; annual or monthly). A newly created paid org starts in its trial (7 days unless `trialLength` says otherwise), so this is also the flow for any test that needs a trialing organization, unless a gated trial flow's `Select only when:` condition is met. Covers discount badge display on a Families organization too (any eligible Stripe coupon imported to Admin portal applies automatically at checkout).

**Parameters:** `orgName`, `billingEmail`, `planTier`, `cadence`, `seats`, `trialLength`

**Precondition state:** state:authenticated-free-user

**Steps:**

1. Navigate to `https://localhost:8080/#/create-organization?trialLength=<trialLength>` (`<trialLength>` is days of trial; use `7`, the plan's trial period, unless the test needs another length; `0` creates the org with no trial)
2. Fill "Organization name" (labelled "Vault name" when the `VFO1Foundation` flag is on) with `<orgName>` and "Billing email" with `<billingEmail>`
3. Click the `<planTier>` radio (`Families`, `Teams`, or `Enterprise`)
4. If `<planTier>` is Teams or Enterprise, set "User seats" to `<seats>` (Families is a packaged plan and has no seat field)
5. Under "Summary", click the radio labelled "Monthly" when `<cadence>` is `monthly`, or "Annually" when it is `annually`; Families offers Annually only. Select by label, not by the radio's numeric `interval…` element id
6. In the Payment information section, leave "Credit card" selected and fill the card number iframe (`frameLocator('[title="Secure card number input frame"]')`): `4242424242424242`
7. Fill the expiry iframe (`frameLocator('[title="Secure expiration date input frame"]')`): `12/29`
8. Fill the CVC iframe (`frameLocator('[title="Secure CVC input frame"]')`): `123`
9. Set Country (`data-testid="country"`) to `United States` and fill ZIP / Postal code (`data-testid="postal-code"`) with `12345`
10. Click "Submit"
    - Feedback: toast "Organization created"; redirect to the new organization

**Post-condition state(s):**

- Default: state:trialing-paid-org

**Sources:**

- `clients/apps/web/src/app/admin-console/organizations/create/organization-information.component.html` (`"organizationName" | vfo1I18n: "vaultName"`, `"billingEmail" | i18n`; in order) — step 2's labels
- `clients/apps/web/src/app/billing/organizations/organization-plans.component.html` (`formControlName="productTier"`, `!plan.PasswordManager.baseSeats`, `"userSeats" | i18n`, `"summary" | i18n`, `id="interval{{ selectablePlan.type }}"`, `(isAnnual ? "annually" : "monthly") | i18n`, `"submit" | i18n`; in order) — the tier radio, the seat field's gate and label, the cadence radio, and the submit button
- `clients/apps/web/src/app/billing/organizations/organization-plans.component.ts` (`this._familyPlan = PlanType.FamiliesAnnually;`, `title: this.i18nService.t("organizationCreated"),`, `request.trialLength = trialLength;`; in order) — Families has an annual plan only; the success toast; the requested trial length goes on the create request
- `clients/apps/web/src/app/admin-console/settings/create-organization.component.ts` (`this.trialLength = qParams.trialLength ? parseInt(qParams.trialLength) : undefined;`) — step 1's `trialLength` query parameter
- `clients/apps/web/src/app/billing/payment/components/enter-payment-method.component.ts` (`id="card-payment-method"`) — the default "Credit card" method
- `clients/apps/web/src/app/billing/payment/components/enter-billing-address.component.ts` (`data-testid="country"`, `data-testid="postal-code"`; in order) — step 9's fields
- `server/src/Core/Billing/Organizations/Services/OrganizationBillingService.cs` (`TrialPeriodDays = subscriptionSetup.SkipTrial`, `: subscriptionSetup.TrialLength ?? plan.TrialPeriodDays`; in order) — the requested length, else the plan's trial period, applied to every paid-org signup

---

### flow:trigger-marketing-trial-verification-email

**Use when:** Setting up the first stage of a marketing-initiated trial for a new user (with or without payment). It produces the verification email and retrieves the trial-initiation URL. For an account that already exists, use `flow:complete-marketing-trial-signup-existing-user`, which sends its own email.

**Select only when:** a marketing-initiated trial is called for (a trial started from the bitwarden.com marketing site, including acceptance criteria that describe the `/#/trial-initiation` signup pages), or the organization must have no payment method on file, or Stripe must record the trial as marketing-initiated

**Parameters:** `email`, `productTier`, `trialLength`, `paymentOptional`

**Precondition state:** none

**Steps:**

1. **EXTERNAL TRIGGER**: POST to `http://localhost:33656/accounts/trial/send-verification-email`. This simulates the marketing-site trial verification email; no Bitwarden service initiates it. Request body:
   ```json
   {
     "email": "<email>",
     "name": "Test User",
     "receiveMarketingEmails": false,
     "productTier": <productTier>,
     "products": [0],
     "trialLength": <trialLength>,
     "paymentOptional": <paymentOptional>
   }
   ```
   Reference values. `productTier`: `0` = Free, `1` = Families, `2` = Teams, `3` = Enterprise, `4` = TeamsStarter; use `1`, `2`, or `3`, the tiers the trial wizard renders for. `products` is fixed at `[0]` (`0` = PasswordManager), so the link opens `/#/trial-initiation`; Secrets Manager trials are not covered by this catalog. `trialLength` must be at least `1`: `0` skips the trial. `paymentOptional`: `true` skips the payment step in the downstream completion flow; `false` requires payment. `<email>` must not already have an account: an existing account is sent a `/#/create-organization` link instead.
2. Use the `reading-mailcatcher-api` skill (`--recipient <email> --pattern "Verify"`) to read the verification email; stdout is the trial-initiation URL, so capture it for the next flow.
   - Feedback: trial-initiation URL is available on stdout

**Post-condition state(s):**

- Default: state:marketing-trial-verification-email-received

**Sources:**

- `server/src/Core/Billing/Enums/ProductTierType.cs` (`Free = 0`, `Families = 1`, `Teams = 2`, `Enterprise = 3`, `TeamsStarter = 4`; in order) — `productTier` values
- `server/src/Core/Billing/Enums/ProductType.cs` (`PasswordManager = 0`) — the fixed `products` value
- `server/src/Core/Billing/Models/Mail/TrialInititaionVerifyEmail.cs` (`if (IsExistingUser)`, `return "create-organization";`, `? "trial-initiation"`; in order) — the emailed link's route
- `clients/apps/web/src/app/billing/trial-initiation/trial-billing-step/trial-billing-step.service.ts` (`skipTrial: trial.length === 0,`) — a trial length of `0` skips the trial
- `clients/apps/web/src/app/billing/trial-initiation/complete-trial-initiation/complete-trial-initiation.component.ts` (`stepperProductTypes: ProductTierType[] = [`, `ProductTierType.Teams,`, `ProductTierType.Enterprise,`, `ProductTierType.Families,`; in order) — the tiers the trial stepper renders for

---

### flow:complete-marketing-trial-signup-with-payment

**Use when:** Completing a marketing-initiated trial for a new user when the trigger set `paymentOptional=false`. This path always creates one user seat; a test that needs more seats uses `flow:create-paid-org`.

**Select only when:** a marketing-initiated trial is called for (a trial started from the bitwarden.com marketing site, including acceptance criteria that describe the `/#/trial-initiation` signup pages), or Stripe must record the trial as marketing-initiated

**Parameters:** `password`, `orgName`, `cadence`, `trialInitiationUrl` (the URL captured from `flow:trigger-marketing-trial-verification-email`)

**Precondition state:** state:marketing-trial-verification-email-received

**Steps:**

1. Navigate to `<trialInitiationUrl>` while logged out
   - Feedback: "Email verified" toast appears; the "Create Account" step is open
2. Fill the master password and confirm-master-password fields with `<password>` (the fixed dev master password `test-master-password-12`); click "Create account"
   - Feedback: the "Organization Information" step opens
3. Fill "Organization name" with `<orgName>`; click "Next"
   - Feedback: the "Billing" step opens
4. When `<cadence>` is `monthly`, click the Monthly radio (`#monthly-cadence-button`); otherwise leave Annually, the default. Families offers Annually only
5. Fill the card number iframe (`frameLocator('[title="Secure card number input frame"]')`): `4242424242424242`
6. Fill the expiry iframe (`frameLocator('[title="Secure expiration date input frame"]')`): `12/29`
7. Fill the CVC iframe (`frameLocator('[title="Secure CVC input frame"]')`): `123`
8. Set Country to `United States` and fill the ZIP / Postal code field with `12345`
9. Click "Start trial"
   - Feedback: the "Confirmation Details" step opens
10. Click "Get Started"
    - Feedback: redirect to the new organization's vault

**Post-condition state(s):**

- Default: state:trialing-org-marketing-with-payment

**Sources:**

- `clients/apps/web/src/app/billing/trial-initiation/complete-trial-initiation/complete-trial-initiation.component.html` (`label="Create Account"`, `{ key: 'createAccount' }`, `label="Organization Information"`, `[nameOnly]="true"`, `("startTrial" | i18n) : ("next" | i18n)`, `label="Billing"`, `label="Confirmation Details"`, `"getStarted" | i18n | titlecase`; in order) — the wizard's step order and buttons
- `clients/apps/web/src/app/billing/trial-initiation/trial-billing-step/trial-billing-step.component.html` (`id="annual-cadence-button"`, `@if (prices.monthly)`, `id="monthly-cadence-button"`, `"startTrial" : "submit"`; in order) — the cadence radios (monthly only when a monthly price exists) and the "Start trial" button
- `clients/apps/web/src/app/billing/trial-initiation/trial-billing-step/trial-billing-step.component.ts` (`new FormControl<Cadence>(Cadences.Annually`) — Annually is the default cadence
- `clients/apps/web/src/app/billing/trial-initiation/trial-billing-step/trial-billing-step.service.ts` (`case "families": {`, `annually: annually!.PasswordManager.basePrice,`, `case "teams":`, `? { type: planType, passwordManagerSeats: 1 }`; in order) — Families has an annual price only; one user seat

---

### flow:complete-marketing-trial-signup-without-payment

**Use when:** Completing a marketing-initiated trial for a new user when the trigger set `paymentOptional=true` (and a `trialLength` above 0). The trial is always on an annual plan.

**Select only when:** a marketing-initiated trial is called for (a trial started from the bitwarden.com marketing site, including acceptance criteria that describe the `/#/trial-initiation` signup pages), or the organization must have no payment method on file

**Parameters:** `password`, `orgName`, `trialInitiationUrl` (the URL captured from `flow:trigger-marketing-trial-verification-email` invoked with `paymentOptional=true`)

**Precondition state:** state:marketing-trial-verification-email-received

**Steps:**

1. Navigate to `<trialInitiationUrl>` while logged out
   - Feedback: "Email verified" toast appears; the "Create Account" step is open
2. Fill the master password and confirm-master-password fields with `<password>` (the fixed dev master password `test-master-password-12`); click "Create account"
   - Feedback: the "Organization Information" step opens
3. Fill "Organization name" with `<orgName>`; click "Start trial" (the billing step is skipped because the trigger used `paymentOptional=true`)
   - Feedback: the "Confirmation Details" step opens
4. Click "Get Started"
   - Feedback: redirect to the new organization's vault

**Post-condition state(s):**

- Default: state:trialing-org-marketing-without-payment

**Sources:**

- `clients/apps/web/src/app/billing/trial-initiation/complete-trial-initiation/complete-trial-initiation.component.html` (`label="Create Account"`, `{ key: 'createAccount' }`, `label="Organization Information"`, `[nameOnly]="true"`, `("startTrial" | i18n) : ("next" | i18n)`, `*ngIf="showBillingStep"`, `label="Confirmation Details"`, `"getStarted" | i18n | titlecase`; in order) — the wizard's step order and buttons
- `clients/apps/web/src/app/billing/trial-initiation/complete-trial-initiation/complete-trial-initiation.component.ts` (`return PlanType.TeamsAnnually;`, `return PlanType.EnterpriseAnnually;`, `return PlanType.FamiliesAnnually;`, `return !this.paymentOptional && !this.isSecretsManagerFree;`; in order) — the no-payment path's annual plan and the skipped billing step

---

### flow:complete-marketing-trial-signup-existing-user

**Use when:** Completing a marketing-initiated trial for an account that already exists. The server sends an existing account a `/#/create-organization` link instead of `/#/trial-initiation`, so this flow sends its own trial email after the account exists. A payment method is always required on this path, and the cadence can be changed.

**Select only when:** a marketing-initiated trial is called for (a trial started from the bitwarden.com marketing site, including acceptance criteria that describe the `/#/trial-initiation` signup pages), or Stripe must record the trial as marketing-initiated

**Parameters:** `email` (the logged-in account's email), `productTier`, `trialLength`, `orgName`, `billingEmail`, `cadence`, `seats`

**Precondition state:** state:authenticated-free-user

**Steps:**

1. **EXTERNAL TRIGGER**: POST to `http://localhost:33656/accounts/trial/send-verification-email`, simulating the marketing-site trial email. Request body:
   ```json
   {
     "email": "<email>",
     "name": "Test User",
     "receiveMarketingEmails": false,
     "productTier": <productTier>,
     "products": [0],
     "trialLength": <trialLength>,
     "paymentOptional": false
   }
   ```
   `<productTier>` is `1` (Families), `2` (Teams), or `3` (Enterprise). `<trialLength>` must be at least `1`.
2. Use the `reading-mailcatcher-api` skill (`--recipient <email> --pattern "Verify"`). The account's earlier signup email matches the same pattern and the reader takes the newest match, so if stdout is a `finish-signup` link the trial email has not arrived yet: re-run the reader, up to 5 times a few seconds apart, until stdout contains `/#/create-organization?`, and capture that URL. If it never does, stop and report that the trial email did not arrive.
   - Feedback: a `https://localhost:8080/#/create-organization?...` URL is on stdout
3. Navigate to that URL in the same logged-in browser
   - Feedback: the Create organization page opens with the `<productTier>` plan preselected (at `/#/settings/add-plan` instead when the `VFO1Foundation` flag is on)
4. Fill "Organization name" with `<orgName>` and "Billing email" with `<billingEmail>`
5. If `<productTier>` is `2` (Teams) or `3` (Enterprise), set "User seats" to `<seats>`
6. Under "Summary", click the radio labelled "Monthly" when `<cadence>` is `monthly`, or "Annually" when it is `annually`; Families offers Annually only (`<productTier>` `1`)
7. In the Payment information section, leave "Credit card" selected and fill the card number iframe (`frameLocator('[title="Secure card number input frame"]')`): `4242424242424242`
8. Fill the expiry iframe (`frameLocator('[title="Secure expiration date input frame"]')`): `12/29`
9. Fill the CVC iframe (`frameLocator('[title="Secure CVC input frame"]')`): `123`
10. Set Country (`data-testid="country"`) to `United States` and fill ZIP / Postal code (`data-testid="postal-code"`) with `12345`
11. Click "Submit"
    - Feedback: toast "Organization created"; redirect to the new organization

**Post-condition state(s):**

- Default: state:trialing-org-marketing-with-payment

**Sources:**

- `server/src/Core/Billing/Models/Mail/TrialInititaionVerifyEmail.cs` (`if (IsExistingUser)`, `return "create-organization";`; in order) — an existing account gets a `/#/create-organization` link
- `clients/apps/web/src/app/oss-routing.module.ts` (`canActivate: [deepLinkGuard(), authGuard],`, `path: "create-organization",`; in order) — the page requires a logged-in session
- `clients/apps/web/src/app/admin-console/settings/create-organization.component.ts` (`if (qParams.product != null)`, `InitiationPath.PasswordManagerTrialFromMarketingWebsite`; in order) — the link's `product` parameter marks the org marketing-initiated
- `clients/apps/web/src/app/billing/organizations/organization-plans.component.html` (`!plan.PasswordManager.baseSeats`, `"userSeats" | i18n`, `"summary" | i18n`, `(isAnnual ? "annually" : "monthly") | i18n`, `"submit" | i18n`; in order) — the seat field, the cadence radio, and the submit button
- `clients/apps/web/src/app/billing/payment/components/enter-billing-address.component.ts` (`data-testid="country"`, `data-testid="postal-code"`; in order) — step 10's fields
- `clients/apps/web/src/app/billing/organizations/organization-plans.component.ts` (`this._familyPlan = PlanType.FamiliesAnnually;`, `title: this.i18nService.t("organizationCreated"),`; in order) — Families has an annual plan only; the success toast

---

### flow:send-sales-assisted-trial-invitation

**Use when:** First stage of a sales-assisted trial: an Admin portal user sends a trial invitation to a new user's email address.

**Select only when:** a sales-assisted trial is called for (a trial sent from the Admin portal), or the vault must show the free-trial banner's "Contact your Bitwarden sales representative to set up billing." text, or Stripe must record the trial as sales-assisted

**Parameters:** `email`, `productTier`, `trialLength`

**Precondition state:** state:admin-portal-authenticated

**Steps:**

1. Navigate to `http://localhost:62911/sales-assisted-trial` (the page's nav link is behind the `pm-35092-auth-sales-assisted-trials` flag, but the page itself is not, so navigate by URL)
   - Feedback: "Send Sales-Assisted Trial Invitation" heading
2. Fill "Email" with `<email>`; it must not already have a Bitwarden account
3. Set "Product Tier" to `<productTier>`: `Families`, `Teams`, or `Enterprise` (the select also offers Free, which shows no trial wizard, so never choose it)
4. Leave "Password Manager" selected (the default); Secrets Manager trials are not covered by this catalog
5. Set "Trial Length (Days)" to `<trialLength>` (1–30)
6. Click "Send invitation"
   - Feedback: the alert "Invitation sent." appears
7. Use the `reading-mailcatcher-api` skill (`--recipient <email> --pattern "invited to try Bitwarden"`); stdout is the invitation link (the plain-text email prints it after "Get started:"), so capture it for the next flow
   - Feedback: a URL containing `salesAssistedToken=` is on stdout

**Post-condition state(s):**

- Default: state:sales-assisted-trial-invitation-received

**Note:** The Admin portal user needs the `Org_InitiateSalesAssistedTrial` permission (granted to the owner, admin, and sales roles). The page rejects an email that already has an account with "A Bitwarden account already exists with this email address."

**Sources:**

- `server/src/Admin/Auth/Controllers/SalesAssistedTrialController.cs` (`[Route("sales-assisted-trial")]`, `[RequirePermission(Permission.Org_InitiateSalesAssistedTrial)]`, `ProductTier = ProductTierType.Enterprise,`, `TrialLength = 30`, `TempData["Success"] = "Invitation sent.";`; in order) — the route, the permission, the form defaults, and the success alert
- `server/src/Admin/Auth/Views/SalesAssistedTrial/Index.cshtml` (`<h1>Send Sales-Assisted Trial Invitation</h1>`, `.Where(t => t != ProductTierType.TeamsStarter)`, `id="product-@product"`, `min="1" max="30"`, `Send invitation`; in order) — the heading, the tier filter (only Teams Starter is removed), the product radios, the trial-length range, and the button
- `server/src/Admin/Auth/Models/SalesAssistedTrial/SalesAssistedTrialInviteModel.cs` (`[Display(Name = "Product Tier")]`, `[Display(Name = "Trial Length (Days)")]`; in order) — the field labels
- `server/src/Core/Billing/TrialInitiation/Registration/Implementations/SendSalesAssistedTrialInvitationCommand.cs` (`A Bitwarden account already exists with this email address.`) — new users only
- `server/src/Core/Billing/Models/Mail/Mailer/SalesAssistedTrialInvitationEmailView.cs` (`= "You're invited to try Bitwarden";`) — the email subject

---

### flow:complete-sales-assisted-trial-signup

**Use when:** Completing a sales-assisted trial from the invitation link. No payment method is collected and the trial is on an annual plan.

**Select only when:** a sales-assisted trial is called for (a trial sent from the Admin portal), or the vault must show the free-trial banner's "Contact your Bitwarden sales representative to set up billing." text, or Stripe must record the trial as sales-assisted

**Parameters:** `password`, `orgName`, `trialInvitationUrl` (the URL captured from `flow:send-sales-assisted-trial-invitation`)

**Precondition state:** state:sales-assisted-trial-invitation-received

**Steps:**

1. Navigate to `<trialInvitationUrl>` while logged out
   - Feedback: "Email verified" toast appears; the "Create Account" step is open
2. Fill the master password and confirm-master-password fields with `<password>` (the fixed dev master password `test-master-password-12`); click "Create account"
   - Feedback: the "Organization Information" step opens
3. Fill "Organization name" with `<orgName>`; click "Start trial" (the link carries `paymentOptional=true`, so the billing step is skipped)
   - Feedback: the "Confirmation Details" step opens
4. Click "Get Started"
   - Feedback: redirect to the new organization's vault

**Post-condition state(s):**

- Default: state:trialing-org-sales-assisted

**Sources:**

- `server/src/Core/Billing/Models/Mail/Mailer/SalesAssistedTrialInvitationEmailView.cs` (`&salesAssistedToken={WebUtility.UrlEncode(Token)}`, `"&paymentOptional=true&fromEmail=true"`; in order) — the link's token and no-payment parameters
- `clients/apps/web/src/app/oss-routing.module.ts` (`path: "trial-initiation",`, `canActivate: [unauthGuardFn()],`; in order) — the link's page requires a logged-out browser
- `clients/apps/web/src/app/billing/trial-initiation/complete-trial-initiation/complete-trial-initiation.component.html` (`label="Create Account"`, `{ key: 'createAccount' }`, `label="Organization Information"`, `[nameOnly]="true"`, `("startTrial" | i18n) : ("next" | i18n)`, `*ngIf="showBillingStep"`, `label="Confirmation Details"`, `"getStarted" | i18n | titlecase`; in order) — the wizard's step order and buttons
- `clients/apps/web/src/app/billing/trial-initiation/complete-trial-initiation/complete-trial-initiation.component.ts` (`InitiationPath.SalesAssistedTrialFromAdminPortal`, `return PlanType.TeamsAnnually;`, `return PlanType.EnterpriseAnnually;`, `return PlanType.FamiliesAnnually;`; in order) — the sales-assisted initiation path and the annual plan
