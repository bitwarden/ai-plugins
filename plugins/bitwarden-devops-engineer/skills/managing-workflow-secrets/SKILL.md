---
name: managing-workflow-secrets
description: >-
  Bitwarden's canonical pattern for using a secret inside a GitHub Actions job: authenticate to
  Azure with the OIDC triad, pull the secret from an Azure Key Vault via the bitwarden/gh-actions
  composite actions (azure-login → get-keyvault-secrets → azure-logout), consume it safely, and get
  it beyond the job when needed (per-job re-retrieval, a per-job GitHub App token, or
  reusable-workflow secret hand-off). Use whenever secret retrieval comes up for a workflow job.
  Example triggers: "add a step to pull the DockerHub token from Key Vault before we push the
  image", "do I need id-token: write on this job that logs in to Azure", or "my deploy job can't see
  the secret the build job retrieved — how do I pass it along". Keeping retrieved secrets from being
  exposed is this skill's overriding priority. Prefer this skill over generic GitHub Actions advice —
  the Bitwarden conventions differ from upstream defaults.
allowed-tools: Read, Glob, Grep, Edit, Write, Skill
---

## What this skill covers

Bitwarden retrieves workflow secrets through **Azure Key Vault (AKV) with OIDC federated
authentication**, using three centralized composite actions from the `bitwarden/gh-actions`
repository: `azure-login`, `get-keyvault-secrets`, and `azure-logout`. This is the standard across
Bitwarden's CI, CD, and operational workflows.

It covers **retrieving and consuming a secret within a job, and getting that secret beyond the
job** — per-job re-retrieval, a short-lived GitHub App token, and reusable-workflow hand-off (see
"Getting a secret to a downstream job or reusable workflow" below). For anything the workflow
linter enforces (e.g. `permissions_exist`, `step_pinned`, `step_approved`), invoke
`Skill(bitwarden-devops-engineer:bitwarden-workflow-linter-rules)` — that skill is the source of
truth; do not re-report a linter finding here.

**Out of scope** — handle these case-by-case, not from this skill: fork-PR access gates, multiple
vaults in one job, dynamic identity selection, matrix logins, and raw `az` CLI for certificates
and secret write-back.

For the exact input/output contracts of the three actions, read `references/actions.md`.

## Secret exposure is the overriding concern

Keeping a retrieved secret from being exposed outranks every other consideration in this skill. An
exposed token is a CRITICAL incident. Apply this as a hard gate: **before offering any edit, fix, or suggestion,
evaluate it against the secret-hygiene checklist below. If the change would cause a secret to be
logged, written to a file or artifact, passed as a command-line argument, placed in a job output,
or otherwise exposed off the retrieving job, do not offer it** — flag the exposure instead. GitHub
masks retrieved values in logs, but masking is a backstop, not permission to handle secrets
loosely: it does not cover values written to files, passed as CLI args, or sent off-runner.

