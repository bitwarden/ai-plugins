# Discovery Standards

Loaded by the orchestrator in Step 1. The **Hygiene Sweep** is invoked by name from the Step 3 Agent 1 (code quality) prompt. The **Line Number Accuracy** rule is propagated verbatim into every Step 2–5 subagent prompt.

## Hygiene Sweep

Agent 1 (code quality) performs a hygiene sweep of the diff before submitting findings; the Step 2 architect performs an analogous doc/code consistency pass per its own directive. When referenced, look specifically for:

- **Dead code added by this PR** — allowlist/registry/lookup-table entries added for features that don't flow through the validated entry point; unused imports; unreachable branches.
- **Stale references** — documentation, comments, error messages, or assertions in this diff that contradict the same diff's implementation.
- **Cross-site inconsistency** — a new call site that differs from established sibling sites in a way not explained by the change (e.g., four platform dialogs where three carry a title and the fourth silently drops it).

This is not an exhaustive checklist — surface anything diff-visible that a senior engineer would flag in a real review.

## Line Number Accuracy

Cite **actual file line numbers**, not positions within the diff. Derive them from the hunk header:

- Parse `@@ -A,B +C,D @@` — `+C` is the starting file line for the hunk. New files use `@@ -0,0 +1,N @@`, so C=1.
- From `+C`, count `+` lines and context lines (no prefix) up to your target. Skip `-` lines, `@@` lines, and `---`/`+++` lines.

**Never guess. Always derive from the hunk header.**
