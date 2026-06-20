# Pipeline Mechanics

Per-stage detail for the fixed pipeline `SELECT → CHECK YOURSELF → PILOT → FAN-OUT → REPORT → REMEDIATE`. The reality-check stages (CHECK YOURSELF, the pilot gate, the report reconciliation) are covered in `safety-and-self-checks.md`; this file covers the mechanical stages.

## SELECT

Enumerate, then filter, using `finding-targets.md`. The output is an **explicit, finite list** of resolved targets — names for multi-repo, paths for monorepo — each annotated with why it was included (which signal matched). Show the list to the user. A campaign that cannot name its targets is not ready to run.

Record the count. It anchors the reconciliation in REPORT: `selected = applied + already-compliant + skipped-not-applicable + failed`.

## PILOT

Pick one representative target — not the easiest one; one whose shape is typical of the fleet. Run the recipe on it, surface the full diff, validate it. The pilot is the contract: "this exact change, ×N." Its mechanics are identical to one FAN-OUT iteration, except it stops for explicit confirmation and discards (or keeps, if the user approves) its branch. Lock the `pr_spec` here — title format, body template, labels — because FAN-OUT replicates it without re-prompting.

## FAN-OUT

Process confirmed targets in chunks of at most `max_targets_per_run`. For agentic recipes, send one chunk's Agent calls in a single message so they run concurrently. Each target is handled **in isolation** — its failure is recorded and the rest continue.

Per target, in order:

1. **Clone / locate.** Multi-repo: shallow-clone into a scratch dir. Monorepo: operate on the project path within the single clone.
2. **Re-verify applicability.** Confirm the signal is actually present (code search can be stale). If absent → `skipped-not-applicable`, stop here.
3. **Check idempotency.** If the recipe's idempotency condition is already satisfied → `already-compliant`, stop here (no branch, no commit, no PR).
4. **Branch.** Create the deterministic branch from the `pr_spec` template, cut from the target's default branch — never work on the default branch itself. Same input → same name, so a re-run reuses it rather than forking a duplicate.
5. **Apply the recipe.** Deterministic: run the edit/script. Agentic: spawn the scoped sub-agent with only this target and its minimal toolset. If the result is somehow an empty diff, treat it as `already-compliant` and discard the branch.
6. **Second pass.** Run the per-target skeptical review (see `safety-and-self-checks.md`) — did the recipe do _only_ what the intent describes?
7. **Diff-shape check.** Compare this diff against the pilot's. A materially different shape (far more files, unexpected paths) is a red flag — the recipe hit something unanticipated. Flag it; do not silently ship it.
8. **Validate.** Run the target's gate (`validation` field + `Skill(perform-preflight)`). Fail → `failed`, no commit, no PR.
9. **Secrets-scan** the staged diff. Any hit → `failed`, no commit.
10. **Commit** per `Skill(committing-changes)`, using the locked title/type.
11. **Push and open a draft PR** per the locked `pr_spec` — never to a default branch, never force-pushed. Capture the PR URL.

If `dry_run` is set, perform steps 1–9 and stop before commit/push; record what _would_ have shipped.

## REPORT

Aggregate one row per target:

| Target   | Status                                                        | PR           | Notes                                |
| -------- | ------------------------------------------------------------- | ------------ | ------------------------------------ |
| `<name>` | applied / already-compliant / skipped-not-applicable / failed | `<url or —>` | `<divergence, failure reason, or —>` |

Then state the reconciliation explicitly: `selected = applied + already-compliant + skipped-not-applicable + failed`. If the arithmetic does not close, a target was dropped silently — find it before reporting done. Surface divergence flags and failure reasons in full; do not bury them under a success headline. See the prove-don't-declare discipline in `safety-and-self-checks.md`.

## REMEDIATE

Re-run the campaign against only the `failed` and `skipped-not-applicable` subset. Because every recipe declares an idempotency condition, a target that already succeeded is a clean no-op if it sneaks back into the set. Fix the root cause first — a recipe that failed validation on five targets the same way needs a recipe fix, not five retries.

## Idempotency rules

- The recipe's idempotency condition is checked before applying; if already satisfied, the target is recorded `already-compliant` — no branch, no commit, no PR.
- Branch names are deterministic functions of the campaign + target, so re-runs reuse branches and PRs rather than multiplying them.
- A re-run of a fully-successful campaign produces zero new changes and zero new PRs.

## Rate limits

The GitHub API is rate-limited and bulk enumeration plus per-target calls can exhaust it. On a 403 or 429, back off exponentially and retry; insert a small delay between per-target API calls in large runs. Prefer one enumeration pass reused across the campaign over re-querying per target. A rate-limit pause is not a campaign failure — wait and resume.
