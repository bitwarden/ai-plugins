---
name: synthesize-standup-report
description: |
  Synthesizes a terse Mode A draft scaffold from the combined activity
  JSON emitted by generate-standup-report plus the user's preferences.
  Produces a draft markdown string only -- no delivery, no collection.
  The output is a structured starting point intended to be rewritten through
  the user's voice; human finishing is expected, not optional.
  Use when an agent has both the activity JSON and the loaded preferences in
  hand and needs the rendered draft text. Delivery is deliver-standup-report's
  job; collection is generate-standup-report's job.
---

# Synthesize Standup Report

This skill consumes the combined activity JSON from `generate-standup-report` and the user's preferences from `~/.claude/standup/preferences.md` (the calling agent loads and supplies these), and produces a Mode A draft scaffold as a markdown string. The output is terse and data-grounded — a structured starting point intended to be rewritten through the user's voice. Human finishing is expected. It reads recent standup reports from `~/.claude/standup/reports/` to build historical context (Step 1), directs the calling agent to write durable context back to preferences when applicable (Step 0), makes no other file writes, no API calls, and performs no delivery.

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
    "authored_prs":     {status, count, items},
    "reviews_given":    {status, count, items},
    "jira_done":        {status, count, items},
    "jira_created":     {status, count, items},
    "jira_comments":    {status, count, items},
    "confluence_edits": {status, count, items},
    "jira_grooming":    {status, count, items, summary},
    "in_progress":      {status, count, items},
    "blocked":          {status, count, items}
  }
}
```

Each category: `{status: "ok"|"error", count: int, items: [...], error: str|null}`.
`in_progress` and `blocked` are current-state snapshots; they are not
filtered by the time window. `jira_grooming` carries a qualitative
`summary` object with `fields_by_frequency` (ranked list of field kinds,
most-to-least frequent, no counts) and `top_areas` (up to 6
`{key, summary, parent}` objects for the most-groomed epics). Items in
`jira_done`, `jira_created`, `in_progress`, and `blocked`
carry a `comments` array (`[{author, created, excerpt}, ...]`, oldest first,
capped at 50 entries). The same `comments` field appears on `linked_ticket`
objects within `authored_prs` and `reviews_given` items.

See `generate-standup-report` for the full per-category item schema.

**Involvement depth signals (gather.py v1.8.0+)**: When present, use these fields as the primary involvement indicators. Fall back to `own_comment_count`-based heuristics when absent (older gather.py output):

- `authored_prs` items: `involvement_tier: "AUTHORED"` (constant)
- `reviews_given` items: `involvement_tier` (`"SUBSTANTIVE_REVIEW"` or `"LIGHT_REVIEW"`), `review_states` (list of review state strings, e.g. `["APPROVED"]`), `user_merged_pr` (bool — true when the user merged the PR)
- `jira_done` and `jira_created` items: `user_comment_count` (int — count of the user's own comments on the ticket)
- `confluence_edits` items: `is_page_creator` (bool — true when the user authored version 1 of the page)
- `jira_grooming.summary`: `field_counts` (`{field_name: count}` dict), `issues_touched` (int — total distinct issues groomed in the window)

### 2. The User's Preferences

The calling agent reads the user's preferences file and supplies the user's Template (the freeform output-format text). Treat the Template as applied-as-written: the user may describe a report format, phrasing rules, prose instructions, or leave it blank. Do not assume the preferences follow a fixed structure or use particular section names. Read what the user wrote and honor it directly. Where the Template is blank or silent on an aspect, apply this skill's built-in defaults below.

The calling agent should also extract the user's team from the `## Team` section of the preferences file (value after `Team:`) and supply it alongside the Template. When the team value is blank or absent, cross-team detection is disabled and all items are treated equally.

The calling agent should also extract the `## Durable Context` section (`### Priorities`, `### Ongoing Narratives`, `### How I Frame Things`) if present and supply it alongside the Template. If the section is absent or all subheadings are empty, treat it as not set. When Step 0 (Refining Questions) surfaces a durable fact during an interactive session, the calling agent writes that fact back to the appropriate subheading in `~/.claude/standup/preferences.md` — the calling agent handles the file write; this skill directs when and what to write.

