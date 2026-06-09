# Bitwarden Email Patterns for Mailcatcher

## Account Verification (New Registration)

**Subject:** `Verify Your Email`
**Recipient:** The new account email address
**Link format:** `https://localhost:8080/#/finish-signup?token=BwRegistrationEmailVerificationToken&email=<encoded>`

**Extraction:**

```bash
curl -s http://localhost:1080/messages/${MSG_ID}.plain | \
  grep -oE 'https://localhost:8080/#/finish-signup[^ >)"]+' | head -1
```

---

## Admin Portal Magic Link Login

**Subject:** `[Admin] Continue Logging In` or `Continue Logging In`
**Recipient:** Admin email (find in `server/dev/secrets.json`, key `"admins"`)
**Link format:** `http://localhost:62911/login/confirm?email=<admin>&token=<token>&returnUrl=/`

**Extraction:**

```bash
curl -s http://localhost:1080/messages/${MSG_ID}.plain | \
  grep -oE 'http://localhost:62911/login/confirm[^ >)"]+' | head -1
```

---

## Trial Activation Link

**Subject:** Varies — check for `trial`, `start`, `activate`
**Recipient:** Trial initiator email
**Link format:** `https://localhost:8080/#/...?trialLength=...&token=...`

**Extraction:**

```bash
curl -s http://localhost:1080/messages/${MSG_ID}.plain | \
  grep -oE 'https?://localhost[^ >)"]+' | grep -iE 'trial|verify|token|register' | head -1
```

---

## Organization Invite

**Subject:** `Join <OrgName> on Bitwarden`
**Recipient:** Invited user email
**Link format:** `https://localhost:8080/#/accept-organization?orgId=...&orgUserId=...&token=...`

**Extraction:**

```bash
curl -s http://localhost:1080/messages/${MSG_ID}.plain | \
  grep -oE 'https://localhost:8080/#/accept-organization[^ >)"]+' | head -1
```

---

## Emergency Access Invite

**Subject:** `Emergency Access Request`
**Recipient:** Grantee email
**Link format:** `https://localhost:8080/#/accept-emergency?id=...&token=...`

**Extraction:**

```bash
curl -s http://localhost:1080/messages/${MSG_ID}.plain | \
  grep -oE 'https://localhost:8080/#/accept-emergency[^ >)"]+' | head -1
```

---

## Welcome Email (No Action Required)

**Subject:** `Welcome to Bitwarden!`
**Purpose:** Confirmation only — no link extraction needed
**Verification:** Confirm receipt to validate registration completed

---

## API Quick Reference

| Operation | Command |
|-----------|---------|
| List all messages | `curl -s http://localhost:1080/messages` |
| Get plain text body | `curl -s http://localhost:1080/messages/{id}.plain` |
| Get HTML body | `curl -s http://localhost:1080/messages/{id}.html` |
| Get JSON metadata | `curl -s http://localhost:1080/messages/{id}.json` |
| Delete specific message | `curl -X DELETE http://localhost:1080/messages/{id}` |
| Clear all messages | `curl -X DELETE http://localhost:1080/messages` — **ALWAYS ask user first; irreversible** |
