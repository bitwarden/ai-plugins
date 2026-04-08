---
name: bitwarden-workflow-linter-rules
description: Use this skill when linting and fixing GitHub Actions workflow findings from the Bitwarden workflow linter (bwwl). Covers the full workflow: running the linter, parsing errors only, applying per-rule fixes, verifying, and reporting results.
---

# Bitwarden Workflow Linter (bwwl)

The Bitwarden workflow linter (`bwwl`) enforces rules on all `.github/workflows/` files. This skill runs the linter, fixes every detected error, verifies the fixes, and reports results.

## Setup

If `bwwl` is not available in the current environment, install it before proceeding:

```bash
python3 -m venv /tmp/bwwl-venv
source /tmp/bwwl-venv/bin/activate
pip install bitwarden_workflow_linter --quiet
```

Requires Python 3.13+. Do not attempt to install it outside of a virtualenv. If setup fails, inform the user and wait for confirmation before continuing.

## Execution Steps

### Step 1: Run the Linter

```bash
bwwl lint -f .github/workflows
```

Capture both stdout and stderr. Note all file paths, line numbers, rule names, and error descriptions in the output.

### Step 2: Parse Output — Errors Only

From the linter output, produce a structured list of **errors only** — exclude warnings and informational findings. Group by:

1. **File** — which workflow file has issues
2. **Rule** — which rule is violated
3. **Location** — line number or context

This filtered list drives all subsequent steps.

### Step 3: Fix Detected Errors

Use the Read tool to examine each affected file, then use the Edit tool to apply fixes. Apply the correct fix for each rule as defined below.

#### Mechanical Rules — apply automatically

**`name_capitalized`**
- **Trigger:** A workflow-level or job-level `name:` value does not start with a capital letter.
- **Fix:** Capitalize the first character of the name value. Do not change anything else.

**`name_exists`**
- **Trigger:** A workflow or job is missing a `name:` key entirely.
- **Fix:** Ask the user what name to use, then add a `name:` key at the correct level with a capitalized value.

**`permissions_exist`**
- **Trigger:** A workflow or job is missing an explicit `permissions:` key.
- **Fix:** Add `permissions: {}` at the workflow level if all jobs are missing it, or at the individual job level if only some jobs are missing it. Prefer job-level permissions.

**`pinned_job_runner`**
- **Trigger:** A job's `runs-on:` uses an unpinned label.
- **Fix:** Replace with the current pinned equivalent:
  - `ubuntu-latest` → `ubuntu-24.04`
  - `windows-latest` → `windows-2022`
  - `macos-latest` → `macos-14`

**`step_pinned`**
- **Trigger:** A `uses:` reference is not pinned to a full commit SHA (e.g., uses a tag like `@v3` or branch like `@main`).
- **Fix:**
  1. Resolve the correct commit SHA via the GitHub API: `gh api repos/{owner}/{repo}/commits/{ref} --jq '.sha'`
  2. Show the SHA and a verification link (`https://github.com/{owner}/{repo}/commit/{sha}`) to the user before applying.
  3. Wait for the user to confirm the SHA. If they provide a different SHA, use that instead.
  4. Replace the `uses:` value with `{action}@{sha}` and add a comment with the original tag: `# {original-ref}`
  - **Example:** `uses: actions/checkout@v4` → `uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4`

**`underscore_outputs`**
- **Trigger:** A multi-word output name in a `$GITHUB_OUTPUT` write or `outputs:` block uses hyphens or camelCase instead of underscores.
- **Fix:** Rename the output key to use underscores. Update all references to that output within the same file.

**`job_environment_prefix`**
- **Trigger:** An environment variable name at the job level does not follow `SCREAMING_SNAKE_CASE`.
- **Fix:** Rename to `SCREAMING_SNAKE_CASE` and update all usages within the job.

**`check_pr_target`**
- **Trigger:** A workflow using `pull_request_target` has jobs not restricted to the default branch.
- **Fix:** Add a condition to the affected jobs: `if: github.ref == 'refs/heads/main'`

#### Judgment Rules — pause and ask the user

**`step_approved`**
- **Trigger:** A step's `uses:` references an action not on the Bitwarden approved actions list.
- **Options to present to the user:**
  1. **Add to approved list** — if the action is legitimate and BRE has reviewed it, add it to `bitwarden/workflow-linter`'s approved actions config.
  2. **Replace** — swap with an approved alternative that provides the same functionality.
  3. **Remove** — delete the step if it is not essential.
- Do not make this change automatically. Show the unapproved action name, ask which option the user wants, then act.

**`run_actionlint` (complex findings)**
- **Trigger:** `actionlint` reports an error that is not a simple formatting issue (e.g., type mismatches in expressions, invalid context references, shell script errors).
- **Action:** Show the finding verbatim, suggest a fix based on actionlint's message, and ask the user to confirm before applying.
- Simple actionlint findings (e.g., `shellcheck` style warnings with a clear single-line fix) may be applied automatically.

### Step 4: Verify Fixes

After all fixes are applied, re-run the linter:

```bash
bwwl lint -f .github/workflows
```

Confirm all previously reported errors are resolved and no new errors were introduced. If errors remain, analyze why the fix didn't work, adjust, and repeat until clean.

### Step 5: Report Results

```
## Linting Results

### Files Modified
- `.github/workflows/build.yml`
- `.github/workflows/deploy.yml`

### Errors Fixed
1. **permissions_exist** (2 occurrences)
   - Added `permissions: {}` to build.yml
   - Added `permissions: contents: write` to deploy.yml

2. **pinned_job_runner** (3 occurrences)
   - Replaced `ubuntu-latest` with `ubuntu-24.04` in build.yml (2 jobs)
   - Replaced `ubuntu-latest` with `ubuntu-24.04` in deploy.yml (1 job)

### Remaining Issues
None - all workflows pass linting.
```
