#!/usr/bin/env bash
#
# preflight-credentials.sh -- PreToolUse gate for the standup plugin.
#
# Fires (via hooks/hooks.json) before any `python3 ...` Bash tool call.
# Self-scopes to the collector's `gather.py` invocation; for every other
# python3 command it exits 0 (allow, no-op).
#
# When it IS the gather.py call, it verifies credential PRESENCE only:
#   - JIRA_API_TOKEN is set and non-empty
#   - `gh auth status` succeeds (GitHub CLI is authenticated)
# It NEVER reads, prints, or logs any token/credential VALUE.
#
# Exit codes (PreToolUse semantics):
#   0  -> allow the tool call to proceed
#   2  -> BLOCK the tool call; stderr is surfaced to the model/user
#
# The hook receives the tool-call JSON on stdin:
#   { "tool_name": "Bash", "tool_input": { "command": "python3 .../gather.py ..." } }

set -u

# Read the hook payload from stdin (may be empty in manual tests).
payload="$(cat 2>/dev/null || true)"

# Extract the Bash command string. Prefer jq; fall back to a grep/sed shim
# so the hook works even if jq is unavailable on the host.
if command -v jq >/dev/null 2>&1; then
  cmd="$(printf '%s' "$payload" | jq -r '.tool_input.command // ""' 2>/dev/null)"
else
  cmd="$(printf '%s' "$payload" \
    | tr -d '\n' \
    | sed -n 's/.*"command"[[:space:]]*:[[:space:]]*"\(.*\)".*/\1/p')"
fi

# Self-scope: only guard the collector entry point. Any other python3 call
# (or an unparseable payload) is allowed through untouched.
case "$cmd" in
  *gather.py*) : ;;   # this is the standup collector -> run the checks
  *) exit 0 ;;
esac

# Dry-run / help modes make zero network calls and need no credentials.
case "$cmd" in
  *--dry-run*|*--help*|*" -h"*) exit 0 ;;
esac

# --- Credential PRESENCE checks (never echo any value) ---
missing=""

if [ -z "${JIRA_API_TOKEN:-}" ]; then
  missing="${missing}
  - JIRA_API_TOKEN is not set. Export your Atlassian API token before running the standup report (e.g. via your shell profile or a secrets manager). The token value is never read or printed by this check."
fi

if ! gh auth status >/dev/null 2>&1; then
  missing="${missing}
  - GitHub CLI is not authenticated. Run 'gh auth login' and retry. This check only inspects auth STATUS; no token is read or printed."
fi

if [ -n "$missing" ]; then
  printf 'Standup preflight failed - missing prerequisite(s):%s\n' "$missing" >&2
  exit 2
fi

exit 0
