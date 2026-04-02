---
description: Audit and remediate GitHub Actions action usage across the Bitwarden org
argument-hint: [action-name] [--mode incident|audit] [--replace <new-action>]
allowed-tools: Read, Edit, Glob, Grep, Bash(gh search code:*), Bash(gh api:*), Bash(gh repo clone:*), Bash(gh pr create:*), Bash(git checkout:*), Bash(git switch:*), Bash(git add:*), Bash(git commit:*), Bash(git push:*), Bash(git diff:*)
---

Audit usage of a GitHub Actions action across the entire Bitwarden org and produce a remediation plan. Supports two modes:

- **`incident`** (default): Targeted search for a specific action — used when an action is compromised or deprecated.
- **`audit`**: Sweep all workflow files org-wide for any unpinned action references.

## Step 1: Parse Arguments

- `action-name`: The action to search for (e.g., `tj-actions/changed-files`). Required in `incident` mode, omitted in `audit` mode.
- `--mode incident|audit`: Defaults to `incident` if an action name is provided, `audit` if not.
- `--replace <new-action>`: Optional. If provided, the remediation will swap the target action for this one instead of updating the pin.

## Step 2: Search Org-Wide

**Incident mode** — search for the specific action:

```bash
gh search code "uses: <action-name>" --owner bitwarden --extension yml --limit 100
```

Also search without the `uses:` prefix to catch indirect references:

```bash
gh search code "<action-name>" --owner bitwarden --extension yml --limit 100
```

**Audit mode** — find all workflow files with unpinned action references (not pinned to a full SHA):

```bash
gh search code "uses:" --owner bitwarden --extension yml --limit 100
```

Then filter results to find `uses:` lines that do NOT match the pattern `@[a-f0-9]{40}` (i.e., not pinned to a hash).

> **Note:** GitHub code search indexes can lag by minutes to hours after a recent push. Results may not reflect the very latest commits. Flag this caveat in the output.

## Step 3: Parse and Display Results

For each result, determine:

1. **Repo** and **file path**
2. **Current `uses:` value** (full line)
3. **Pin status:**
   - `hash` — pinned to a full 40-char SHA (compliant)
   - `tag` — pinned to a version tag (e.g., `@v3`, `@v1.2.3`)
   - `branch` — pointing to a branch (e.g., `@main`)
   - `none` — no pin at all

Display a table:

| Repo | File | Current Reference | Pin Status |
|------|------|-------------------|------------|
| ...  | ...  | ...               | ...        |

In `incident` mode, include all statuses. In `audit` mode, omit `hash` rows (already compliant).

If there are no findings, inform the user and stop.

## Step 4: Resolve Safe Hash (incident mode) or Confirm Action (audit mode)

**Incident mode:**

Determine the remediation approach:
- If `--replace <new-action>` was provided: the fix is to swap to the new action.
- Otherwise: the fix is to pin the existing action to a new safe hash.

If pinning to a new hash, resolve it:

```bash
gh api repos/<owner>/<repo>/commits/<ref> --jq '.sha'
```

Where `<owner>/<repo>` is the action's repo and `<ref>` is the target tag or `main`.

Present to the user:
- Resolved SHA
- Verification link: `https://github.com/<owner>/<repo>/commit/<sha>`

Ask: "Does this SHA look correct? Type `yes` to proceed, or provide a different SHA."

Wait for confirmation before continuing. Use the user-provided SHA if they supply one.

**Audit mode:**

For each unique action found unpinned, resolve its current latest SHA the same way and present a grouped list for the user to review before proceeding.

## Step 5: Select Repos to Remediate

Show the full list of affected repos and ask the user which ones to remediate. Options:
- All repos
- A subset (user provides a comma-separated list)
- None (exit after showing the audit report)

## Step 6: Apply Fixes Per Repo

For each selected repo:

1. Check if a local clone exists at `~/Documents/Repositories/bitwarden/<repo>`. If not, clone it:
   ```bash
   gh repo clone bitwarden/<repo> ~/Documents/Repositories/bitwarden/<repo>
   ```

2. Create a fix branch:
   ```bash
   git checkout -b fix/action-remediation-<action-name-slug>
   ```

3. Apply the fix to each affected file:
   - **Pin update:** Replace the `uses:` line with `uses: <action>@<sha> # <original-ref>`
   - **Replace:** Swap `uses: <old-action>@<ref>` with `uses: <new-action>@<sha> # <tag>`

4. Show a `git diff` of changes in this repo.

## Step 7: Create PRs

After all repos are fixed, ask the user to confirm PR creation.

If confirmed, for each repo:

```bash
git add .github/
git commit -m "Remediate <action-name> action usage"
gh pr create \
  --title "Remediate <action-name> action usage" \
  --body "$(cat <<'EOF'
## Summary

Remediates usage of `<action-name>` across this repository.

**Action taken:** <pin updated to `<sha>` / replaced with `<new-action>`>

**Reason:** <compromised action / deprecated action / unpinned reference>

cc @bitwarden/bre
EOF
)" \
  --draft
```

## Step 8: Final Summary

Output a summary of all actions taken:

| Repo | Files Changed | PR Created | Notes |
|------|--------------|------------|-------|
| ...  | ...          | ...        | ...   |

Remind the user that code search results may have a lag and to verify no repos were missed by checking manually if this is a security incident.
