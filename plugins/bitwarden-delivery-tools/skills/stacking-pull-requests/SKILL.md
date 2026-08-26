---
name: stacking-pull-requests
description: 'Break one change into a stack of dependent pull requests in a Bitwarden repository — plan the layers, carry the ticket key, the conventional-commit type prefix that drives the t: label, the PR template, and the ai-review label onto every layer, gate each layer, submit the chain, address review feedback on a lower layer, and merge the stack. Triggered by "stack these PRs", "stacked diffs", "split this into dependent PRs", "comment on the bottom PR of my chain", "land the whole chain". Not for a single-branch pull request (that is creating-pull-request) or one change fanned across many repositories (that is force-multiplier).'
---

# Stacking Pull Requests

A stack turns one large change into a chain of branches, each rooted on the one below it, where every layer is its own pull request reviewed against its parent rather than against trunk. Reviewers see one concern at a time.

The mechanics belong to GitHub: `Skill(gh-stack)` documents the full `gh stack` command surface, its non-interactive flags, and the traps that hang an agent. This skill does not restate that surface. Aside from the availability and state checks in Step 0, the stack registration in Step 1, and the merge in Step 6 — whose flags come from `Skill(gh-stack)`, not from here — the only `gh stack` commands written down here are the submission sequence in `${CLAUDE_PLUGIN_ROOT}/skills/stacking-pull-requests/references/submitting-a-stack.md`, which stays usable on its own; navigation, rebasing, and conflict handling need `Skill(gh-stack)`. What this skill owns is the part GitHub's tooling knows nothing about: Bitwarden's per-PR conventions, which a stack multiplies by the number of layers, and which `gh stack submit` cannot carry at all.

## Step 0 — Confirm stacks are available

Stacks depend on an external, pre-1.0 extension that is not installed by default, plus the skill that ships with it. Check both before planning anything, because a plan built on unavailable tooling wastes the planning.

- **Extension.** `gh extension list` must show a `github/gh-stack` row. If it is absent, offer `gh extension install github/gh-stack --pin v0.1.0`. Pin it: the extension is pre-1.0, the flag sets in the references were verified against v0.1.0, and this is the component that runs with live `git` and `gh` write credentials.
- **Skill.** A `gh-stack` skill must be resolvable — from a plugin, a `--plugin-dir` load, or a `SKILL.md` at `.claude/skills/gh-stack/` or `~/.claude/skills/gh-stack/`. Check the available-skills listing for the name, and only fall back to `Glob` over those two paths if it is absent there. Do not probe by invoking `Skill(gh-stack)` to see what happens: invoking a missing skill is itself an error, inside a gate whose whole job is to fail cleanly into the fallback. `gh extension install` fetches only a platform binary and never places the skill, so it has to be installed separately; `${CLAUDE_PLUGIN_ROOT}/skills/stacking-pull-requests/references/installing-gh-stack.md` has that procedure, including the commit the copy must be verified against. Extension present and skill absent is therefore the likeliest combination, so offer the procedure — and note that installing the skill does not make it resolvable until Claude Code restarts, so a successful install still leaves this run without it.

The condition for continuing is that both are usable **in this run**: the extension present, and the skill resolvable. Install status is not the same thing — the extension may have been installed a moment ago, since `gh extension list` reflects it immediately, but the skill cannot be. If either is missing, name which one and its remedy, and ask whether to install it.

**A skill installed just now does not become resolvable in this session.** Claude Code discovers skills at session start, so a `SKILL.md` copied into `.claude/skills/gh-stack/` is on disk but unresolvable until a restart — and the re-check above cannot see the difference, because the available-skills listing is fixed for the session while the `Glob` fallback finds the file. Do not read a successful install as the skill being present. Say the install succeeded and tell the user to restart Claude Code and re-run to get the stack path. Continuing into Step 1 delegates `gh stack init`, navigation, rebasing, and the merge to a skill that is not loaded, which is the half-attempted stack this step forbids — and it lands after the user has consented to an install and after the layers are planned.

