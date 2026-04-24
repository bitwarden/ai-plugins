# Report Template

## Severity Icons

- 🛑 **Blocker** — Must fix before merge
- ⚠️ **Important** — Potential issue, should fix
- ♻️ **Refactor** — Code restructuring needed
- 💡 **Suggestion** — Nice-to-have improvement

## Template

```markdown
# Code Review: {PR title} (#{number}) <!-- or "Code Review: Local Changes — {YYYY-MM-DD}" -->

**Date:** {YYYY-MM-DD} | **Reviewed by:** Claude Code

## Summary

| Severity      | Count |
| ------------- | ----- |
| 🛑 Blocker    | {n}   |
| ⚠️ Important  | {n}   |
| ♻️ Refactor   | {n}   |
| 💡 Suggestion | {n}   |

{1-3 sentences for overall assessment.}

## Findings

### 🛑 Blockers

#### {One-line summary (<100 chars)}

`{file/path.ext}:{line}`

  <details><summary>Details</summary>
  {Explanation, why it matters, suggested fix. Include code snippets where helpful.}
  </details>

### ⚠️ Important

### ♻️ Refactor

### 💡 Suggestions

<!-- Only if there are rejected findings. Omit entirely if all confirmed. -->

## Reviewed and Dismissed

   <details><summary>🔍 {n} initial findings dismissed after validation</summary>

   <!-- Repeat the stanza below once per dismissed finding. -->

   #### {One-line summary}
   `{file/path.ext}:{line}`
   **Original severity:** {🛑|⚠️|♻️|💡} {Blocker|Important|Refactor|Suggestion}
   **Original confidence:** {n}/100
   **Dismissed at:** {Step 4 validation | Step 5 severity audit}
   **Dismissed because:** {One-sentence rejection reason}

   </details>
```
