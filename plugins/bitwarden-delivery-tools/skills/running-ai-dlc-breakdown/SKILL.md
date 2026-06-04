---
name: running-ai-dlc-breakdown
description: Drive a Bitwarden tech breakdown end-to-end through the three-phase AI-DLC model (design → construction → execution) in the bitwarden/tech-breakdowns repo. Use when starting, drafting, or executing any tech breakdown — single engineer or pair driving with a Claude agent, two approval gates (Design and Tasks), Q→D→A clarifications, engineering tasks that carry their affected files inline (no separate codegen plan), team refinement, and `state.md` for breakdown-level state that Jira can't capture (phase progress, active task and file, open clarifications).
allowed-tools: Skill, Read, Write, Edit, Bash, Glob, Grep, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_issues, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence
---

This skill drives a Bitwarden tech breakdown from a fresh Jira ticket through to all-shipped, using the three-phase AI-DLC model captured in the [bitwarden/tech-breakdowns](https://github.com/bitwarden/tech-breakdowns) repo. It is the operating playbook for the new mode of work: a single engineer or pair, with a Claude agent, driving the design → construction → execution loop end-to-end against per-artifact approval gates.

This skill assumes:

- The breakdown lives as markdown files in the `tech-breakdowns` repo.
- Execution is single-team. By default, one engineer or pair drives the breakdown end-to-end; teams may opt to hand off between design and execution at the Tasks Approval Gate (see the README's [Handoff option](https://github.com/bitwarden/tech-breakdowns#handoff-option) section for when and how). A breakdown is **never** a cross-team carve-up; if the design surfaces work another team must own, that team owns a separate breakdown.
- Implementation is driven by sequential codegen, file-by-file, with the agent executing and the engineer reviewing each diff.
- Jira tracks delivery via engineering tasks (PR-review-sized implementation units), not via file-grained codegen steps. QA validates at the story boundary, not the task boundary.

Cross-team coordination _during the design phase_ (interface review, signoff from peer teams) happens through the Cross-team engagement section of `design.md` and the companion `Skill(coordinating-cross-team-breakdown)`. What this skill changes is the execution model, not the coordination model.

## Repo layout

```
breakdowns/<team>/
  PM-12345-feature-name.md            ← the full design (cold-start entry, Phase 1)
  PM-12345-feature-name/              ← sibling folder, created when design begins
    state.md                          ← breakdown-level state (phase progress, codegen position, open clarifications); Jira is the source of truth for ticket-level state
    construction/
      tasks.md                        ← engineering tasks (each carries its affected files); the construction artifact and final construction gate
    clarifications/                   ← Q→D→A files (created on demand)
      q-<topic>.md
templates/
  tech-breakdown.md                   ← single-file design template
  state.md
  construction/                       ← the single tasks artifact
  clarifications/question.md
```

Templates are canonical. Copy from `templates/`, never edit in place.

Three phases. Design is a single self-contained `.md` containing spec, architecture, functional design (per layer), non-functional design, infrastructure design, cross-team coordination, and agent context — gated by one Design Approval Gate at its bottom. Construction is thin — just `tasks.md`, where each engineering task carries its affected files inline (no separate codegen plan), gated by one Tasks Approval Gate. Execution is the loop of working each task, transitioning Jira Tasks, and updating `state.md` — no folder of its own.

## Bootstrap

Before drafting anything, orient on the work:

1. **Read the Jira epic** the breakdown is being written against. Pull description, comments, and any linked Confluence pages.
2. **Read all child user stories** under the epic and their acceptance criteria. Stories are **inputs** to the design — they describe user-observable outcomes the breakdown must deliver. If no user stories exist for the epic, **stop and surface this as a blocker**: stories belong to Product and should exist before engineering decomposition begins. Either work with Product to author them, or scope the breakdown to a single existing story.
3. **Check for an originating BW Initiative.** If the work sits under one, **run `Skill(navigating-the-initiative-funnel)` first** to pull the shepherd, sibling teams, architecture plan, and PoC PRs. The initiative context feeds the Specification and Cross-team engagement sections of `design.md`.
4. **Identify the owning team** and confirm the breakdown will live in `breakdowns/<team>/`.
5. **Copy `templates/tech-breakdown.md`** into the team's folder, renamed to `<JIRA-KEY>-<short-name>.md` (e.g., `PM-23289-sync-push-notifications.md`).
6. **Create the sibling folder** with the same name and copy `templates/construction/*.md` and `templates/state.md` into it.
7. **Delete the template checklist** at the top of the overview file.

## The three phases

The skill runs each phase as a gated loop: draft → clarify (Q→D→A as needed) → complete artifacts → request gate approval → either iterate or advance. **Two approval gates total per breakdown**: the Design Approval Gate (rolls up all design work) and the Tasks Approval Gate (rolls up all construction work). Individual artifacts have completion checklists, not per-artifact gates.

### Phase 1 — Design

Single file: `breakdowns/<team>/<JIRA-KEY>-<short-name>.md`. Self-contained — spec, architecture, all design detail, cross-team coordination, and agent context in one cold-start-readable document.

**Drafting order (top to bottom in the file):**

1. **Specification.** Description, User Value, **User Stories** (list each one with Jira ID, "As a … I want …" line, and AC summary — these are inputs, not authored here), Functional Requirements (each mapped to the story IDs it implements), Alternatives, Success Criteria. Don't paste Product spec; link it and frame in the team's voice.
2. **Clarifications Log.** Run an AI clarify pass against the draft _before_ requesting cross-team review. AI-raised questions go in `clarifications/q-<topic>.md` files via the Q→D→A pattern; resolved answers fold back into the relevant section and the log entry becomes a short stub.
3. **Architecture (high-level).** Current State (what exists today in code, with paths), Proposed architecture (prefer Mermaid diagrams over images), Out of Scope, Known Limitations, Prototypes. The architecture must cover every user story listed in the Specification.
4. **Functional Design.** Per-layer changes: data model, server logic, API surface, SDK, client services, UI, background jobs, testing strategy. Fill only the layers this change touches; remove the rest. Each subsection's checklist evaluated explicitly (mark N/A when skipped, don't leave blank).
5. **Non-Functional Design.** Security, cryptography, observability, operations. Can be iterated in parallel with Infrastructure Design.
6. **Infrastructure Design.** Deployment, environments, feature flagging strategy and QA path. Can be iterated in parallel with Non-Functional Design.
7. **Cross-team engagement.** Walk the three subsections — consuming other teams' APIs, changes required in other teams' code, sequencing & ordering. Populate the signoff table. **Hand off to `Skill(coordinating-cross-team-breakdown)`** when chasing signoffs.
8. **Agent Context.** Durable reference content for future agent invocations: repos affected (with `CLAUDE.md` pointers), existing patterns to follow, external references, things an agent should not assume. Stable design-phase context only — current-position state (which phase, who's driving, last gate) lives in `state.md`, not here. Populate explicitly, not as an afterthought.

**Design Approval Gate.** Sign the gate at the bottom of the design when every section above is complete AND cross-team signoffs are captured. Status advances PROPOSED → ACCEPTED. Update `state.md` with the transition.

### Phase 2 — Construction

Two artifacts in the sibling `construction/` folder. Each has a completion checklist but no per-artifact gate; both roll up to the single **Tasks Approval Gate**.

**`tasks.md`** is the single construction artifact, carrying the Tasks Approval Gate at its bottom. Decompose the design into **engineering tasks**, each a coherent implementation slice that delivers (part of) one or more user stories. Typical grain: 3-7 tasks per breakdown, ~1-3 days each.

Engineering tasks are **not user stories**. The relationship is one-to-many: one story → multiple engineering tasks. Each task has:

- **Stories served** — Jira IDs from the design's User Stories section
- **Files affected** — explicit file list with `(N)` for new / `(M)` for modified. This is the agent's execution scope for the task; no separate codegen plan.
- **Definition of Done** — engineering-shaped (tests pass, code reviewed, build green), **not** user-AC. Story AC stays on the Jira story; engineering tasks don't duplicate it.
- **Test scenarios** — edge cases for QA to cross-check (story AC is the user-facing contract)
- **Blocked on** — prerequisites among the other tasks
- **Jira ID** — created as a Jira **Task** under the parent epic, linked to the story or stories it serves via "implements" or similar (not as a sub-task; engineering tasks need their own QA-capable status lifecycle)

  Include a **Coverage check** subsection mapping every user story from the overview to at least one task. If a story is uncovered, the decomposition is incomplete.

  Slicing principle: vertical implementation slices, not horizontal layer batches.

  Note the exception path: if user stories don't exist (the blocker from bootstrap wasn't resolved), engineering tasks may carry story-shaped AC and be created as Jira Stories instead of Tasks-linked-to-stories. Use sparingly; the right fix is upstream.

Before signing the Tasks Approval Gate, two engagements happen — these are gating, not optional:

- **Team refinement session.** The driving engineer/pair walks the whole team (engineers, tech lead, QA, PM as appropriate) through the construction artifacts and the proposed task slicing. Two things happen: (1) the broader team gets read-in, catches what the pair missed, and aligns with QA on test scenarios; (2) each task's ticket-ready content gets fleshed out — the implementation pointers, one-paragraph context, sharpened scenarios, affected file list. The task entries in `tasks.md` carry structural fields out of construction; refinement is where the team adds the rest so each task is ready to become a Jira Task. Capture session date, attendees, and changes in the Team refinement section of `tasks.md`.
- **QA review.** The responsible QA Engineer reviews tasks and test scenarios (typically as part of refinement). Capture separately so QA ownership is unambiguous.

After the Tasks Approval Gate is signed, update `state.md` with the transition and proceed to execution.

### Phase 3 — Execution

Not a folder. Once the Tasks gate is signed, execution begins.

**Task "done" and story "done" are different events.** Tasks close on engineering DoD (tests, review, build, behind flag if applicable). Stories close on QA validation against story AC. QA does **not** gate individual task merges; it validates at the story boundary. The flagging path (chosen in the design's Infrastructure Design section) determines how tasks merge safely without per-task QA.

Execution loop (each step shows the owner):

1. **Create Jira Tasks** — **engineer** (or agent via Atlassian MCP, with engineer review) creates a Jira **Task** per engineering task (siblings of the parent stories under the same epic), linking each Task to the story or stories it serves via "implements" or similar. Cross-link the breakdown.
2. **Execute task by task** — **engineer + agent** work each engineering task in `tasks.md`. For the current task, the agent generates / modifies each file listed in the task's Files affected; engineer reviews the diff and commits. Move to the next file, then the next task.
3. **Close tasks as they merge** — **engineer** transitions the Jira Task to Done when engineering DoD is met (tests, review, build, behind flag if applicable).
4. **Notify QA when a story is ready** — when all tasks serving a story have merged (and the flag is enabled in staging if flagged), **engineer/pair** notifies the QA Engineer.
5. **QA validates** — **QA Engineer** validates the story against its AC (not task DoD). Story closes on pass.
6. **Flag flip (flagged path only)** — once the story is validated in staging, **engineer** coordinates the production flag flip per the team's release process.

**Who updates `state.md`:** the engineer owns it for the things `state.md` tracks (phase progress, codegen position, open clarifications, last gate). During an AI-DLC session, the agent updates `state.md` as a side-effect of its work (codegen step complete, gate signed, clarification surfaced). For asynchronous breakdown-level events (a gate signed outside the session, a clarification answered later), the engineer updates `state.md` directly or asks the agent in the next session. **Ticket-level events (PR merges, Jira Task transitions, QA validations, flag flips) update Jira, not `state.md`** — Jira is the source of truth for those.

The breakdown is complete when the Jira board shows all stories closed (and all flags flipped, if applicable). `state.md`'s Phase progress section reflects this via the Execution checkboxes.

### QA testing process

See the README's QA testing process section for the full model. Skill-level summary:

**Two paths**, decided in the design's Infrastructure Design section:

- **Feature-flagged (default).** Tasks merge to main behind the flag. Story-level QA happens when all tasks for a story land + flag is enabled in staging. Flag flips to prod after QA passes.
- **Non-flagged.** Three sub-cases:
  - **Task = story:** one task delivers a whole user-observable behavior; QA validates story AC at task merge.
  - **Sequenced harmless intermediates:** tasks merge in dependency order; the final wiring task is QA's validation point.
  - **Feature branch:** discouraged; must justify in `infrastructure.md`.

**QA's two touchpoints:**

- **Upstream — during construction refinement.** QA reviews `tasks.md`, confirms story AC is clear, suggests edge cases. Gating for the Tasks Approval Gate.
- **Downstream — during execution.** QA validates each story when its tasks have merged (+ flag enabled in staging if flagged). Gating for the story closing in Jira.

QA does not validate individual engineering tasks. Engineering DoD covers implementation correctness; story AC covers the user-facing contract.

## Clarifications: two mechanisms, one index

Clarifications come from two sources and use two different mechanisms. Keep them separate.

| Source                                    | Mechanism                                       | Lives in                          | Lifecycle in `design.md` Clarifications Log? |
| ----------------------------------------- | ----------------------------------------------- | --------------------------------- | -------------------------------------------- |
| **Human-raised** (PM, AppSec, peer team)  | Free-form table entry                           | Clarifications Log in `design.md` | Yes — full lifecycle (Open → Resolved)       |
| **AI-raised** (this skill, mid-iteration) | Q→D→A files: multi-choice with `[Answer]:` tags | `clarifications/q-<topic>.md`     | Only as a resolved stub after fold-back      |

The Clarifications Log is the **unified index** a future reader uses to see what questions drove the design. Q→D→A files are the **working artifacts** the agent uses during iteration. Open AI-raised questions live in their q-file and are tracked in `state.md`'s Open clarifications section — **not** in the design log (they're noise until resolved).

### The Question → Doc → Approval pattern (AI-raised only)

When clarification is needed mid-iteration (any phase), do not chase the question conversationally. Use the Q→D→A pattern:

1. **Create a question file** at `breakdowns/<team>/<breakdown-name>/clarifications/q-<topic>.md` using `templates/clarifications/question.md`. Questions use multiple-choice format with options A/B/C/X (X = custom) and `[Answer]:` tags.
2. **Stop and announce.** Tell the user: "Created `clarifications/q-<topic>.md` with N questions. Fill in each `[Answer]:` tag and let me know when ready." Add the file to `state.md`'s Open clarifications section.
3. **Wait.** Do not proceed past the questions. Do not infer answers.
4. **On the trigger phrase** — when the user says some variant of _"We have answered your clarification questions. Please re-read the file and proceed"_ — re-read the question file from disk (the user has edited it), validate answers for ambiguity, then **fold significant decisions back into the relevant phase doc** (Spec, Architecture, functional-design, etc.). Three follow-on updates:
   - The question file's Resolved decisions section gets the fold-back note (q-file becomes audit trail).
   - The Clarifications Log in `design.md` gets a short stub row: status Resolved, source `q-<topic>.md`, resolver name, one-line answer with link to the updated section.
   - `state.md`'s Open clarifications section drops the q-file.
5. **Resume.** Continue the phase work with the new context.

Answer-format guidance for the user (encoded in the template):

- Letter + label: `C — financial summary`
- Letter + label + reasoning: `C — financial summary; needed for the quarterly review`
- Combined letters: `B and C — rate limiting at both gateway and application level`
- Custom: `X — ...` freely when no option fits

### Human-raised clarifications

Questions from PM, AppSec, peer teams, or anyone else reviewing the design come in free-form and don't fit the multi-choice shape. **Log them directly in the Clarifications Log table** in `design.md` with status Open, the source (person), an owner, and a target resolution date. Update to Resolved with a one-line answer and link to the section when the question is answered. Do not create a q-file for human-raised questions — the Q→D→A mechanism is specifically the agent's working tool.

## `state.md` — breakdown-level state

**`state.md` captures what Jira can't show.** Jira is the source of truth for ticket-level state (task counts, story status, assignees, who's in QA right now); `state.md` captures breakdown-level state (which approval gates have been signed, file-by-file codegen position, open Q→D→A clarifications). An agent picking up cold reads the design + `state.md` + the Jira board. Don't duplicate ticket counts in `state.md`.

