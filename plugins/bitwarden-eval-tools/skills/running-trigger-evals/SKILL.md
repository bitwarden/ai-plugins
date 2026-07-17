---
name: running-trigger-evals
description: Runs and reports a Bitwarden skill's trigger-rate eval. Use when users want to check a skill's trigger rate, benchmark its triggering against a recorded baseline, verify a description or when_to_use edit didn't regress triggering, or set up a triggering eval and baseline for a net-new Bitwarden skill.
allowed-tools: "Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/trigger_eval.py:*), Bash(mkdir -p ${CLAUDE_PLUGIN_DATA}/running-trigger-evals/eval-reports:*), Write(${CLAUDE_PLUGIN_DATA}/running-trigger-evals/eval-reports/*)"
version: 1.0.0
---

# Running trigger evals

## Scope

Triggering only: does the skill's description fire on the real asks it should
catch, and stay silent on near-misses and out-of-scope asks. Not output
structure or behavior once triggered; use `/skill-creator:skill-creator` for
those.

## Decision: installed vs isolated mode

Pick the mode by whether the skill under test is registered in the
environment that will run the eval:

- **installed**: already-installed skill. Requires `--skill-token` (or
  `--skill-path` to derive it from the parsed `name:` field).
- **isolated**: not yet installed (in development or an unmerged PR).
  Requires `--skill-path`; optionally `--description` to test a candidate
  edit before writing it to `SKILL.md`.

## Inputs to gather

Before running, collect:

- **The eval set**: a JSON array of `{query, should_trigger}` cases. Locate an
  existing one under the skill's `evals/` directory, or author one (see
  `references/authoring-eval-sets.md`).
- **The target**: either the registered `--skill-token` (installed) or the
  `--skill-path` to the skill directory (isolated, or installed to derive the
  token from the parsed `name:` field).
- **Sibling tokens**, if any, whose triggering overlap you want visibility on
  (`--exclude-skill`, repeatable, report-only; never changes pass/fail).
- **A baseline**, if checking for regression (`--baseline`, with
  `--check-regression`).

## Workflow

1. **Locate or author the eval set.** Cover both classes: true positives on
   real phrasings, and near-miss / out-of-scope negatives. Keep the
   true/false split roughly even; the runner warns to stderr when it is
   skewed by more than ~20%, but it never blocks.
2. **Choose the mode, then run the script via Bash.** Run the following as
   two separate Bash calls, not bundled into one command: each matches its
   own `allowed-tools` pattern independently, and a bundled command may not
   match either.

   First, create the report directory if it doesn't exist yet:

   ```bash
   mkdir -p ${CLAUDE_PLUGIN_DATA}/running-trigger-evals/eval-reports
   ```

   Then run the eval, redirecting stdout into that directory; stderr carries
   progress and diagnostics:

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/trigger_eval.py \
     --mode installed \
     --eval-set path/to/trigger-eval.json \
     --skill-token my-skill-token \
     --runs-per-query 3 --num-workers 8 --timeout 45 \
     > ${CLAUDE_PLUGIN_DATA}/running-trigger-evals/eval-reports/my-skill-token.json
   ```

   For an isolated skill, swap `--mode isolated --skill-path path/to/skill`
   for the token.

3. **Read the reliability rate, not just the blended rate.** Judge
   production-facing triggering on the `reliability` block's `all_runs_agree`
   signal: a case firing three of five runs still passes the blended
   threshold but is a real reliability problem.
4. **Record or refresh the baseline.** For a net-new skill, the recorded
   report becomes the contract for future runs. For an edit, keep the
   existing baseline and compare against it. A case at a perfect rate across
   many iterations has stopped giving signal; move it to the lighter
   `--check-regression` check rather than continuing to tune against it.
5. **Optionally check regression before merging** with `--check-regression
--baseline path/to/baseline.json`. This is opt-in and gates nothing on its
   own; the caller decides what a flagged regression means for the merge.

## Additional Resources

- `scripts/trigger_eval.py`: the runner (stdlib-only).
- `references/cli-reference.md`: full flag table, report JSON schema, exit codes.
- `references/authoring-eval-sets.md`: balance rule, near-miss authoring, blinding.
- `examples/sample-eval-set.json`: a tiny illustrative 4-case set.
- `examples/sample-report.json`: an annotated example of the output shape.
