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

## Pin Compliance Rules

Bitwarden enforces two distinct pinning requirements depending on who owns the action. This mirrors the logic in `step_pinned.py` in the `bitwarden/workflow-linter` repo.

**Internal actions** — any `uses:` reference starting with `bitwarden/`:
- **Compliant:** pinned to `@main` (e.g., `bitwarden/gh-actions/azure-login@main`)
- **Non-compliant:** pinned to a SHA, a tag, any other branch, or unpinned

**Third-party actions** — any `uses:` reference not starting with `bitwarden/` and not a local path (`./`):
- **Compliant:** pinned to a full 40-character commit SHA with an inline version comment (e.g., `actions/checkout@abc123...def456 # v4.1.1`)
- **Non-compliant:** pinned to a tag, a branch, a short SHA (< 40 chars), missing the inline comment, or unpinned

**Local/relative actions** — `uses:` values starting with `./`:
- Skip entirely. These are local composite actions and are not subject to pinning rules.

## Modes

- **`incident`** (default): Targeted search for a specific action — used when an action is compromised or deprecated.
- **`audit`**: Sweep all workflow files org-wide for any non-compliant action references.

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

**Audit mode** — find all workflow files and extract `uses:` references:

```bash
gh search code "uses:" --owner <org> --path .github/workflows/ --limit 100
```

Then apply the two-rule filter:
- **Internal** (`bitwarden/`): flag any reference NOT at `@main`
- **Third-party** (all others, excluding `./`): flag any reference NOT matching `@[a-f0-9]{40}` with a trailing inline comment

> **Note:** GitHub code search indexes can lag by minutes to hours after a recent push. Results may not reflect the very latest commits. Flag this caveat in the output.

## Step 3: Parse and Display Results

For each `uses:` reference (excluding local `./` paths), determine:

1. **Repo** and **file path**
2. **Current `uses:` value** (full line)
3. **Action type:**
   - `internal` — starts with `bitwarden/`
   - `third-party` — all others (excluding local)
4. **Pin status:**
   - `hash` — pinned to a full 40-char SHA
   - `tag` — pinned to a version tag (e.g., `@v3`, `@v1.2.3`)
   - `branch` — pointing to a named branch (e.g., `@main`, `@master`)
   - `none` — no ref at all
5. **Compliant:**
   - Internal + `branch` + branch is `main` → ✅
   - Third-party + `hash` + has inline comment → ✅
   - Everything else → ❌

Display a table:

| Repo | File | Current Reference | Type | Pin Status | Compliant |
| ---- | ---- | ----------------- | ---- | ---------- | --------- |
| ...  | ...  | ...               | ...  | ...        | ...       |

In `incident` mode, include all rows. In `audit` mode, omit compliant (✅) rows.

If there are no non-compliant findings, inform the user and stop.

## Step 4: Resolve Remediation Targets

Apply the correct fix approach based on action type. Do **not** treat all non-compliant references the same way.

**Internal actions** (`bitwarden/`):
- The fix is always to change the ref to `@main`. No SHA resolution needed.
- Flag if the action is currently on a SHA — this likely means it was incorrectly treated as third-party at some point.

**Third-party actions:**
- Resolve the current SHA for each unique non-compliant action:

```bash
gh api repos/<owner>/<repo>/commits/<ref> --jq '.sha'
```

Where `<owner>/<repo>` is the action's repo and `<ref>` is the target tag or `main`.

Present to the user:

- Resolved SHA
- Verification link: `https://github.com/<owner>/<repo>/commit/<sha>`

Ask: "Does this SHA look correct? Type `yes` to confirm, or provide a different SHA."

Wait for confirmation before finalizing the report.

> In **audit mode**, group unique third-party actions and resolve each once rather than per-occurrence.

## Step 5: Summary Report

Output a final summary:

| Repo | File | Current Reference | Type | Compliant | Remediation |
| ---- | ---- | ----------------- | ---- | --------- | ----------- |
| ...  | ...  | ...               | ...  | ...       | ...         |

The **Remediation** column should contain:
- For internal actions: `change ref to @main`
- For third-party actions: the resolved 40-char SHA + inline comment to add (e.g., `@abc123...def456 # v4.1.1`)

Inform the user that they can use the `action-remediate` skill to apply fixes based on these findings.