`state.md` tracks four things:

1. **Jira pointers** — epic ID and board/filter link, so anyone navigating from `state.md` can drill into ticket detail.
2. **Phase progress** — checkboxes for breakdown-level milestones that Jira doesn't represent: design sections complete, cross-team signoffs done, Design Approval Gate signed, Tasks Approval Gate signed.
3. **Task execution** — flagging path, active task (which Jira Task is in progress now, which story it serves), active file within the task (which file the agent is touching now, file N of M for this task). Sub-task granularity that Jira doesn't carry.
4. **Open clarifications** — pending `clarifications/q-*.md` files. Q-files are repo artifacts, not Jira items.
5. **Last gate** — most recent approval gate, date, outcome (Approved / Request Changes), notes on anything that changed since approval.

**Update `state.md` on:**

- Approval gate signed → update Phase progress + Last gate
- Codegen step complete → bump the codegen progress counter; update Active codegen step
- New clarification file created → add to Open clarifications
- Clarification resolved → remove from Open clarifications

**Don't update `state.md` for ticket events** — those live in Jira. PR merges, Jira Task transitions to Done, QA passing a story, flag flips: these are visible on the Jira board, which `state.md` links to.

The skill should never advance phases without checking `state.md` is current for the things it owns. If state and reality diverge on the items above, fix state first.

