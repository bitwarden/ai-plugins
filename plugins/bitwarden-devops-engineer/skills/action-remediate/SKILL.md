---
name: action-remediate
description: >
  Remediate GitHub Actions action findings identified by the action-audit skill. Applies hash pins
  or action replacements across selected repos and creates draft PRs. Run the action-audit skill
  first to identify findings before using this skill.

  <example>
  User: Go ahead and fix the unpinned actions from the audit
  Action: Trigger action-remediate to apply fixes and create PRs
  </example>

  <example>
  User: Replace tj-actions/changed-files with the safe version across those repos
  Action: Trigger action-remediate to swap the action and create PRs
  </example>
allowed-tools: Read, Edit, Glob, Grep, Bash(gh pr create:*), Bash(git checkout:*), Bash(git add .github/:*), Bash(git commit:*), Bash(git push:*), Bash(git diff:*)
---

## Rules

- **No mutating API calls without confirmation.** `gh api` GET requests are allowed freely. Any call using `-X POST`, `-X PUT`, `-X PATCH`, or `-X DELETE` must be shown to the user and approved before execution.
- **Never force-push, delete branches, or delete repositories.**
- **Only modify files under `.github/`.** Do not touch application code, scripts, or configuration outside of workflow files.
- **Show a diff and get confirmation before every commit.**
- **All PRs must be created as drafts.**
- **Flag uncertainty.** If a finding is ambiguous or a fix could break a workflow, stop and ask rather than guessing.

## Step 1: Confirm Audit Findings

Before proceeding, verify that the user has audit findings to act on. These should come from a prior run of the `action-audit` skill. Confirm:

- Which repos to remediate (all, a subset, or specific ones)
- The remediation approach: **pin update** (update to a verified SHA) or **replace** (swap to a different action)
- The target SHA or replacement action

If any of this is unclear, ask the user before continuing.

## Step 2: Apply Fixes Per Repo

For each selected repo:

1. Ask the user for the base directory where their repos are cloned (if not already known). Check if a local clone exists at `<base-dir>/<repo>`. If not, inform the user and skip that repo.

2. Create a fix branch:

   ```bash
   git checkout -b fix/action-remediation-<action-name-slug>
   ```

3. Apply the fix to each affected file:
   - **Pin update:** Replace the `uses:` line with `uses: <action>@<sha> # <original-ref>`
   - **Replace:** Swap `uses: <old-action>@<ref>` with `uses: <new-action>@<sha> # <tag>`

4. Show a `git diff` of changes in this repo and get confirmation before proceeding.

## Step 3: Create PRs

After fixes are confirmed, for each repo:

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
EOF
)" \
  --draft
```

## Step 4: Final Summary

Output a summary of all actions taken:

| Repo | Files Changed | PR Created | Notes |
| ---- | ------------- | ---------- | ----- |
| ...  | ...           | ...        | ...   |

Remind the user that code search results may have a lag and to verify no repos were missed by checking manually if this is a security incident.
