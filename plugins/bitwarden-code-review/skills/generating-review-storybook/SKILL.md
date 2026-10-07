---
name: generating-review-storybook
description: Generate a static, double-clickable "review storybook" that walks human reviewers through a stack of pull requests or commits one screen at a time, verdict first with diffs as drill-down. Use when the user wants a review storybook, a PR or stack walkthrough, or to make a stack of AI-written PRs faster to review. Not for reviewing a single PR (use code-review-local).
---

# Generating a Review Storybook

Package a stack of PRs (or commits) into a static HTML walkthrough that a reviewer can open by double-clicking. Verdict-first, diffs as drill-down, copy-as-Markdown handoffs. The artifact is bundled in `assets/template/`; interview the user, build a config, and run the scaffolder.

The page loads the Prism highlighter from jsDelivr, pinned by integrity hash, and the Inter font from Google Fonts. Its Content-Security-Policy admits only those sources and blocks every outbound connection and form submission, so the private diffs and notes it holds stay in the browser.

**What the storybook is for.** A human reviewing AI-written code. The PR/commit stack itself is the thing under review; the storybook just packages it for fast triage. Claude findings (from `performing-multi-agent-code-review` or `bitwarden-code-review:code-review-local`) are an optional pre-baking step that populates each PR's verdict and inline findings; without them, every PR shows as `pending` and the reviewer drives the decision unaided. Existing human reviewer threads from the GitHub PR can be pulled in optionally via `${CLAUDE_SKILL_DIR}/scripts/fetch_pr_threads.py` and rendered inline at the diff line they reference.

**Core principle:** The scaffolder is deterministic. Synthesis is the judgment step: ask the user enough to fill the config faithfully, then let `${CLAUDE_SKILL_DIR}/scripts/scaffold.py` render the artifact.

## When to Use

Use when the user wants:

- A "storybook", "walkthrough", "PR-fatigue tool", "reviewer guide", or "stack review packet" for 2+ PRs or commits.
- To pre-package a stack so a reviewer can decide quickly.
- Verdicts surfaced before diffs.

## When NOT to Use

- **A single PR review**: that's `bitwarden-code-review:code-review` or `code-review-local`, not this skill.
- **Posting comments to GitHub**: the storybook is a local artifact; reviewer notes export as Markdown.
- **Generating per-PR review verdicts from scratch**: this skill consumes verdicts; it does not produce them. To get verdicts, run code review first, then read the review files per **Reading Review Files** below.

## Inputs You Need from the User

Ask only what you don't already have. Reasonable defaults exist for most fields.

- **Stack list**: PR numbers (in stack order) or commit SHAs. Required.
- **GitHub repo**: `owner/name` (defaults to `bitwarden/server`). Ask if not obvious from context.
- **Title and short summary**: one line + 2-3 sentences for the cover. Synthesize from PR titles if the user doesn't dictate one.
- **Tickets per PR**: Jira keys (optional). Lifts the "Why this exists" framing.
- **Verdicts** (optional, three modes; see below).

## Verdict Modes

| Mode          | Trigger                          | Action                                                                                                                  |
| ------------- | -------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Pending       | No reviews exist yet (default)   | Set every PR's `verdict` to `pending`. Cover and per-page cards show "Pending review."                                  |
| Pre-baked     | User has review files            | Read each PR's review file, then write its verdict and its findings into the stack config per **Reading Review Files**. |
| Inline review | User wants reviews generated now | Out of scope for v1. Instead, run `bitwarden-code-review:code-review-local` per PR first, then use Pre-baked.           |

## Reading Review Files

Two review outputs feed Pre-baked mode, and neither leaves a per-PR file in the working directory on its own:

- **Multi-agent reports** from `performing-multi-agent-code-review` are written to `${CLAUDE_PLUGIN_DATA}/code-reviews/` as `code-review-{model}-PR-{number}.md`, one per PR. If more than one model reviewed a PR, ask which report to use.
- **Single-agent summaries** from `/code-review-local` are written to `review-summary.md` in the working directory, and each run overwrites the last. Copy each PR's summary to a per-PR file before reviewing the next PR.

Read each PR's review file yourself and fill that stack item's `verdict`, `verdict_note`, and `findings`. Leave `verdict_label` unset so the scaffolder derives it.

**Verdict.** Take it as the review states it:

- A summary's `**Overall Assessment:**` line: REQUEST CHANGES is `block`; APPROVE is `approve-fix` when the summary has a critical or important finding, otherwise `approve`; NO VERDICT is `no-verdict`, with the reason sentences beneath it as `verdict_note`.
- A multi-agent report has no assessment line. Its Summary severity table is the verdict: any Blocker is `block`, otherwise any Important is `approve-fix`, otherwise `approve`.
- A `**Not covered:**` line in either format goes into `verdict_note`, without the label, so the gap shows on that PR.
- A PR with no review file stays `pending`. Never infer a verdict from anything else.

**Findings.** Add one `findings.items[]` entry per reported finding and set the counts to match. Severities map as follows:

| Review severity            | Storybook `severity` |
| -------------------------- | -------------------- |
| 🛑 Blocker, ❌ CRITICAL    | `critical`           |
| ⚠️ Important, ⚠️ IMPORTANT | `important`          |
| ♻️ Refactor, ♻️ DEBT       | `debt`               |
| 🎨 SUGGESTED               | `suggested`          |
| ❓ QUESTION                | `question`           |

