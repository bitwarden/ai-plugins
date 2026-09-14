# creating-pull-request trigger evals

Reproducible trigger-rate test for the `bitwarden-delivery-tools:creating-pull-request` skill. Run before merging any change to the skill's `description` or `when_to_use` frontmatter to confirm the change doesn't degrade triggering on the natural-language phrasings the skill is designed to catch (or start firing on near-miss queries that belong to a sibling skill).

## Why a custom runner

The upstream `skill-creator` harness measures triggering by registering a temporary copy of the skill under a UUID-suffixed name and watching whether the model invokes that exact name. When the real plugin-registered skill is already installed in the test environment, the model invokes the real one and the harness records a false negative. `run_real_eval.py` instead watches `claude -p` stream events for any invocation of the real `creating-pull-request` skill, ignoring unrelated session-init or workflow skills that may fire first.

## Files

- `trigger-eval.json` — 22-query test set: 10 should-trigger natural-language phrasings ("package this up into a PR", "ship a draft", "get this in front of reviewers", etc.) and 12 should-not-trigger near-misses against sibling delivery skills (`committing-changes`, `labeling-changes`, `perform-preflight`, `applying-pr-conventions`) and against existing-PR management queries. A request for a title, body, or label alone belongs to `applying-pr-conventions`; this skill wins only when the request is to open the PR.
- `run_real_eval.py` — runner. Spawns parallel `claude -p` subprocesses, parses streamed tool-use events, computes per-query trigger rates.
- `baseline.json` — last known-good run. Records the `model`, `plugin_dirs`, and `runs_per_query` that produced it; a run under different conditions fails the diff.

## Running

Requires Python 3.10+ and an authenticated `claude` CLI on `PATH`.

The runner sets no permission mode, and the should-trigger queries are imperative ("open a draft pr for me"). Run it from a disposable repository with a local bare remote, so a subprocess that acts on the query pushes nowhere real and `gh` has no GitHub host to resolve:

```bash
S=$(mktemp -d) && cd "$S" && git init -q --bare origin.git
git init -q -b main work && cd work
git config user.email e@x && git config user.name t
mkdir -p .github src
printf '## Tracking\n\n## Objective\n' > .github/PULL_REQUEST_TEMPLATE.md
printf 'export const noop = () => {};\n' > src/index.ts
git add -A && git commit -qm "chore: scaffold"
git remote add origin ../origin.git && git push -q -u origin main
git checkout -q -b feat/example
printf 'export const feature = () => true;\n' > src/feature.ts
git add -A && git commit -qm "feat: add feature"
git push -q -u origin feat/example
```

The branch needs real commits and a remote. Given an empty branch or no remote, the model reports that there is nothing to ship rather than invoking the skill, and every should-trigger query scores zero.

```bash
python3 <evals>/run_real_eval.py \
  --eval-set <evals>/trigger-eval.json \
  --plugin-dir <repo>/plugins/bitwarden-delivery-tools \
  --runs-per-query 3 \
  --num-workers 8 \
  --timeout 90 \
  --model claude-opus-5 \
  > result.json
```

`--plugin-dir` points the subprocesses at `bitwarden-delivery-tools` in the working tree rather than the installed cache. Every skill these queries compete for lives in that one plugin, so one directory covers them all.

`baseline.json` was recorded under exactly this setup. A run in a different environment will diff for reasons unrelated to the skill.

22 queries × 3 runs = 66 `claude -p` invocations. With 8 workers the run takes a few minutes.

## Regression check

```bash
diff <(jq -S . baseline.json) <(jq -S . result.json)
```

Empty diff means no regression. If a new failure appears, fix the skill description rather than the eval set — the eval set encodes intent, not implementation. If the change is intentional and the new run is the new desired behavior, replace `baseline.json` with `result.json` and commit alongside the description change.

## Updating the test surface

Update `trigger-eval.json` (not the runner) when the test surface needs to evolve: a new natural-language phrasing the skill should catch, a new sibling skill creating a new near-miss, or an existing query that turned out to be ambiguous. Keep should-trigger and should-not-trigger counts roughly balanced.