## Hard rules (AI-DLC inheritance)

These come from the AI-DLC pattern and are not negotiable:

1. **2-option approval format only.** Each approval gate is "Request Changes" or "Approve and Continue." Never present a 3-option menu. Never invent an emergent navigation pattern.
2. **Never proceed past a gate without explicit approval.** "Looks fine" is not approval. The user must signal Approve and Continue.
3. **Never proceed past open Q→D→A questions.** If a `clarifications/q-*.md` file has unanswered `[Answer]:` tags, the phase work stops.
4. **Update progress immediately.** Don't batch. Don't defer. As soon as a file is generated, update `state.md`'s Active file within task line; when a task's files are all merged, update Phase progress.
5. **Never overwrite `state.md` or audit content.** Update in place via Edit; don't Write over the whole file.
6. **Always validate content before file creation.** Mermaid diagrams parse, links resolve, file paths exist where claimed.
7. **Always read the canonical templates** before drafting an artifact. Templates evolve; don't work from memory.
8. **Never carve work across teams.** A breakdown is single-team. Cross-team work means multiple breakdowns, one per owning team.
9. **User stories are inputs, not outputs.** Read them during bootstrap from Jira; reference them in the design's Specification; ensure construction's `tasks.md` covers every story. Don't author stories in this breakdown — they belong to Product and live in Jira. If they're missing, that's a blocker.
10. **Engineering task Definition of Done is not user AC.** Story AC stays on the Jira story. Engineering tasks describe implementation work; their DoD is implementation-shaped (tests pass, code reviewed, build green).