**The fallback covers every outcome that leaves the skill unresolvable for this run** — the user declines, an install fails, or the skill install succeeds. In all three the change ships as a single pull request: hand off to `Skill(creating-pull-request)` and state in the handoff that the stack path was already tried and is unavailable for this run, so it proceeds as one PR instead of routing back here. Do not say it was declined when it was installed; the handoff signal is the same either way. Say plainly that the change is shipping as one PR. Never half-attempt a stack.

**Existing stack state.** Once both are usable in this run, invoke `Skill(gh-stack)` and have it report the current stack with `gh stack view --json`. Read the exit code: `0` means the current branch is in a stack, and anything else means treat it as not in one. Do not run it through a pipe when you need that status — the shell reports the last command's exit code, not `gh`'s. Exit `2` covers "not in a stack" but also "not a git repository" and a detached HEAD, so require that a successful payload names the current branch rather than trusting the code alone. Exit `9` is different and worth catching here: it means the repository does not have stacked PRs enabled, which otherwise surfaces only at submit, after every layer has been planned, gated, and titled. Treat it as unavailable tooling and take the single-branch fallback.

## Step 1 — Plan the layers before writing code

Layer boundaries are a design decision, and retrofitting them onto a finished branch is the expensive way to discover that. Decide the chain first.

Two properties make a layer a real layer:

- **Independently reviewable.** It is one coherent concern a reviewer can judge without the layers above it.
- **Independently green.** It builds, lints, and passes its tests with only the layers below it present. A layer that is red on its own is not reviewable and cannot merge, since `gh stack merge` lands the chain bottom-to-top.

Foundational work goes at the bottom, consumers above it. If code in one layer depends on code in another, the dependency belongs in the same layer or a lower one — never a higher one.

**Don't stack when:** the change fits comfortably in one PR; the layers cannot be made independently green; or the work is the same change repeated across many repositories, which is a fan-out rather than a chain and belongs to `Skill(force-multiplier)`.

Confirm the planned layers with the user before creating branches. Name each layer's concern and the Jira ticket the stack serves. One ticket normally spans the whole stack.

**Then build the layers.** Step 2 assumes every planned layer already exists as a branch with its commits on it, and three entry shapes reach it:

- **Nothing written yet.** Create each branch on the one below it and write the layers bottom-up.
- **Already in a stack**, which is what exit `0` in Step 0 reports. The layers exist; add to them rather than rebuilding, and see the submission reference for appending a layer to a stack already on GitHub.
- **One oversized branch already written**, which is how most requests here arrive ("split this into dependent PRs", "I want stacked diffs instead of one 2000-line review"). Decide which existing commits belong to which layer before moving anything, then redistribute them. Whether a commit is foundation or consumer is the planning judgment this skill owns; the branch and rebase mechanics are `Skill(gh-stack)`'s.

**Register the layers as a stack.** On the first and third shapes the branches are not yet a stack as far as `gh stack` is concerned, and `gh stack push` in the submission sequence exits `2` without one — after every layer has been gated, titled and previewed, which is the late failure Step 0 exists to prevent. Validate every branch name against the allowlist in `${CLAUDE_PLUGIN_ROOT}/skills/stacking-pull-requests/references/submitting-a-stack.md` before composing the command — two of the three shapes take names from the repository rather than names you chose. Then `gh stack init --base "<stack base>" "<layer-1>" "<layer-2>" …` covers both: it adopts branches that already exist and creates the ones that do not. `<stack base>` is the branch layer 1 was cut from — trunk usually, but `rc`, `hotfix-rc`, or another release branch when the stack is rooted there. Name it explicitly rather than letting it default: every command that takes a base takes this one, and a stack registered against the repository default branch submits its bottom layer at trunk. Confirm with `gh stack view --json` before moving on.

Each layer's first commit takes the full format from `Skill(committing-changes)`.

## Step 2 — Gate every layer, not just the top

Both delivery gates are per-PR, so in a stack they run per layer.

