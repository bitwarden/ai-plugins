---
name: action-audit
description: >
  Audit GitHub Actions action usage across an org. Searches for a specific action (incident mode)
  or sweeps all workflow files for unpinned action references (audit mode). Produces a read-only
  report of findings with pin status and resolved SHAs. Does not modify any files.

  <example>
  User: We need to check if any repos are using tj-actions/changed-files
  Action: Trigger action-audit in incident mode for that action
  </example>

  <example>
  User: Can you find all unpinned actions across the org?
  Action: Trigger action-audit in audit mode
  </example>
allowed-tools: Read, Glob, Grep, Bash(gh search code:*), Bash(gh api:*)
---

## Rules

- **This skill is strictly read-only.** Do not modify, create, or delete any files.
- **No mutating API calls.** `gh api` GET requests are allowed freely. Do not use `-X POST`, `-X PUT`, `-X PATCH`, or `-X DELETE`.
- **Flag uncertainty.** If a finding is ambiguous, note it in the report rather than guessing.

## Modes

- **`incident`** (default): Targeted search for a specific action — used when an action is compromised or deprecated.
- **`audit`**: Sweep all workflow files org-wide for any unpinned action references.

## Step 1: Parse Context

Determine the mode from the user's request:

- If the user names a specific action (e.g., `tj-actions/changed-files`), use **incident** mode.
- If the user asks for a general sweep of unpinned actions, use **audit** mode.
- If a replacement action is mentioned, note it for the remediation step (handled separately by the `action-remediate` skill).

## Step 2: Search Org-Wide

**Incident mode** — search for the specific action:

```bash
gh search code "uses: <action-name>" --owner <org> --path .github/workflows/ --limit 100
```

Also search without the `uses:` prefix to catch indirect references:

```bash
gh search code "<action-name>" --owner <org> --path .github/workflows/ --limit 100
```

**Audit mode** — find all workflow files with unpinned action references (not pinned to a full SHA):

```bash
gh search code "uses:" --owner <org> --path .github/workflows/ --limit 100
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
| ---- | ---- | ----------------- | ---------- |
| ...  | ...  | ...               | ...        |

In `incident` mode, include all statuses. In `audit` mode, omit `hash` rows (already compliant).

If there are no findings, inform the user and stop.

## Step 4: Resolve SHAs

**Incident mode:**

Determine the remediation approach:

- If the user mentioned a replacement action: note it in the report.
- Otherwise: resolve the safe hash for pinning.

Resolve the SHA:

```bash
gh api repos/<owner>/<repo>/commits/<ref> --jq '.sha'
```

Where `<owner>/<repo>` is the action's repo and `<ref>` is the target tag or `main`.

Present to the user:

- Resolved SHA
- Verification link: `https://github.com/<owner>/<repo>/commit/<sha>`

Ask: "Does this SHA look correct? Type `yes` to confirm, or provide a different SHA."

Wait for confirmation before finalizing the report.

**Audit mode:**

For each unique action found unpinned, resolve its current latest SHA the same way and present a grouped list for the user to review.

## Step 5: Summary Report

Output a final summary:

| Repo | File | Current Reference | Pin Status | Resolved SHA |
| ---- | ---- | ----------------- | ---------- | ------------ |
| ...  | ...  | ...               | ...        | ...          |

Inform the user that they can use the `action-remediate` skill to apply fixes based on these findings.
