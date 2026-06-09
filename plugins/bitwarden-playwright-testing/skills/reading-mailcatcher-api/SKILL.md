---
name: reading-mailcatcher-api
description: Use this skill whenever you need to read an email from the local Bitwarden Mailcatcher inbox — account verification, magic link login, trial activation, OTP codes, password resets, or any other email-driven flow. Uses cURL against the Mailcatcher REST API at http://localhost:1080 to find a message by recipient or subject and extract URLs or tokens from its body. Prefer this over the Mailcatcher browser UI in automated contexts (Playwright's browser CORS restrictions block direct fetch access). Invoke whenever a workflow needs to read, click, or extract content from a message Bitwarden just sent — including account creation, login flows, organization invites, trial activations, and password resets.
argument-hint: --recipient <email> --pattern <subject-keyword> [--link-filter <regex>]
allowed-tools: [Bash, Read]
---

## Quick reference — use the script

For all programmatic uses (test runs, ad-hoc fetches, debugging), call the co-located script directly:

```
bash ${CLAUDE_SKILL_DIR}/scripts/read-mailcatcher.sh --recipient <email> --pattern <subject-keyword> [--link-filter <regex>]
```

- **stdout** (on success): the extracted URL, ready to navigate to or paste into a form field
- **exit 1 + stderr** (on failure): `NO_MATCH: <diagnostic>` — either no message matched after one retry, or the matched message contained no URL passing the link filter

The script already retries once after a 3-second sleep on the first miss; callers don't need their own retry loop. The procedural reference below documents the underlying Mailcatcher API the script wraps — read it when modifying the script, debugging unexpected output, or doing a one-off curl by hand.

## User invocation

This skill is user-invocable. From any Claude Code session you can trigger it directly with the arguments declared in the `argument-hint` frontmatter — Claude will run the script and return the extracted URL (or the `NO_MATCH` diagnostic). Useful for debugging email flows, exploring Mailcatcher contents, or sanity-checking the script outside the test pipeline.

Example:

```
--recipient testuser-s1@example.com --pattern "Verify"
```

## When to Use

Invoke this skill whenever a workflow needs to:
- Click a verification link sent to a new account's email
- Log into the Admin Portal via magic link
- Activate a trial or invite via a link in a welcome/trial email
- Extract a one-time code or token from any email body

## Prerequisites

Mailcatcher must be running (Docker Compose service). Verify with:

```bash
curl -s http://localhost:1080/messages > /dev/null && echo "OK" || echo "Mailcatcher not running"
```

## Step-by-Step Workflow

### Step 1 — List all messages

```bash
curl -s http://localhost:1080/messages
```

Returns a JSON array of message objects:

```json
[
  {
    "id": 42,
    "sender": "<noreply@bitwarden.com>",
    "recipients": ["<user@example.com>"],
    "subject": "Verify Your Email",
    "created_at": "2026-04-21T10:00:00Z",
    "size": "4200",
    "formats": ["html", "plain"]
  }
]
```

### Step 2 — Find the target message

Filter by **recipient email** and/or **subject keyword** and select the **highest ID** (most recent):

```bash
curl -s http://localhost:1080/messages | python3 -c "
import sys, json

msgs = json.load(sys.stdin)

target_email = 'user@example.com'
subject_keyword = 'Verify'
matches = [m for m in msgs if
    any(target_email in r for r in m['recipients']) and
    subject_keyword.lower() in m['subject'].lower()
]
if not matches:
    print('NO_MATCH')
    sys.exit()

best = max(matches, key=lambda m: m['id'])
print(best['id'])
"
```

**Handle both outcomes before proceeding:**
- `NO_MATCH` — no matching email yet; wait 3–5 seconds and retry (up to ~30 s total before giving up)
- A numeric ID — proceed to Step 3

**When filtering:**
- Match on recipient email when the test account address is known (preferred)
- Match on subject keyword when recipient is generic/unknown
- Always take `max(id)` — higher ID = more recent message

### Step 3 — Fetch the message body

For link/token extraction, plain text is usually sufficient and easier to parse:

```bash
MSG_ID=42
curl -s http://localhost:1080/messages/${MSG_ID}.plain
```

Use `.html` only when the plain text body is empty or the link is only in the HTML part:

```bash
curl -s http://localhost:1080/messages/${MSG_ID}.html
```

### Step 4 — Extract the link or token

**Extract any URL matching a keyword pattern:**

```bash
curl -s http://localhost:1080/messages/${MSG_ID}.plain | \
  grep -oE 'https?://[^ >)"]+' | grep -i 'verify\|confirm\|signup\|token\|trial\|login' | head -1
```

**Extract an admin magic link:**

```bash
curl -s http://localhost:1080/messages/${MSG_ID}.plain | \
  grep -oE 'http://localhost:62911/login/confirm[^ >)"]+' | head -1
```

**Extract a web vault verification/signup link:**

```bash
curl -s http://localhost:1080/messages/${MSG_ID}.plain | \
  grep -oE 'https://localhost:8080/#/[^ >)"]+' | head -1
```

## Common Email Types and Patterns

See `${CLAUDE_SKILL_DIR}/references/email-patterns.md` for subject lines, link formats, and extraction commands for all common Bitwarden email types.

## Important Notes

- **Tokens expire** — extract and use links immediately; do not cache them for later steps
- **No auth required** — Mailcatcher runs with no credentials on localhost:1080
- **High-volume sessions** — when many test accounts are created, always filter by recipient email, not just subject, to avoid getting the wrong message
- **CORS blocker** — never attempt `fetch('http://localhost:1080/...')` from Playwright's browser context; always use curl from the agent shell
- **Delete messages** — if isolation is needed, `curl -X DELETE http://localhost:1080/messages` clears all messages. **ALWAYS ask the user before running this command** — it is irreversible and will destroy evidence from earlier test steps.

## Result

See the **Quick reference** at the top of this file for the script's exit-and-stdout contract — that is the authoritative return shape.
