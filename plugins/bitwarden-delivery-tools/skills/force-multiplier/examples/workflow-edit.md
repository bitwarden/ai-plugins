# Example — Retire a deprecated GitHub Actions workflow across the fleet

A worked campaign showing a **deterministic** recipe and the **reference-check** that a destructive change requires. Read it for shape, then generalize.

**Recipe type:** deterministic (remove a file). **Signal type:** file-existence (`.github/workflows/<name>.yml` present). **Destructive:** yes — so a reference-check pre-step runs before anything is removed.

## Campaign spec

```yaml
intent: "Remove the deprecated <name>.yml workflow from every repo that still has it."
scope: multi-repo
target_selector:
  enumerate: "gh repo list bitwarden --no-archived --limit 1000 --json name,defaultBranchRef"
  applicability_filter:
    signal: ".github/workflows/<name>.yml present"
    detect: "gh api repos/bitwarden/<repo>/contents/.github/workflows/<name>.yml --jq .sha"
recipe:
  type: deterministic
  body: "git rm .github/workflows/<name>.yml"
  idempotency: "the file is absent → already done, no-op"
validation: "repo lint of remaining workflows (e.g. actionlint if defined) + Skill(perform-preflight)"
pr_spec:
  branch: "force-multiplier/retire-<name>-workflow"
  title: "[PM-XXXXX] ci: Remove deprecated <name> workflow"
  body: "<filled from the repo's PULL_REQUEST_TEMPLATE.md>"
  labels: ["ai-review"]
  draft: true
safety_policy:
  max_targets_per_run: 10
  destructive: true
  dry_run: false
  pilot: required
```

## How the pipeline plays out

- **SELECT** — keep repos where the workflow file exists.
- **CHECK YOURSELF** — destructive, so the **reference-check pre-step is mandatory** before any removal: across the selected repos, is `<name>` a _required status check_ on the default branch, or is it referenced by another workflow via `uses:` / `workflow_call`? Removing a required check blocks every future merge on that repo; removing a called workflow breaks its caller. Any repo where the workflow is depended on is pulled out for a human decision — it does not get auto-removed.
- **PILOT** — remove the file on one repo, show the one-line diff, run the remaining-workflow lint. Confirm nothing else changed. Lock the PR shape, confirm, fan out over the _cleared_ subset.
- **FAN-OUT** — per repo: branch, `git rm` the file, second-pass (the diff should be exactly one deleted file — anything more is a red flag), validate, secrets-scan, commit, draft PR.
- **REPORT** — repo → applied/skipped/failed → PR URL, plus a separate callout of repos held back by the reference-check with _why_. The held-back repos are not failures; they are decisions pending.
- **REMEDIATE** — after the human resolves the held-back repos (e.g. the required-check setting is cleared first), re-run on just those.
