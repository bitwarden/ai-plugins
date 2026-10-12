# Skill-trigger eval runner

`run_real_eval.py` measures whether the model auto-selects a skill in this plugin from a natural-language query. It is a copy of the runner `bitwarden-testing-tools` uses, kept here so this plugin's evals run without another plugin's files. Each skill ships only its eval data under `skills/<skill>/evals/`.

## What it does

Spawns parallel `claude -p` subprocesses (one per query × run), parses the streamed `stream-json` tool-use events, and counts a trigger only on a plugin-qualified `Skill` invocation (`<plugin>:<skill>`) or a `Read` of the skill's own `SKILL.md`. It prints per-query PASS/FAIL to stderr and a JSON summary with per-query trigger rates to stdout.

Each subprocess runs with `--allowedTools Skill Read`, so adversarial should-not-trigger queries cannot run tools, and in its own process group, so the whole Node process tree is reaped on completion or `--timeout`.

## Arguments

- `--eval-set` (required): path to the skill's `trigger-eval.json`.
- `--skill`, `--plugin`: the target tokens. Both are inferred from the eval-set path when run from a skill's `evals/` directory.
- `--runs-per-query` (default `3`): samples per query.
- `--num-workers` (default `3`): concurrency. Each `claude -p` holds about 1GB while it runs.
- `--timeout` (default `90`): per-query wall-clock bound in seconds. An expiry is recorded as a non-trigger and warns on stderr.
- `--model` (default `claude-opus-4-8`): match the model of the reading you compare against.

## Running

Requires Python 3.10+ and an authenticated `claude` CLI on `PATH`. To measure this working tree rather than an installed copy, pin the inventory with two `claude` flags injected through a shim first on `PATH` (the runner launches `claude` by a `PATH` lookup, so a shell alias is never consulted): `--setting-sources project` drops your user-level plugins, skills, hooks, and MCP servers, and `--plugin-dir` loads this plugin from the working tree.

```bash
PLUG="$(git rev-parse --show-toplevel)/plugins/bitwarden-mailcatcher-tools"
REAL="$(type -P claude)"                       # real binary, bypassing any shell alias
SHIM="$(mktemp -d)"; chmod 700 "$SHIM"
cat > "$SHIM/claude" <<SH
#!/bin/bash
exec "$REAL" "\$@" --setting-sources project --plugin-dir "$PLUG"
SH
chmod +x "$SHIM/claude"
export PATH="$SHIM:$PATH"

cd "$PLUG/skills/reading-mailcatcher-api/evals"
python3 ../../../evals/run_real_eval.py --eval-set trigger-eval.json \
  --runs-per-query 3 --num-workers 3 --timeout 90 --model claude-opus-4-8 > result.json
```

Remove the shim when done with `rm -rf "$SHIM"`. Do **not** relocate `CLAUDE_CONFIG_DIR` to isolate the inventory instead: on macOS the login token is keyed to the config directory, so a relocated directory reads an empty Keychain entry and every query records a false non-trigger.

## No committed baseline

A trigger reading depends on which skills are installed alongside the target, so the suite commits no `baseline.json`. The skill's own `evals/README.md` records its last reading as dated prose naming the inventory it was measured against, and the suite is an on-demand diagnostic rather than a merge gate.
