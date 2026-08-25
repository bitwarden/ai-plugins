# reading-mailcatcher-api trigger evals

Trigger-rate diagnostic for the `bitwarden-testing-tools:reading-mailcatcher-api` skill: whether the phrasings it names actually trigger it, and whether near-miss queries asking for SMTP configuration, email-template work, container management, or server-side flow explanation stay quiet.

## Files

- `trigger-eval.json`: 20-query test set. 10 should-trigger phrasings covering the flows the skill names (account verification, magic link, trial activation, OTP, password reset, org invite, emergency access) addressed by recipient and by subject. 10 should-not-trigger near-misses that share the words "email", "mail", and "mailcatcher" but want something the skill does not do: debugging mail delivery, configuring SMTP, starting containers, writing or reviewing email-template code, explaining the server-side flow, or inventorying test coverage.
- `run_real_eval.py`: a thin configuration wrapper over the plugin's shared runner at `scripts/eval_harness.py`, setting only the target skill token. The harness spawns parallel `claude -p` subprocesses, parses streamed tool-use events, and computes per-query trigger rates.

## Running

Use an isolated `CLAUDE_CONFIG_DIR` so the run never touches the live harness: seed a throwaway config directory with real credentials and settings, point its marketplace at this worktree, install the plugin there, and run the suite foregrounded against that isolated config.

```bash
WT="$(git rev-parse --show-toplevel)"
ISO="$(mktemp -d)"
rm -rf "$ISO"; mkdir -p "$ISO"
cp ~/.claude/.credentials.json "$ISO/"; cp ~/.claude/settings.json "$ISO/"
[ -f ~/.claude.json ] && cp ~/.claude.json "$ISO/.claude.json"
CLAUDE_CONFIG_DIR="$ISO" claude plugin marketplace add "$WT"
CLAUDE_CONFIG_DIR="$ISO" claude plugin install bitwarden-testing-tools@bitwarden-marketplace

cd "$WT/plugins/bitwarden-testing-tools/skills/reading-mailcatcher-api/evals"
CLAUDE_CONFIG_DIR="$ISO" python3 run_real_eval.py --eval-set trigger-eval.json --runs-per-query 3 --num-workers 5 --timeout 90 --model claude-opus-4-8 > result.json

rm -rf "$ISO"
```

Trigger rates depend on which sibling skills are installed alongside this one, since the model is choosing among all of them. Run this measured against the four-skill foundation inventory: `assessing-test-coverage`, `reading-mailcatcher-api`, `using-stripe-cli`, and `writing-manual-test-cases`.

## Last observed reading

Recorded 2026-08-25 with `claude-opus-4-8` at 3 runs per query, measured against the four-skill foundation inventory (`assessing-test-coverage`, `reading-mailcatcher-api`, `using-stripe-cli`, `writing-manual-test-cases`): should-trigger 10/10, should-not-trigger 10/10.

## When to run

Run this suite when the skill's `description` frontmatter changes. It is a diagnostic reading, not a merge gate.
