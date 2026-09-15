# Shared skill-trigger eval engine

`run_real_eval.py` is the one eval runner for every skill in this plugin. Each skill ships
only its own eval data — `trigger-eval.json` (the query set) and `baseline.json` (the last
known-good run) under `skills/<skill>/evals/`. There is no per-skill copy of the engine, so
an engine fix lands once and applies everywhere.

## Why a custom runner

The upstream `skill-creator` harness measures triggering by registering a temporary copy of
the skill under a UUID-suffixed name and watching whether the model invokes that exact name.
When the real plugin-registered skill is already installed in the test environment, the model
invokes the real one and the harness records a false negative. This runner instead watches
`claude -p` stream events for a plugin-qualified `<plugin>:<skill>` `Skill` invocation or a
`Read` of the skill's own `SKILL.md` (see _What it does_), ignoring unrelated session-init or
workflow skills that may fire first.

## What it does

Spawns parallel `claude -p` subprocesses (one per query × run) via a process pool, parses the
streamed `stream-json` tool-use events, and counts a "trigger" only on a plugin-qualified
`Skill` invocation (`<plugin>:<skill>`) or a `Read` of the skill's own `SKILL.md` — never a
bare token substring elsewhere in a tool input. It prints per-query PASS/FAIL to stderr
and a JSON summary (with per-query trigger rates) to stdout.

Each subprocess is launched with `--allowedTools Skill Read` so the adversarial
should-not-trigger queries can't clone repos or run build/test toolchains, and runs in its
own session so the whole Node process tree is reaped as a group on trigger, completion, or
timeout — `--timeout` bounds anything that stalls.

## Arguments

- `--eval-set` (required) — path to the skill's `trigger-eval.json`.
- `--skill` — the target skill token. Omit it and the runner infers the token from the
  eval-set path (the eval file's grandparent directory is the skill directory), so a run from
  a skill's `evals/` dir needs no flag.
- `--plugin` — the plugin token that qualifies a `Skill` invocation (`<plugin>:<skill>`).
  Omit it and the runner infers it from the eval-set path (the plugin root is the eval file's
  great-great-grandparent directory), so a run from a skill's `evals/` dir needs no flag. Pass
  it explicitly when running the engine from a layout the path inference does not fit.
- `--runs-per-query` (default `3`) — samples per query; use `7` for a baseline.
- `--num-workers` (default `3`) — concurrency, and the memory knob. Each `claude -p`
  subprocess holds ~1GB while it runs, so raising this raises peak memory.
- `--timeout` (default `90`) — per-query wall-clock bound in seconds. An expiry is recorded as
  a non-trigger and warns on stderr, so a slow run is not silently read as a real failure.
- `--model` (default `claude-opus-4-8`) — pass the same model the baseline was recorded on so
  verdicts are comparable. Each `baseline.json` records its model in a top-level `model` field;
  match it. Both current baselines were recorded on `claude-opus-4-8`, the model most users run.

## Running

Requires Python 3.10+ and an authenticated `claude` CLI on `PATH`. The plugin must be installed
and enabled (`claude plugin install bitwarden-testing-tools@bitwarden-marketplace`), or every
query records a false non-trigger. The eval reads the installed copy, not this working tree, so
**reinstall after editing a skill** (uninstall + install) before running.

Run from the skill's `evals/` directory so the `--skill` and `--plugin` tokens are inferred:

```bash
cd skills/<skill>/evals
python3 ../../../evals/run_real_eval.py \
  --eval-set trigger-eval.json \
  --runs-per-query 7 \
  --num-workers 3 \
  --timeout 90 \
  --model claude-opus-4-8 \
  > result.json
```

A 20-query set at `--runs-per-query 7` is 140 `claude -p` invocations; with 3 workers it takes
several minutes. `--num-workers` is the memory knob (see _Arguments_). The two coverage skills
share trigger space, so after any description change to one, re-run the other's eval too to
confirm neither cannibalizes the other's triggers.

## Regression check

Diff each query's PASS/FAIL verdict, not the raw `trigger_rate` values (which are stochastic and
flag sampling noise):

```bash
project='{
  model, should_trigger_pass, should_not_trigger_pass,
  results: [.results[] | {query, should_trigger, pass: ((.trigger_rate >= 0.5) == .should_trigger)}]
}'
diff <(jq -S "$project" baseline.json) <(jq -S "$project" result.json)
```

Empty diff means no regression; a non-empty diff means a query flipped PASS↔FAIL (the changed
`pass` field names it). A baseline may _record_ a should-trigger query below threshold (see
below) — a run that leaves it there still diffs clean. If a new failure appears, fix the skill
`description` rather than the eval set — the eval set encodes intent, not implementation. If the
change is intentional, replace `baseline.json` with `result.json` and commit it alongside the
description change.

## Known below-threshold queries

None. On `claude-opus-4-8` both baselines pass every query: `recommending-test-layers` at 10/10
should-trigger and 10/10 should-not-trigger, `assessing-test-coverage` likewise 10/10 and 10/10.
The mechanism still allows a baseline to _record_ a should-trigger query below threshold and diff
clean; when the model was `claude-sonnet-5`, `assessing-test-coverage`'s branch-audit phrasing
(`audit the current test coverage on the feat/cipher-key-rotation branch — I just want to see what
exists, not recommendations`) sat at 2/7, but on Opus it triggers 7/7. If one drops below
threshold on a future run, list it here rather than editing the eval set.

## Add evals for a new skill

No engine copy, no token to set:

1. Create `skills/<new-skill>/evals/trigger-eval.json` — a balanced set of should-trigger
   phrasings and should-not-trigger near-misses (`{"query": ..., "should_trigger": ...}`).
2. Record the first run as the baseline:
   ```bash
   cd skills/<new-skill>/evals
   python3 ../../../evals/run_real_eval.py --eval-set trigger-eval.json \
     --runs-per-query 7 --num-workers 3 --timeout 90 --model claude-opus-4-8 > baseline.json
   ```
   The runner writes the model into a top-level `"model"` field, so the baseline records the
   model it was measured on with no manual step.
3. If the skill has a should-trigger query recorded below threshold, add a line for it under
   _Known below-threshold queries_ above. No per-skill README — this one covers every skill.
