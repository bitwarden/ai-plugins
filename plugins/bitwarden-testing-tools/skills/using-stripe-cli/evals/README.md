# using-stripe-cli evals

Trigger-rate diagnostic for the `bitwarden-testing-tools:using-stripe-cli` skill, plus a behavior-eval case set that documents its load-bearing decisions as worked examples in the `skill-creator` schema.

## Files

- `trigger-eval.json`: 20-query test set. 10 should-trigger phrasings covering read-only Stripe test-mode data needs: subscription and test-clock status, payment and charge failures, price and coupon lookups, customer payment methods, invoices, and webhook events. 10 should-not-trigger near-misses covering code authoring, live or production data, Stripe configuration, and general questions about the billing flow, including a live customer and a production subscription named to test whether "test" phrasing alone is doing the work.
- `run_real_eval.py`: a thin configuration wrapper over the plugin's shared runner at `scripts/eval_harness.py`, setting only the target skill token. The harness spawns parallel `claude -p` subprocesses, parses streamed tool-use events, and computes per-query trigger rates.
- `behavior-eval.json`: seven cases and their 28 expectations covering the skill's read-only boundary, the single permitted write of advancing an already-attached test clock, the subordination rule that Stripe must not create state the application's own flows can create, the database and feature-flag shortcuts it refuses, and untrusted content inside Stripe metadata. Cases are advice-only and mutation-safe: they grade the decision the skill produces and issue no Stripe calls, so they need no Stripe credentials and re-runs are safe.

No `baseline.json` or `behavior-baseline.json` is committed. A trigger baseline is tied to whichever sibling skills are installed alongside this one at the time it was recorded, so it drifts every time the plugin's skill inventory grows; the reading below states its own inventory instead. The behavior suite runs through a conversational with-skill-versus-without-skill ablation with no scriptable benchmark command, so the case set stands on its own as a behavioral specification rather than against a stored baseline.

## Running

Use an isolated `CLAUDE_CONFIG_DIR` so the run never touches the live harness: seed a throwaway config directory with real credentials and settings, point its marketplace at this worktree, install the plugin there, and run the suite foregrounded against that isolated config.

```bash
WT="$(git rev-parse --show-toplevel)"
ISO="$(mktemp -d)"          # 0700 by default; keep it that way so the copied token stays private
trap 'rm -rf "$ISO"' EXIT   # clean up even if the run is interrupted
cp ~/.claude/.credentials.json "$ISO/"; cp ~/.claude/settings.json "$ISO/"
[ -f ~/.claude.json ] && cp ~/.claude.json "$ISO/.claude.json"
CLAUDE_CONFIG_DIR="$ISO" claude plugin marketplace add "$WT"
CLAUDE_CONFIG_DIR="$ISO" claude plugin install bitwarden-testing-tools@bitwarden-marketplace

cd "$WT/plugins/bitwarden-testing-tools/skills/using-stripe-cli/evals"
CLAUDE_CONFIG_DIR="$ISO" python3 run_real_eval.py --eval-set trigger-eval.json --runs-per-query 3 --num-workers 5 --timeout 90 --model claude-opus-4-8 > result.json
```

Trigger rates depend on which sibling skills are installed alongside this one, since the model is choosing among all of them. Run this measured against the four-skill foundation inventory: `assessing-test-coverage`, `reading-mailcatcher-api`, `using-stripe-cli`, and `writing-manual-test-cases`.

The behavior suite runs separately, through `/skill-creator:skill-creator` in Benchmark mode with a config-blind grader, and has no scriptable command here.

## Last observed reading

Recorded 2026-08-25 with `claude-opus-4-8` at 3 runs per query, measured against the four-skill foundation inventory (`assessing-test-coverage`, `reading-mailcatcher-api`, `using-stripe-cli`, `writing-manual-test-cases`): should-trigger 10/10, should-not-trigger 10/10.

## When to run

Run the trigger suite when the skill's `description` frontmatter changes. It is a diagnostic reading, not a merge gate. Run the behavior suite when a decision it covers changes in `SKILL.md`.
