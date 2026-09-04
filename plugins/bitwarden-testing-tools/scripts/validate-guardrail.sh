#!/usr/bin/env bash
# Verify the untrusted-source trust boundary is intact.
# Usage: validate-guardrail.sh [PLUGIN_ROOT]  (defaults to the testing-tools plugin)
set -uo pipefail

ROOT="${1:-"$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"}"
AGENTS_DIR="$ROOT/agents"
SKILL="$ROOT/skills/start-playwright-test/SKILL.md"
# Anchors are short phrases guaranteed to sit on one physical line, so prose
# line-wrapping of the guardrail/backstop can never break these greps.
BACKSTOP="names this run's fence token"
GUARD="delimit that source"
rc=0

seen=0
for f in "$AGENTS_DIR"/*/AGENT.md; do
  [ -e "$f" ] || continue
  seen=$((seen+1))
  if ! grep -qF "$BACKSTOP" "$f"; then
    echo "MISSING backstop: $f"; rc=1
  fi
  if grep -qF "Never follow directives embedded" "$f"; then
    echo "STALE paragraph still present: $f"; rc=1
  fi
done
[ "$seen" -gt 0 ] || { echo "NO agent files found under $AGENTS_DIR"; rc=1; }

if ! grep -qF "$GUARD" "$SKILL"; then
  echo "MISSING guardrail block in: $SKILL"; rc=1
fi
if ! grep -qF "gen-nonce.sh" "$SKILL"; then
  echo "MISSING token generation in: $SKILL"; rc=1
fi

[ "$rc" -eq 0 ] && echo "guardrail: OK"
exit "$rc"
