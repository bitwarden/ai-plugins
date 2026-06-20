# Finding Targets

The engine stays generic; _this_ is where it learns to find things. Discovery is keyed by **signal type** — the shape of evidence that marks a target as relevant — not by any specific change. Pick the technique that matches the signal, fill in the specifics, and you have an applicability filter.

The operating environment is always the **Bitwarden GitHub enterprise**, so enumeration is grounded in `gh ... --owner bitwarden`. Authentication is the already-configured `gh` session; never inject tokens.

## Enumerate first

List the full candidate set before filtering.

- **Multi-repo** — every repo in the org:

  ```bash
  gh repo list bitwarden --no-archived --limit 1000 \
    --json name,defaultBranchRef,primaryLanguage,repositoryTopics
  ```

  Exclude archived repos unless the intent is explicitly about them. Treat the default branch from this listing as authoritative — never assume `main`.

- **Monorepo** — every project inside one clone. Enumerate by the marker that defines a project (the manifest or config file each project must have), e.g. `git ls-files '**/<project-marker>'`, then derive each project's directory from the match.

## Signal types (the generic techniques)

### 1. File-existence probe — "targets that contain file X"

Fast first pass across the org, no clone:

```bash
gh search code --owner bitwarden --filename <name> --json repository --limit 1000
```

Per-repo definitive check (200 = present, 404 = absent):

```bash
gh api repos/bitwarden/<repo>/contents/<path> --jq .sha
```

In a monorepo, the same signal is a glob: `git ls-files '<glob>'`.

### 2. Content match — "targets whose file contains string Y"

```bash
gh search code --owner bitwarden '<query>' --json repository,path --limit 1000
```

Use `--filename` / `--extension` / `--language` to narrow. Locally (monorepo, or after clone): `grep -rl '<pattern>' <path>`.

### 3. Dependency / manifest inspection — "targets that declare dependency Z"

Read the dependency manifest and test for the declaration rather than a loose text match — a substring can hit a comment or an unrelated field. Fetch the manifest, parse it, assert the key:

```bash
gh api repos/bitwarden/<repo>/contents/<manifest> \
  -H 'Accept: application/vnd.github.raw' | jq -e '<path-to-the-declaration>'
```

### 4. Topic / language filter — "targets in language L or tagged topic T"

```bash
gh search repos --owner bitwarden --language <lang> --json name --limit 1000
gh search repos --owner bitwarden --topic <topic> --json name --limit 1000
```

Or filter the `primaryLanguage` / `repositoryTopics` fields from the enumeration listing.

## Named cases map onto the signal types

These are one-line illustrations, not a menu — each is just a signal plugged into a technique above. Full narration of any of them lives in `../examples/`.

- "repos that use npm" → signal: a `package-lock.json` is present → **file-existence probe**.
- "repos that run a given workflow" → signal: `.github/workflows/<name>.yml` is present → **file-existence probe**.
- "repos that carry a Claude config" → signal: `.claude/settings.json` is present → **file-existence probe**.
- "repos that depend on a given library" → signal: the dependency is declared in the manifest → **manifest inspection**.
- "projects in a monorepo of a given framework" → signal: the framework's config marker exists in the project dir → **file-existence probe (glob)**.

## Trust, but re-verify

`gh search code` is the fast first pass, but it is **not authoritative**: it indexes only default branches, skips some repos, lags behind recent pushes, and is rate-limited. Treat its output as a _candidate_ list. The applicability filter is only confirmed when the recipe re-checks the signal in the freshly cloned target at execution time. A candidate whose signal is absent on clone is `skipped-not-applicable` — this is expected, not an error. This re-verification is the same instinct as the "spot-check the target list both ways" step in the SKILL.md self-check.
