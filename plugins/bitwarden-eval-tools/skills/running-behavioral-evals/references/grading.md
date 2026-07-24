# Grading against ground truth

The intuitive move, diff the two outputs and trust the original, is the one that fails.

## The control is not an oracle

Two runs of the same frozen skill, same input, same model, flipped about half their per-item verdicts. The cause was search-scope divergence, which files each run happened to open, not anything in the skill.

So a single treatment-versus-control difference may sit entirely inside the control's own noise, and "the treatment disagrees with the original" is a question rather than a defect. The answer comes from the live system.

## Establish ground truth from the live system

For each decisive claim where the variants disagree, verify by hand:

- Open the actual test file at the actual commit and read what it asserts. Not a summary, including one a subagent produced.
- Check the actual branch state. A test present at a PR-head SHA may have been reverted on the default branch, and a permalink can resolve to code no longer shipped.
- Read the actual data or API response, not a paraphrase.

Record what you confirmed in `SESSION-STATE.md` so later runs adjudicate against the same fact.

## Verify, do not recall

Re-read both reports from their files, every time. Memory smooths over differences and invents agreements that are not in the text. If your comparison says both agree on X, point at the line in each file. Same for the frozen control and any prior run before citing what it found.

## The rubric is committed, not improvised

Expectations live in the skill's own `evals/behavior-eval.json` and are written before the first run. Writing them afterward lets the runs shape the rubric, which is how an experiment ends up proving whatever it happened to find.

Each expectation is one claim with a yes/no answer someone else could confirm:

- "Does not claim coverage for tests reverted off the default branch"
- "Cites the export endpoint as a single shared action rather than a per-plan gap"

Pass or fail per expectation, no partial credit. Script the checks that can be scripted; reserve human judgment for the rest.

Keep subjective qualities (tone, readability, structure) out of the rubric. Judge them separately if they matter. Shape in `conventions.md`.

## Adjudicate disagreements against the repo, not the control

Resolve each disagreement at ground truth, then record which variant was correct. In the experiment this skill distills, the original produced confident false positives: it called two unimplemented features covered, and declared coverage that had been reverted off the default branch. The stripped variant was right. Trusting the original would have "corrected" the treatment toward the wrong answer.

## Measure the noise floor

Run the control against itself first: same skill, same input, same model, twice. Their disagreement is the noise floor for that input. A treatment-versus-control difference below the floor is not a signal. Act only on differences that exceed it or reproduce across several inputs.

## Record the counts, not the impression

Every graded run updates `behavior-baseline.json`, keyed on `<model>/<effort>`, with `runs_per_arm` and the per-expectation breakdown. Keep the breakdown: an aggregate that holds while one expectation collapses from `4/4` to `0/4` is the regression you most want to catch, and the aggregate hides it.

## Attribution before action

Attribute a graded difference before changing anything (see `ablation-accretion.md`): skill, model, run noise, or run structure. Only a skill-content cause justifies an edit. Reproduce what you are unsure about, and change one variable at a time.
