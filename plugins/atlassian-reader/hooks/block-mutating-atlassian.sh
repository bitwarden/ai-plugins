#!/bin/bash
set -euo pipefail

# PreToolUse hook: enforces read-only Atlassian API access via ALLOWLIST.
# Only explicitly safe curl patterns are permitted — everything else is denied.
#
# The atlassian-reader skill needs exactly:
#   - Direct curl invocations (no eval, bash -c, pipes to shell)
#   - GET method only (explicit -X GET, or implicit GET with no method flag)
#   - -G + --data-urlencode for JQL/CQL query building
#   - Standard read-only flags: -H, -s, -S, --fail, -L, etc.
#
# Security model: fail CLOSED. Unknown patterns are denied.

deny() {
  cat <<HOOKEOF
{
  "hookSpecificOutput": {
    "permissionDecision": "deny"
  },
  "systemMessage": "BLOCKED by read-only hook: $1"
}
HOOKEOF
  exit 0
}

input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // empty')

# Pass through anything not targeting Atlassian
if [[ ! "$command" =~ atlassian\.(com|net) ]]; then
  exit 0
fi

# --- Gate 1: Block shell indirection ---
# These wrap or obscure the real command, defeating all subsequent checks.
# Match eval/source as whole words anywhere — no legitimate use in this skill.
if echo "$command" | grep -qEi '\beval\b|\bsource\b'; then
  deny "Shell indirection (eval/source) detected targeting Atlassian API. Only direct curl invocations are permitted."
fi

if echo "$command" | grep -qEi 'bash[[:space:]]+-c[[:space:]]'; then
  deny "Subshell execution (bash -c) detected targeting Atlassian API. Only direct curl invocations are permitted."
fi

if echo "$command" | grep -qEi '\|[[:space:]]*(bash|sh|zsh)([[:space:]]|$)'; then
  deny "Pipe to shell detected targeting Atlassian API. Only direct curl invocations are permitted."
fi

# --- Gate 2: Require direct curl command ---
# If it targets Atlassian and isn't curl, deny unconditionally. Fail closed.
if ! echo "$command" | grep -qE '(^|[;&|])[[:space:]]*curl[[:space:]]'; then
  deny "Non-curl command detected targeting Atlassian API. Only direct curl invocations are permitted by the read-only hook."
fi

# --- Gate 3: Only allow -X GET (allowlist, not blocklist) ---
# If -X/--request is present at all, the value must be literally GET. Anything else
# (POST, PO""ST, $METHOD, or unknown values) is denied.
if echo "$command" | grep -qEi '(-X[[:space:]]*[[:alpha:]]|-X[[:space:]]|--request([[:space:]]|=))'; then
  if ! echo "$command" | grep -qE '(-X[[:space:]]*|--request[[:space:]]*=?[[:space:]]*)GET([[:space:]]|$)'; then
    deny "Non-GET HTTP method detected targeting Atlassian API. The Atlassian reader skill is strictly read-only. Only GET requests are permitted."
  fi
fi

# --- Gate 4: Block --json flag (implies POST, curl >= 7.82) ---
if echo "$command" | grep -qE '(^|[[:space:]])(--json)([[:space:]=]|$)'; then
  deny "--json flag detected targeting Atlassian API. This flag implies a POST request. The Atlassian reader skill is strictly read-only."
fi

# --- Gate 5: Block data payload flags without -G ---
# -G converts data flags to GET query params (safe, used for JQL/CQL).
# Without -G, data flags imply POST. Match with or without space after flag.
if echo "$command" | grep -qEi '(^|[[:space:]])(-d[[:space:]"'\''@]|-d$|--data([[:space:]=]|$)|--data-raw([[:space:]=]|$)|--data-binary([[:space:]=]|$)|--data-urlencode([[:space:]=]|$))'; then
  if ! echo "$command" | grep -qE '(^|[[:space:]])-G([[:space:]]|$)'; then
    deny "Data payload flag detected targeting Atlassian API without -G flag, implying a POST request. Use -G with --data-urlencode for GET query parameters, or remove the data flag."
  fi
fi

# --- Gate 6: Block upload, output-to-file, and config-from-file flags ---
# These are never needed by the read-only skill.
BLOCKED_FLAGS=(
  '-F[[:space:]"'"'"']|--form[[:space:]=]'           # multipart upload
  '-T[[:space:]"'"'"']|--upload-file[[:space:]=]'     # PUT file upload
  '-o[[:space:]"'"'"']|--output[[:space:]=]'          # write response to file
  '-O([[:space:]]|$)'                                  # write response to file (remote name)
  '-K[[:space:]"'"'"']|--config[[:space:]=]'           # load flags from file (bypasses all checks)
)

BLOCKED_REASONS=(
  "File upload flag (-F/--form)"
  "File upload flag (-T/--upload-file)"
  "Output-to-file flag (-o/--output)"
  "Output-to-file flag (-O)"
  "Config-from-file flag (-K/--config). This loads curl options from a file, bypassing safety checks"
)

for i in "${!BLOCKED_FLAGS[@]}"; do
  if echo "$command" | grep -qEi "(^|[[:space:]])(${BLOCKED_FLAGS[$i]})"; then
    deny "${BLOCKED_REASONS[$i]} detected targeting Atlassian API. The Atlassian reader skill is strictly read-only and does not permit this flag."
  fi
done

# --- Gate 7: Block variable expansion in method position ---
# Catches: curl -X $METHOD, curl -X ${METHOD}, curl -X $(cmd)
if echo "$command" | grep -qE '(-X|--request)[[:space:]]*=?[[:space:]]*(\$\{?\w|\$\()'; then
  deny "Variable expansion in HTTP method position detected targeting Atlassian API. The method must be a literal value (GET) for safety verification."
fi

exit 0