- `message`: the finding's one-line summary (the bullet text in a summary, the `####` heading in a report).
- `location`: the `path:line` in backticks, copied exactly, path and line both. Inline anchoring needs an exact match to a file path and line in the diff, so a shortened path or a corrected line will not land.
- `suggestion`: a sentence or two from the finding's Details block in a report; empty when the review gives none.
- Skip everything under a report's `## Reviewed and Dismissed` section. Those findings were rejected.

## Workflow

1. **Interview the user.** Confirm stack list, repo, title, and verdict mode. Don't ask about defaults you can fill yourself.

2. **Capture diffs.** For each PR/commit, run:

   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/capture_diffs.py" --repo <owner/name> pr 1234 2345 ...
   # or for commits:
   python3 "${CLAUDE_SKILL_DIR}/scripts/capture_diffs.py" commit a1b2c3 d4e5f6
   ```

   Pipe the output into a temp file (e.g. `/tmp/diffs.json`).

3. **(Pre-baked mode only) Read the review files.** Locate each PR's review file, then read it per **Reading Review Files**.

4. **(Optional) Pull human reviewer comments.** When the user wants existing GitHub review threads inlined alongside Claude findings, run for each PR:

   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/fetch_pr_threads.py" --repo <owner/name> --pr 1234 --key 1234 \
     --output /tmp/threads-1234.json
   ```

   The output is a `{ key: [...comments] }` map ready to merge into each stack item's `comments[]`. Outdated threads are skipped by default; resolved threads are kept with a `_(resolved)_` suffix so the reviewer can see "this was caught and fixed" context. See `references/data-schema.md` for the comment shape.

5. **Synthesize chapters.** Read the PR body and skim the file list. Break each PR into 2-5 logical chapters that walk the reviewer through the change in a meaningful order, not alphabetical. Each chapter declares a `title`, a `narrative` paragraph that says what this chapter is _about_ (not what each file does), and the `paths[]` that belong to it. Tests usually go in the same chapter as the code they cover. If you can't articulate a narrative for a group, that's a sign the grouping is wrong. **Skip this step only when the PR is genuinely a single concern**. Even then, one chapter with a real narrative beats a flat file list. When a chapter has more files than one screen holds, or reads best as ordered steps (contract, then implementation, then tests), split it into `scenes[]` so each step gets its own page; the scenes subsection of `references/data-schema.md` covers the shape, and `examples/storybook.json` shows a chapter split this way.

6. **Compose the config JSON.** See `references/data-schema.md` for the shape. Save to `/tmp/storybook.json`. Inline diffs from step 2 into each stack item's `diff_b64` field; write each item's `verdict`, `verdict_note`, and `findings` from step 3; attach the chapters from step 5 as `stack[i].chapters`.

7. **Run the scaffolder.**

   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/scaffold.py" --config /tmp/storybook.json \
     --output-root "${CLAUDE_PLUGIN_DATA}/storybooks"
   ```

   The storybook is written to a new `<slug>-<timestamp>/` directory under the output root. The script prints the `file://` URL; share that with the user. Pass `--output <dir>` in place of `--output-root` only if the user explicitly asks for a different location; it writes to that exact directory.

8. **Verify locally.** Open the printed URL. Sanity-check: cover renders with the right title; each PR walks through chapters in a logical order with real narrative; AI findings and human comments (if any) appear inline at the diff line they reference; export-notes copies Markdown.

## Output Location Convention

- **Default:** `${CLAUDE_PLUGIN_DATA}/storybooks/<slug>-<timestamp>/`, passed to the scaffolder as `--output-root "${CLAUDE_PLUGIN_DATA}/storybooks"`. The plugin data path is only substituted into this skill's text, never exported to the shell, so the scaffolder needs it as an argument. The slug is derived from the config `title` (or override via `slug` field). The timestamp keeps successive regenerations of the same stack from clobbering each other.
- **Don't override** unless the user asks. Keeping artifacts under the plugin data directory makes them easy to find, keeps them out of the repo, and survives `git clean`.

## Customization

For brand overrides, language imports, and storage-prefix hygiene, see `references/customization.md`.

## Verification Checklist

Before reporting "done":

- [ ] `index.html` opens and the cover renders.
- [ ] Every PR has at least one page, and each page shows its diff.
- [ ] Every changed file appears exactly once. An "Other files" group means a chapter missed paths; add them to the right chapter and re-run.
- [ ] Per-PR walkthrough is grouped into chapters with narrative, not a flat alphabetical file list.
- [ ] Verdicts on the cover match what the user expects (pending / approve / approve-fix / block / no-verdict), and every coverage gap the reviews reported shows on its PR.
- [ ] Inline-comment +/save flow works on at least one diff line.
- [ ] Export-notes button copies the running tally as Markdown.

If any of these fail, do not claim success. Fix and re-run scaffold.

## Anti-Patterns

- **Don't hand-edit the generated `data.js`**: it is regenerated on every scaffold run. Edit the config, re-run.
- **Don't bundle verdicts you can't justify.** If review files don't exist, leave verdicts as `pending`. The cover visibly signals that and the reviewer expects it.
