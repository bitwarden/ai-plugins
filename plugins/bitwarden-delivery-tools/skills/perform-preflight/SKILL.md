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

**Before anything else, check whether this layer already has an open pull request.** If it does, a fix on it belongs to `Skill(stacking-pull-requests)` Step 5, which rebases and force-pushes every layer above behind a confirmation listing them. Say so and stop rather than gating a commit that would strand those layers. This is the case that reaches here unattended: `Skill(committing-changes)` runs this checklist before staging, so a commit aimed at a lower layer passes through this section whether or not the stack workflow is driving.

- Do this section only if `gh stack view --json` exits `0` **and** its payload names the current branch. Any non-zero status skips it, and do not try to interpret which one you got — `Skill(stacking-pull-requests)` Step 0 owns what each status means and the install offer that follows.
- **Say when you skipped, and why.** A silent skip is indistinguishable from three satisfied checkboxes, and `stacking-pull-requests` Step 2 requires this section per layer. Report one of:
  - `Stacked Branches: skipped, gh stack view --json exited <N>`
  - `Stacked Branches: skipped, gh stack view --json exited 0 but its payload does not name this branch`
- **Leave the checkboxes unchecked on a skip.** A bare `exited 0` with ticks reads as a clean run to a human and to Step 2 alike.
- **A caller may assert this branch is a layer**, in which case run the section on that assertion instead of the probe. It must supply the parent branch with the assertion, since the rebase checkbox takes its parent from the payload that is absent on this path; without one, report that checkbox unverifiable rather than guessing.
- Do not pipe `gh stack view --json` when you need that status. The shell reports the last command's exit code, not `gh`'s, so a pipe silently turns the gate on the wrong process.

A stack merges bottom-to-top and all-or-nothing, so a layer that is red on its own blocks every layer above it.

- [ ] This layer builds, lints, and passes its tests with only the layers below it present
- [ ] This layer is rebased on its parent — `git merge-base --is-ancestor "<parent-branch>" HEAD` exits 0, where `<parent-branch>` is the layer immediately below this one in the `gh stack view --json` payload captured above. That name is repository data, so validate it against `^[A-Za-z0-9_][A-Za-z0-9._/-]*$` before composing the command and quote it as shown; a branch name is legal git syntax and can still be a shell payload. Report the checkbox unverifiable if it fails the pattern. On the bottom layer, whose parent is the stack base, report this unverified rather than substituting that base: the trunk-drift paragraph below deliberately keeps it off the checklist, and checking it here would reintroduce it
- [ ] This layer references no code that lands in a layer above it

The last item has no command behind it; it is a read-through of what this layer calls. Report it as checked-by-inspection rather than verified.

How far trunk has moved is deliberately not a checkbox. Trunk advances constantly, so gating a commit on it would fire most of the time and force a full-stack rebase and force-push, invalidating reviews on lower layers.

See `Skill(stacking-pull-requests)` for the surrounding workflow, for walking the rest of the stack, and for whether the `gh-stack` tooling is available at all.

## On Failure

If any check fails, fix the issue before proceeding — with one conditional exception. A failed **rebase checkbox** depends on whether the layer already has an open pull request. Before submission, when it does not, rebase it on its parent and restack the layers above it onto the result — `Skill(gh-stack)` has that command. There is nothing to force-push and no review to invalidate, but the branches above are still rooted on the pre-rebase tip and are stranded until they are restacked. Once it does, do not fix it here: the rebase rewrites and force-pushes every layer above, which belongs to `Skill(stacking-pull-requests)` Step 5 behind the confirmation it requires listing every affected PR. Report it and stop in that case. For test failures, diagnose the root cause rather than skipping. For lint/format failures, run the repo's auto-fix command if available. If a check cannot be resolved, flag it to the user with the specific failure output.
