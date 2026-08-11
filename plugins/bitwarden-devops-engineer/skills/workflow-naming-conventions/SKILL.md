---
name: workflow-naming-conventions
description: >-
  Reference for Bitwarden GitHub Actions naming conventions that the workflow linter (bwwl) does
  not enforce. Covers three standards — job IDs (kebab-case), step names (Sentence case
  imperative), and workflow file names (kebab-case.yml, `_` prefix for reusable) — plus an
  advisory canonical step-name glossary and reference-sweep procedures for job ID and filename
  renames. Use when auditing or authoring workflows and questions like "what casing should job IDs
  use", "should this reusable workflow be build.yml or _build.yml", or "review these workflows for
  naming consistency" come up. Read alongside bitwarden-workflow-linter-rules, which is the source
  of truth for linted rules; this skill covers only the gaps.
---

## Ownership

This skill covers only what `bwwl` cannot check. For anything the linter enforces, `bitwarden-workflow-linter-rules` is the source of truth — do not report a finding here that duplicates a linter rule.

| Naming category                        | Owner                                                                 |
| -------------------------------------- | --------------------------------------------------------------------- |
| Job IDs                                | **This skill**                                                        |
| Step name casing                       | **This skill**                                                        |
| Workflow file names                    | **This skill**                                                        |
| Workflow and job display `name:`       | `bitwarden-workflow-linter-rules` — `name_capitalized`, `name_exists` |
| Outputs                                | `bitwarden-workflow-linter-rules` — `underscore_outputs`              |
| Job-level env vars                     | `bitwarden-workflow-linter-rules` — `job_environment_prefix`          |
| Inputs, bash variables, artifact names | **No standard.** Do not invent one — flag the gap instead.            |

`name_capitalized` checks only that the first character is capitalized. `Get Package Version` passes the linter and still deviates from the Sentence case standard below. The two are complementary.

## Standards

### `job-id-kebab-case`

- **Applies to:** every key under `jobs:`.
- **Standard:** `kebab-case`.
- **Correct:** `build`, `test`, `lint`, `publish`, `upload`, `build-artifacts`, `deploy-service`, `check-permissions`, `calculate-version`.
- **Deviates:** `bump_version`, `cut_branch`, `deployService`, `DeployService`, `BUILD_ARTIFACTS`.
- **Flag when:** a job ID uses `snake_case`, `camelCase`, `PascalCase`, or `UPPER_SNAKE`. Single-word IDs are compliant and are never a finding.

A job ID is an identifier, not a label. Before proposing a rename, resolve every reference:

1. `needs:` in the same file, in both scalar and list form.
2. `${{ needs.<job-id>.* }}` expressions anywhere in the file.
3. `jobs.<job-id>.outputs` at the workflow level of a reusable workflow.

Check-run names derive from a job's `name:`, not its ID, so a job-ID rename does not affect required status checks — **unless** the job has no `name:`, in which case the ID becomes the check name and a rename can break a ruleset that requires it. `name_exists` already flags a job with no `name:`; if you encounter one, fix that first and rename second.

### `step-name-sentence-case`

- **Applies to:** every `name:` under `steps:`.
- **Standard:** Sentence case with a leading imperative verb — capitalize the first word plus proper nouns and acronyms only. Proper nouns and acronyms keep their own casing: `Azure`, `Docker`, `Node`, `.NET`, `SDK`, `RC`, `MSSQL`.
- **Correct:** `Check out repo`, `Set up .NET`, `Print environment`, `Log in to Azure`, `Generate Docker image tag`, `Install Node dependencies`, `Run tests`, `Push changes`, `Upload SDK artifacts`.
- **Deviates:** `Delete Release Branch`, `Get Package Version`, `Build & Package Binaries`, `Upload SDK Artifacts`, `Dependency install`.
- **Flag when:** a step name uses Title Case, ALL CAPS, or drops the leading imperative verb.

Step names are display-only — they are not addressable from expressions, since `steps.<id>` resolves the step's `id:`. Changing one is safe and needs no reference sweep. This is the only standard here an agent may apply directly during an edit.

### `workflow-file-naming`

- **Applies to:** every file in `.github/workflows/`.
- **Standard:** `kebab-case.yml`, with a `_` prefix if and only if the workflow is _exclusively_ reusable. The extension is always `.yml`, never `.yaml`. The prefix and the casing are independent — `_deploy_service.yml` is correctly prefixed and incorrectly cased; the compliant form is `_deploy-service.yml`.
- **Correct:** `build-app.yml`, `scan-dependencies.yml`, `_version.yml`, `_deploy-service.yml`.
- **Deviates:** `build_only.yml`, `API_tests.yml`, `Integration_Tests.yml`, `deploy-service.yaml`, `_deploy_service.yml`.
- **Flag when:** the name is not `kebab-case`, the extension is `.yaml`, an exclusively reusable workflow lacks the `_` prefix, or a `_`-prefixed file is not exclusively reusable.