Where the Template is silent on some aspect of the report, fall back to this skill's default behavior, described below. The default report shape is shown in `default-output-example.md` alongside this skill. That file's body is the canonical default text (also written verbatim into a preferences file's `## Output format` by `/standup:init` when the user accepts the default). Anything the user's Template does specify takes precedence over the corresponding default.

## Output Contract

This skill emits a single draft markdown string: a Mode A standup scaffold written in first-person voice. The output is terse and structured; it is a starting point, not a finished deliverable. Human finishing adds emotional texture and personal framing; the first-person structural skeleton is already in place. The
caller receives the text and is responsible for delivery.

By default, when the user's Template does not specify a different shape, the
report follows the default output style shown in `default-output-example.md`: a
one-sentence summary line carrying a red/amber/green signal, then a `Last week`
section, a `This week` section, and a `Blockers` section, as illustrated below.

```
:large_green_circle: [SINGLE_SENTENCE_SUMMARY]

`Last week:`
- ...

`This week:`
- ...

`Blockers:`
- ...
```

The draft is terse and honest, written in first-person voice — bullets speak as the user, not about the user. Use "I" as subject when natural, or lead with a direct-action verb implying a first-person actor ("Landed", "Reviewed", "Drove", "Shipped"). Mode A structure applies — data-grounded and terse, without emotional padding unsupported by data — but the prose registers as the user's own voice, not a third-person activity summary. The user's finishing pass adds emotional texture and subjective color; this skill provides the first-person structural skeleton. When the user's Template supplies its own format, section labels, or rules, follow those instead. They override this default shape in full.

## Synthesis Pipeline

The steps below are this skill's DEFAULT behavior. They apply only where the user's Template does not specify its own approach; any instruction in the user's Template overrides the matching default here. To shape a given report, consult the user's Template first, then fall back to these defaults.

### First-Person Voice Rule

**All bullets must speak as the user, not about the user.** This rule applies to every step in the pipeline — Last week, This week, and Blockers alike.

- Use "I" as the grammatical subject when natural: "I drove the design review for [PM-123]", "I reviewed the vault-item export PR and surfaced two edge cases."
- Lead with a direct-action verb that implies a first-person actor when "I" would read as stilted: "Landed", "Reviewed", "Drove", "Shipped", "Closed", "Resolved". The outcome-intention openers in Step 5 (Land, Ship, Close, Deliver, Finalize, Complete, Resolve, Merge) satisfy this rule without requiring "I".
- Never write a bullet that describes the user in the third person or passive voice: not "The vault export was delivered", not "Review was provided on X", not "Work completed on Y".
- This rule does not authorize adding emotional texture, hedging, or subjective color not grounded in the data — those remain the user's finishing-pass contribution. First-person structure is built in; personal voice depth is not.

### Mechanism-Disclosure Rule

**When a bullet's mechanism was deliberately chosen over a rejected alternative, a parenthetical disclosing the trade-off rationale is permitted and encouraged.** Surfacing the why — not just what was done — communicates decision quality to the audience.

- Format: `[outcome] by [mechanism] ([trade-off rationale])`. Example: "Resolved vault sync timeout by switching to exponential backoff (polling caused CPU spikes on mobile)."
- The parenthetical must name what the mechanism avoids or why it was chosen over the alternative: "by X (not Y because Z)" and "by X (avoiding Y, which caused Z)" are valid forms.
- Ground the trade-off in the ticket description, PR body, or comment thread — never invent rationale absent from the data.
- Keep the parenthetical to one brief clause (~10 words or fewer). Longer rationale belongs in a comment thread, not a standup bullet.
- This rule does not authorize subjective color or speculation — only factual trade-off disclosure grounded in available data.

### Step 0: Refining Questions (interactive only)

This step runs before applying durable context and before drafting. **Interactivity gate**: skip this step entirely when the calling agent is running non-interactively — e.g., in the autonomous eval loop, a CI context, or any scenario where no human is present to answer. When skipped, proceed directly to Step 2 (Apply Durable Context) using data and any durable context already in hand.

When running interactively, apply the hard cap: at most 3 questions total (Tier-1 + up to 2 Tier-2). Never exceed this.

#### Tier-1 question (always ask once, when interactive)

Ask exactly one question before drafting:

> **"How would you characterize this week in one sentence?"**

This targets the highest-leverage signal gap: the author's subjective workload self-read, pacing perception, and social standing cannot be derived from ticket data. This question elicits it directly.

**Handling the answer:**

- **Answer provided**: use the answer as (or as the seed of) the BLUF summary line, near-verbatim. Do not paraphrase the hedge, self-assessment, or emotional coloring out of it. The user's words are the signal.
- **Declined or blank**: skip the voiced BLUF. Fall back to the data-accurate aggregate BLUF (Mode-A behavior). The question is an enhancement, not a hard dependency.
- **RAG color is never overridden by the Tier-1 answer**: the RAG color is still derived from current-state data in Step 3. The Tier-1 answer supplies the _voice_ of the BLUF; the data supplies the _signal_. If the user's sentence and the data-derived color conflict, surface both honestly rather than reconciling silently.
- **Voice-safety rule**: do NOT add hedge words, emotional coloring, or self-assessment the user did not supply. Do NOT paraphrase the user's characterization into fact-delivery prose. Place it near-verbatim; do not invent around it.

#### Tier-2 follow-ups (conditional, at most 2)

After the Tier-1 answer, fire a follow-up only when a specific trigger applies. Apply at most two Tier-2 follow-ups. Stop after 3 questions total.

| Trigger                                                                                                                | Follow-up question                                              |
| ---------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| Tier-1 answer names a person, OR activity data contains teammate collaboration signals                                 | "Anyone whose work you'd want to call out or credit this week?" |
| Tier-1 answer or data contains a not-yet-done / uncertain cue ("still", "might", "trying", "going to", "either... or") | "Anything you're mid-decision on or might drop?"                |
| No trigger fires                                                                                                       | Ask nothing further. Do not probe a quiet week.                 |

One optional standing Tier-2 (ask at most once per session, then migrate to Durable Context): "Any work this week that didn't produce a ticket or PR?" — captures ticketless work. Skip if `## Durable Context / ### Ongoing Narratives` already carries active ticketless narratives.

**Tier-2 answer handling**: use near-verbatim, same voice-safety rule as Tier-1. Teammate credits go into Steps 4 and 5 (Last week and This week) bullet attribution. Path-uncertainty signals feed earned hedging in Steps 4–7. Ticketless work becomes eligible items in Step 4 (Last week) selection.

#### Durable context persistence

After the questions, assess whether any answer reveals a durable recurring fact — something the user would give the same answer to week after week:

- A standing ticketless commitment (e.g., "I'm on the AppSec review rotation")
- An ongoing multi-week narrative (e.g., "The MDM work will be a recurring theme through Q4")
- A framing preference (e.g., "I tend to hedge on security work because it is often partial")

If a durable fact surfaces: write it into the appropriate subheading (`### Priorities`, `### Ongoing Narratives`, or `### How I Frame Things`) of the `## Durable Context` section of `~/.claude/standup/preferences.md`. Once persisted, this fact need not be re-asked — future sessions will read it from durable context in Step 2.

### Step 1: Historical Report Context (cross-week continuity)

Before drafting, read the 3 most recent files from `~/.claude/standup/reports/` sorted by filename descending — the `standup-YYYY-MM-DD-HHMM.md` timestamp in the filename is the sort key. If the directory does not exist or contains fewer than 1 file, skip this step silently.

Perform a lightweight extraction from the retrieved files:

1. **Language patterns**: Note recurring phrases, terminology, and sentence structures the user habitually uses. Carry these patterns into the current draft — preserve established idiom over introducing variety.
2. **Verb choices**: Note which outcome-intention openers (Land, Ship, Close, etc.) appear in past This Week bullets. Prefer established verb choices when they fit the current week's items; do not rotate through the full allowed-verb set randomly. Disregard any banned openers (In Progress on, Working on, etc.) that appear in historical reports — those are not patterns to preserve.
3. **Ongoing narratives**: Identify initiatives or items that appear across multiple reports. When these appear in the current week's data, connect them to the established narrative thread rather than introducing them fresh. For example, if "the Rust CLI migration" appeared in This Week for two consecutive reports and is still in progress, acknowledge the continuity rather than re-introducing it as a new item.
4. **Carried items**: Note items that appeared in past This Week or Blockers sections and now appear in Last week or remain In Progress. Acknowledge progression rather than re-describing from scratch.

Use the extracted patterns to inform voice, framing, and continuity throughout Steps 2–8. **Do not copy or paraphrase past report text.** The goal is consistent idiom and narrative continuity, not repetition of prior content.

### Step 2: Apply Durable Context (if present)

Before drafting, review the durable context supplied by the calling agent. Use `### Priorities` to weight item selection — items advancing stated priorities are preferred over routine activity. Use `### Ongoing Narratives` to frame items in their initiative context rather than as isolated tickets. Use `### How I Frame Things` to calibrate editorial voice — if the user expresses earned hedging, skepticism, or honest-cost language in their framing preferences, preserve that in the draft. Durable context informs but does not override the `## Output format` Template. If durable context is absent or empty, skip this step.

### Step 3: Apply the RAG Heuristic (default)

Read the in-progress and blocked current-state categories (`in_progress` and `blocked` in the activity JSON) directly. Map them onto the red/amber/green bands using these default day-thresholds unless the user's Template states different ones: 3 days for a stale PR with changes requested and no new commits, 7 days for a stalled in-progress item unchanged in place. Rules:

- Any blocked item nudges toward amber at minimum.
- A heavy or critical blocked load pushes to red.
- PR-review staleness uses the 3-day default; in-progress staleness uses the 7-day default (unless the user's Template states otherwise).
- Zero non-empty categories returned is the red floor.
- When signals are mixed or ambiguous, choose amber over green.

Do NOT infer blocked or in-progress status from in-window activity; read current state only from the in-progress and blocked categories (`in_progress` / `blocked`), never from the in-window activity categories.

### Step 4: Build `Last week:` (past-highlights section)

Apply this default selection pipeline in this order (the steps pull against each other, so order is mandatory) unless the user's Template specifies its own approach:

1. **Select globally**: across all in-window activity (authored_prs through jira_grooming), pick the most important items. If the user's Template sets a highlighted-item cap, treat it as a ceiling, not a target to fill. If none, apply no cap.
2. **Enrich only the survivors**: attach a short WHAT/WHY clause to each selected item, grounded strictly in that item's `summary` + `description_excerpt` (Jira) or `title` + `body_excerpt` (PR). Never infer market or business justification absent from the source text. Enrichment applies only to selected items and never justifies exceeding the cap.
3. **Collapse the rest**: by default, fold all remaining genuinely-routine automated work (lock-file / dependency-bump / Renovate maintenance closes, bot-approval reviews with `own_comment_count` 0, standalone low-importance ticket filings) into at most ONE trailing tail bullet or drop them entirely. Grooming (jira_grooming) and substantive Confluence (confluence_edits) are NOT routine; they are first-class and eligible for their own selected bullets.

**Bullet pattern: code/ship items**: lead with the PROBLEM SOLVED or VALUE DELIVERED, then the mechanism with a "by ..." clause, then the reference(s) and backticked Jira status. Never start a code/ship bullet with a git verb ("Merged", "Opened", "Landed") as the first word.

**Bullet pattern: review items**: lead with the review engagement ("Reviewed the \<what\> PR", "Gave inline feedback on \<what\>"). The accomplishment IS the review. Never state the review decision verb (no "Approved", "LGTM", "Requested changes", "Rejected", "approved and merged"). Call a review notably heavy when `involvement_tier: SUBSTANTIVE_REVIEW` is present — or, for gather.py output predating v1.8.0 (field absent), when `own_comment_count >= 8` (`own_comment_count_capped: true` is a qualifying floor). De-noise only bot-authored version-bump/dependency PR "reviews" with `own_comment_count` 0 into the tail.

**Status annotation**: the parenthetical status is the linked Jira ticket's status only, backticked, preserving Jira's native casing (e.g. `` `In QA` ``, `` `Done` ``). For authored PRs, take status from `linked_ticket.status` when non-null. Null linked ticket or null status: describe the action, assert no status. Drop the GitHub review decision; never write "In QA, approved".

**Cross-team annotation**: When `linked_ticket.team` is non-empty and differs from the user's team (supplied by the calling agent), the item is cross-team work. Annotate the bullet to credit the collaboration: for authored PRs, append "(cross-team — [team name])" after the status annotation. For reviews given on a cross-team ticket, lead with "Reviewed [what] for [team name]" and include "(cross-team)" in the annotation. This surfaces the D5 Teammate & Cross-Team Credit signal. When `linked_ticket.team` is empty or matches the user's team, emit no cross-team annotation.

**Involvement Tier Weighting**: When `involvement_tier` is present on `authored_prs` or `reviews_given` items, use it to guide selection priority:

- `AUTHORED` items: standup-worthy by default; include unless the PR had zero in-window activity (`activity_count_in_window == 0`).
- `SUBSTANTIVE_REVIEW` items: standup-worthy when the PR was merged or is still open with decisions pending.
- `LIGHT_REVIEW` items: include only when something notable is present — `user_merged_pr: true`, an unusual PR state (e.g. returned from QA), or linked ticket context (e.g. a cross-team ticket with a pending decision). Otherwise fold into the tail or omit.

For `jira_done` and `jira_created` items: when `user_comment_count >= 3`, characterize the item as one Addison actively engaged with — use framing like "Drove resolution on...", "Resolved after driving the thread on...", or "Closed after actively working the thread". When `user_comment_count < 3` or the field is absent, use standard close characterization.

**Grooming (jira_grooming)**: first-class, eligible for its own bullet(s). Name which epics/areas from `summary.top_areas` and describe the kinds of refinement in priority order from `summary.fields_by_frequency`. Apply the created-vs-refinement gate first: cross-reference groomed `top_areas` / `issue_key`s against `jira_created` keys. When the grooming is on tickets the user created this window (or whose creation traces to another person's breakdown per the description/comments), say "created and set up / organized the ticket tree" and credit the source (a first name as kudos is acceptable). Reserve "drove refinement" / "grooming" / "designed" for pre-existing tickets the user materially changed. Emit no raw counts and no magnitude words ("hundreds", "dozens", "many", "a large number of", "N updates"); `fields_by_frequency` gives order, not volume.

**Confluence (confluence_edits)**: surface as its own bullet only when a page carries real substance (design doc, decision, meaningful new content), described by what it communicated via `title` + `body_excerpt`. Route routine recurring check-in / status pages into the tail or omit them. Never use meta-phrasing like "authored the documentation cadence" or "kept docs current". When `is_page_creator: true`, lead with "Created" (e.g., "Created the [Page Name] doc covering [substance]"); when `is_page_creator: false` or the field is absent, lead with "Updated" or "Edited". These are meaningfully different standup bullets.

**Comment-thread status synthesis**: for any item in a returned / checkpoint-bounce status ("Returned from QA", "Reopened"), a Blocked status, or otherwise needing context: read its `comments` thread and surface what happened: what QA/the reviewer flagged, why it is blocked, what decision was reached, what it is waiting on. Prioritize the most recent substantive comment, and specifically any thread whose latest comment is from someone other than the searched user (awaiting their action). Synthesize the salient point; never dump the thread; never invent feedback. This applies in `Last week:` (linked-ticket returned statuses), `This week:` (returned/in-progress items), and `Blockers:` (why each is blocked).

**Markdown links**: by default, render every Jira key as `[PM-#####](url)` and every PR as `[owner/repo#N](url)` using the `url` fields on the JSON items; no bare unlinked keys. If the user's Template asks for bare keys/numbers instead, leave references unlinked.

**Name discipline**: by default, kudos-only: never a person's first+last name anywhere, and no person's name at all except as a deliberate credit/kudos (first name or role only, never a full name); describe PRs and reviews by their subject, not their author. The user's Template may relax or restate this.

### Step 5: Build `This week:` (in-progress section)

Source this section entirely from `in_progress`. It is complete, not capped; cover all in-progress work. This section may legitimately be longer than `Last week:`.

- Lead each bullet with the PROBLEM / GOAL the work serves, then the forward action advancing it, then the markdown link + backticked status. Ground the "why" in the item's `summary` / `description_excerpt` / `comments`; if the excerpt does not support a why, keep the item factual.
- **This Week verb discipline (outcome-intention framing)**: Frame each This Week bullet as an intended outcome for this cycle, not an in-progress activity report. Use outcome-intention openers: _Land_, _Ship_, _Close_, _Deliver_, _Finalize_, _Complete_, _Resolve_, _Merge_. **Banned openers**: "In Progress on", "Iterating on", "Working on", "Continuing", "Making progress on" — these describe present-state activity the reader can already infer from the status annotation and score as D6 audience-calibration failures under rubric v3.0. Rationale: This Week answers "what do you intend to complete this cycle?" — a forward prediction about intended outcome, not an activity report. Exception: when path-uncertainty is earned (surfaced in Step 0 Tier-2 or present in Durable Context), soften to "Aim to close" / "Target to ship" rather than bare activity language — outcome-framed hedging is acceptable; activity-framed hedging is not.
- For in-progress items with a linked ticket where `linked_ticket.team` != user's team, add a cross-team annotation (e.g., "(working with [team name])") to credit the collaboration.
- Group Epics / Initiatives by theme using `parent` / summaries; list active Tasks / Bugs individually.
- Cap each bullet at approximately 2–3 genuinely related items. Only items sharing a real theme (same parent / initiative or clearly one workstream) may share a bullet. Do NOT staple unrelated epics onto one line to compress. Do NOT emit a catch-all / miscellaneous / "Continue X, Y, and Z" dumping bullet. Each unrelated epic gets its own concise one-line bullet. Length from honest per-item lines is correct; cramming unrelated items is not.
- For returned / reopened / blocked items, read `comments` and surface the real status story as in Step 4.

### Step 6: Build `Blockers:` section

Source this section entirely from `blocked`. List all blocked items, each with: brief what + markdown link + `` `Blocked` ``. Write "None" only when `blocked` is empty. Do not fold On Hold / Waiting into this section.

For each blocked item, read its `comments` thread to say WHY it is blocked / what it is waiting on, grounded in an actual comment.

### Step 7: Self-Edit Pass

Re-read the full draft before the self-lint gate and revise for:

- **Redundancy**: delete any phrase or clause that says the same thing twice; keep one.
- **Why-first**: every bullet must lead with the problem/goal, not the mechanism. Rewrite any bullet opening with a git verb, a mechanism, or an ID.
- **Attribution**: no over-claim; apply the created-vs-refinement rule; names as kudos only; status annotations as Jira status only, backticked.

### Step 8: Self-Lint Gate (HARD)

Scan the draft for banned magnitude patterns and rewrite every match before the
report ships. This gate is a hard stop; the report must not go out with a raw
activity count.

**Banned patterns**:

1. Digit immediately preceding a grooming/volume noun: matches like "526 issues
   touched", "18 tickets updated" (pattern: `\d+\s+(issues?|fields?|tickets?|PRs?)\s+(touched|groomed|updated|changed)`).
2. Bare magnitude words for grooming or activity volume: "hundreds", "dozens",
   "many", "a large number of", "N updates".

Rewrite by naming the epics/areas (from `jira_grooming` `top_areas`) and the kinds of
refinement in order (from `fields_by_frequency`), with no number.

Grooming volume is the repeat offender. Apply this gate regardless of how the
grooming bullet was constructed.

## Coverage and Error Handling

- **Empty category** (`status: "ok"`, `count: 0`): legitimately quiet window. Omit or state briefly; never treat as failure.
- **Errored category** (`status: "error"`): skip it in bullets; note it once in prose as "(data unavailable)".
- **Null `linked_ticket` or null `linked_ticket.status`**: describe the PR action without asserting a lifecycle status.

## What This Skill Does Not Do

- No delivery. Delivery is `deliver-standup-report`'s responsibility.
- No collection. The activity JSON must already be in hand before this skill is invoked.
- Preferences file reads: handled by the calling agent before invoking this skill (reads `~/.claude/standup/preferences.md` and supplies the Template and Durable Context). Preferences file writes: limited to durable-context persistence in Step 0 — when a refining-question answer reveals a durable recurring fact, this skill directs the calling agent to write it to the appropriate `## Durable Context` subheading in `~/.claude/standup/preferences.md`. No other file writes or direct API calls.
