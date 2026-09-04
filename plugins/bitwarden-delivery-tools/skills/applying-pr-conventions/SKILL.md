---
name: applying-pr-conventions
description: "Compose the three conventions a Bitwarden pull request needs — a title carrying the conventional commit type prefix that drives the t: label, a body following the repo's PR template, and an AI review label decision. Mostly invoked by another delivery skill: once for a single branch, once per layer of a stack, or once at the pilot target of a fan-out. Returns those three values and nothing else — it never runs a code review, never shows a submission preview, and never pushes or creates a pull request. Not for actually opening a pull request (that is creating-pull-request), a chain of dependent pull requests (stacking-pull-requests), or a fan-out across repositories (force-multiplier)."
---

# Applying Bitwarden's Pull Request Conventions

Bitwarden pull requests depend on three signals that are easy to forget and hard to fix after submission:

- the **conventional commit type prefix** in the title (CI reads it to apply the `t:` label),
- the **repo's PR template** (reviewers use its sections to orient),
- the **AI review label** (routes the PR to specific automation).

Missing any one is silent — CI will not reject the PR, and the reviewer just becomes confused.

This skill produces those three values for one pull request. It does not decide when they are used. Reviewing, previewing, pushing, and creating belong to whichever workflow invoked it, so the same conventions apply identically to a single branch, to every layer of a stack, and to every target of a fan-out.

**What you get back:** a title string, a body string, and a label choice. Hand all three to the caller. Do not run `git push`, `gh pr create`, or `gh pr edit` from here, and do not show a submission preview — the caller's preview is the catch-net, and a second one here either duplicates it or contradicts it.

## 1 — Determine the change type and propose the title

The title must follow this exact format:

```
[PM-XXXXX] <type>: <short imperative summary>
```

The `<type>:` prefix is what CI scans (lowercased) to assign the `t:` label. Without it the PR ships with no type label and triage cannot filter it. Read `${CLAUDE_PLUGIN_ROOT}/references/change-type-labels.md` to pick the keyword.

If the Jira ticket key is not in the branch name or recent conversation, ask the user. Do not leave `PM-XXXXX` as a placeholder — a real ticket key is required for tracking links to resolve.

**Show the proposed title to the user before continuing.** This is the first chance to catch typos, a missing prefix, or the wrong ticket key.

## 2 — Read the repo's PR template and draft the body

Always read `.github/PULL_REQUEST_TEMPLATE.md` from the target repo before drafting. Even with a body draft in mind, the template's sections are what reviewers expect to scan. Skipping this is a common failure mode — PRs ship with improvised bodies missing sections reviewers depend on.

If the template exists:

- use its sections verbatim as the body structure,
- fill each section based on the actual change,
- keep section headers (e.g. `## 🎟️ Tracking`, `## 📔 Objective`) — they are load-bearing for reviewer scanning,
- delete sections that do not apply (Screenshots with no UI change, for example), unless the template comments say to leave them.

If no template exists, fall back to:

```markdown
## 🎟️ Tracking

<!-- Link to the Jira issue or GitHub issue this change comes from. -->

## 📔 Objective

<!-- Describe what this PR accomplishes — what bug, what feature, what refactor. -->

## 📸 Screenshots

<!-- Required for UI changes; delete if not applicable. -->
```

**The caller may hand you review outcomes to record.** A skipped code review, and every deferred CRITICAL or IMPORTANT finding, goes in the Objective section. Write whatever the caller passes; do not go looking for review results yourself, and do not assert a review happened when the caller said nothing about one.

## 3 — Ask about the AI review label

Use the `AskUserQuestion` tool:

- **Question**: "Would you like to add an AI review label to this PR?"
- **Options**: `ai-review`, `ai-review-vnext`, `No label`

Return the answer to the caller. **Ask this once per decision, not once per invocation** — see below.

## Applying these across more than one pull request

Two callers do this, and they do it differently. `stacking-pull-requests` invokes this **once per layer**, because each layer states its own position in the chain and picks its own type keyword. `force-multiplier` invokes it **once, at its pilot target**, then replicates the confirmed pattern across the fan-out without invoking again — it cannot answer an interactive prompt dozens of times, and the whole point of its pilot is to settle one pattern.

For the per-layer case:

- **Compose the title and body per unit.**
- **Ask the label question once**, on the first invocation, and have the caller carry the answer into the rest. A caller that asks per layer is asking the same question N times and can end up with a stack whose layers disagree.
- **Take the ticket key as given** across the set. One ticket normally spans a whole stack, and the key repeats on every layer.
- **Choose the type keyword per unit.** It is a property of what that layer or target actually changes, not of the set — a stack often mixes `feat` and `refactor`.

If the caller has already settled the label for the set, skip step 3 entirely rather than re-asking.

## Common failure modes

These are what a caller's submission preview is built to catch. Recognizing them helps while composing:

- **Title with no type prefix** → `[PM-12345] Add autofill for passkeys` ships with no `t:` label. Include `feat:`, `fix:`, etc.
- **Generic body replacing the template** → reviewers expect the template's sections. Read the template even when the body feels obvious.
- **`PM-XXXXX` left as a placeholder** → tracking links will not resolve.
- **The label answer getting dropped** between here and submission — return it explicitly rather than assuming the caller remembers it.

Recovery after submission is awkward: the title is permanent in the merge commit, and labels feed downstream filtering and automation.

## Related skills

- `Skill(creating-pull-request)` — the single-branch workflow that reviews, previews, and submits around these conventions.
- `Skill(stacking-pull-requests)` — applies them per layer of a stack, with one whole-stack preview.
- `Skill(force-multiplier)` — applies them once at a pilot target, then replicates across a fan-out.
- `Skill(labeling-changes)` — the conventional commit keyword reference behind step 1.
