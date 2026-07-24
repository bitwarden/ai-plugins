# Isolation and blinding

If a run can see the other variant, the ledger, or a prior result, its output tells you nothing.

## Why separate top-level sessions

**Run each variant in its own fresh, top-level session.** Not subagents.

Subagents were tried first and failed. Skill routing leaks across the subagent boundary: one instructed to use `variant-a` can load `variant-b`, because the parent session's plugin state bleeds in. The failure is silent, so you catch it only in the taint check, after wasting the run. Separate top-level sessions do not share that state.

Subagents are fine for throwaway iteration while shaping the treatment. Not for the runs that decide the verdict.

## Do not prime the subject

- Do not say what the other variant produced.
- Do not say what correct or complete looks like.
- Do not name the thing you are worried it will miss. "Be sure to check the revert PR" tests whether the model follows instructions, not whether the skill finds the revert.

Prompts for the two variants must be byte-for-byte identical except the skill name.

## Neutral phrasing for questions

A blanket "do not ask me any questions" suppresses behavior that may be exactly what you are measuring. If a skill's value includes knowing when to stop and ask the user to clone a missing repository, a no-questions prompt prevents that behavior from ever appearing and you will conclude the skill lacks it.

Use: **"Proceed with sensible defaults; ask only if you genuinely need a decision from me."** Do not name the specific decision you are curious about; that primes it.

## Always capture an execution log

Require a factual execution log alongside the work product: ordered steps, every tool, skill, and CLI call with its purpose, and anything that blocked it or it could not determine. Facts only, no meta-commentary.

Two later phases depend on it. The taint check reads it to confirm which skill loaded. Attribution reads it to tell a skill difference from a search-path difference.

## The taint check

1. Read each execution log, and grep the raw transcript where available, for the `Skill(...)` invocation. It must have loaded **only its own variant**. Wrong variant or both means tainted.
2. Confirm it never read the other variant's files, the directive ledger, or anything under `results/`.
3. Record **CLEAN** or **TAINTED** in `SESSION-STATE.md` with the evidence, for example "loaded assessing-test-coverage-min, 0 reads of the rich skill, 0 reads of results/".

Discard a tainted run. Do not reason about how much it probably saw. Re-run it clean.

## Quarantine

Runs often write into a plugin data directory that the next run can list and read. As soon as a run completes, move its artifacts into `results/<input>/` inside the experiment directory, and treat `results/` as off-limits to any subject run.

Do this immediately, every time, before the next run starts. A blind that leaks halfway through invalidates everything after the leak.
