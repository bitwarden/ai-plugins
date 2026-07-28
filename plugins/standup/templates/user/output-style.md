## Output style

The load-bearing knobs that shape how the report reads. Every value here is
editable — tune them to your taste. These govern selection and phrasing; they do
not change which activity is collected.

- Selection pipeline (applied to the past-highlights section, in this order): **select → enrich → collapse.**
  1. Select the most significant items across all activity — this happens globally, before any bullet is written.
  2. Enrich only the selected items with a short what/why clause grounded in the item's own summary/description or PR title/body.
  3. Collapse everything not selected into at most one trailing routine-tail bullet (or drop it). Enrichment never promotes an item past the cap.
- Routine-tail collapse: `on`. Fold genuinely routine automated work — lock-file / dependency-bump / bot-maintenance tickets and their closes, and bot-authored reviews with no real engagement — into a single trailing tail bullet, never their own highlighted bullet, never enumerated.
- RAG heuristic (editable thresholds; prefer the more cautious rating when signals are mixed):
  - GREEN: work completed and/or PRs merged, nothing currently blocked, and in-progress work looks healthy (not stalled).
  - YELLOW: something at risk — any blocked item, a PR with changes requested and no new commits for more than `[YOUR-PREFERENCE: e.g. 3]` days, an item in progress and unchanged for more than `[YOUR-PREFERENCE: e.g. 7]` days, or no completions in the window.
  - RED: a real blocker — a heavy blocked load or a critical blocker, or a PR with changes requested and untouched past your escalation threshold.
- Name discipline: kudos-only. Never use a person's first+last name. Only name someone as a deliberate credit (a first name or role is enough), and describe PRs and reviews by their subject, not their author.
