# stacking-pull-requests trigger evals

Reproducible trigger-rate test for the `bitwarden-delivery-tools:stacking-pull-requests` skill. Run before merging any change to the skill's `description`, to confirm the change keeps firing on stack phrasings without stealing queries that belong to `creating-pull-request` or `force-multiplier`.

## Why a custom runner

The upstream `skill-creator` harness measures triggering by registering a temporary copy of the skill under a UUID-suffixed name and watching whether the model invokes that exact name. When the real plugin-registered skill is already installed in the test environment, the model invokes the real one and the harness records a false negative. `run_real_eval.py` instead watches `claude -p` stream events for any invocation of the real `stacking-pull-requests` skill, ignoring unrelated session-init or workflow skills that may fire first.

## Files

- `trigger-eval.json` — 20-query test set: 10 should-trigger phrasings covering layer planning, submission, lower-layer feedback, and merging the chain, and 10 should-not-trigger near-misses routed at `creating-pull-request` (single-branch PR work), `force-multiplier` (one change across many repos), `committing-changes`, `perform-preflight`, and plain git questions.
- `run_real_eval.py` — runner. Spawns parallel `claude -p` subprocesses, parses streamed tool-use events, computes per-query trigger rates.

No baseline is committed. The skill ships in the same change as this eval, so there is no prior run to compare against; the regression check below starts working once someone records one.

## Running

The query set is imperative and mutating — "submit the stack", "commit these changes", "rebase my branch onto main and force push" — so each subprocess is confined three ways: `--disallowedTools Bash Edit Write NotebookEdit`, `--strict-mcp-config` with an empty `--mcp-config` so no MCP server loads, and a fresh temp working directory. Deny rules beat any allow rule in your settings, and triggering is read from the streamed `tool_use` block, which the model emits before a tool runs, so none of this costs the measurement anything.

MCP needs its own switch rather than a deny rule: a server starts at session init, ahead of any tool-permission check, so `--disallowedTools` cannot stop one from launching. This repo ships one that runs through `bash -c` and holds a write-scoped token.

Run it with absolute paths, and write the result outside the repository so eval artifacts never land in a commit:

```bash
python3 <repo>/plugins/bitwarden-delivery-tools/skills/stacking-pull-requests/evals/run_real_eval.py \
  --eval-set <repo>/plugins/bitwarden-delivery-tools/skills/stacking-pull-requests/evals/trigger-eval.json \
  --plugin-dir <repo>/plugins/bitwarden-delivery-tools \
  --runs-per-query 3 \
  --num-workers 8 \
  --model claude-opus-5 \
  > /tmp/stack-eval-result.json
```

Requires Python 3.10+ and an authenticated `claude` CLI on `PATH`.

`--plugin-dir` is required, and argparse enforces it. Without it the subprocesses load whatever copy of this plugin sits in the installed cache, which will not contain `stacking-pull-requests` until this change ships: every should-trigger query scores zero and every near-miss passes trivially against a skill that was never loaded. Pointing it at the branch also supplies `creating-pull-request` and `force-multiplier` from the code under test, which is what the near-misses are written against. The runner records `model` and, for each plugin directory, its `name@version` from `plugin.json` — not the directory basename, which is identical for a branch checkout and the installed cache. A run under different conditions fails the regression diff rather than quietly comparing against a different setup.

20 queries × 3 runs = 60 `claude -p` invocations. With 8 workers the run takes a few minutes. The 120-second default timeout is sized by the should-not-trigger cases: a trigger ends as soon as the token appears, but a non-trigger has to reach the terminal `result` event, and any timeout is scored an error that fails the run.

## Regression check

Once `baseline.json` exists:

```bash
diff <(jq -S . baseline.json) <(jq -S . /tmp/stack-eval-result.json)
```

An empty diff means no regression. Investigate any query whose trigger rate moved, particularly the `creating-pull-request` and `force-multiplier` near-misses, which guard the routing boundary this skill introduced.
