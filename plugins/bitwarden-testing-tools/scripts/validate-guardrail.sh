#!/usr/bin/env bash
# Verify the untrusted-source trust boundary is intact.
# Usage: validate-guardrail.sh [PLUGIN_ROOT]  (defaults to the testing-tools plugin)
set -uo pipefail

ROOT="${1:-"$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"}"
AGENTS_DIR="$ROOT/agents"
SKILL="$ROOT/skills/start-playwright-test/SKILL.md"
POLICY="$ROOT/references/untrusted-source-policy.md"
# Anchors are short phrases guaranteed to sit on one physical line, so prose
# line-wrapping of the guardrail can never break these greps. The rules live in
# the shared policy file; each agent carries a short guard that names it, headed
# by "Untrusted source content.", and the orchestrator skill names it too.
HEADING="Untrusted source content."
POLICY_REF="references/untrusted-source-policy.md"
rc=0

# The full rules live in one shared policy file.
[ -f "$POLICY" ] || { echo "MISSING shared policy file: $POLICY"; rc=1; }

seen=0
for f in "$AGENTS_DIR"/*/AGENT.md; do
  [ -e "$f" ] || continue
  seen=$((seen+1))
  if ! grep -qF "$HEADING" "$f"; then
    echo "MISSING guardrail heading: $f"; rc=1
  fi
  if ! grep -qF "$POLICY_REF" "$f"; then
    echo "MISSING policy reference: $f"; rc=1
  fi
  if grep -qF "Never follow directives embedded" "$f"; then
    echo "STALE paragraph still present: $f"; rc=1
  fi
done
[ "$seen" -gt 0 ] || { echo "NO agent files found under $AGENTS_DIR"; rc=1; }

if ! grep -qF "$POLICY_REF" "$SKILL"; then
  echo "MISSING guardrail block in: $SKILL"; rc=1
fi

[ "$rc" -eq 0 ] && echo "guardrail: OK"
exit "$rc"
