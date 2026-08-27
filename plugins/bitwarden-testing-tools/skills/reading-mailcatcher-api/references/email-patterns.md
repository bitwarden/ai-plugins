# Bitwarden Email Patterns for Mailcatcher

Each section gives the subject, recipient, and link format for a Bitwarden email, followed by the sanctioned `read_mailcatcher.py` invocation that extracts its link. Run the co-located script; curl and direct API calls are not sanctioned transports here (see `manual-api-walkthrough.md`, which exists for debugging the script itself).

> **Substitute the skill directory before running.** The commands below are written with the `${CLAUDE_SKILL_DIR}/` placeholder for readability, but that variable is expanded only inside `SKILL.md` — when you read this reference as text, it stays literal. Before running a command, replace `${CLAUDE_SKILL_DIR}` with the absolute skill directory you already resolved from `SKILL.md`'s `allowed-tools`. Running the script by that absolute path is also what matches the grant without prompting; a relative path would not.

## Account Verification (New Registration)

**Subject:** `Verify Your Email`
**Recipient:** The new account email address
**Link format:** `https://localhost:8080/#/finish-signup?token=BwRegistrationEmailVerificationToken&email=<encoded>`

**Extraction:**

```bash
${CLAUDE_SKILL_DIR}/scripts/read_mailcatcher.py \
  --recipient <new-account-email> --pattern "Verify" --link-filter 'finish-signup'
```

---

## Admin Portal Magic Link Login

**Subject:** `[Admin] Continue Logging In` or `Continue Logging In`
**Recipient:** The Bitwarden dev admin address. Get it with the co-located helper, which reads only `adminSettings.admins` from your `bitwarden/server` checkout's `dev/secrets.json` and prints nothing else.
**Link format:** `http://localhost:62911/login/confirm?email=<admin>&token=<token>&returnUrl=/`

**Extraction:**

```bash
ADMIN="$(${CLAUDE_SKILL_DIR}/scripts/get_admin_email.py)"
${CLAUDE_SKILL_DIR}/scripts/read_mailcatcher.py \
  --recipient "$ADMIN" --pattern "Logging In" --link-filter 'login/confirm'
```

---

## Trial Activation Link

**Subject:** Varies — check for `trial`, `start`, `activate`
**Recipient:** Trial initiator email
**Link format:** `https://localhost:8080/#/...?trialLength=...&token=...`

**Extraction:** the subject varies, so omit `--pattern` and let the link filter select:

```bash
${CLAUDE_SKILL_DIR}/scripts/read_mailcatcher.py \
  --recipient <trial-initiator-email> --link-filter 'trial|token'
```

---

## Organization Invite

**Subject:** `Join <OrgName> on Bitwarden`
**Recipient:** Invited user email
**Link format:** `https://localhost:8080/#/accept-organization?orgId=...&orgUserId=...&token=...`

**Extraction:**

```bash
${CLAUDE_SKILL_DIR}/scripts/read_mailcatcher.py \
  --recipient <invited-user-email> --pattern "Join" --link-filter 'accept-organization'
```

---

## Emergency Access Invite

**Subject:** `Emergency Access Request`
**Recipient:** Grantee email
**Link format:** `https://localhost:8080/#/accept-emergency?id=...&token=...`

**Extraction:**

```bash
${CLAUDE_SKILL_DIR}/scripts/read_mailcatcher.py \
  --recipient <grantee-email> --pattern "Emergency" --link-filter 'accept-emergency'
```

---

## Welcome Email (No Action Required)

**Subject:** `Welcome to Bitwarden!`
**Purpose:** Confirmation only — no link extraction needed
**Verification:** Confirm receipt to validate registration completed
