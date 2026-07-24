---
name: running-behavioral-evals
description: Run a behavioral A/B evaluation of a Claude skill. Compare two variants (or a stripped-down "min" against a rich original) on real inputs in isolated blind sessions, grade their outputs against independently verified ground truth, and decide which variant wins. Includes the ablation-accretion recipe for trimming a skill down to only the directives that earn their tokens.
when_to_use: Use when someone wants to know whether a skill actually works, or which of two skill versions produces better results. Phrasings like "eval this skill", "does this skill actually help", "A/B these two skill versions", "test the skill's behavior on real inputs", "is the stripped-down version as good as the original", "prove this instruction earns its place", or "ablate this skill". Also use when setting up a repeatable experiment to trim a skill to its minimum and add directives back only when a run demonstrates they are needed. Do NOT use for static or structural review of a skill's file layout and wording (that is a separate structural review), for trigger-rate evaluation of whether a skill fires (use the trigger-eval harness in evals/), or for evaluating agents rather than skills.
---

# Running Behavioral Evals

Does this skill change what the model produces, and is the change an improvement? You answer it by running two variants against the same real inputs, in isolated sessions that cannot see each other, then grading their outputs against ground truth you verified yourself.

Not whether the skill reads well (structural review) or whether it fires (trigger evals). Only the work product.

## The one belief that keeps you honest

**A skill run is noisy, and the original version is not a stable oracle.** The same skill, same input, run twice, can flip roughly half its per-item verdicts, mostly from search-scope divergence: which files the model happens to open. Three consequences:

- A single B-versus-A diff proves nothing. The difference may sit entirely inside A's own noise.
- Ground truth comes from the live system, verified by hand. Never from a run of either variant.
- Measure the noise floor first: run the control twice on one input and see how much it disagrees with itself.

Skip this and you will tune a skill to fix differences that were never there.

## What a run produces

A populated experiment directory, not a chat summary:

```
<experiment>/
  SESSION-STATE.md              # what is tested, current state, findings, open items
  directive-ledger.md           # version ledger + directive table + per-run log
  run-prompts.md                # the exact blinded prompts, one per variant
  results/<input>/              # paired artifacts, quarantined from later runs
    <input>__<variant>__<model>__<timestamp>-coverage.md
    <input>__<variant>__<model>__<timestamp>-execution-log.md
```

Two more artifacts live with the skill under test, committed alongside it:

```
<skill>/evals/behavior-eval.json      # the rubric: cases and their expectations
<skill>/evals/behavior-baseline.json  # the report card, refreshed every run
```

Templates for the three top-level files are in `assets/`; all naming, directory, and JSON shapes in `references/conventions.md`. Copy the templates first, fill them in as you go.

## The loop

Six phases, in order. Read the reference a phase names before running it the first time.

### 1. Scaffold

Create the experiment directory, copy the templates, name the two variants in `SESSION-STATE.md`:

- **Control**: what you compare against. In an ablation experiment, the rich original. It stays **frozen**; freezing it is what makes later runs comparable.
- **Treatment**: the version under test. In an ablation experiment, the stripped-down variant.

Record the inputs too. Use real ones (a real Jira issue, a real CSV, a real PR); invented inputs hide the messiness that separates a good skill from a lucky one.

Locate the skill's `evals/behavior-eval.json`, or author it now. Its `expectations` arrays are what you grade against, and writing them before the first run is what stops the rubric from being shaped by what the runs happened to produce. Shape in `references/conventions.md`.

### 2. Design the blinded run

One prompt per variant in `run-prompts.md`, **identical except for the skill name**. Any other difference contaminates the comparison.

- **Do not prime the subject.** No hints about what you expect, what the other variant did, or what correct looks like.
- **Use neutral phrasing for questions.** Say "ask only if you genuinely need a decision from me," not "do not ask me questions." A blanket ban suppresses behavior that is itself under test, such as a skill whose value is knowing when to stop and ask.

Require two artifacts from every run: the work product, and a factual execution log (ordered steps, every tool call and its purpose, anything that blocked it). The log is how you attribute a difference later.

See `references/isolation-and-blinding.md`.

### 3. Run in isolation

**Each variant in its own separate, top-level session.** No subagents for decisive runs: a subagent asked to use one variant can end up loading the other, silently ruining the comparison. Separate top-level sessions are the only isolation that reliably holds.

### 4. Taint-check and quarantine

Prove the blind held. Mechanical and non-negotiable:

- Grep each transcript to confirm the run loaded **only its own variant** and never read the other variant, the ledger, or prior results.
- Record **CLEAN** or **TAINTED** in `SESSION-STATE.md`. A tainted run is discarded, not patched.
- **Quarantine** finished artifacts into `results/<input>/`, out of any directory the next run might discover.

Grep targets in `references/isolation-and-blinding.md`.

### 5. Grade against ground truth

Verify the decisive facts against the live system: open the actual test files, check the actual branch, read the actual API response. Then grade each output against its case's `expectations` in `behavior-eval.json`, pass or fail per expectation, no partial credit.

- **Verify, do not recall.** Re-read both reports from the files; memory-based comparison invents agreements that are not there.
- **Adjudicate divergent claims against the repo, not the control.** When the variants disagree, the control is not automatically right.

See `references/grading.md`.

### 6. Decide, or accrete

Record the counts in `behavior-baseline.json` under the `<model>/<effort>` key you ran, per case, per arm (`new-skill`, `old-skill`, `no-skill`), with the per-expectation breakdown. Then write the verdict in `SESSION-STATE.md`: which variant was more accurate, and whether the difference survived your noise floor.

A regression is a per-expectation count falling for the same case, arm, and `<model>/<effort>` key. Compare only within a key; across keys you are looking at an unmeasured configuration, not a regression.

In an ablation-accretion experiment, decide here whether a directive goes back into the treatment. **Add one only when a run reproduces the specific failure it prevents.** Keep it terse, bump the treatment version, log the promotion in `directive-ledger.md`. Full recipe, including the trap where two individually-earned directives combine into a loophole, in `references/ablation-accretion.md`.

Repeat on new inputs until the treatment meets or beats the control across enough inputs that the result is not one lucky run.

## Attribution

A difference can come from the skill, the model, run-to-run noise, or how the run was structured (a run that delegated to a focused subagent looks deeper than one that worked inline). Vary one factor per comparison, and use model-matched pairs when the question is about the skill.

## What skill-creator provides, and what it does not

Reuse from `/skill-creator:skill-creator`: the `eval-viewer` for capturing and viewing outputs, and `aggregate_benchmark.py` for per-configuration mean and standard deviation. Its optional `comparator` agent blinds two outputs against each other and is worth using for that.

Rubrics and results do not come from it. They use this marketplace's own `behavior-eval.json` and `behavior-baseline.json`, which key results on model and effort and keep a per-expectation breakdown.

It does not provide the parts this skill owns. It runs variants as subagents inside one session, grades from paths named for the configuration, treats the other variant as the baseline rather than verified ground truth, prescribes one run per configuration, surfaces prior iterations into the current review, and has no ablation procedure.

## Known environment gotcha

`${CLAUDE_PLUGIN_DATA}` does not reliably expand inside a skill's Bash or Write steps. Do not use it for output paths; resolve the experiment directory to an explicit project-relative path. See `references/conventions.md`.