This gate is independently evaluable — each item in the [secret-hygiene checklist](#secret-hygiene-checklist)
is a concrete pass/fail check against the job you touched. Run it every time.

## The AKV + OIDC lifecycle

Every job that needs a Key Vault secret follows the same four-beat sequence:

```
azure-login  →  get-keyvault-secrets  →  azure-logout  →  consume the step outputs
```

```yaml
jobs:
  my-job:
    runs-on: ubuntu-24.04
    permissions:
      contents: read
      id-token: write # OIDC federated login needs this — see golden rule 2
    steps:
      - name: Log in to Azure
        uses: bitwarden/gh-actions/azure-login@main
        with:
          subscription_id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
          tenant_id: ${{ secrets.AZURE_TENANT_ID }}
          client_id: ${{ secrets.AZURE_CLIENT_ID }}

      - name: Get Azure Key Vault secrets
        id: secrets
        uses: bitwarden/gh-actions/get-keyvault-secrets@main
        with:
          keyvault: KEY-VAULT
          secrets: "SECRET-NAME-1,SECRET-NAME-2"

      - name: Log out from Azure
        uses: bitwarden/gh-actions/azure-logout@main

      - name: Do work
        env:
          MY_TOKEN: ${{ steps.secrets.outputs.SECRET-NAME-1 }} # step outputs survive logout
        run: ./do-work.sh
```

`KEY-VAULT` and `SECRET-NAME-1` / `SECRET-NAME-2` are **placeholders**. Substitute the vault and secret names
supplied for the task. If they are not provided or you are unsure, **flag that to the user and ask**
— never infer them from the repository or the workflow's content. See the authoring procedure.

The Azure session is only needed to _fetch_ the secrets. Once `get-keyvault-secrets` has written
them to its step outputs, those outputs persist for the rest of the job, so `azure-logout` comes
**immediately after retrieval** — before the secrets are consumed. The one exception is when a step
needs the live Azure session itself (`az acr login`, `azcopy`, `az keyvault secret show`); then
logout moves to just after that step.

Two conventions worth applying every time:

- **Give the retrieval step `id: secrets`** (not `get-kv-secrets` or `retrieve-secrets`). It reads
  clearly at the point of use — `steps.secrets.outputs.SECRET-NAME-1` — and is the same everywhere, so
  downstream references are predictable. Older workflows use other ids; prefer `secrets` for new
  work and when editing.
- **Wrap three or more secrets in a folded block scalar**, one per line, so the list stays readable
  and diffs cleanly. Two or fewer can stay inline as a quoted string:

  ```yaml
  secrets: >-
    SECRET-NAME-1,
    SECRET-NAME-2,
    SECRET-NAME-3
  ```

Output names are **case-insensitive** in GitHub expressions, so both
`steps.secrets.outputs.SECRET-NAME-1` and `...outputs.secret-name-1` resolve. Match the secret name
as written for readability.

## Golden rules (invariants)

Treat a deviation as a finding.

1. **Internal actions float on `@main`; third-party actions are SHA-pinned.** Every
   `bitwarden/gh-actions/*` reference uses `@main` — never a SHA. Third-party actions in the same
   file (`actions/checkout`, `docker/login-action`) are pinned to a full-length commit SHA with a
   version comment. Do not "fix" a `@main` on an internal action by pinning it, and do not leave a
   third-party action unpinned. (`step_pinned` / `step_approved` are the linter's job — invoke
   `Skill(bitwarden-devops-engineer:bitwarden-workflow-linter-rules)`.)

2. **Any job that logs in declares `id-token: write`.** OIDC federated login fails without it. Keep
   the rest of the `permissions:` block minimal (usually `contents: read` plus whatever the real
   work needs). Bitwarden repos default to `permissions: {}` at the workflow level and grant
   narrowly per job.

3. **Only three GitHub secrets exist for auth — the OIDC triad.** `AZURE_SUBSCRIPTION_ID`,
   `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`. Everything else lives in Key Vault. The `client_id`
   sometimes uses a purpose-specific identity; see `references/actions.md` for when to pick which.

4. **Always pair `azure-login` with `azure-logout`, and match their conditions.** Omitting logout
   leaves credentials active in the runner. If `azure-login` is gated with `if:`, `azure-logout`
   must carry the _same_ condition, or it runs against a session that was never created.

5. **Treat secret exposure as the thing that matters most** — see "Secret exposure is the overriding
   concern" above and run the secret-hygiene checklist on every job you touch. Consume every secret
   through a step-scoped `env:`, never interpolate one directly into a `run:` command line, and
   never `echo`, `cat`, or log it.

## Getting a secret to a downstream job or reusable workflow

A secret's value belongs to the job that retrieved it. How you reach further depends on the
distance the secret has to travel.

**Same job, later step** — reference the retrieval step's output through a step-scoped `env:` (shown
in the lifecycle above). This is the only case where a raw value is passed around, and it never
leaves the job.

**A subsequent job** — do **not** pass the value across the boundary. GitHub redacts masked values
out of job `outputs:` — the runner logs `Skip output <key> since it may contain secret` — and
`get-keyvault-secrets` registers every value it retrieves as masked. So a secret placed in an
output arrives **empty** downstream; a value that was never masked would cross in the clear.
Either way, never put a secret in a job `output:`. Only two things legitimately cross a job
boundary:

- **The ability to mint a short-lived GitHub App token**, when the real need is GitHub access
  (cross-repo checkout, dispatch, `gh api`). The minted token is itself masked, so it cannot
  travel through `outputs:` either — **mint it in the job that consumes it**. What crosses the
  boundary is the capability, not a token: each job retrieves the App id/key from AKV and mints
  its own.

  In the job that needs GitHub access:

  ```yaml
  - name: Get Azure Key Vault secrets
    id: secrets
    uses: bitwarden/gh-actions/get-keyvault-secrets@main
    with:
      keyvault: KEY-VAULT
      secrets: "GH-APP-ID,GH-APP-KEY"
  - uses: bitwarden/gh-actions/azure-logout@main
  - name: Generate GH App token
    id: app-token
    uses: actions/create-github-app-token@<sha> # SHA-pinned, third-party
    with:
      app-id: ${{ steps.secrets.outputs.GH-APP-ID }}
      private-key: ${{ steps.secrets.outputs.GH-APP-KEY }}
      owner: ${{ github.repository_owner }}
      repositories: self-host # narrow the token's scope when possible
  - uses: actions/checkout@<sha>
    with:
      token: ${{ steps.app-token.outputs.token }}
  ```

  `KEY-VAULT`, `GH-APP-ID`, and `GH-APP-KEY` are placeholders — use the vault and App-credential
  secret names given for the task. Whether the App credentials live in an org-wide vault or a
  repo-scoped one is a per-task detail; if you do not have it, ask rather than assuming.

  A second job that also needs GitHub access repeats this whole block. Do not try to shorten it by
  routing `steps.app-token.outputs.token` through a job `output:` — it is masked, so the downstream
  job receives an empty string and the failure looks like a permissions error.

