# Report Template

## Severity Icons

- 🛑 **Blocker** — Must fix before merge
- ⚠️ **Important** — Potential issue, should fix
- ♻️ **Refactor** — Code restructuring needed

## Source-Agent Friendly Names

Every finding carries a `source_agent` value (per `finding-shape.md`). Render it on each finding using the friendly label below — it tells the reader which subagent caught the issue, which aids triage and per-agent calibration.

| `source_agent` | Rendered label                |
| -------------- | ----------------------------- |
| `architect`    | Architecture agent            |
| `quality`      | Code quality agent            |
| `bug`          | Bug analysis agent            |
| `security`     | Security & logic agent        |
| `validation`   | Validation agent (collateral) |

## Template

```markdown
# Code Review: {PR title} (#{number}) <!-- or "Code Review: Local Changes — {YYYY-MM-DD}" -->

**Date:** {YYYY-MM-DD} | **Reviewed by:** Claude Code

## Summary

| Severity     | Count |
| ------------ | ----- |
| 🛑 Blocker   | {n}   |
| ⚠️ Important | {n}   |
| ♻️ Refactor  | {n}   |

{1-5 sentences for overall assessment.}

## Findings

### 🛑 Blockers

#### {One-line summary (<100 chars)}

`{file/path.ext}:{line}`
**Caught by:** {Friendly agent label}

  <details><summary>Details</summary>
  {Explanation, why it matters, suggested fix. Include code snippets where helpful.}
  </details>

### ⚠️ Important

### ♻️ Refactor

<!-- Only if there are rejected findings. Omit entirely if all confirmed. -->

## Reviewed and Dismissed

   <details><summary>🔍 {n} initial findings dismissed after validation</summary>

   <!-- Repeat the stanza below once per dismissed finding. -->

#### {One-line summary}

`{file/path.ext}:{line}`
**Caught by:** {Friendly agent label}
**Original severity:** {🛑|⚠️|♻️} {Blocker|Important|Refactor}
**Original confidence:** {n}/100
**Dismissed at:** {Step 4 validation | Step 5 severity audit}
**Dismissed because:** {One-sentence rejection reason}

   </details>
```
