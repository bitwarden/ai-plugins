---
name: creating-pull-request
description: "Open a pull request from a branch in a Bitwarden repository — pick the conventional commit type prefix that drives the t: label, fill in the repo's PR template, choose an ai-review label, and confirm a full submission preview before running gh pr create. Not for a chain of dependent pull requests (that is stacking-pull-requests)."
when_to_use: 'Use when the user is ready to open a pull request from a branch — phrasings like "create a PR", "open a PR", "ship a draft", "put it up for review", "ready for review", or "ship it". Also use when drafting a PR title or body, picking the conventional commit type prefix, or choosing the t: or ai-review label for a PR being opened (takes precedence over labeling-changes in PR-creation contexts). Do not use for a chain of dependent pull requests (that is stacking-pull-requests), conceptual questions ("how do PRs work"), or managing existing PRs (status, merging, addressing comments).'
---

# Creating a Pull Request

This workflow exists because Bitwarden PRs depend on three signals that are easy to forget and hard to fix after submission:

- the **conventional commit type prefix** in the title (CI reads it to apply the `t:` label),
- the **repo's PR template** (reviewers use its sections to orient),
- the **AI review label** (routes the PR to specific automation).

Missing any one of these is silent — CI won't reject the PR, and the reviewer just becomes confused. So this workflow surfaces each decision step by step and shows a full submission preview before anything is pushed, so slip-ups are caught while they're cheap to fix.

## Workflow

Follow these steps in order. Each one produces information the next step needs, and the preview in Step 3 depends on all of them.

**First, is this one pull request or a stack?** A request for a chain of dependent pull requests belongs to `Skill(stacking-pull-requests)` — hand off.

One exception, and it is the reverse direction: an invocation stating the stack path was already tried and is unavailable for this run — declined, the install failed, or the skill installed but is not resolvable until a restart — is `stacking-pull-requests` handing a single ordinary pull request _here_. Run the whole workflow, gate included; nobody owns the review on that path. Handing it back is the loop this exception exists to prevent.

### Step 1 — Confirm preflight, then run the code-review gate

A PR opened on broken work, or on work that skipped review, wastes reviewer time and buries the real problem under comment threads. Settle preflight first, then run the review.

**1a — Confirm preflight passed.** Use the `AskUserQuestion` tool:

- **Question**: "Has `perform-preflight` passed on this branch?"
- **Options**:
  - `Yes — proceed`
  - `No — run it now` — invoke `perform-preflight`, then continue once it passes

If preflight cannot be made to pass, stop and report the failure rather than opening the PR. Only ask 1b once preflight is green: running preflight can change code, and the review should see the final diff.

**1b — Run the code review, matched to the change's blast radius.** A local code review is a required gate before opening a PR. Use the `AskUserQuestion` tool:

