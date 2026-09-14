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
`claude -p` stream events for any invocation of the real skill token, ignoring unrelated
session-init or workflow skills that may fire first.

## What it does

Spawns parallel `claude -p` subprocesses (one per query × run) via a process pool, parses the
streamed `stream-json` tool-use events, and counts a "trigger" the moment the target skill
token streams into a `Skill` or `Read` tool input. It prints per-query PASS/FAIL to stderr
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
- `--runs-per-query` (default `3`) — samples per query; use `7` for a baseline.
- `--num-workers` (default `3`) — concurrency, and the memory knob. Each `claude -p`
  subprocess holds ~1GB while it runs, so raising this raises peak memory.
- `--timeout` (default `90`) — per-query wall-clock bound in seconds.
- `--model` (default `claude-sonnet-5`) — pass the same model the baseline was recorded on so
  verdicts are comparable.

## Add evals for a new skill

No engine copy, no token to set:

1. Create `skills/<new-skill>/evals/trigger-eval.json` — a balanced set of should-trigger
   phrasings and should-not-trigger near-misses (`{"query": ..., "should_trigger": ...}`).
2. Record the first run as the baseline:
   ```bash
   cd skills/<new-skill>/evals
   python3 ../../../evals/run_real_eval.py --eval-set trigger-eval.json \
     --runs-per-query 7 --num-workers 3 --timeout 90 --model claude-sonnet-5 > baseline.json
   ```
3. Add a short `evals/README.md` covering that skill's test surface and the regression-check
   recipe (copy a sibling's).
