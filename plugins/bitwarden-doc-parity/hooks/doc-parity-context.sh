#!/bin/bash
# doc-parity-context.sh
# SessionStart hook: injects the base documentation obligations into every
# session as additional context, so no repo has to hand-carry them in its
# root CLAUDE.md. The canonical obligation text lives in
# doc-parity-instructions.md next to this script.
#
# Fail-open: if the fragment or jq is unavailable, the session proceeds
# without the context rather than erroring.

set -uo pipefail

FRAGMENT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}/hooks/doc-parity-instructions.md"

if [[ ! -f "$FRAGMENT" ]] || ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

jq -n --rawfile ctx "$FRAGMENT" '{
  hookSpecificOutput: {
    hookEventName: "SessionStart",
    additionalContext: $ctx
  }
}'
