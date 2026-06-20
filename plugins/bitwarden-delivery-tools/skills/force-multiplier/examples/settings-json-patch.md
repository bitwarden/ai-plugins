# Example — Patch `.claude/settings.json` across every repo that has one

A worked campaign showing a **deterministic deep-merge** recipe whose idempotency is structural — the merge converges, so a re-run changes nothing. Read it for shape, then generalize.

**Recipe type:** deterministic (deep-merge a JSON patch). **Signal type:** file-existence (`.claude/settings.json` present).

## Campaign spec

```yaml
intent: "Add a standard <key> setting to .claude/settings.json in every repo that already has one, without disturbing existing keys."
scope: multi-repo
target_selector:
  enumerate: "gh repo list bitwarden --no-archived --limit 1000 --json name,defaultBranchRef"
  applicability_filter:
    signal: ".claude/settings.json present"
    detect: "gh api repos/bitwarden/<repo>/contents/.claude/settings.json --jq .sha"
recipe:
  type: deterministic
  body: "deep-merge the patch object into .claude/settings.json (jq '. * $patch'), preserving existing keys"
  idempotency: "the merged result equals the current file → no change written, no-op"
validation: "JSON parses + schema sanity check + Skill(perform-preflight)"
pr_spec:
  branch: "force-multiplier/claude-settings-<key>"
  title: "[PM-XXXXX] chore: Standardize <key> in .claude/settings.json"
  body: "<filled from the repo's PULL_REQUEST_TEMPLATE.md>"
  labels: ["ai-review"]
  draft: true
safety_policy:
  max_targets_per_run: 10
  destructive: false
  dry_run: false
  pilot: required
```

## How the pipeline plays out

- **SELECT** — keep repos that already have `.claude/settings.json`. Repos without one are `skipped-not-applicable` — this campaign standardizes existing configs, it does not create new ones.
- **CHECK YOURSELF** — confirm the intent is _merge_, not _replace_: existing keys must survive. The idempotency here is the deep-merge itself — a repo that already has the standard value yields an identical file and writes nothing. Spot-check two repos to confirm the merge preserves their bespoke keys.
- **PILOT** — merge the patch on one repo, show the diff (it should add only `<key>`, nothing else), confirm existing keys are untouched, validate the JSON parses. Lock the PR shape, confirm, fan out.
- **FAN-OUT** — per repo: branch, deep-merge the patch, second-pass (diff should be a minimal addition; a large diff means the merge clobbered something — red flag), validate, secrets-scan (settings files are a classic place a token leaks in), commit, draft PR.
- **REPORT** — repo → status → PR URL. Repos that needed the patch are `applied` with a PR; repos already carrying the value are `already-compliant` (the idempotent no-op — no diff, no PR), so the count still reconciles as `selected = applied + already-compliant + skipped-not-applicable + failed`.
- **REMEDIATE** — re-run on failures only; already-merged repos no-op cleanly.
