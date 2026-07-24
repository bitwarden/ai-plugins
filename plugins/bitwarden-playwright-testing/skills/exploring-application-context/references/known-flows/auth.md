# Known Bitwarden States and Flows — Auth

Curated reference of validated, reusable test states and UI flows for Bitwarden authentication — consumed verbatim by `exploring-application-context` and `build-test-cases`.

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
