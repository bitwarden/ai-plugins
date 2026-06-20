# Safety and Self-Checks

Force Multiplier's whole risk is leverage: one mistake becomes _N_. The defense is not cleverness per target — it is proof at every gate. This file is the full checks-and-balances model. Three reality checks bracket the run: **before** (check yourself), **on one** (pilot), and **after** (reconcile).

## Reality-check #1 — Check yourself, before you touch anything

Expanded from the SKILL.md gate. Answer all of it honestly; "probably fine" is not an answer.

- **Intent.** Restate it in your own words and get confirmation. The thing you are about to repeat ×N must be the thing that was asked for — not the more interesting thing you would rather do, not the adjacent thing you noticed.
- **Target list, both directions.** Open two or three _included_ targets and confirm the signal is really there — no false positives. Then reason about _exclusions_: what uses the thing under a different name, path, or version and would be silently missed — no false negatives. A wrong target list poisons the whole run.
- **Idempotency.** Re-running the recipe on an already-done target must be a clean no-op. If it is not, you cannot safely remediate, and a partial run becomes unrecoverable. Fix this first.
- **Reversibility.** If the recipe deletes or rewrites, treat it as destructive and run the reference-check below before anything else.
- **Blast radius.** Confirm `max_targets_per_run`. A large fleet chunks; it never fans out unbounded in one shot. The cap is a circuit breaker.
- **Sub-agent scope.** Each per-target agent gets the minimum toolset and only its single target. Forbid `WebFetch`/`WebSearch` unless the recipe truly needs them — they bypass `gh` auth and audit.

If any answer is missing, you are not ready to pilot. Name what is unresolved.

## Reality-check #2 — The pilot gate (prove it on one)

You do not get to declare the recipe correct. You get to prove it — once, in full, before it scales.

- Run the recipe on one representative target and surface the **entire** diff. Read every line, at the standard of "I am about to apply this to the whole fleet and explain every line." No scanning.
- Pretend your worst enemy wrote the recipe, and interrogate the pilot diff:
  - Did it do **only** what the intent describes, or did it improve adjacent code nobody asked about?
  - Did it solve the stated problem, or a different, more interesting one?
  - Edge cases — empty file, missing section, the config that already has the value, the variant spelling — handled, or assumed away?
  - Anything added and unused? Any copy-paste seam from whatever it was patterned on?
- Validate the pilot for real — build/lint/test, not "it should pass." If you cannot run validation, say so explicitly instead of implying confidence you have not earned.
- If the pilot diverges from intent or fails validation: **STOP.** Do not fan out. Fix the recipe and re-pilot. A bad recipe caught at the pilot costs one target; caught at REPORT it costs _N_.

## Reality-check #2b — The per-target second pass

Each fan-out target gets its own quick skeptical pass before its commit, because targets differ and a recipe that was clean on the pilot can misfire on an outlier:

- Did this target's recipe do only what was asked on _this_ target?
- Does its diff shape match the pilot's? A target with far more files changed, or changes in unexpected paths, is a signal the recipe hit something unanticipated — flag it, do not ship it silently.
- Did validation actually pass, or was it skipped?

## Reality-check #3 — Reconcile, don't declare victory

A finished run is not a successful run until the numbers close and the claims are proven.

- **Reconcile the arithmetic:** `selected = applied + already-compliant + skipped-not-applicable + failed`. If it does not close, a target vanished silently — find it.
- **Prove the PRs:** each `applied` target has a real PR URL, and each PR is a draft on a non-default branch. "I opened the PRs" is a claim; the URLs are the proof. An `already-compliant` target needed no change, so it has no PR by design — that is not a missing PR.
- **Surface the bad news first.** Failures, divergence flags, and skips go in the report in full, not buried under a success headline.

## Reference-check (required before destructive recipes)

Before a recipe deletes or rewrites something, prove the thing is not depended on:

- Is the file/workflow/symbol referenced elsewhere — a required status check, a `uses:` reference, an import, a documented entry point? Removing a depended-on thing breaks the target even when the local edit looks clean.
- Run this as a read-only pre-step across the affected targets and report what it finds. If anything depends on the target of deletion, the campaign pauses for a human decision.

## Secrets handling

- Scan the staged diff for secrets before **every** commit — token prefixes, key material, and high-entropy strings, using the repo's configured scanner when one exists. Any hit aborts that target's commit — it is recorded `failed`, never committed. A secret committed once across a fan-out is leaked _N_ times.
- Never commit credentials, tokens, or keys, even in examples or fixtures.

## Credential posture

- Reuse the already-configured `gh` authentication. Do not invent token-injection flows, do not read secrets into environment variables for logging, do not write credentials to disk.
- Least privilege: the campaign needs read access to enumerate and write access to open draft PRs — nothing more. It never merges.

## Dry-run

`--dry-run` performs everything through validation and the secrets-scan, then stops before commit, push, and PR. It reports what _would_ have shipped per target. Use it as the zero-risk rehearsal of a campaign before committing to the real fan-out.