- `Skill(perform-preflight)` on each layer, including its Stacked Branches section. That skill checks the layer it is on; this step owns walking the stack, so check out each layer in turn and run it there. Walk bottom to top. A failed rebase checkbox on a lower layer is fixed by rebasing it and restacking everything above, which rewrites those layers' commits. Going upward means each higher layer is gated after that rewrite; top-down gates it before, so its tests, review path and deferred findings describe commits the restack replaced, and Step 4's preview renders that stale record as current.
- The code-review gate from `Skill(creating-pull-request)` Step 1b, per layer. Layer scoping is the wrinkle: both review paths default to `origin/HEAD`, so on layer 3 they re-review layers 1 and 2. That step's own base-ref paragraph is authoritative on which path can be scoped to a single layer and what to record when neither can — follow it rather than a second copy here.

**Record what each gate produced.** Step 4's preview prints a review path and a deferred-finding count per layer, and nothing else carries them: `creating-pull-request` writes those into its own Step 3 preview, which never runs per layer. So as each layer's gate finishes, note the path taken (`Standard`, `Substantial`, or a user-volunteered skip), every deferred CRITICAL or IMPORTANT finding, and whatever `perform-preflight` reported for its Stacked Branches section — a skip there has to reach the preview, or a layer whose stack checks never ran renders as `preflight: pass`. Carry the review path and the deferred findings into that layer's PR body, and all three into its preview row — the preflight report has a slot only in the preview.

**Tell the reviewer where the layer sits.** A lower layer legitimately adds code with no caller yet, because the caller lands above it. State the layer's position and what lands above it in the review request, otherwise a reviewer reasonably reads incomplete-by-design work as dead code.

## Step 3 — Give every layer its Bitwarden conventions

Each layer is a pull request, so each layer needs the same conventions a single-branch PR does. Invoke `Skill(applying-pr-conventions)` **once per layer** to compose them.

That skill produces a title, a body, and a label choice, and nothing else — it does not review, preview, push, or create. Which is what makes it safe to call in a loop: this step collects N sets of conventions, Step 4 previews them together, and the submission reference creates the pull requests. Do not route layers through `Skill(creating-pull-request)` instead. That workflow ends in a per-PR preview and its own `gh pr create`, so per layer it would ask the user to authorize a submission the stack has not been previewed for, then push outside the submission sequence and create pull requests that sequence tries to create again.

Two things this step carries across the loop rather than asking per layer:

- **The label.** One decision for the whole stack, applied to every layer. Ask it on the first layer and pass the answer into the rest; `applying-pr-conventions` skips its label question when the caller has already settled it.
- **The ticket key.** One ticket normally spans the stack, so the key repeats on every layer.

The type keyword is the opposite — chosen per layer, since a stack often mixes `feat` and `refactor`. Each layer's body also states its own position in the chain, which is the other reason the body cannot be composed once and reused.

**`gh stack submit` cannot carry any of this.** Its only flags are `--auto`, `--open`, and `--remote`; there is no title, body, or label flag, and `--auto` generates titles that carry no type prefix. A stack submitted that way ships N pull requests with no `t:` label and no template body. `${CLAUDE_PLUGIN_ROOT}/skills/stacking-pull-requests/references/submitting-a-stack.md` has the two paths that do work and the commands for each.

## Step 4 — Preview the whole stack, then submit

`creating-pull-request` shows one submission preview per PR. For a stack, show one preview covering every layer, because a wrong base is the failure this catch-net exists for and it is only visible when the chain is laid out together:

```
═══════════════════════════════════════
  STACK SUBMISSION PREVIEW
═══════════════════════════════════════
Target repo:    <owner/repo>
Stack base:     <stack base>   (trunk, or the release branch layer 1 was cut from)
Draft:          <Yes / No>   (Step 6 runs `gh pr ready` on every draft before merging)
AI review:      <ai-review / ai-review-vnext / No label>

  1. <branch>   base: <stack base>  <full title>   → t:<label>
       preflight: <pass | Stacked Branches skipped: reason>   review: <Standard | Substantial | Skipped (user request)>   deferred: <N>
  2. <branch>   base: <layer 1>     <full title>   → t:<label>
       preflight: <pass | Stacked Branches skipped: reason>   review: <Standard | Substantial | Skipped (user request)>   deferred: <N>
  3. <branch>   base: <layer 2>     <full title>   → t:<label>
       preflight: <pass | Stacked Branches skipped: reason>   review: <Standard | Substantial | Skipped (user request)>   deferred: <N>

Bodies:
---
<each layer's full body, exactly as it will be submitted>
---
═══════════════════════════════════════
```

Every layer carries its own review path and deferred-finding count, because `creating-pull-request` Step 1b records a user-volunteered skip and any deferred CRITICAL or IMPORTANT findings for surfacing at preview time, and this is the preview that replaces its Step 3. A skip on one layer must not be invisible behind a tick.

Confirm with `AskUserQuestion` before anything is pushed, offering submit / edit a layer / change the label / cancel. Only submit on an explicit confirmation, then follow `${CLAUDE_PLUGIN_ROOT}/skills/stacking-pull-requests/references/submitting-a-stack.md`.

## Step 5 — Feedback on a lower layer

A comment on a lower layer gets fixed on that layer. Navigate down to it, commit the fix there, rebase the layers above it, and return. `Skill(gh-stack)` has the commands and the shared-branch and conflict traps.

Rebasing the layers above rewrites branches that already carry open pull requests and reviewer comments, and landing it means force-pushing each one. Treat that with the same discipline as Step 4: before rebasing, use `AskUserQuestion` to confirm, listing every layer that will be rewritten and force-pushed. Comments anchored to rewritten commits may be marked outdated, so say which PRs are affected rather than only how many.

Never patch a lower layer's problem at the top of the stack. It leaves the lower PR wrong on its own, and reviewers of that PR are looking at code that no longer reflects the fix. `Skill(bitwarden-code-review:addressing-code-review-comments)` still governs how to evaluate the feedback itself.

## Step 6 — Merging

Step 4's confirmation authorized submission, not merging. Both actions here span every layer, so confirm again with `AskUserQuestion` before either, showing each PR number, its current draft state, and the merge method. Marking a draft ready notifies reviewers and triggers label automation, and is reversible with `gh pr ready --undo`; the merge lands the whole chain into trunk and is not. Pass the confirmed method explicitly on the merge — a bare `gh stack merge` reuses whichever method was last used, which is not necessarily the one just agreed.

Layers are normally created as drafts, and `gh stack merge` refuses a draft. Take the stack out of draft first: check each layer's state and run `gh pr ready <pr>` bottom to top on any still in draft. Skipping this stalls the whole chain, since the merge is all-or-nothing.

`gh pr merge` does not work on a stacked PR. Merging goes through `gh stack merge`, which lands the chain bottom-to-top: if one PR cannot merge, none do. Only open-and-not-draft state is checked, so a stack cannot bypass Bitwarden's required checks, and a base branch with a merge queue takes the stack into the queue instead of merging it directly. `Skill(gh-stack)` has the flags.

## Related skills

- `Skill(gh-stack)` — every `gh stack` command and its non-interactive flags. All mechanics live there.
- `Skill(applying-pr-conventions)` — the per-layer title, body, and label this skill applies N times.
- `Skill(creating-pull-request)` — its Step 1 review gate, run per layer in Step 2; the rest of that workflow is the single-branch path and does not run from here.
- `Skill(perform-preflight)` — the per-layer quality gate, including its stack section.
- `Skill(committing-changes)` — commit format; in a stack, each layer's first commit carries the full format.
- `Skill(force-multiplier)` — the other multi-PR shape: one change across many repositories, in parallel rather than stacked.
- `Skill(bitwarden-code-review:addressing-code-review-comments)` — how to evaluate lower-layer feedback in Step 5. Ships with `bitwarden-code-review`; if that plugin is absent, evaluate the feedback without it rather than stopping.
