#!/usr/bin/env bash
# Fetch a Bitwarden Mailcatcher message matching a recipient + subject, and print
# the first matching URL from its body on stdout.
#
# Exit 0 on success (prints the extracted URL on stdout).
# Exit 1: no matching message found, or a matched message had no local-host URL (diagnostic on stderr).
# Exit 3: Mailcatcher unreachable or returned invalid JSON.
# Exit 2: usage error.
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
  local json
  if ! json="$(curl -fsS "$MAILCATCHER_URL/messages" 2>/dev/null)"; then
    echo "ERROR: Mailcatcher unreachable at $MAILCATCHER_URL" >&2
    return 3
  fi
  printf '%s' "$json" | RECIPIENT="$RECIPIENT" PATTERN="$PATTERN" python3 -c "
import sys, json, os
try:
    msgs = json.load(sys.stdin)
except Exception:
    sys.exit(3)
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

# Local dev hosts allowed for extracted URLs (must match external-trigger.sh).
LOCAL_HOSTS="localhost 127.0.0.1 ::1 bitwarden.test"

is_local_url() {
  URL="$1" python3 -c '
import os, sys, urllib.parse
h = (urllib.parse.urlparse(os.environ["URL"]).hostname or "").lower()
allowed = set("'"$LOCAL_HOSTS"'".split())
sys.exit(0 if h in allowed else 1)
' 2>/dev/null
}

extract_url() {
  local id="$1"
  local body url
  body="$(curl -fsS "$MAILCATCHER_URL/messages/${id}.plain" 2>/dev/null || true)"
  if [ -z "$body" ]; then
    echo "WARNING: plain body empty for message $id; using HTML body for URL extraction" >&2
    body="$(curl -fsS "$MAILCATCHER_URL/messages/${id}.html" 2>/dev/null || true)"
  fi
  url="$(printf '%s' "$body" | grep -oE 'https?://[^ >\")]+' | grep -iE "$LINK_FILTER" | head -1)"
  [ -z "$url" ] && return 0
  if ! is_local_url "$url"; then
    echo "NO_MATCH: extracted URL '$url' is not a local dev host" >&2
    return 2
  fi
  printf '%s\n' "$url"
}

attempt() {
  local id rc
  id="$(find_message_id)"; rc=$?
  if [ "$rc" -eq 3 ]; then
    return 3
  fi
  if [ -z "$id" ]; then
    return 1
  fi
  local url
  url="$(extract_url "$id")"; rc=$?
  if [ "$rc" -eq 2 ]; then
    return 2
  fi
  if [ -z "$url" ]; then
    echo "NO_MATCH: message $id matched but contained no URL filtered by '$LINK_FILTER'" >&2
    return 2
  fi
  printf '%s\n' "$url"
  return 0
}

attempt; rc=$?
[ "$rc" -eq 0 ] && exit 0
[ "$rc" -eq 3 ] && exit 3          # unreachable — retry won't help
[ "$rc" -eq 2 ] && exit 1          # message/URL problem already reported — retry won't help

# rc was 1 (no message yet) — Mailcatcher may not have received it; retry once.
sleep 3
attempt; rc=$?
[ "$rc" -eq 0 ] && exit 0
[ "$rc" -eq 3 ] && exit 3
[ "$rc" -eq 2 ] && exit 1

if [ -n "$PATTERN" ]; then
  echo "NO_MATCH: no email for recipient '$RECIPIENT' with subject containing '$PATTERN'" >&2
else
  echo "NO_MATCH: no email for recipient '$RECIPIENT'" >&2
fi
exit 1
