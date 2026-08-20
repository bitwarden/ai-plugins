# Action Contracts

The three centralized composite/node actions live in `bitwarden/gh-actions` and are always
referenced at `@main`. Their contracts below are the source of truth for what inputs are valid and
what outputs you can consume.

## Contents

1. [`azure-login`](#azure-login)
2. [`azure-logout`](#azure-logout)
3. [`get-keyvault-secrets`](#get-keyvault-secrets)
4. [OIDC triad and client identities](#oidc-triad-and-client-identities)
5. [Vault and secret names are provided, not inferred](#vault-and-secret-names-are-provided-not-inferred)

---

## `azure-login`

`bitwarden/gh-actions/azure-login@main` — composite action that performs an OIDC federated login
to Azure, with built-in retry.

| Input                    | Required | Default   | Notes                                                                           |
| ------------------------ | -------- | --------- | ------------------------------------------------------------------------------- |
| `tenant_id`              | yes      | —         | `${{ secrets.AZURE_TENANT_ID }}`                                                |
| `client_id`              | yes      | —         | An `AZURE_CLIENT_ID*` secret (see identities below)                             |
| `subscription_id`        | no       | `""`      | `${{ secrets.AZURE_SUBSCRIPTION_ID }}`; omit only with `allow_no_subscriptions` |
| `allow_no_subscriptions` | no       | `"false"` | Set `true` for Partner Center (no subscription)                                 |
| `retry_base_delay`       | no       | `"5"`     | Seconds; base for the exponential backoff between attempts                      |

Behavior worth knowing:

- **It retries.** The action wraps `Azure/login` in up to three attempts with exponential backoff
  (`retry_base_delay` × 1, then × 2), so transient OIDC failures self-heal. You do not need to add
  your own retry around it.
- **It requires `id-token: write`** on the job. Without it the federated login cannot mint a
  token and the step fails. This is the most common cause of "login works locally / on one job but
  not another".
- **The triad's scope is a repo setting, not a workflow fact.** If it is environment-scoped, a job
  without `environment:` resolves the `secrets.AZURE_*` expressions to empty strings and the login
  fails. You cannot read the scope from the workflow — ask rather than assume.
- **No `subscription-id` needed for tenant-only auth.** With `allow_no_subscriptions: true`, drop
  `subscription_id` entirely (used only for Partner Center tenants with no subscription).

---

## `azure-logout`

`bitwarden/gh-actions/azure-logout@main` — composite action, **no inputs**. It runs
`az logout || true`, so it is safe to call even if the session is already gone.

- Always pair it with a preceding `azure-login`.
- Place it immediately after `get-keyvault-secrets` (secret step outputs persist past logout),
  unless a later step needs the live session (`az acr login`, `azcopy`, `az keyvault secret
show/set`), in which case it moves to just after that step.
- Match any `if:` condition on the corresponding `azure-login`.

---

## `get-keyvault-secrets`

`bitwarden/gh-actions/get-keyvault-secrets@main` — node action that reads named secrets from a
Key Vault and exposes each as a step output.

| Input      | Required | Notes                                                                            |
| ---------- | -------- | -------------------------------------------------------------------------------- |
| `keyvault` | yes      | Name of the Key Vault (not a URL); provided per task — e.g. `KEY-VAULT`          |
| `secrets`  | yes      | Comma-separated list of secret names (inline for ≤2, folded block scalar for ≥3) |

Outputs:

- **One output per requested secret**, named after the secret. Consume as
  `${{ steps.<id>.outputs.<SECRET-NAME> }}`.
- **Output names are case-insensitive** in GitHub expressions, so `outputs.SECRET-NAME-1` and
  `outputs.secret-name-1` resolve to the same value. Both casings appear in real workflows; match
  the requested name for readability.
- Requires that `azure-login` has already run in the same job (it uses the active session).

Usage notes:

- **Use `id: secrets`.** It reads clearly downstream (`steps.secrets.outputs.<NAME>`) and stays
  the same across files. Older workflows use `get-kv-secrets` / `retrieve-secrets` /
  `retrieve-secret` / `get-secrets`; prefer `secrets` for new work. For a second vault in the same
  job, disambiguate by purpose (`secrets`, `secrets-2`) rather than reverting to a mechanism-named
  id.
- **Format the `secrets:` list by size.** One or two secrets can stay inline as a quoted string;
  three or more go in a folded block scalar, one per line, so the list is readable and diffs
  cleanly:

  ```yaml
  secrets: >-
    SECRET-NAME-1,
    SECRET-NAME-2,
    SECRET-NAME-3
  ```

- A single call can fetch many secrets. To pull from two vaults, use two steps (one login/logout
  brackets both) with a distinct `id:` per retrieval.
- The `secrets:` list can be built from inputs or workflow-level `env:` rather than hard-coded.
- **Retrieve only what the job uses, and consume via step-scoped `env:`.** The retrieved values
  are masked in logs, but do not `echo`/`cat`/log them, write them to files, or pass them as CLI
  args — masking is a backstop, not a license. An exposed token is a critical incident.

---

## OIDC triad and client identities

Only the OIDC triad is stored as GitHub Actions secrets; everything else lives in Key Vault.

| GitHub secret           | Purpose                                           |
| ----------------------- | ------------------------------------------------- |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription for OIDC                       |
| `AZURE_TENANT_ID`       | Azure AD tenant for OIDC                          |
| `AZURE_CLIENT_ID`       | Default app registration for OIDC federated login |

The `client_id` sometimes uses a **purpose-specific identity** for least privilege rather than the
default `AZURE_CLIENT_ID` — for example a read-only Key-Vault identity, a write-back identity used
only for secret rotation (`az keyvault secret set`), a Partner Center identity paired with
`allow_no_subscriptions: true`, or a per-environment identity selected dynamically in a deploy.
These are named as `AZURE_CLIENT_ID_<PURPOSE>` GitHub secrets and each corresponds to a real Azure
app registration.

Pick the narrowest identity that fits the job. **Use the identity you were given for the task; do
not introduce a new `AZURE_CLIENT_ID_*` on your own** — if the right one is unclear, confirm with
the user rather than guessing or inventing a name.

---

## Vault and secret names are provided, not inferred

The `keyvault` value and every entry in the `secrets:` list are supplied per task. **Never infer
them from the repository, the workflow's contents, or the surrounding steps, and never invent
one.** If a name is missing or you are unsure, flag it to the user and ask.

- In drafts and examples, use the placeholders **`KEY-VAULT`** for the vault and **`SECRET-NAME-1`**,
  **`SECRET-NAME-2`**, … for the secret names, and swap in the real values only once they are confirmed.
- Secret names you retrieve are still secret material in transit — apply the hygiene rules in the
  `get-keyvault-secrets` section above regardless of the name.
- When editing an existing workflow, read the vault and secret names already present in that file
  and preserve them exactly; matching an existing, in-file name is reading, not inferring.

This skill contains no catalogue of real vault or secret names. Confirm names with the user or read
them from the file you are editing.
