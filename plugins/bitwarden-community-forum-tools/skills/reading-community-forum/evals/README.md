# reading-community-forum trigger evals

Trigger-rate diagnostic for the `bitwarden-community-forum-tools:reading-community-forum` skill. It checks two things: that forum-research phrasings trigger it, and that near-misses stay quiet.

## Files

- `trigger-eval.json`: a 12-query test set.
  - **Should trigger (6):** forum research, feature-request votes, known workarounds, staff replies, thread summaries and roadmap tags.
  - **Should not trigger (6):** posting to the forum, Jira, Confluence, Stripe, code review, and writing a Discourse plugin.

## Running

Use the plugin's runner, [`evals/run_real_eval.py`](../../../evals/run_real_eval.py). See [its README](../../../evals/README.md) for prerequisites and for pinning the skill inventory to this working tree.

## Last reading

2026-10-20, `claude-opus-4-8`, 3 runs per query, inventory pinned to this plugin with `--setting-sources project --plugin-dir`.

- **Should trigger:** 6/6 queries, 3/3 runs each.
- **Should not trigger:** 6/6 queries, 0/3 runs each. Four runs timed out at 90 seconds and count as non-triggers: 1 of 3 for the Stripe query and 3 of 3 for the Discourse-plugin query. Those two rows are weaker evidence than the other four.
