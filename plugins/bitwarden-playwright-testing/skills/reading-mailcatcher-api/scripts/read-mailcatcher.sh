#!/usr/bin/env bash
# Fetch a Bitwarden Mailcatcher message matching a recipient + subject, and print
# the first matching URL from its body on stdout. Exit 0 on success.
# On NO_MATCH, exits 1 with a single-line diagnostic on stderr.
#
# Usage:
#   read-mailcatcher.sh --recipient <email> [--pattern <subject-keyword>] [--link-filter <regex>]
#
# --pattern is optional. Omit (or pass empty) to match any subject and just take the
# most recent message for the recipient.
#
# Defaults:
#   --link-filter: verify|confirm|signup|token|trial|login|finish-signup
#
# Designed to be called via the Bash tool from the test-runner. The skill body in
# ../SKILL.md documents the underlying Mailcatcher REST API this wraps.

set -u

MAILCATCHER_URL="${MAILCATCHER_URL:-http://localhost:1080}"
RECIPIENT=""
PATTERN=""
LINK_FILTER="verify|confirm|signup|token|trial|login|finish-signup"

while [ $# -gt 0 ]; do
  case "$1" in
    --recipient)   RECIPIENT="$2"; shift 2 ;;
    --pattern)     PATTERN="$2"; shift 2 ;;
    --link-filter) LINK_FILTER="$2"; shift 2 ;;
    -h|--help)
      sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//' >&2
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [ -z "$RECIPIENT" ]; then
  echo "ERROR: --recipient is required" >&2
  exit 2
fi

find_message_id() {
  curl -fsS "$MAILCATCHER_URL/messages" 2>/dev/null | RECIPIENT="$RECIPIENT" PATTERN="$PATTERN" python3 -c "
import sys, json, os

try:
    msgs = json.load(sys.stdin)
except Exception:
    sys.exit(2)

recipient = os.environ['RECIPIENT'].lower()
pattern = os.environ['PATTERN'].lower()

matches = [
    m for m in msgs
    if any(recipient in r.lower() for r in m.get('recipients', []))
    and (not pattern or pattern in m.get('subject', '').lower())
]
if not matches:
    sys.exit(1)
print(max(matches, key=lambda m: m['id'])['id'])
"
}

extract_url() {
  local id="$1"
  local body
  body="$(curl -fsS "$MAILCATCHER_URL/messages/${id}.plain" 2>/dev/null || true)"
  if [ -z "$body" ]; then
    body="$(curl -fsS "$MAILCATCHER_URL/messages/${id}.html" 2>/dev/null || true)"
  fi
  printf '%s' "$body" | grep -oE 'https?://[^ >\")]+' | grep -iE "$LINK_FILTER" | head -1
}

attempt() {
  local id
  id="$(find_message_id)"
  if [ -z "$id" ]; then
    return 1
  fi
  local url
  url="$(extract_url "$id")"
  if [ -z "$url" ]; then
    echo "NO_MATCH: message $id matched but contained no URL filtered by '$LINK_FILTER'" >&2
    return 2
  fi
  printf '%s\n' "$url"
  return 0
}

if attempt; then
  exit 0
fi

# One retry — Mailcatcher may not have received the message yet.
sleep 3
if attempt; then
  exit 0
fi

if [ -n "$PATTERN" ]; then
  echo "NO_MATCH: no email for recipient '$RECIPIENT' with subject containing '$PATTERN'" >&2
else
  echo "NO_MATCH: no email for recipient '$RECIPIENT'" >&2
fi
exit 1
