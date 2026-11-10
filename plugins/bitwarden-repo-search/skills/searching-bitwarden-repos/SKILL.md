---
name: searching-bitwarden-repos
description: "Search across all repositories in the Bitwarden GitHub organization to find where specific code, features, or topics live. Use for 'where is passkey code', 'which repo has X', 'find where feature Y is implemented', or any cross-repo code discovery question."
argument-hint: "[search-query]"
arguments: [query]
allowed-tools: "Bash(gh *), Bash(jq *)"
---

# Searching Bitwarden Repos

Search across all repositories in the **bitwarden** GitHub organization to find where code, features, or topics are located. Return structured results grouped by repository with file paths and direct GitHub URLs.

## Steps

### 1. Search for code across the organization

Use GitHub code search to find where the query term appears across all bitwarden repos:

```bash
gh search code "org:bitwarden $query" --json repository,path,textMatches --limit 50
```

If results are too broad, refine with language or path filters:

```bash
gh search code "org:bitwarden $query language:rust" --json repository,path,textMatches --limit 30
gh search code "org:bitwarden $query path:src" --json repository,path,textMatches --limit 30
```

### 2. Identify relevant repositories

If code search returns too many results or the user wants a higher-level view, list repos that might be relevant:

```bash
gh search repos "org:bitwarden $query" --json name,description,url
gh repo list bitwarden --limit 100 --json name,description,url,primaryLanguage,updatedAt
```

### 3. Drill into specific repos

For the most relevant repos found, get more detail:

```bash
gh repo view bitwarden/<repo-name> --json name,description,url,stargazerCount,primaryLanguage,topics,defaultBranchRef
```

Browse the repo tree to understand structure when needed:

```bash
gh api repos/bitwarden/<repo-name>/git/trees/main --jq '.tree[].path'
```

### 4. Present results

Organize findings clearly:

- **Which repos** contain code related to the query
- **Which files/paths** are most relevant, grouped by repo
- **Brief summary** of what each repo's role is in relation to the query
- **Direct GitHub URLs** to the relevant files so the user can navigate there

Format as a table when there are multiple repos. Include the repo description and primary language.

## Known Feature-to-Repo Mappings

Before running searches, check if the query matches a known feature below. If it does, present the known mapping first and only search GitHub if the user wants more detail or the mapping seems incomplete.

### Passkeys (vault storage)

Bitwarden has two separate passkey concepts:

1. **Passkeys saved in vault** (Bitwarden as a software authenticator):
   - **passkey-rs** — Core WebAuthn/CTAP2 protocol engine (Rust)
   - **sdk-internal** → `crates/bitwarden-fido/` — Bridge layer to Bitwarden vault
   - **clients** → `apps/browser/src/autofill/fido2/`, `libs/common/src/platform/services/fido2/`
   - **android** and **ios** — consume SDK via UniFFI bindings
   - **server** — stores encrypted cipher only

2. **Passkeys for Bitwarden account login** (WebAuthn):
   - **server** → `src/Api/Auth/Controllers/WebAuthnController.cs`
   - **clients** → `apps/browser/src/auth/`
   - **sdk-internal** → `crates/bitwarden-fido/src/device_auth_key.rs`

### Passwordless.dev (separate product)

- **passwordless-server**, **passwordless-client-js**, **passwordless-dotnet**, **passwordless-java**, **passwordless-python** — separate Bitwarden product, not the vault passkey feature

## Notes

- The GitHub org is always **bitwarden** unless the user specifies otherwise
- Prefer `gh search code` for finding specific code or features
- Prefer `gh repo list` or `gh search repos` for discovering repos by topic
- Use `--limit` to avoid overwhelming output; start with 50 and increase if needed
- If rate-limited, wait briefly and retry
