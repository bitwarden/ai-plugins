# Running the trigger evals

Shared setup for every `skills/*/evals/` trigger suite in this plugin. Each suite's own `README.md` covers what is specific to it — its `trigger-eval.json`, `--runs-per-query`, regression check, and last observed reading. This file covers what they share: prerequisites, pinning the skill inventory, and the run command.

The runner is `eval_harness.py` (this directory); each suite's `run_real_eval.py` is a thin wrapper that sets only its target skill token. The harness spawns parallel `claude -p` subprocesses, parses their streamed tool-use events, and computes per-query trigger rates. It kills a subprocess the instant a query reaches for `Agent`/`Task`, or a `Bash` command outside the read-only `gh`/`git` allowlist, without first invoking the target skill.

## Prerequisites

- Python 3.10+.
- An authenticated `claude` CLI on `PATH` — the harness spawns real `claude -p` agents, so it needs working auth and network.

## Pin the skill inventory

A trigger reading is only meaningful against a fixed inventory: the model's choice depends on every skill description it sees. These suites measure against the plugin's skill inventory as of the current branch, loaded from this worktree so the reading reflects the branch's `SKILL.md` rather than a published copy. Each suite's own README records the exact inventory its last reading was measured against.

Pin it per invocation with two `claude` flags:

- `--setting-sources project` — drops your user-level plugins, skills, hooks, and MCP servers, leaving only the CLI's constant bundled built-ins.
- `--plugin-dir <plugin-root>` — loads this plugin from the worktree.

The harness launches `claude` as a subprocess — a direct `PATH` lookup, not a shell interpretation — so a shell alias is never consulted. Inject the flags with a `claude` shim first on `PATH`:

```bash
WT="$(git rev-parse --show-toplevel)"
PLUG="$WT/plugins/bitwarden-testing-tools"
REAL="$(type -P claude)"                       # real binary, bypassing any shell alias
SHIM="$(mktemp -d)"; chmod 700 "$SHIM"
cat > "$SHIM/claude" <<EOF
#!/bin/bash
exec "$REAL" "\$@" --setting-sources project --plugin-dir "$PLUG"
EOF
chmod +x "$SHIM/claude"
export PATH="$SHIM:$PATH"
```

Do **not** relocate `CLAUDE_CONFIG_DIR` to isolate the inventory. On macOS the login token is keyed to the config directory, so a relocated dir reads a different (empty) Keychain entry and every query records a false non-trigger. Pinning with the flags above keeps your authenticated default config intact.

### Verify the pin (optional)

```bash
claude -p hi --output-format stream-json --verbose --model claude-opus-4-8 \
  | python3 -c "import sys,json; [print(len(e.get('skills',[])),'skills;',[s for s in e['skills'] if 'testing-tools' in str(s)]) for e in map(json.loads,sys.stdin) if e.get('subtype')=='init']"
```

Expect the plugin's `bitwarden-testing-tools:*` skills present (alongside the bundled built-ins) and zero MCP servers.

## Run

From a suite's `evals/` directory, with the shim on `PATH`:

```bash
python3 run_real_eval.py --eval-set trigger-eval.json \
  --runs-per-query <N> --num-workers 5 --timeout 90 \
  --model claude-opus-4-8 > result.json
```

`<N>` and any regression check are per suite — see its `README.md`. `result.json` is a transient run artifact and is not committed.

## Resource note

Each `claude -p` subprocess is a full agent. The adversarial should-not-trigger queries are real-work prompts; the harness bails them the instant they reach for `Agent`/`Task` or non-allowlisted `Bash`, but `--num-workers` agents still run concurrently. Keep `--num-workers` at 5 — raising it much higher, or removing the early exit, can spawn enough parallel clone/build work to exhaust memory.

## Cleanup

Remove the shim when done: `rm -rf "$SHIM"`.
