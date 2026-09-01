# Manual Mailcatcher API walkthrough (debugging only)

This skill sanctions only the co-located `read_mailcatcher.py` script for reading Mailcatcher; its `allowed-tools` grants that script alone, and curl, direct API calls, and sub-agents are not sanctioned transports. This file exists for interactive debugging when the script itself is misbehaving.

Every command here needs a fresh permission prompt. This skill's `allowed-tools` grants only the co-located script.

## Prerequisite check

Verify Mailcatcher is reachable before working through the steps below:

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

- `NO_MATCH` — no matching email yet; `read_mailcatcher.py` retries once after a 3 s sleep (`RETRY_DELAY`), so when stepping through by hand, wait ~3 s and retry once — if it is still missing, the message has most likely not been sent
- A numeric ID — proceed to Step 3

**When filtering:**

- Match on recipient email when the test account address is known (preferred)
- Match on subject keyword when recipient is generic/unknown
- Always take `max(id)` — higher ID = more recent message

### Step 3 — Fetch the message body

For link/token extraction, plain text is usually sufficient and easier to parse:

```bash
curl -s http://localhost:1080/messages/<message-id>.plain
```

`<message-id>` is the numeric id from Step 2. Substitute it into each command below: every block runs in a fresh shell, so a value set in one does not carry into the next.

Use `.html` only when the plain text body is empty or the link is only in the HTML part:

```bash
curl -s http://localhost:1080/messages/<message-id>.html
```

### Step 4 — Extract the link or token

**Extract any URL matching a keyword pattern:**

```bash
curl -s http://localhost:1080/messages/<message-id>.plain | \
  grep -oE 'https?://[^ >)"]+' | grep -i 'verify\|confirm\|signup\|token\|trial\|login\|finish-signup' | head -1
```

**Extract an admin magic link:**

```bash
curl -s http://localhost:1080/messages/<message-id>.plain | \
  grep -oE 'http://localhost:62911/login/confirm[^ >)"]+' | head -1
```

**Extract a web vault verification/signup link:**

```bash
curl -s http://localhost:1080/messages/<message-id>.plain | \
  grep -oE 'https://localhost:8080/#/[^ >)"]+' | head -1
```

## Message metadata and deletion (debugging only)

Fetch a message's raw JSON metadata (id, recipients, subject, available formats):

```bash
curl -s http://localhost:1080/messages/<message-id>.json
```

The two commands below are destructive and irreversible. Clearing the inbox mid-run destroys verification tokens that earlier test steps depend on. They are not covered by this skill's `allowed-tools`, so each requires a fresh permission prompt.

| Operation               | Command                                                                                   |
| ----------------------- | ----------------------------------------------------------------------------------------- |
| Delete specific message | `curl -X DELETE http://localhost:1080/messages/{id}`                                      |
| Clear all messages      | `curl -X DELETE http://localhost:1080/messages` — **ALWAYS ask user first; irreversible** |
