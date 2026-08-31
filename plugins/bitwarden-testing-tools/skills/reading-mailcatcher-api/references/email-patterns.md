# Bitwarden Email Patterns for Mailcatcher

Each section gives the subject, recipient, and link format for a Bitwarden email, followed by the sanctioned `read_mailcatcher.py` invocation that extracts its link. Run the co-located script; curl and direct API calls are not sanctioned transports here (see `manual-api-walkthrough.md`, which exists for debugging the script itself).

> **Substitute the plugin root before running.** The commands below use the `${CLAUDE_PLUGIN_ROOT}/` placeholder for readability. When the skill runs, `${CLAUDE_PLUGIN_ROOT}` is already set in its environment and the shell expands it for you, and it is the same variable the skill's `allowed-tools` grant is written against, so an expanded invocation auto-approves without a prompt. (`${CLAUDE_SKILL_DIR}` is deliberately not used here: it is not currently substituted inside `allowed-tools` permission matchers, so a grant written against it would prompt on every call.) If you run one of these commands by hand from a plain shell where the variable is not set, resolve it first with `printenv CLAUDE_PLUGIN_ROOT` (or set it to this plugin's absolute directory) and invoke the script by that absolute path; a relative path would not match the grant.

## Account Verification (New Registration)

**Subject:** `Verify Your Email`
**Recipient:** The new account email address
**Link format:** `https://localhost:8080/#/finish-signup?token=BwRegistrationEmailVerificationToken&email=<encoded>`

**Extraction:**

```bash
${CLAUDE_PLUGIN_ROOT}/skills/reading-mailcatcher-api/scripts/read_mailcatcher.py \
  --recipient <new-account-email> --pattern "Verify" --link-filter 'finish-signup'
```

---

## Admin Portal Magic Link Login

**Subject:** `[Admin] Continue Logging In` or `Continue Logging In`
**Recipient:** The Bitwarden dev admin address. Get it with the co-located helper, which reads only `adminSettings.admins` from your `bitwarden/server` checkout's `dev/secrets.json` and prints nothing else. It reads `server/dev/secrets.json` relative to the current working directory (run from the workspace root that holds your `bitwarden/server` checkout, or pass `--secrets-file <path>`), and exits 3 if that file is missing or has no `adminSettings.admins` key. By default it prints only the first configured admin address (the Admin Portal login address); pass `--all` to list every configured admin, one per line.
**Link format:** `http://localhost:62911/login/confirm?email=<admin>&token=<token>&returnUrl=/`

**Extraction:** run these as two separate Bash calls. Do not wrap the helper in `$(...)` command substitution: Claude Code's Bash matcher flags any `$(...)` or backtick command as possible injection and will not auto-approve it against the grant, so it always prompts.

```bash
# 1. Print the admin address:
${CLAUDE_PLUGIN_ROOT}/skills/reading-mailcatcher-api/scripts/get_admin_email.py
```

```bash
# 2. Pass that printed address literally as --recipient (replace <admin-address>):
${CLAUDE_PLUGIN_ROOT}/skills/reading-mailcatcher-api/scripts/read_mailcatcher.py \
  --recipient <admin-address> --pattern "Logging In" --link-filter 'login/confirm'
```

---

## Trial Activation Link

**Subject:** Varies — check for `trial`, `start`, `activate`
**Recipient:** Trial initiator email
**Link format:** `https://localhost:8080/#/...?trialLength=...&token=...`

**Extraction:** the subject varies, so omit `--pattern` and let the link filter select:

```bash
${CLAUDE_PLUGIN_ROOT}/skills/reading-mailcatcher-api/scripts/read_mailcatcher.py \
  --recipient <trial-initiator-email> --link-filter 'trial|token'
```

---

## Organization Invite

**Subject:** `Join <OrgName> on Bitwarden`
**Recipient:** Invited user email
**Link format:** `https://localhost:8080/#/accept-organization?orgId=...&orgUserId=...&token=...`

**Extraction:**

```bash
${CLAUDE_PLUGIN_ROOT}/skills/reading-mailcatcher-api/scripts/read_mailcatcher.py \
  --recipient <invited-user-email> --pattern "Join" --link-filter 'accept-organization'
```

---

## Emergency Access Invite

**Subject:** `Emergency Access Request`
**Recipient:** Grantee email
**Link format:** `https://localhost:8080/#/accept-emergency?id=...&token=...`

**Extraction:**

```bash
${CLAUDE_PLUGIN_ROOT}/skills/reading-mailcatcher-api/scripts/read_mailcatcher.py \
  --recipient <grantee-email> --pattern "Emergency" --link-filter 'accept-emergency'
```

---

## Welcome Email (No Action Required)

**Subject:** `Welcome to Bitwarden!`
**Purpose:** Confirmation only — no link extraction needed
**Verification:** Confirm receipt to validate registration completed
