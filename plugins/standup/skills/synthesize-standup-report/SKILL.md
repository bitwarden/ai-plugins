---
name: synthesize-standup-report
description: |
  Synthesizes a finished RAG-status standup report from the combined activity
  JSON emitted by generate-standup-report plus the user's resolved preference
  knobs. Produces the final markdown string only -- no delivery, no collection.
  Use when an agent has both the activity JSON and the loaded preferences in
  hand and needs the rendered report text. Delivery is deliver-standup-report's
  job; collection is generate-standup-report's job.
---

# Synthesize Standup Report

This skill consumes the combined activity JSON from `generate-standup-report` and the resolved preference knobs from `~/.claude/standup/preferences.md` (the calling agent loads and supplies these), and produces the finished RAG-status standup report as a markdown string. It performs no file I/O, no API calls, and no delivery.

## Input Contract

The calling agent supplies two inputs:

### 1. Activity JSON

The combined JSON document emitted by `generate-standup-report`. Top-level
shape:

```
{
  "schema_version": "1.0",
  "generated_at": "<ISO-8601>",
  "window": {"start": "...", "end": "...", "input_timeline": "..."},
  "identity": {"atlassian": {...}, "github": {...}},
  "categories": {
    "cat1_authored_prs":     {status, count, items},
    "cat2_reviews_given":    {status, count, items},
    "cat3_jira_done":        {status, count, items},
    "cat4_jira_created":     {status, count, items},
    "cat5_jira_comments":    {status, count, items},
    "cat6_confluence_edits": {status, count, items},
    "cat7_jira_grooming":    {status, count, items, summary},
    "cat8_in_progress":      {status, count, items},
    "cat9_blocked":          {status, count, items}
  }
}
```

Each category: `{status: "ok"|"error", count: int, items: [...], error: str|null}`.
`cat8_in_progress` and `cat9_blocked` are current-state snapshots; they are not
filtered by the time window. `cat7_jira_grooming` carries a qualitative
`summary` object with `fields_by_frequency` (ranked list of field kinds,
most-to-least frequent, no counts) and `top_areas` (up to 6
`{key, summary, parent}` objects for the most-groomed epics). Items in
`cat3_jira_done`, `cat4_jira_created`, `cat8_in_progress`, and `cat9_blocked`
carry a `comments` array (`[{author, created, excerpt}, ...]`, oldest first,
capped at 50 entries). The same `comments` field appears on `linked_ticket`
objects within `cat1_authored_prs` and `cat2_reviews_given` items.

See `generate-standup-report` for the full per-category item schema.

### 2. Resolved Preference Knobs

The calling agent reads `~/.claude/standup/preferences.md` at run start (per
ADR-084, load-on-demand; never auto-loaded) and extracts the following from its
`## Output format` and `## Output style` sections:

| Knob | Source section | What it governs |
|---|---|---|
| Section labels | `## Output format` | Names for the past-highlights / in-progress / blockers sections |
| Markdown-link on/off | `## Output format` | Render Jira/PR references as `[key](url)` or bare keys |
| Highlighted-item cap | `## Output style` | Optional ceiling on the past-highlights section (integer). When absent, no cap applies — include all significant items. |
| Selection pipeline | `## Output style` | Authoritative select → enrich → collapse step detail for `Last week:` |
| Routine-tail collapse on/off | `## Output style` | Whether genuinely-routine automated work collapses into one tail bullet |
| RAG heuristic day-thresholds | `## Output style` | Day-count bands for GREEN / YELLOW / RED classification |
| Name-discipline rule | `## Output style` | Per-report name-use policy (e.g. kudos-only) |

All knobs are supplied by the caller. None of them are hardcoded in this skill.

## Output Contract

This skill emits a single finished markdown string: the RAG-status standup
report. The caller receives the text and is responsible for delivery.

```
:large_green_circle: [SINGLE_SENTENCE_SUMMARY]

`Last week:`
- ...

`This week:`
- ...

`Blockers:`
- ...
```

The RAG emoji and summary line reflect the heuristic applied in Step 1. Section
labels are replaced by the prefs-resolved values. The report is terse, honest,
first-person prose in the voice of the searched user (the `identity.atlassian`
identity in the JSON).

## Synthesis Pipeline

### Step 1 — Apply the RAG Heuristic

