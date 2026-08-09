---
name: creating-pull-request
description: Open a pull request from a branch in a Bitwarden repository — pick the conventional commit type prefix that drives the t: label, fill in the repo's PR template, choose an ai-review label, and confirm a full submission preview before running gh pr create.
when_to_use: Use when the user is ready to open a pull request from a branch — phrasings like "create a PR", "open a PR", "ship a draft", "put it up for review", "ready for review", or "ship it". Also use when drafting a PR title or body, picking the conventional commit type prefix, or choosing the t: or ai-review label for a PR being opened (takes precedence over labeling-changes in PR-creation contexts). Do not use for conceptual questions ("how do PRs work") or managing existing PRs (status, merging, addressing comments).
---

# Creating a Pull Request

This workflow exists because Bitwarden PRs depend on three signals that are easy to forget and hard to fix after submission:

- the **conventional commit type prefix** in the title (CI reads it to apply the `t:` label),
- the **repo's PR template** (reviewers use its sections to orient),
- the **AI review label** (routes the PR to specific automation).

Missing any one of these is silent — CI won't reject the PR, and the reviewer just becomes confused. So this workflow surfaces each decision step by step and shows a full submission preview before anything is pushed, so slip-ups are caught while they're cheap to fix.

## Workflow

Follow these steps in order. Each one produces information the next step needs, and the preview in Step 5 depends on all of them.

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
  - `Substantial` — architectural, cross-cutting, or security-touching: run `Skill(performing-multi-agent-code-review)`, telling it to review the full branch diff against `origin/HEAD` (not just uncommitted changes); there is no PR yet

Present only these two options; do not add a skip option. Honor a skip only if the user volunteers one unprompted, then record it in the PR body's Objective section (Step 3) and surface it in the Step 5 preview. Never skip on your own initiative.

After the review:

- Address every CRITICAL and IMPORTANT finding, or record why each is deferred in the PR body's Objective section (Step 3).
- On the `Substantial` path only, you may re-run `Skill(performing-multi-agent-code-review)` with a different `--model-*` value for the highest-risk changes (auth, crypto, data handling, migrations); findings vary by model, so a second pass can catch what the first missed. Optional, never required.
- If a review path wrote output into the repo, remove it before pushing so it never lands in a commit — but only files this run created (a `??` in `git status --porcelain`). For example, `code-review-local` writes `review-summary.md` and `review-inline-comments.md` to the working-directory root; the multi-agent path writes outside the repo and needs no cleanup. Never delete a tracked file of the same name.

Each review path checks its own prerequisites and reports what to install if something is missing. If a path can't run, install what it reports or fall back to the other path and note the limitation in the PR body. If neither path is available, stop and prompt the user to install `bitwarden-code-review` (`/plugin install bitwarden-code-review@bitwarden-marketplace`) before continuing. Never silently skip the review.

When `creating-pull-request` runs as a step inside another delivery skill's workflow (for example a bulk campaign or a prototype PR), that workflow owns whether and how a review runs; skip this gate. Today neither in-plugin caller runs a review — wiring it in is a tracked follow-up.

### Step 2 — Determine change type and propose the title

The title must follow this exact format:

```
[PM-XXXXX] <type>: <short imperative summary>
```

The `<type>:` prefix is what CI scans (lowercased) to assign the `t:` label. Without it, the PR ships with no type label and triage can't filter it. Read `${CLAUDE_PLUGIN_ROOT}/references/change-type-labels.md` to pick the right keyword.

If the Jira ticket key isn't in the branch name or recent conversation, ask the user. Don't leave `PM-XXXXX` as a placeholder — a real ticket key is required for tracking links to resolve.

**Show the proposed title to the user before continuing.** This is the first chance for them to catch typos, a missing prefix, or the wrong ticket key.

### Step 3 — Read the repo's PR template

Always read `.github/PULL_REQUEST_TEMPLATE.md` from the target repo before drafting the body. Even when you have a body draft in mind, the template's sections are what other reviewers expect to scan. Skipping this is a common failure mode — PRs ship with improvised bodies that miss sections reviewers depend on.

If the template exists:

- use its sections verbatim as the body structure,
- fill each section based on the actual change,
- keep section headers (e.g. `## 🎟️ Tracking`, `## 📔 Objective`) — they're load-bearing for reviewer scanning,
- delete sections that don't apply (Screenshots with no UI change, for example), unless the template comments say to leave them.

If no template exists, fall back to:

```markdown
## 🎟️ Tracking

<!-- Link to the Jira issue or GitHub issue this change comes from. -->

## 📔 Objective

<!-- Describe what this PR accomplishes — what bug, what feature, what refactor. -->

## 📸 Screenshots

<!-- Required for UI changes; delete if not applicable. -->
```

### Step 4 — Ask about the AI review label

Use the `AskUserQuestion` tool to ask:

- **Question**: "Would you like to add an AI review label to this PR?"
- **Options**: `ai-review`, `ai-review-vnext`, `No label`

Capture the answer. You'll surface it in Step 5 and pass it on the command line in Step 6.

### Step 5 — Show the full submission preview, then confirm

This is the most important step in this workflow. **Before running any `git push` or `gh pr create`, show the user a single preview block containing every decision made above.** This is the catch-net for failure modes like title typos, missing type prefix, body drifting from the template, or the AI review label getting dropped between Step 4 and submission.

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
  - `Submit as shown` — proceed to Step 6 with the previewed values
  - `Edit title or body` — apply the requested edit, then redisplay the preview and re-ask
  - `Change ai-review label` — re-run the Step 4 label question, then redisplay the preview and re-ask
  - `Cancel` — stop without pushing or creating the PR

Only continue to Step 6 when the user selects `Submit as shown`. The recap is non-negotiable — some failures (title in the merge commit, label-driven automation routing) are painful to undo once the PR is live, so a visible chance to catch issues at submission time pays for itself many times over.

### Step 6 — Push and create

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
- include `--label` only if the user picked a label in Step 4 (omit it for "No label"),
- multiple labels can be passed by repeating `--label`.

After `gh pr create` returns, post the PR URL back to the user.

## Common Failure Modes

These are what the Step 5 preview is built to prevent. Recognizing them helps when adjusting the draft mid-workflow:

- **Title with no type prefix** → `[PM-12345] Add autofill for passkeys` ships with no `t:` label. Include `feat:`, `fix:`, etc.
- **Generic body replacing the template** → reviewers expect the template's sections. Read the template even when the body feels obvious.
- **Label answer dropped between Step 4 and Step 6** → the recap surfaces it; if it's missing there, it's about to be missing on the PR.
- **`PM-XXXXX` left as a placeholder** → tracking links won't resolve. Catch in Step 2 or Step 5.

If any of these slip past the preview, recovery is awkward — the title is permanent in the merge commit, and labels feed downstream filtering and automation.
