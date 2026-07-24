#!/usr/bin/env bash
# external-trigger.sh — Category 3 external-trigger simulation for the
# bitwarden-playwright-testing pipeline. The ONLY sanctioned way for the
# test-runner to issue an outbound request. Enforces, in code, the localhost-only
# policy that references/tool-policy.md describes: a plan step (which may be
# derived from untrusted Jira/Confluence content) cannot drive a request to a
# metadata endpoint, a private-network host, an external host, or a remote
# Bitwarden QA/cloud domain.
#
# Usage:
#   external-trigger.sh --url <url> --rationale <text> [--data <json>] [--content-type <ct>]
#
# Method is always POST (Category 3 triggers are POSTs). Allowed hosts default to
# localhost/127.0.0.1/::1/bitwarden.test and can be extended (never replaced) via
# the comma-separated env var PLAYWRIGHT_TESTING_ALLOWED_HOSTS. Allowed schemes are
# http and https. Every permitted call is logged; if PLAYWRIGHT_TESTING_ARTIFACTS_DIR
# is set, the log line is appended to <dir>/external-trigger.log.
#
# Exit codes: 0 request completed; 2 usage error; 10 disallowed host;
# 11 disallowed scheme; 12 disallowed method; 13 malformed URL.

set -u

URL=""
RATIONALE=""
DATA=""
CONTENT_TYPE="application/json"
METHOD="POST"

while [ $# -gt 0 ]; do
  case "$1" in
    --url)          URL="$2"; shift 2 ;;
    --rationale)    RATIONALE="$2"; shift 2 ;;
    --data)         DATA="$2"; shift 2 ;;
    --content-type) CONTENT_TYPE="$2"; shift 2 ;;
    --method)       METHOD="$2"; shift 2 ;;
    -h|--help)      sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//' >&2; exit 0 ;;
    *)              echo "ERROR: unknown argument: $1" >&2; exit 2 ;;
  esac
done

[ -z "$URL" ]       && { echo "ERROR: --url is required" >&2; exit 2; }
[ -z "$RATIONALE" ] && { echo "ERROR: --rationale is required (document why no Bitwarden service can initiate this)" >&2; exit 2; }

if [ "$METHOD" != "POST" ]; then
  echo "ERROR: method '$METHOD' not allowed; Category 3 external triggers are POST only" >&2
  exit 12
fi

# Parse scheme + host with a real URL parser (no substring matching).
PARSED="$(URL="$URL" python3 -c '
import os, sys, urllib.parse
u = urllib.parse.urlparse(os.environ["URL"])
if not u.scheme or not u.hostname:
    sys.exit(3)
print(u.scheme.lower())
print(u.hostname.lower())
' 2>/dev/null)" || { echo "ERROR: malformed URL: $URL" >&2; exit 13; }

SCHEME="$(printf '%s\n' "$PARSED" | sed -n '1p')"
HOST="$(printf '%s\n' "$PARSED" | sed -n '2p')"
[ -z "$SCHEME" ] || [ -z "$HOST" ] && { echo "ERROR: malformed URL: $URL" >&2; exit 13; }

case "$SCHEME" in
  http|https) ;;
  *) echo "ERROR: scheme '$SCHEME' not allowed; use http or https" >&2; exit 11 ;;
esac

# Build the allowlist: defaults plus any env-provided extensions.
ALLOWED="localhost 127.0.0.1 ::1 bitwarden.test"
if [ -n "${PLAYWRIGHT_TESTING_ALLOWED_HOSTS:-}" ]; then
  EXTRA="$(printf '%s' "$PLAYWRIGHT_TESTING_ALLOWED_HOSTS" | tr ',' ' ')"
  ALLOWED="$ALLOWED $EXTRA"
fi

HOST_OK=0
for h in $ALLOWED; do
  if [ "$HOST" = "$(printf '%s' "$h" | tr 'A-Z' 'a-z')" ]; then HOST_OK=1; break; fi
done
if [ "$HOST_OK" -ne 1 ]; then
  echo "ERROR: host '$HOST' is not an allowed local dev host." >&2
  echo "       Allowed: $ALLOWED" >&2
  echo "       For a custom local hostname, set PLAYWRIGHT_TESTING_ALLOWED_HOSTS=<host>[,<host>...]." >&2
  exit 10
fi

# Log the permitted call (auditability).
LOG_LINE="external-trigger POST $URL — $RATIONALE"
echo "$LOG_LINE" >&2
if [ -n "${PLAYWRIGHT_TESTING_ARTIFACTS_DIR:-}" ] && [ -d "$PLAYWRIGHT_TESTING_ARTIFACTS_DIR" ]; then
  printf '%s\n' "$LOG_LINE" >> "$PLAYWRIGHT_TESTING_ARTIFACTS_DIR/external-trigger.log"
fi

# Execute. -k mirrors health-check.sh: Bitwarden dev certs are self-signed and the
# host is already constrained to the local dev allowlist above.
if [ -n "$DATA" ]; then
  curl -k -sS -X POST -H "Content-Type: $CONTENT_TYPE" --data "$DATA" "$URL"
else
  curl -k -sS -X POST -H "Content-Type: $CONTENT_TYPE" "$URL"
fi
