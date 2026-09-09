# Why the Stacked Branches Rules Are What They Are

The Stacked Branches section of `perform-preflight` carries the rules. This file carries the reasoning behind them, plus the two On Failure branches for a failed rebase checkbox.

## Why the stop exists

`Skill(committing-changes)` runs the preflight checklist before staging, on every commit in every repository. So a commit aimed at a lower layer of a stack passes through that section whether or not the stack workflow is driving. That is the case that reaches the gate unattended, and it is the one the stop is for.

The fix itself belongs to `Skill(stacking-pull-requests)` Step 5, which rebases and force-pushes every layer above the commit behind a confirmation listing them. Gating the commit here instead would let it land and strand those layers on the pre-commit tip.

## Why the two carve-outs

**A gate-only pass strands nothing.** Running the checklist over a layer without committing changes nothing below the layers above it, so there is nothing to restack.

**The topmost layer has nothing above it.** Step 5 exists for a fix on a _lower_ layer. It rebases what sits above; on the top layer that set is empty, so stopping there redirects a routine fix to a step with nothing to offer it.

## Why two invocations do not stop

`stacking-pull-requests` Step 5 does commit on the layer, but it restacks everything above behind its own confirmation listing every pull request that gets force-pushed. It is the sanctioned route for this fix, and stopping would block the one path allowed to take it.

Step 2 commits nothing. It walks the stack gating each layer, and on a stack already on GitHub every layer legitimately has an open pull request, so stopping would halt that walk on the bottom layer.

The claim has to be explicit in the invocation. An invocation that merely happens to sit on a layer with an open pull request, with a commit behind it, is exactly the case the stop exists for.

## Why a missing assertion field is not a guess

A caller may assert this branch is a layer rather than letting the probe run. Treating an unstated pull request as absent would restack the layers above on an unverified premise, and "nothing to force-push" is the one claim this section cannot afford to assume. Reading an unstated position as topmost would waive the stop outright. A missing parent branch is narrower: only the rebase checkbox depends on it.

## Why the branch name is validated

`<parent-branch>` reaches the checklist from one of two places: the `gh stack view --json` payload, or a caller that asserted this branch is a layer. Neither is chosen locally, so both are untrusted. A branch name is legal git syntax and can still be a shell payload: `main$(id)` is a valid branch name and `git check-ref-format --branch` accepts it. Quoting does not save you, because command substitution runs inside double quotes. Validate against `^[A-Za-z0-9_][A-Za-z0-9._/-]*$` from either source before composing the command.

The assertion path is the weaker of the two. A payload came from `gh`; an assertion is free text handed over by another skill or the user, and it is the source most likely to be wrong or hostile. `stacking-pull-requests/references/submitting-a-stack.md` states the same rule for the branch names it composes with, and keeps it source-agnostic for this reason.

## Why trunk drift is not a checkbox

Trunk advances constantly, so gating a commit on it would fire most of the time and force a full-stack rebase and force-push, invalidating reviews on lower layers. The bottom layer's parent is the stack base, so its rebase checkbox is reported unverified rather than checked against that base: substituting it would reintroduce trunk drift through the back door.

## A failed rebase checkbox

**When the layer has no pull request yet**, rebase it on its parent and restack the layers above onto the result. `Skill(gh-stack)` has that command. There is nothing to force-push and no review to invalidate, but the branches above are still rooted on the pre-rebase tip and stay stranded until they are restacked. If `gh-stack` is not resolvable, report the checkbox failed and stop rather than improvising the rebase by hand: the section's entry gate only proves the extension is present, and `${CLAUDE_PLUGIN_ROOT}/skills/stacking-pull-requests/references/installing-gh-stack.md` calls extension-present-skill-absent the likeliest combination.

**When it already has one**, do not fix it here, and that holds even when Step 5 is driving. The rebase rewrites and force-pushes every layer above, which needs the kind of confirmation Step 5 takes before its own restack. But Step 5 rebases the layers _above_ a fix; it has no step that rebases this layer onto its parent, so a layer that has drifted from its parent is outside its flow too. Report it and stop, and let the user decide. This is the one branch no caller is sanctioned for.
