---
name: perform-preflight
description: Quality gate checklist to run before committing or creating a PR, with a section covering the current branch when it is one layer of a stack. Use when finishing implementation, checking work quality, or preparing to commit. Triggered by "preflight", "self review", "ready to commit", "check my work", "quality gate". Gating a whole stack layer by layer belongs to stacking-pull-requests, which calls this per layer.
---

# Preflight Checklist

Run this checklist before committing or creating a PR. Consult the repo's CLAUDE.md for platform-specific commands (test runner, linter, formatter).

## Tests

- [ ] Run tests for affected modules (consult CLAUDE.md for commands)
- [ ] New code has test coverage
- [ ] No existing tests broken

## Code Quality

- [ ] Lint and format pass (consult CLAUDE.md for commands)
- [ ] No TODO comments without Jira ticket references
- [ ] Public APIs documented per repo convention (KDoc, DocC, XML docs, etc.)

## Bitwarden Security

- [ ] Zero-knowledge architecture preserved — no unencrypted vault data logged, persisted, or transmitted
- [ ] Sensitive data uses platform-appropriate secure storage (consult CLAUDE.md Security Rules)
- [ ] No sensitive data in log statements

## Architecture

- [ ] Changes follow patterns in CLAUDE.md and architecture docs
- [ ] Dependency injection and error handling follow repo convention
- [ ] String resources added to the correct location (if applicable)

## Stacked Branches

Only applies when the current branch is one layer of a stack. Test that rather than assume it, since preflight is often invoked directly rather than from the stack workflow. Run `gh stack view --json`, then:

- Do this section only if `gh stack view --json` exits `0` **and** its payload names the current branch. Any non-zero status skips it, and do not try to interpret which one you got — `Skill(stacking-pull-requests)` Step 0 owns what each status means.
- Do not pipe `gh stack view --json` when you need that status. The shell reports the last command's exit code, not `gh`'s.
- Read the current branch's entry in the payload just fetched — open-pull-request status and layer position both come from it. Do not make a second call.

**Stop, and defer the fix to `Skill(stacking-pull-requests)` Step 5, when all three hold:** this layer has an open pull request, a commit is about to land on it, and at least one layer sits above it. Say so rather than gating a commit that would strand those layers.

**Do not stop when any of these holds:** the pass is gate-only with no commit; this is the topmost layer; or the invocation states it is `stacking-pull-requests` Step 2 or Step 5. That claim has to be explicit — merely sitting on a layer with an open pull request is the case the stop exists for.

- **Say when you skipped, and why.** A silent skip is indistinguishable from three satisfied checkboxes, and `stacking-pull-requests` Step 2 requires this section per layer. Report one of:
  - `Stacked Branches: skipped, gh stack view --json exited <N>`
  - `Stacked Branches: skipped, gh stack view --json exited 0 but its payload does not name this branch`
- **Leave the checkboxes unchecked on a skip.** A bare `exited 0` with ticks reads as a clean run to a human and to Step 2 alike.
- **A caller may assert this branch is a layer**, in which case run on the assertion instead of the probe. It has to carry the parent branch, the open-pull-request status, and whether any layer sits above. Missing fields differ in consequence:
  - **No parent branch** — report the rebase checkbox unverifiable rather than guessing.
  - **No pull-request status, or no position** — treat the stop above as unresolved and stop.

A stack merges bottom-to-top and all-or-nothing, so a layer that is red on its own blocks every layer above it.

- [ ] This layer builds, lints, and passes its tests with only the layers below it present
- [ ] This layer is rebased on its parent — `git merge-base --is-ancestor "<parent-branch>" HEAD` exits 0
- [ ] This layer references no code that lands in a layer above it

The last item has no command behind it; it is a read-through of what this layer calls. Report it as checked-by-inspection rather than verified.

`<parent-branch>` comes from the payload entry below this one, or from a caller assertion. **Validate it against `^[A-Za-z0-9_][A-Za-z0-9._/-]*$` and quote it before composing the command, whichever source it came from**, and report the checkbox unverifiable if it fails. Double-quoting alone does not contain it: a parent of `main$(id)` runs the substitution inside `git merge-base --is-ancestor "<parent-branch>" HEAD`. An assertion is the less trustworthy of the two, since it arrives as free text. On the bottom layer, report the checkbox unverified rather than substituting the stack base.

`${CLAUDE_PLUGIN_ROOT}/skills/perform-preflight/references/stacked-branches.md` carries the reasoning behind each rule above, why trunk drift is deliberately not a checkbox, and both branches for a failed rebase checkbox. `Skill(stacking-pull-requests)` owns the surrounding workflow, walking the rest of the stack, and whether the `gh-stack` tooling is available at all.

## On Failure

If any check fails, fix the issue before proceeding — with one conditional exception. A failed **rebase checkbox** turns on whether the layer already has an open pull request: with no pull request yet, rebase it on its parent and restack the layers above; with one already open, report it and stop rather than fixing it here, even when Step 5 is driving. `${CLAUDE_PLUGIN_ROOT}/skills/perform-preflight/references/stacked-branches.md` has both branches in full.

For test failures, diagnose the root cause rather than skipping. For lint/format failures, run the repo's auto-fix command if available. If a check cannot be resolved, flag it to the user with the specific failure output.