Read `cat8_in_progress` and `cat9_blocked` directly for current state. Map them onto the GREEN / YELLOW / RED bands using the day-thresholds from the prefs `## Output style` RAG heuristic — do NOT hardcode day-numbers. Rules:

- Any `cat9_blocked` item nudges toward YELLOW at minimum.
- A heavy or critical blocked load pushes to RED, per prefs bands.
- PR-review staleness and in-progress staleness use the prefs day-thresholds.
- Zero non-empty categories returned is the RED floor.
- When signals are mixed or ambiguous, choose YELLOW over GREEN.

Do NOT infer blocked or in-progress status from in-window activity (cat1–cat7); read it only from cat8/cat9.

### Step 2 — Build `Last week:` (past-highlights section)

Apply the selection pipeline defined in the prefs `## Output style` section in this order — the steps pull against each other, so order is mandatory:

1. **Select globally**: across all in-window activity (cat1–cat7), pick the most significant items. If a highlighted-item cap is set in prefs, treat it as a ceiling — not a target to fill. If absent, apply no cap.
2. **Enrich only the survivors**: attach a short WHAT/WHY clause to each selected item, grounded strictly in that item's `summary` + `description_excerpt` (Jira) or `title` + `body_excerpt` (PR). Never infer market or business justification absent from the source text. Enrichment applies only to selected items and never justifies exceeding the cap.
3. **Collapse the rest**: when the prefs routine-tail collapse knob is `on`, fold all remaining genuinely-routine automated work (lock-file / dependency-bump / Renovate maintenance closes, bot-approval reviews with `own_comment_count` 0, standalone low-importance ticket filings) into at most ONE trailing tail bullet or drop them entirely. Grooming (cat7) and substantive Confluence (cat6) are NOT routine — they are first-class and eligible for their own selected bullets.

**Bullet pattern — code/ship items**: lead with the PROBLEM SOLVED or VALUE DELIVERED, then the mechanism with a "by ..." clause, then the reference(s) and backticked Jira status. Never start a code/ship bullet with a git verb ("Merged", "Opened", "Landed") as the first word.

**Bullet pattern — review items**: lead with the review engagement ("Reviewed the \<what\> PR", "Gave inline feedback on \<what\>"). The accomplishment IS the review. Never state the review decision verb (no "Approved", "LGTM", "Requested changes", "Rejected", "approved and merged"). Call a review notably heavy only when `own_comment_count >= 8` (a `own_comment_count_capped: true` value is a qualifying floor). De-noise only bot-authored version-bump/dependency PR "reviews" with `own_comment_count` 0 into the tail.

**Status annotation**: the parenthetical status is the linked Jira ticket's status only, backticked, preserving Jira's native casing (e.g. `` `In QA` ``, `` `Done` ``). For authored PRs, take status from `linked_ticket.status` when non-null. Null linked ticket or null status: describe the action, assert no status. Drop the GitHub review decision; never write "In QA, approved".