**Exclusively reusable** means the `on:` block declares nothing outside `workflow_call` and `workflow_dispatch`. `workflow_dispatch` is a manual testing and operations escape hatch, not a standalone entry point, so it does not disqualify the prefix.

Any other trigger — `push`, `pull_request`, `pull_request_target`, `schedule`, `release`, `workflow_run`, `repository_dispatch` — makes the workflow **dual-purpose**: it both runs on its own and is callable by others. Dual-purpose workflows take no prefix. This is a deliberate and common design, not a deviation. Presence of `workflow_call` alone never justifies a prefix finding; check the full trigger set first.

| `on:` block                           | Prefix              |
| ------------------------------------- | ------------------- |
| `workflow_call`                       | Required            |
| `workflow_call` + `workflow_dispatch` | Required            |
| `workflow_call` + any auto-trigger    | None — dual-purpose |
| No `workflow_call`                    | None                |

**Renaming a workflow file is destructive.** The filename is the workflow's public identifier — it addresses the workflow from outside the repo, and every external reference breaks silently on rename. Never rename one as part of an audit or an unrelated edit. Report it and let the repo owner schedule it.

If a rename is explicitly requested, establish the known reference set first, then use `git mv`:

1. **In-repo callers** — grep the repo for the filename. Catches `uses: ./.github/workflows/<file>` and any local script that names it.
2. **Org-wide references** — `gh search code "<file>" --owner bitwarden`. Catches `uses: bitwarden/<repo>/.github/workflows/<file>@<ref>` in other repos plus any script or tooling that names the file. A local grep will not find these.

**This establishes a floor, not a ceiling.** Nothing outside the org's indexed code is discoverable: automation in other systems, runbook and documentation links, and anything invoking the workflow by filename through the dispatch API. Report what the two searches found and state plainly that the set may be incomplete — the residual unknown is exactly why the rename belongs to the repo owner and not to an audit.

Run history is keyed to the file path and always detaches on rename. Prior runs remain but no longer group under the renamed workflow. This is unavoidable — surface it, do not try to preserve it.

## Advisory: canonical step names

Preferred wording, not a standard. Consistent phrasing makes steps greppable across repos, but a step name outside this table is never a finding — most step names are legitimately unique to their workflow.

| Action                    | Canonical form                                          | Also seen                                                                               |
| ------------------------- | ------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Check out the repository  | `Check out repo`                                        | `Checkout repo`, `Checkout code`, `Checkout Branch`, `Check out repository`, `Checkout` |
| Log in to Azure           | `Log in to Azure`                                       | `Login to Azure`, `Azure Login`                                                         |
| Log out from Azure        | `Log out from Azure`                                    | —                                                                                       |
| Install a toolchain       | `Set up {tool}` — two words, matching `actions/setup-*` | `Setup {tool}`                                                                          |
| Retrieve secrets from AKV | `Retrieve secrets`                                      | `Get secrets`, `Setup secrets`                                                          |
| Print the environment     | `Print environment`                                     | `Print Environment`                                                                     |

When a step name both deviates from Sentence case and appears in this table (`Azure Login`), the casing is the finding and the canonical form is the suggested fix.

## Applying these standards

- **A deviation is a flag, not a verdict.** These standards describe the target state; they do not authorize a rename. Real workflows carry deliberate exceptions — a job ID matched by external tooling, a filename referenced by a system outside this repo, a step name that reads better than the canonical phrase. Surface the deviation with what a compliant form would be, and let the owner decide. Do not treat silence as consent.
- **Only step names are safe to change in place.** Job IDs and filenames both require a reference sweep first. Never fold either rename into an unrelated change.
- **Renames are all-or-nothing.** A partially applied rename is worse than the original deviation — it produces a broken workflow instead of an inconsistent one. If the full reference set cannot be resolved, do not start.
- **Do not double-report.** If an item is already covered by `name_capitalized`, `underscore_outputs`, or `job_environment_prefix`, the finding belongs to the linter. See the ownership table.
- **Flag gaps honestly.** Inputs, bash variable casing, and artifact names have no enforced standard. Say so; do not assert a convention this skill does not define.