- **Question**: "How deep is this change? (sets review depth)"
- **Options**:
  - `Standard` — a typical feature, fix, docs, or config change: run `/bitwarden-code-review:code-review-local` (tell it to review the current branch's changes; there is no PR yet)
  - `Substantial` — architectural, cross-cutting, or security-touching: run `Skill(performing-multi-agent-code-review)`, telling it to review the full branch diff against the base ref (not just uncommitted changes); there is no PR yet

The base ref is `origin/HEAD` for a branch cut from trunk, and the release branch itself — `origin/rc`, `origin/hotfix-rc` — for a branch cut from one; Step 4 keys `--base` on the same distinction. `Standard` resolves `origin/HEAD` unconditionally, so on a release-cut branch its three-dot diff takes the merge base with trunk and sweeps in every already-merged commit that release branch carries. Use `Substantial` with the explicit range there, or record in the PR body that the review was not base-scoped. When `stacking-pull-requests` is driving this per layer, the review has to be scoped to that layer or it re-reviews every layer below. Only `Substantial` can be scoped: use its commit-range mode with the explicit range `<parent-branch>..<layer-head>`. `Standard` resolves `origin/HEAD` itself and takes no base ref, so on any layer above the bottom its diff reaches below the layer. Say so when asking — name `Substantial` as the layer-scoped option — and if the user picks `Standard` anyway, record in that layer's PR body that the review was not layer-scoped.

Present only these two options; do not add a skip option. Honor a skip only if the user volunteers one unprompted, then record it in the PR body's Objective section (Step 2) and surface it in the Step 3 preview. Never skip on your own initiative.

After the review:

- Address every CRITICAL and IMPORTANT finding, or record why each is deferred in the PR body's Objective section (Step 2).
- On the `Substantial` path only, you may re-run `Skill(performing-multi-agent-code-review)` with a different `--model-*` value for the highest-risk changes (auth, crypto, data handling, migrations); findings vary by model, so a second pass can catch what the first missed. Optional, never required.
- If a review path wrote output into the repo, remove it before pushing so it never lands in a commit — but only files this run created (a `??` in `git status --porcelain`). For example, `code-review-local` writes `review-summary.md` and `review-inline-comments.md` to the working-directory root; the multi-agent path writes outside the repo and needs no cleanup. Never delete a tracked file of the same name.

Each review path checks its own prerequisites and reports what to install if something is missing. If a path can't run, install what it reports or fall back to the other path and note the limitation in the PR body. If neither path is available, stop and prompt the user to install `bitwarden-code-review` (`/plugin install bitwarden-code-review@bitwarden-marketplace`) before continuing. Never silently skip the review.

**One thing another delivery skill may do with this step:** run 1b alone. `stacking-pull-requests` does, once per layer, because the review gate is per pull request and a stack has N of them. It runs `perform-preflight` itself per layer, so do not also run 1a, and return after 1b rather than continuing into Step 2.

Otherwise the gate runs on every entry, including the stack-fallback case above — that path bailed before its own gate, so nobody owns the review.

Skills wanting the title, body, and label rather than this gate should invoke `Skill(applying-pr-conventions)` directly; it is a peer of this workflow, not a step inside it. That is the whole of `force-multiplier`'s use, which is why it no longer enters here at all and why there is no longer a way to skip this gate.

### Step 2 — Compose the title, body, and label

Invoke `Skill(applying-pr-conventions)`. It owns all three: the `[PM-XXXXX] <type>: <summary>` title and the type keyword behind the `t:` label, the body built from the repo's `.github/PULL_REQUEST_TEMPLATE.md`, and the `ai-review` label question.

Pass it what Step 1 produced, since it does not go looking for review results itself: the review path taken, any skip the user volunteered, and every deferred CRITICAL or IMPORTANT finding. Those go into the body's Objective section.

Carry back the title, the body, and the label choice — Step 3's preview shows all three and Step 4 submits them.

### Step 3 — Show the full submission preview, then confirm

This is the most important step in this workflow. **Before running any `git push` or `gh pr create`, show the user a single preview block containing every decision made above.** This is the catch-net for failure modes like title typos, missing type prefix, body drifting from the template, or the AI review label getting dropped between Step 2 and submission.

Use this exact format:

```
═══════════════════════════════════════
  PULL REQUEST SUBMISSION PREVIEW
═══════════════════════════════════════
Target repo:    <owner/repo>
Branch:         <branch-name>
Draft:          <Yes / No>
Title:          <full title as it will be submitted>
Type prefix:    <type>  →  will apply  t:<label>
AI review:      <ai-review / ai-review-vnext / No label>
Code review:    <Standard | Substantial | Skipped (user request)>  →  <N deferred findings recorded>

Body:
---
<full body, exactly as it will be submitted>
---
═══════════════════════════════════════
```

Then use the `AskUserQuestion` tool to confirm:

- **Question**: "Submit this PR as previewed?"
- **Options**:
  - `Submit as shown` — proceed to Step 4 with the previewed values
  - `Edit title or body` — apply the requested edit, then redisplay the preview and re-ask
  - `Change ai-review label` — re-run the label question from `Skill(applying-pr-conventions)`, then redisplay the preview and re-ask
  - `Cancel` — stop without pushing or creating the PR

Only continue to Step 4 when the user selects `Submit as shown`. The recap is non-negotiable — some failures (title in the merge commit, label-driven automation routing) are painful to undo once the PR is live, so a visible chance to catch issues at submission time pays for itself many times over.

### Step 4 — Push and create

Push the branch and run `gh pr create` with the confirmed values. Pass the body via `--body-file`, not `--body`: the body carries model- and review-generated text (derived from untrusted repo content), and interpolating it into a double-quoted shell argument would let backticks or `$(…)` execute. Write it to a temp file and hand `gh` the path:

```bash
git push -u origin <branch-name>
# Write the confirmed body to a temp file first (no shell interpolation of its contents).
gh pr create --draft \
  --title "[PM-XXXXX] <type>: <summary>" \
  --body-file "$body_file" \
  --label "<label>"
```

Defaults that hold unless the user said otherwise:

- create as **draft** — only skip `--draft` if the user explicitly asked for a ready-for-review PR,
- include `--label` only if a label was picked in Step 2 (omit it for "No label"),
- multiple labels can be passed by repeating `--label`,
- omit `--base` for a branch cut from trunk, and pass `--base <branch>` when the branch was cut from `rc`, `hotfix-rc`, or another release branch — with no `--base`, `gh pr create` targets the repository default branch and silently points the PR at trunk. Stack layers are submitted by `Skill(stacking-pull-requests)`, which passes each layer's `--base` itself; this step does not run per layer.

After `gh pr create` returns, post the PR URL back to the user.

## Common Failure Modes

These are what the Step 3 preview is built to prevent. Recognizing them helps when adjusting the draft mid-workflow:

- **Title with no type prefix** → `[PM-12345] Add autofill for passkeys` ships with no `t:` label. Include `feat:`, `fix:`, etc.
- **Generic body replacing the template** → reviewers expect the template's sections. Read the template even when the body feels obvious.
- **Label answer dropped between Step 2 and Step 4** → the recap surfaces it; if it's missing there, it's about to be missing on the PR.
- **`PM-XXXXX` left as a placeholder** → tracking links won't resolve. Catch in Step 2 or Step 3.

If any of these slip past the preview, recovery is awkward — the title is permanent in the merge commit, and labels feed downstream filtering and automation.
