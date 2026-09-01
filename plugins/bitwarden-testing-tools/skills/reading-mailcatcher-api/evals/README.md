# reading-mailcatcher-api trigger evals

Trigger-rate diagnostic for the `bitwarden-testing-tools:reading-mailcatcher-api` skill: whether the phrasings it names actually trigger it, and whether near-miss queries asking for SMTP configuration, email-template work, container management, or server-side flow explanation stay quiet.

## Files

- `trigger-eval.json`: 19-query test set. 9 should-trigger phrasings covering the flows the skill names (account verification, magic link, trial activation, org invite, emergency access) addressed by recipient and by subject. 10 should-not-trigger near-misses that share the words "email", "mail", and "mailcatcher" but want something the skill does not do: debugging mail delivery, configuring SMTP, starting containers, writing or reviewing email-template code, explaining the server-side flow, or inventorying test coverage.
- `run_real_eval.py`: a thin configuration wrapper over the plugin's shared runner at `scripts/eval_harness.py`, setting only the target skill token. The harness spawns parallel `claude -p` subprocesses, parses streamed tool-use events, and computes per-query trigger rates.

## Running

Run against an isolated `CLAUDE_CONFIG_DIR` seeded from your real one, never your live config: isolation pins the skill inventory the model is choosing among (so the reading is reproducible) and forces the install to come from this worktree rather than a published copy. Relocating the config root leaves it unauthenticated, so the credential file gets copied in too.

```bash
WT="$(git rev-parse --show-toplevel)"
ISO="$(mktemp -d)"          # 0700; holds a copy of your OAuth token, so keep it private
trap 'rm -rf "$ISO"' EXIT   # cleans up on normal exit or Ctrl-C, but not on SIGKILL
cp ~/.claude/.credentials.json ~/.claude/settings.json "$ISO/"
[ -f ~/.claude.json ] && cp ~/.claude.json "$ISO/.claude.json"
CLAUDE_CONFIG_DIR="$ISO" claude plugin marketplace add "$WT"
CLAUDE_CONFIG_DIR="$ISO" claude plugin install bitwarden-testing-tools@bitwarden-marketplace

cd "$WT/plugins/bitwarden-testing-tools/skills/reading-mailcatcher-api/evals"
CLAUDE_CONFIG_DIR="$ISO" python3 run_real_eval.py --eval-set trigger-eval.json --runs-per-query 3 --num-workers 5 --timeout 90 --model claude-opus-4-8 > result.json
```

Measure against the four-skill foundation inventory: `assessing-test-coverage`, `reading-mailcatcher-api`, `using-stripe-cli`, and `writing-manual-test-cases`. If the run is `SIGKILL`ed (the trap won't fire), delete `$ISO` by hand so the token copy isn't left under `$TMPDIR`.

## Last observed reading

Recorded 2026-08-25 with `claude-opus-4-8` at 3 runs per query, measured against the four-skill foundation inventory (`assessing-test-coverage`, `reading-mailcatcher-api`, `using-stripe-cli`, `writing-manual-test-cases`): should-trigger 9/9, should-not-trigger 10/10. (The 2026-08-25 run passed all 10 should-trigger phrasings then in the set; the password-reset phrasing was removed afterward because the skill documents no password-reset pattern, leaving the 9 above.)

## When to run

Run this suite when the skill's `description` frontmatter changes. It is a diagnostic reading, not a merge gate.
