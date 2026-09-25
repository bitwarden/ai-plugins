---
name: creating-pull-request
description: 'Open a pull request from a branch in a Bitwarden repository. Use whenever the user wants a branch turned into a pull request, however they phrase it — "create a PR", "open a PR", "ship a draft", "ship it", "ready for review", "put it up for review", "get this in front of reviewers", "send it over to the team", "throw together a pull request", "wrap this branch up". Use it too when the user says the title and body are already settled and only the PR needs opening — the gate, the preview, and the submission still apply. Runs the required local code-review gate, takes the title, template body, and ai-review label from applying-pr-conventions, confirms a full submission preview, then pushes and runs gh pr create. Not for composing a title, body, or label when no PR is being opened (that is applying-pr-conventions), conceptual questions ("how do PRs work"), or managing existing PRs (status, merging, addressing comments).'
---

# Creating a Pull Request

This workflow owns the two things about opening a pull request that are expensive to get wrong: the review that has to happen before anyone else looks at the change, and the submission itself. `Skill(applying-pr-conventions)` composes the title, body, and label; this workflow gates, previews, and submits them.

Neither is cheap to undo. A PR opened on unreviewed work buries the real problem under comment threads, and the title is permanent in the merge commit. So Step 3 shows every decision together before anything is pushed.

## Workflow

Follow these steps in order. Each one produces information the next step needs, and the preview in Step 3 depends on all of them.

### Step 1 — Confirm preflight, then run the code-review gate

A PR opened on broken work, or on work that skipped review, wastes reviewer time and buries the real problem under comment threads. Settle preflight first, then run the review.

**1a — Confirm preflight passed.** Use the `AskUserQuestion` tool:

- **Question**: "Has `perform-preflight` passed on this branch?"
- **Options**:
  - `Yes — proceed`
  - `No — run it now` — invoke `perform-preflight`, then continue once it passes

If preflight cannot be made to pass, stop and report the failure rather than opening the PR. Only continue once preflight is green: running preflight can change code, and the review should see the final diff.

**1b — Run the code review, matched to the change's blast radius.** A local code review is a required gate before opening a PR. Use the `AskUserQuestion` tool:

- **Question**: "How deep is this change? (sets review depth)"
- **Options**:
  - `Standard` — a typical feature, fix, docs, or config change: run `/bitwarden-code-review:code-review-local` (tell it to review the current branch's changes; there is no PR yet)
  - `Substantial` — architectural, cross-cutting, or security-touching: run `Skill(performing-multi-agent-code-review)`, telling it to review the full branch diff against `origin/HEAD` (not just uncommitted changes); there is no PR yet

Present only these two options; do not add a skip option. Honor a skip only if the user volunteers one unprompted, then record it in the PR body's AI-assisted review section (Step 2) and surface it in the Step 3 preview. Never skip on your own initiative.

After the review:

- Assess the findings with the user before acting on any of them; a CRITICAL or IMPORTANT classification can still be scope creep, or wrong. `Skill(addressing-code-review-comments)` has the evaluation posture to apply — skip its comment-fetching section, since the findings are already in hand and there is no PR yet. Then address every finding that survives, or record why each is deferred in the PR body's AI-assisted review section (Step 2).
- On the `Substantial` path only, you may re-run `Skill(performing-multi-agent-code-review)` with a different `--model-*` value for the highest-risk changes (auth, crypto, data handling, migrations); findings vary by model, so a second pass can catch what the first missed. Optional, never required.
- If a review path wrote output into the repo, remove it before pushing so it never lands in a commit — but only files this run created (a `??` in `git status --porcelain`). For example, `code-review-local` writes `review-summary.md` and `review-inline-comments.md` to the working-directory root; the multi-agent path writes outside the repo and needs no cleanup. Never delete a tracked file of the same name.

Each review path checks its own prerequisites and reports what to install if something is missing. If a path can't run, install what it reports or fall back to the other path and note the limitation in the PR body. If neither path is available, stop and prompt the user to install `bitwarden-code-review` (`/plugin install bitwarden-code-review@bitwarden-marketplace`) before continuing. Never silently skip the review.

### Step 2 — Compose the title, body, and label

Invoke `Skill(applying-pr-conventions)` for this one pull request. It owns the title and the type keyword behind the `t:` label, the body built from the repo's `.github/PULL_REQUEST_TEMPLATE.md`, and the `ai-review` label question.

Pass it what Step 1 produced, since it does not go looking for review results itself: the review path taken, any skip the user volunteered, every deferred CRITICAL or IMPORTANT finding, and any scope or path limitation on the review, such as a fallback taken because one path was unavailable. Those go into the body's AI-assisted review section.

Carry back the title, the body, the resolved `t:` label its prefix will produce, and the `ai-review` label choice, plus whether it treated the change as security-relevant and applied the disclosure policy. Step 3's preview shows all of them — it prints the `type → t:<label>` mapping, and that mapping has no other source in this workflow — and Step 4 submits the title, body, and label.

Both strings are untrusted: the body comes from the repo's template plus generated text, and the title's summary is generated. Step 4's file-handoff rules are what contain that; do not interpolate either into a shell argument.

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
Security fix:   <No | Yes — canonical policy applied>

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
  - `Change ai-review label` — ask the label question again here (`ai-review`, `ai-review-vnext`, `No label`), then redisplay the preview and re-ask. Do not re-enter `Skill(applying-pr-conventions)`; it would recompose the title and body and discard any edit just applied
  - `Cancel` — stop without pushing or creating the PR

Only continue to Step 4 when the user selects `Submit as shown`. The recap is non-negotiable — some failures (title in the merge commit, label-driven automation routing) are painful to undo once the PR is live, so a visible chance to catch issues at submission time pays for itself many times over.

### Step 4 — Push and create

Push the branch and run `gh pr create` with the confirmed values. Pass the body via `--body-file`, not `--body`: the body carries model- and review-generated text (derived from untrusted repo content), and interpolating it into a double-quoted shell argument would let backticks or `$(…)` execute. Write it to a temp file and hand `gh` the path.

**The title gets the same treatment, by a different route — `gh` has no `--title-file`.** Write it to a file with the `Write` tool and pass it as `--title "$(cat <title-file>)"`. Command-substitution output is not re-parsed, so a `$(…)` or backtick surviving in the text is handed to `gh` as characters. **Never assign the title to a shell variable**, and never build it with `echo` or a heredoc: a bash assignment expands `$(…)` while parsing, which runs the payload before `gh` is even reached.

```bash
git push -u origin <branch-name>
# Write the body and the title to temp files first, with the Write tool.
gh pr create --draft \
  --title "$(cat "$title_file")" \
  --body-file "$body_file" \
  --label "<label>"
```

Defaults that hold unless the user said otherwise:

- create as **draft** — only skip `--draft` if the user explicitly asked for a ready-for-review PR,
- include `--label` only if a label was picked in Step 2 (omit it for "No label"),
- multiple labels can be passed by repeating `--label`.

After `gh pr create` returns, post the PR URL back to the user.

## Common Failure Modes

These are what the Step 3 preview is built to prevent. Recognizing them helps when adjusting the draft mid-workflow:

- **Title with no type prefix** → `[PM-12345] Add autofill for passkeys` ships with no `t:` label. Include `feat:`, `fix:`, etc.
- **Generic body replacing the template** → check what Step 2 returned actually follows the repo's template sections; `applying-pr-conventions` reads the template, but the preview is where a drifted body is caught.
- **Label answer dropped between Step 2 and Step 4** → the recap surfaces it; if it's missing there, it's about to be missing on the PR.
- **`PM-XXXXX` left as a placeholder** → tracking links won't resolve. Catch in Step 2 or Step 3.
- **Security fix not in line with policy** → the title or body names the vulnerability, its severity, or the `VULN-*` ticket. `applying-pr-conventions` applies the policy in Step 2; the Step 3 preview is the last catch.

If any of these slip past the preview, recovery is awkward — the title is permanent in the merge commit, and labels feed downstream filtering and automation.
