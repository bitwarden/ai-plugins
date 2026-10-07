# reading-mailcatcher-api trigger evals

Trigger-rate diagnostic for the `bitwarden-mailcatcher-tools:reading-mailcatcher-api` skill: whether the phrasings it names actually trigger it, and whether near-miss queries asking for SMTP configuration, email-template work, container management, or server-side flow explanation stay quiet.

## Files

- `trigger-eval.json`: 19-query test set. 9 should-trigger phrasings covering the flows the skill names (account verification, magic link, trial activation, org invite, emergency access) addressed by recipient and by subject. 10 should-not-trigger near-misses that share the words "email", "mail", and "mailcatcher" but want something the skill does not do: debugging mail delivery, configuring SMTP, starting containers, writing or reviewing email-template code, explaining the server-side flow, or inventorying test coverage.

## Running

The plugin's shared runner, [`evals/run_real_eval.py`](../../../evals/README.md), spawns parallel `claude -p` subprocesses, parses streamed tool-use events, and computes per-query trigger rates. See its README for prerequisites and for pinning the plugin's skill inventory to this working tree. Then, from this directory:

```bash
python3 ../../../evals/run_real_eval.py --eval-set trigger-eval.json --runs-per-query 3 --num-workers 3 --timeout 90 --model claude-opus-4-8 > result.json
```

## Last observed reading

Recorded 2026-10-07 with `claude-opus-4-8` at 3 runs per query, measured against this plugin's own inventory (`reading-mailcatcher-api` alone, loaded with `--setting-sources project --plugin-dir` on this plugin): should-trigger 9/9, should-not-trigger 9/10. The one miss was `what test coverage exists for the password reset email path?` at 2/3. Re-run alone at 7 runs it triggered 2/7, a pass, and 3/7 with the description this skill had before 2026-10-07, so the current description is no worse on it. The query is a near-miss written for the `assessing-test-coverage` skill, which is not installed alongside this plugin, so with no sibling to take it the model sometimes reads this skill to check. Expect it to sit near the threshold in a single-plugin inventory.

## When to run

Run this suite when the skill's `description` frontmatter changes. It is a diagnostic reading, not a merge gate.
