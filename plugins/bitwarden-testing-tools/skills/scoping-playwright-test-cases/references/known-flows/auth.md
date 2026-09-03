# Known Bitwarden States and Flows — Auth

Curated reference of validated, reusable test states and UI flows for Bitwarden authentication — consumed verbatim by `scoping-playwright-test-cases` and the downstream test-case authoring step.

---

## Known States

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

---

## Known Flows

### flow:create-new-user-and-login

- **Use when:** Any test that requires a fresh authenticated user account with no prior subscription or organization state.
- **Parameters:** `email`, `password` (the fixed dev master password `test-master-password-12`; see Note)
- **Note:** The dev master password is fixed at `test-master-password-12` for every test account, so credentials can be reconstructed from the email alone. It is a local dev fixture, never a real account credential. Any value of at least 12 characters is valid, but this is the convention. A test case needing a distinct password writes that value into its own SETUP step.
- **Precondition state:** none
- **Steps:**
  1. Navigate to `https://localhost:8080/#/signup`
  2. Fill the Email field with `<email>`
  3. (Optional) Fill the Name field
  4. Click Continue
     - Feedback: "Check your email" confirmation state appears
  5. Run `${CLAUDE_PLUGIN_ROOT}/skills/reading-mailcatcher-api/scripts/read_mailcatcher.py --recipient <email> --pattern "Verify"` to fetch the verification email; stdout is the magic-link URL
  6. Navigate to the magic-link URL (it targets `https://localhost:8080/#/finish-signup?...`)
     - Feedback: finish-signup form appears
  7. Fill the Master Password field with `<password>` (the fixed dev master password `test-master-password-12`)
  8. Fill the Confirm Master Password field with `<password>`
  9. Click Create Account
     - Feedback: redirect to the vault
- **Post-condition state(s):**
  - Default: state:authenticated-free-user
