# Manual Mailcatcher API walkthrough (debugging only)

The pipeline forbids this transport. `executing-web-tests` states that the co-located script is the only sanctioned way to read Mailcatcher, and that curl, direct API calls, and sub-agents must not be used instead. This file exists for interactive debugging when the script itself is misbehaving.

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
