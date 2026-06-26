# Example — Migrate the fleet from npm to pnpm

A worked campaign showing an **agentic** recipe applied to a non-trivial per-repo migration. Read it for shape, then generalize.

**Recipe type:** agentic (a scoped sub-agent runs the migration; the `validation` gate proves the result). **Signal type:** file-existence (`package-lock.json` present).

## Campaign spec

```yaml
intent: "Migrate each Node repo from npm to pnpm: replace package-lock.json with pnpm-lock.yaml and update CI to use pnpm."
scope: multi-repo
target_selector:
  enumerate: "gh repo list bitwarden --no-archived --limit 1000 --json name,defaultBranchRef"
  applicability_filter:
    signal: "package-lock.json present at repo root"
    detect: "gh api repos/bitwarden/<repo>/contents/package-lock.json --jq .sha"
recipe:
  type: agentic
  body: |
    a scoped sub-agent, given only this repo: run `pnpm import`, delete package-lock.json,
    update the CI workflow to pnpm, and fix any scripts that hardcode `npm`
  idempotency: "pnpm-lock.yaml present AND package-lock.json absent → already migrated, no-op"
validation: "pnpm install --frozen-lockfile + repo build/test (from its CLAUDE.md) + Skill(perform-preflight)"
pr_spec:
  branch: "force-multiplier/npm-to-pnpm"
  title: "[PM-XXXXX] deps: Migrate from npm to pnpm"
  body: "<filled from the repo's PULL_REQUEST_TEMPLATE.md>"
  labels: ["ai-review"]
  draft: true
safety_policy:
  max_targets_per_run: 10
  destructive: false # replaces a lockfile; the old one is recoverable via git history
  dry_run: false
  pilot: required
```

> **Workspace repos:** If `package.json` declares `"workspaces"`, the sub-agent must create `pnpm-workspace.yaml` declaring the workspace packages _before_ running `pnpm import` — pnpm requires it, and workspace packages are silently skipped without it.

## How the pipeline plays out

- **SELECT** — enumerate all non-archived repos, keep only those with a root `package-lock.json`. Show the list; a repo with no lockfile, or one already on pnpm, is `skipped-not-applicable`.
- **CHECK YOURSELF** — confirm the intent (lockfile + CI, nothing else). Spot-check: open two included repos and confirm they really build with npm today; reason about repos that use yarn (a different signal — excluded, correctly). Confirm idempotency: a re-run skips already-migrated repos. Within the cap of 10, the fleet runs in chunks.
- **PILOT** — run the full recipe on one representative repo. Read the entire diff: lockfile swap, CI workflow change, and any script edits the sub-agent made. Did it touch _only_ dependency tooling, or did it wander into source? Run `pnpm install --frozen-lockfile` and the build for real. Lock the PR title/body/label. Confirm, then fan out.
- **FAN-OUT** — per repo, in isolation: branch `force-multiplier/npm-to-pnpm`, hand the scoped sub-agent the migration, second-pass the diff (does its shape match the pilot — roughly a lockfile + a CI file + maybe a script?), validate, secrets-scan, commit, open the draft PR.
- **REPORT** — table of repo → applied/skipped/failed → PR URL. Reconcile the count. A repo whose `pnpm install` failed is `failed` with the error in Notes — not hidden.
- **REMEDIATE** — re-run on the failed subset only, after fixing the recipe if the failures share a cause.
