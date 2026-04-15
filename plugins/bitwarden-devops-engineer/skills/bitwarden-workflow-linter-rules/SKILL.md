---
name: bitwarden-workflow-linter-rules
description: >-
  Reference for all Bitwarden workflow linter (bwwl) rules. Covers all 10 linter rules split into
  two categories: mechanical rules that can be applied automatically (name_capitalized,
  permissions_exist, pinned_job_runner, step_pinned, underscore_outputs, job_environment_prefix,
  check_pr_target) and judgment rules requiring user input (name_exists, step_approved,
  run_actionlint). Use the workflow-audit skill to run the linter and report findings, and the
  workflow-fix skill to apply fixes.

  <example>
  User: What does the step_pinned rule check for?
  Action: Consult this skill for the rule definition and fix procedure
  </example>

  <example>
  User: How do I fix a permissions_exist finding?
  Action: Consult this skill for the fix procedure
  </example>
---

## Mechanical Rules — apply automatically

**`name_capitalized`**

- **Trigger:** A workflow-level or job-level `name:` value does not start with a capital letter.
- **Fix:** Capitalize the first character of the name value. Do not change anything else.

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
- **Fix:** Add a condition to the affected jobs: `if: github.ref == 'refs/heads/<default-branch>'`. Determine the repo's default branch rather than assuming `main`. If the job already has an `if:` condition, combine with `&&` (e.g., `if: <existing-condition> && github.ref == 'refs/heads/<default-branch>'`).

## Judgment Rules — pause and ask the user

**`name_exists`**

- **Trigger:** A workflow or job is missing a `name:` key entirely.
- **Fix:** Ask the user what name to use, then add a `name:` key at the correct level with a capitalized value.

**`step_approved`**

- **Trigger:** A step's `uses:` references an action not on the Bitwarden approved actions list.
- **Options to present to the user:**
  1. **Add to approved list** — if the action is legitimate and has been reviewed and approved, add it to `bitwarden/workflow-linter`'s approved actions config.
  2. **Replace** — swap with an approved alternative that provides the same functionality.
  3. **Remove** — delete the step if it is not essential.
- Do not make this change automatically. Show the unapproved action name, ask which option the user wants, then act.

**`run_actionlint` (complex findings)**

- **Trigger:** `actionlint` reports an error that is not a simple formatting issue (e.g., type mismatches in expressions, invalid context references, shell script errors).
- **Action:** Show the finding verbatim, suggest a fix based on actionlint's message, and ask the user to confirm before applying.
- Simple actionlint findings (e.g., `shellcheck` style warnings with a clear single-line fix) may be applied automatically.
