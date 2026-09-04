# Known Bitwarden States and Flows — Admin

Curated reference of validated, reusable test states and UI flows for the Bitwarden Admin portal — consumed verbatim by `scoping-playwright-application-context` and the downstream test-case authoring step.

---

## Known States

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

---

## Known Flows

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
  4. Run `read_mailcatcher.py --recipient <bitwarden-portal-admin-email> --pattern "Continue Logging In"` (the Mailcatcher reader; path in the tool policy's Canonical script paths) to read the magic link (subject contains "Admin" or "Continue Logging In"); stdout is the URL
  5. Navigate directly to the extracted magic-link URL
     - Feedback: Admin portal home loads, authenticated
- **Post-condition state(s):**
  - Default: state:admin-portal-authenticated