**Grooming (cat7)**: first-class, eligible for its own bullet(s). Name which epics/areas from `summary.top_areas` and describe the kinds of refinement in priority order from `summary.fields_by_frequency`. Apply the created-vs-refinement gate first: cross-reference groomed `top_areas` / `issue_key`s against `cat4_jira_created` keys. When the grooming is on tickets the user created this window (or whose creation traces to another person's breakdown per the description/comments), say "created and set up / organized the ticket tree" and credit the source (a first name as kudos is acceptable). Reserve "drove refinement" / "grooming" / "designed" for pre-existing tickets the user materially changed. Emit no raw counts and no magnitude words ("hundreds", "dozens", "many", "a large number of", "N updates"); `fields_by_frequency` gives order, not volume.

**Confluence (cat6)**: surface as its own bullet only when a page carries real substance (design doc, decision, meaningful new content), described by what it communicated via `title` + `body_excerpt`. Route routine recurring check-in / status pages into the tail or omit them. Never use meta-phrasing like "authored the documentation cadence" or "kept docs current".

**Comment-thread status synthesis**: for any item in a returned / checkpoint-bounce status ("Returned from QA", "Reopened"), a Blocked status, or otherwise needing context — read its `comments` thread and surface what happened: what QA/the reviewer flagged, why it is blocked, what decision was reached, what it is waiting on. Prioritize the most recent substantive comment, and specifically any thread whose latest comment is from someone other than the searched user (awaiting their action). Synthesize the salient point; never dump the thread; never invent feedback. This applies in `Last week:` (linked-ticket returned statuses), `This week:` (returned/in-progress items), and `Blockers:` (why each is blocked).

**Markdown links**: when the prefs markdown-link knob is `on`, render every Jira key as `[PM-#####](url)` and every PR as `[owner/repo#N](url)` using the `url` fields on the JSON items. No bare unlinked keys when the knob is `on`. When `off`, leave references as bare keys/numbers.

**Name discipline**: apply the rule from the prefs `## Output style` name-discipline setting. Example resolution: kudos-only — never a person's first+last name anywhere, and no person's name at all except as a deliberate credit/kudos (first name or role only, never a full name); describe PRs and reviews by their subject, not their author.

### Step 3 — Build `This week:` (in-progress section)

Source this section entirely from `cat8_in_progress`. It is complete, not capped — cover all in-progress work. This section may legitimately be longer than `Last week:`.

- Lead each bullet with the PROBLEM / GOAL the work serves, then the forward action advancing it, then the markdown link + backticked status. Ground the "why" in the item's `summary` / `description_excerpt` / `comments`; if the excerpt does not support a why, keep the item factual.
- Group Epics / Initiatives by theme using `parent` / summaries; list active Tasks / Bugs individually.
- Cap each bullet at approximately 2–3 genuinely related items. Only items sharing a real theme (same parent / initiative or clearly one workstream) may share a bullet. Do NOT staple unrelated epics onto one line to compress. Do NOT emit a catch-all / miscellaneous / "Continue X, Y, and Z" dumping bullet. Each unrelated epic gets its own concise one-line bullet. Length from honest per-item lines is correct; cramming unrelated items is not.
- For returned / reopened / blocked items, read `comments` and surface the real status story as in Step 2.

### Step 4 — Build `Blockers:` section

Source this section entirely from `cat9_blocked`. List all blocked items — each: brief what + markdown link + `` `Blocked` ``. Write "None" only when `cat9_blocked` is empty. Do not fold On Hold / Waiting into this section.

For each blocked item, read its `comments` thread to say WHY it is blocked / what it is waiting on, grounded in an actual comment.

### Step 5 — Self-Edit Pass

Re-read the full draft before the self-lint gate and revise for:

- **Redundancy**: delete any phrase or clause that says the same thing twice; keep one.
- **Why-first**: every bullet must lead with the problem/goal, not the mechanism. Rewrite any bullet opening with a git verb, a mechanism, or an ID.
- **Attribution**: no over-claim; apply the created-vs-refinement rule; names as kudos only; status annotations as Jira status only, backticked.

### Step 6 — Self-Lint Gate (HARD)

Scan the draft for banned magnitude patterns and rewrite every match before the
report ships. This gate is a hard stop — the report must not go out with a raw
activity count.

**Banned patterns**:

1. Digit immediately preceding a grooming/volume noun — matches like "526 issues
   touched", "18 tickets updated" (pattern: `\d+\s+(issues?|fields?|tickets?|PRs?)\s+(touched|groomed|updated|changed)`).
2. Bare magnitude words for grooming or activity volume: "hundreds", "dozens",
   "many", "a large number of", "N updates".

Rewrite by naming the epics/areas (from `cat7` `top_areas`) and the kinds of
refinement in order (from `fields_by_frequency`), with no number.

Grooming volume is the repeat offender — apply this gate regardless of how the
grooming bullet was constructed.

## Coverage and Error Handling

- **Empty category** (`status: "ok"`, `count: 0`): legitimately quiet window. Omit or state briefly; never treat as failure.
- **Errored category** (`status: "error"`): skip it in bullets; note it once in prose as "(data unavailable)".
- **Null `linked_ticket` or null `linked_ticket.status`**: describe the PR action without asserting a lifecycle status.

## What This Skill Does Not Do

- No file writes, no API calls, no delivery. Delivery is `deliver-standup-report`'s responsibility.
- No collection. The activity JSON must already be in hand before this skill is invoked.
- No preferences file I/O. The calling agent reads `~/.claude/standup/preferences.md` and supplies the resolved knobs.