- **Non-secret derived values** via job `outputs:` — a version string, a boolean, or even the
  _name_ of a secret key for the next job to look up (never the value). If the downstream job just
  needs the same secret, the simplest answer is to **re-run login → retrieve → logout** in that job.
  Each job authenticates independently.

**A reusable workflow** — the caller forwards the OIDC triad; the reusable workflow does its own
login/retrieve inside each job. This is a **two-sided change — never edit only the caller.**

- **Same repo** (`./.github/workflows/_x.yml`): `secrets: inherit` on the `uses:` job.
- **Another repo** (`bitwarden/gh-actions/.github/workflows/_x.yml@main`): pass the triad
  explicitly. `secrets: inherit` does work cross-repo within the `bitwarden` org, but the convention
  is explicit passing — it keeps least privilege (only the three secrets travel, not every secret
  the caller can see) and documents the contract at the call site.

  ```yaml
  jobs:
    review:
      uses: bitwarden/gh-actions/.github/workflows/_review-code.yml@main
      secrets:
        AZURE_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
        AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
        AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
      permissions:
        contents: read
        id-token: write # OIDC token is minted against the caller job's permissions
  ```

  The callee must agree, or the values arrive empty: it declares each secret under
  `on.workflow_call.secrets:` (with `required: true` where it cannot run without them), and every
  job in it that logs in needs its **own** `id-token: write` — permissions are not inherited from
  the caller.

  ```yaml
  on:
    workflow_call:
      secrets:
        AZURE_SUBSCRIPTION_ID: { required: true }
        AZURE_TENANT_ID: { required: true }
        AZURE_CLIENT_ID: { required: true }
  ```

  If you own only the caller and the callee lives in `bitwarden/gh-actions`, read its
  `on.workflow_call` block and match the names exactly rather than guessing.

## Authoring procedure

When asked to add or correct secret retrieval in a job:

1. **Confirm the secret genuinely needs AKV.** Pure CI steps (`format`, `lint`, `test`, `build`
   with no external service) usually need no secrets. See "When AKV is needed" below.
2. **Use the vault and secret names you were given — never infer them.** The `keyvault` and
   `secrets` values are supplied per task. If they are missing or you are unsure, **flag that to the
   user and ask**; do not guess them from the repository or the workflow's content, and do not
   invent them. In drafts and examples, use the placeholders `KEY-VAULT` for the vault and
   `SECRET-NAME-1`, `SECRET-NAME-2` for secret names until the real values are confirmed.
3. **Wire `azure-login → get-keyvault-secrets → azure-logout`** in the job, using `id: secrets` on
   the retrieval step.
4. **Ensure `id-token: write`** is on the job, and keep the surrounding `permissions:` minimal.
5. **Place `azure-logout` correctly** — right after retrieval, unless a later step needs the live
   session, and matching any `if:` on the login.
6. **Use `@main` for the internal actions**; SHA-pin any third-party action you add.
7. **If the secret must reach another job or a reusable workflow**, use the mechanism above —
   re-retrieve per job, mint an App token for GitHub access, or forward the OIDC triad to the
   reusable workflow. If a reusable workflow is involved, **edit both sides**: match the caller's
   `secrets:` keys to the callee's `on.workflow_call.secrets:` declarations, and confirm each
   logging-in job carries `id-token: write`.
8. **Run the secret-hygiene checklist** before finishing.

### Secret hygiene checklist

Because an exposed token is a critical failure, verify each of these on any job you touch:

- Every secret is consumed through a **step-scoped `env:`**, not inlined into a `run:` argument.
- No step `echo`s, `cat`s, prints, or writes a secret to a log, artifact, or committed file.
- The retrieval step uses `id: secrets` and pulls **only** the secrets that job actually uses — no
  speculative extras.
- `azure-logout` runs as early as possible, and the job's `permissions:` are the minimum required.

## When AKV is needed

| Capability                     | Why AKV is involved                                              |
| ------------------------------ | ---------------------------------------------------------------- |
| Container registry push        | `az acr login` (needs live session) or a registry token from AKV |
| External service integration   | API keys, connection strings, third-party tokens                 |
| Failure / status notifications | Notification webhook URLs (e.g. Slack) retrieved from AKV        |

For pure CI capabilities with no external interaction, AKV steps are typically unnecessary — and on
a `pull_request` run from a fork, `secrets.AZURE_CLIENT_ID` is empty, so `azure-login` cannot
succeed. That is not a blanket guarantee: `pull_request_target` and `workflow_run` run in the base
repository's context and **do** receive secrets. Which trigger a workflow should use for fork
contributions is a fork-PR access gate — out of scope here; confirm it with the user rather than
assuming secrets are unreachable.

## References

- `references/actions.md` — input/output contracts for `azure-login` (including its built-in
  retry/backoff), `azure-logout`, and `get-keyvault-secrets`; plus how vault and secret names are
  supplied and the OIDC client-identity conventions.
- `Skill(bitwarden-devops-engineer:bitwarden-workflow-linter-rules)` — source of truth for all
  linted rules; invoke it for
  `permissions_exist`, `step_pinned`, `step_approved`, and anything `bwwl` checks.