## Cross-references

- **`Skill(coordinating-cross-team-breakdown)`** — the design-phase cross-team signoff workflow. Drives the Cross-team engagement section of `design.md`. Treat blocking signoffs as gates on Design Approval.
- **`Skill(navigating-the-initiative-funnel)`** — load-bearing when the breakdown sits under a BW Initiative. Pulls the shepherd, sibling teams' epics, architecture plan, and PoC PRs that feed Specification, Architecture, and Cross-team engagement.
- **`Skill(architecting-solutions)` (in `bitwarden-tech-lead`)** — the architectural-judgment lens to apply when drafting Architecture and reviewing functional-design.
- **`Skill(bitwarden-security-context)` (in `bitwarden-security-engineer`)** — route through this when the design's Non-Functional Design § Security section flags cryptographic work or new security definitions.

## Common mistakes

- **Drafting without the Jira ticket and initiative context.** A breakdown drafted in a vacuum diverges from the work that triggered it. Always start from the ticket and (when applicable) the initiative.
- **Treating `state.md` as optional.** Stale state means anyone picking up cold has to reconstruct phase progress and active-task position by reading the design, scanning tasks.md, and clicking through clarifications. `state.md` exists so they don't have to.
- **Duplicating Jira state in `state.md`.** Task counts, story statuses, QA queue, assignees — these all live in Jira. Adding them to `state.md` creates drift between two trackers. `state.md` carries only what Jira can't (phase gates, codegen position, open Q→D→A clarifications).
- **Skipping the Q→D→A pattern for "small" questions.** Conversational clarifications get lost. Question files survive the next context reset; chat does not.
- **Slicing tasks horizontally instead of by logical implementation unit.** "All data model changes" produces a PR that mixes unrelated changes and isn't reviewable as one coherent unit. Each task should be sized for one code review pass and one merge event.
- **Creating Jira tickets before QA reviews `tasks.md`.** QA's job gets harder when ticket scope/scenarios are baked in without their input. Walk them through first.
- **Confusing engineering tasks with user stories.** Stories describe user-observable outcomes with Given/When/Then AC, authored by Product, living in Jira. Engineering tasks describe implementation work and reference stories. Duplicating story AC onto engineering tasks creates two sources of truth and confuses QA.
- **Starting design without user stories.** Stories are inputs to the breakdown. Bootstrap should pull them; missing stories is a blocker, not a section to fill in. Engineering doesn't author stories on Product's behalf.
- **Carving work across teams within one breakdown.** Cross-team execution means separate breakdowns, linked via the Cross-team engagement section. Trying to track multi-team work in one breakdown's `tasks.md` collapses the model.
- **Editing a template instead of copying it.** Templates are canonical; teams copy them. Editing in place corrupts the next breakdown's starting point.
- **Approving a gate to "save time" without reading the artifact.** Downstream gates treat upstream approvals as authoritative. A rubber-stamped Functional Design section becomes the source the tasks trust.
- **Letting `state.md` progress lag execution.** Drift between `state.md`'s active-task line and reality breaks the cold-start dashboard property.

## Reference

- [bitwarden/tech-breakdowns repo](https://github.com/bitwarden/tech-breakdowns) — canonical templates and team folders.
- [tech-breakdowns README](https://github.com/bitwarden/tech-breakdowns/blob/main/README.md) — three-phase model, layout, workflow.
- [AI-DLC working guide](https://github.com/awslabs/aidlc-workflows/blob/main/docs/WORKING-WITH-AIDLC.md) — upstream inspiration for the Q→D→A pattern, approval gates, and state-tracking discipline.
- [EDD — Evolutionary Database Design](https://contributing.bitwarden.com/contributing/database-migrations/edd) — referenced in `functional-design.md`'s data-model checklist.
