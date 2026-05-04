---
name: generating-review-storybook
description: Generate a multi-file static "review storybook" website that walks human reviewers through a stack of pull requests one screen at a time, optimized for triage speed against AI-generated PR fatigue. Use whenever the user wants to create a code-review storybook, build a reviewer-friendly walkthrough of stacked PRs or commits, reduce reviewer cognitive load, or speed up a stack review. Triggers on "review storybook", "PR walkthrough", "stack walkthrough", "reviewer storybook", "AI PR review tool", "make these PRs easier to review", or any time the user wants to package a stack for human review.
---

# Generating a Review Storybook

You are packaging a stack of PRs (or commits) into a self-contained HTML walkthrough that a reviewer can open by double-clicking. Verdict-first, diffs as drill-down, copy-as-Markdown handoffs. The artifact is bundled in `assets/template/` — your job is to interview the user, build a config, and run the scaffolder.

**What the storybook is for.** A human reviewing AI-written code. The PR/commit stack itself is the thing under review — the storybook just packages it for fast triage. Claude findings (from `bitwarden-code-review:code-review-local`) are an optional pre-baking step that populates the per-PR Findings section; without them, every PR shows as `pending` and the reviewer drives the decision unaided. Existing human reviewer comments on the GitHub PR are not pulled in — those stay in the GitHub UI.

**Core principle:** The scaffolder is deterministic. Your job is synthesis: ask the user enough to fill the config faithfully, then let `scripts/scaffold.py` render the artifact.

## When to Use

Use when the user wants:

- A "storybook", "walkthrough", "PR-fatigue tool", "reviewer guide", or "stack review packet" for 2+ PRs or commits.
- To pre-package a stack so a reviewer can decide quickly.
- Verdicts surfaced before diffs.

## When NOT to Use

- **A single PR review** — that's `bitwarden-code-review:code-review` or `code-review-local`, not this skill.
- **Posting comments to GitHub** — the storybook is a local artifact; reviewer notes export as Markdown.
- **Generating per-PR review verdicts from scratch** — this skill consumes verdicts; it does not produce them. To get verdicts, run code review first (manually or via the bitwarden-code-review agent), then feed the resulting `review-summary.md` files in via `parse_review_md.py`.

## Inputs You Need from the User

Ask only what you don't already have. Reasonable defaults exist for most fields.

- **Stack list** — PR numbers (in stack order) or commit SHAs. Required.
- **GitHub repo** — `owner/name` (defaults to `bitwarden/server`). Ask if not obvious from context.
- **Title and short summary** — one line + 2–3 sentences for the cover. Synthesize from PR titles if the user doesn't dictate one.
- **Tickets per PR** — Jira keys (optional). Lifts the "Why this exists" framing.
- **Verdicts** (optional, three modes — see below).

## Verdict Modes

| Mode          | Trigger                          | Action                                                                                                         |
| ------------- | -------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Pending       | No reviews exist yet (default)   | Set every PR's `verdict` to `pending`. Cover and per-page cards show "Pending review."                         |
| Pre-baked     | User has review markdown files   | Run `python scripts/parse_review_md.py KEY=path ...` and merge the result into the stack config.               |
| Inline review | User wants reviews generated now | Out of scope for v1 — instead, run `bitwarden-code-review:code-review-local` per PR first, then use Pre-baked. |

## Workflow

1. **Interview the user.** Confirm stack list, repo, title, and verdict mode. Don't ask about defaults you can fill yourself.

2. **Capture diffs.** For each PR/commit, run:

   ```bash
   python scripts/capture_diffs.py --repo <owner/name> pr 1234 2345 ...
   # or for commits:
   python scripts/capture_diffs.py commit a1b2c3 d4e5f6
   ```

   Pipe the output into a temp file (e.g. `/tmp/diffs.json`).

3. **(Pre-baked mode only) Parse review verdicts.**

   ```bash
   python scripts/parse_review_md.py 1234=reviews/pr-1234.md 2345=reviews/pr-2345.md \
     --output /tmp/verdicts.json
   ```

4. **Compose the config JSON.** See `references/data-schema.md` for the shape. Save to `/tmp/storybook.json`. Inline diffs from step 2 into each stack item's `diff_b64` field; merge verdicts from step 3 into each item's `verdict`, `verdict_label`, and `findings`.

5. **Run the scaffolder.**

   ```bash
   python scripts/scaffold.py --config /tmp/storybook.json
   ```

   By default the storybook is written to `$CLAUDE_PLUGIN_DATA/storybooks/<slug>-<timestamp>/`. The script prints the `file://` URL — share that with the user. Pass `--output <dir>` only if the user explicitly asks for a different location.

6. **Verify locally.** Open the printed URL. Sanity-check: cover renders with the right title; each PR has a page; per-PR Findings section lists items when verdicts were pre-baked; export-notes copies Markdown.

## Output Location Convention

- **Default:** `$CLAUDE_PLUGIN_DATA/storybooks/<slug>-<timestamp>/`. The slug is derived from the config `title` (or override via `slug` field). The timestamp keeps successive regenerations of the same stack from clobbering each other.
- **Don't override** unless the user asks. Keeping artifacts under `CLAUDE_PLUGIN_DATA` makes them easy to find, keeps them out of the repo, and survives `git clean`.

## Customization

For brand overrides, language imports, and storage-prefix hygiene, see `references/customization.md`.

## Verification Checklist

Before reporting "done":

- [ ] `index.html` opens and the cover renders.
- [ ] Per-PR pages count = stack size; each has its diff.
- [ ] Verdicts on the cover match what the user expects (pending / approve / approve-fix / block).
- [ ] Inline-comment +/save flow works on at least one diff line.
- [ ] Export-notes button copies the running tally as Markdown.

If any of these fail, do not claim success — fix and re-run scaffold.

## Anti-Patterns

- **Don't hand-edit the generated `data.js`** — it is regenerated on every scaffold run. Edit the config, re-run.
- **Don't bundle verdicts you can't justify.** If review files don't exist, leave verdicts as `pending`. The cover visibly signals that and the reviewer expects it.
