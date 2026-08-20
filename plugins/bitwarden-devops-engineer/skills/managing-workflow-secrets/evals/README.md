# Evals: managing-workflow-secrets

This directory holds the eval set for the `managing-workflow-secrets` skill: the durable,
re-runnable case definitions plus a single dated snapshot of the last validation run.

## Layout

```
evals/
  README.md          # this file
  evals.json         # THE eval set — case definitions (id, name, prompt, expected_output, files)
  files/             # input workflow fixtures each case starts from
  results/
    SNAPSHOT.md      # dated, point-in-time validation report (benchmark + ablation + triggering)
```

`evals.json` + `files/` are the load-bearing part: the specification you re-run whenever the skill
changes. `results/SNAPSHOT.md` is a historical report, not a live result — see the warning at the
top of that file.

## The cases

| ID  | Name                     | What it exercises                                                        | Fixture                      |
| --- | ------------------------ | ------------------------------------------------------------------------ | ---------------------------- |
| 0   | add-secret-retrieval     | Full AKV+OIDC lifecycle wired into a job; consume via step-scoped `env:` | `build-and-push.yml`         |
| 1   | downstream-job-handoff   | Secret must not cross a job boundary; re-retrieve per job                | `deploy-cant-see-secret.yml` |
| 2   | flag-secret-exposure     | Flag echo / file-write / CLI-arg exposure of a retrieved secret          | `leaky-secret.yml`           |
| 3   | reusable-workflow-triad  | Cross-repo reusable workflow: forward the OIDC triad explicitly          | `caller-workflow.yml`        |
| 4   | multi-secret-folded-list | Three-plus secrets rendered as a folded block scalar, one per line       | `multi-secret-deploy.yml`    |
| 5   | app-token-cross-job      | Mint a short-lived GitHub App token instead of crossing a raw secret     | `app-token-cross-job.yml`    |
| 6   | logout-live-session      | `azure-logout` placement exception when a later step needs the session   | `build-acr.yml`              |
| 7   | ask-for-names            | Never infer vault/secret names — use placeholders and ask                | `deploy-datadog.yml`         |

## Running

There is **no runner committed here.** Each case is: feed the model the `prompt` plus the named
`files/` fixture, with and without the skill, then grade the output against `expected_output`.
Because nothing in the repo regenerates results, `results/SNAPSHOT.md` can only go stale — re-run
before trusting it, and expect it to lag `evals.json` (evals 4 and 5 were added after the snapshot
and have never been run).
