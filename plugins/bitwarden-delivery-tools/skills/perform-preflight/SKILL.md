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

**Before anything else, check whether this layer already has an open pull request** — the `gh stack view --json` payload just fetched carries it per layer; read the current branch's entry rather than making a second call. If it has one **and a commit is about to land on it**, that fix belongs to `Skill(stacking-pull-requests)` Step 5, which rebases and force-pushes every layer above behind a confirmation listing them. Say so and stop rather than gating a commit that would strand those layers. A commit is what this stop is about; a gate-only pass over a layer strands nothing. This is the case that reaches here unattended: `Skill(committing-changes)` runs this checklist before staging, so a commit aimed at a lower layer passes through this section whether or not the stack workflow is driving.

**Two invocations are not that case, and neither stops.** `stacking-pull-requests` Step 5 does commit on the layer, but it then restacks everything above behind its own confirmation listing every pull request that gets force-pushed — it is the sanctioned route for this fix, and stopping here would block the one path allowed to take it. Step 2 commits nothing: it walks the stack gating each layer, and on a stack already on GitHub every layer legitimately has an open pull request, so stopping would halt that walk on the bottom layer. Run the section normally when the invocation states either one. The claim has to be explicit — an invocation that merely happens to sit on a layer with an open pull request, with a commit behind it, is the case the stop exists for.

- Do this section only if `gh stack view --json` exits `0` **and** its payload names the current branch. Any non-zero status skips it, and do not try to interpret which one you got — `Skill(stacking-pull-requests)` Step 0 owns what each status means and the install offer that follows.
- **Say when you skipped, and why.** A silent skip is indistinguishable from three satisfied checkboxes, and `stacking-pull-requests` Step 2 requires this section per layer. Report one of:
  - `Stacked Branches: skipped, gh stack view --json exited <N>`
  - `Stacked Branches: skipped, gh stack view --json exited 0 but its payload does not name this branch`
- **Leave the checkboxes unchecked on a skip.** A bare `exited 0` with ticks reads as a clean run to a human and to Step 2 alike.
- **A caller may assert this branch is a layer**, in which case run the section on that assertion instead of the probe. The assertion has to carry the two things the absent payload would have supplied: the parent branch, which the rebase checkbox needs, and whether this layer already has an open pull request, which both the stop above and the On Failure branch turn on. Missing either, report the rebase checkbox unverifiable rather than guessing — treating an unstated pull request as absent would restack the layers above on an unverified premise, and "nothing to force-push" is the one claim this section cannot afford to assume.
- Do not pipe `gh stack view --json` when you need that status. The shell reports the last command's exit code, not `gh`'s, so a pipe silently turns the gate on the wrong process.

A stack merges bottom-to-top and all-or-nothing, so a layer that is red on its own blocks every layer above it.

- [ ] This layer builds, lints, and passes its tests with only the layers below it present
- [ ] This layer is rebased on its parent — `git merge-base --is-ancestor "<parent-branch>" HEAD` exits 0
- [ ] This layer references no code that lands in a layer above it

The last item has no command behind it; it is a read-through of what this layer calls. Report it as checked-by-inspection rather than verified.

**On the rebase checkbox.** `<parent-branch>` is the layer immediately below this one in the `gh stack view --json` payload captured above. That name is repository data, so validate it against `^[A-Za-z0-9_][A-Za-z0-9._/-]*$` before composing the command and quote it as shown — a branch name is legal git syntax and can still be a shell payload. Report the checkbox unverifiable if it fails the pattern.

On the bottom layer, whose parent is the stack base, report this unverified rather than substituting that base: the trunk-drift paragraph below deliberately keeps it off the checklist, and checking it here would reintroduce it.

How far trunk has moved is deliberately not a checkbox. Trunk advances constantly, so gating a commit on it would fire most of the time and force a full-stack rebase and force-push, invalidating reviews on lower layers.

See `Skill(stacking-pull-requests)` for the surrounding workflow, for walking the rest of the stack, and for whether the `gh-stack` tooling is available at all.

## On Failure

If any check fails, fix the issue before proceeding — with one conditional exception. A failed **rebase checkbox** depends on whether the layer already has an open pull request.

**When the layer has no pull request yet**, rebase it on its parent and restack the layers above it onto the result — `Skill(gh-stack)` has that command. There is nothing to force-push and no review to invalidate, but the branches above are still rooted on the pre-rebase tip and are stranded until they are restacked. If `gh-stack` is not resolvable, report the checkbox failed and stop rather than improvising the rebase by hand: this section's entry gate only proves the extension is present, and `Skill(stacking-pull-requests)` Step 0 calls extension-present-skill-absent the likeliest combination.

**When it already has one**, do not fix it here — and that holds even when Step 5 is driving. The rebase rewrites and force-pushes every layer above, which needs the kind of confirmation `stacking-pull-requests` Step 5 takes before its own restack. But Step 5 rebases the layers _above_ a fix; it has no step that rebases this layer onto its parent, so a layer that has drifted from its parent is outside its flow too. Report it and stop, and let the user decide — this is the one branch no caller is sanctioned for.

For test failures, diagnose the root cause rather than skipping. For lint/format failures, run the repo's auto-fix command if available. If a check cannot be resolved, flag it to the user with the specific failure output.
