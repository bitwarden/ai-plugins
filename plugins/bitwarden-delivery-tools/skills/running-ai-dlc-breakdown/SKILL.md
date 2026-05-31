---
name: running-ai-dlc-breakdown
description: Drive a Bitwarden tech breakdown end-to-end through the three-phase AI-DLC model (design → construction → execution) in the bitwarden/tech-breakdowns repo. Use when starting, drafting, or executing any tech breakdown — single engineer or pair driving with a Claude agent, per-artifact approval gates, Q→D→A clarifications, codegen-plan-to-Jira slicing with team refinement, and `state.md` as the breakdown-wide tracker.
allowed-tools: Skill, Read, Write, Edit, Bash, Glob, Grep, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_issues, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence
---

This skill drives a Bitwarden tech breakdown from a fresh Jira ticket through to all-shipped, using the three-phase AI-DLC model captured in the [bitwarden/tech-breakdowns](https://github.com/bitwarden/tech-breakdowns) repo. It is the operating playbook for the new mode of work: a single engineer or pair, with a Claude agent, driving the design → construction → execution loop end-to-end against per-artifact approval gates.

This skill assumes:

- The breakdown lives as markdown files in the `tech-breakdowns` repo.
- Execution is single-team, single-engineer/pair. A breakdown is **never** a cross-team carve-up; if the design surfaces work another team must own, that team owns a separate breakdown.
- Implementation is driven by sequential codegen, file-by-file, with the agent executing and the engineer reviewing each diff.
- Jira tracks delivery via QA-testable slices, not via file-grained codegen steps.

Cross-team coordination _during the design phase_ (interface review, signoff from peer teams) happens through the Cross-team engagement section of `design.md` and the companion `Skill(coordinating-cross-team-breakdown)`. What this skill changes is the execution model, not the coordination model.

## Repo layout

```
breakdowns/<team>/
  PM-12345-feature-name.md            ← design (Phase 1)
  PM-12345-feature-name/              ← sibling folder, created when construction starts
    state.md                          ← breakdown-wide tracker (all phases)
    construction/
      functional-design.md            ← per-layer implementation design
      non-functional.md               ← security, observability
      infrastructure.md               ← deployment, environments
      codegen-plan.md                 ← file-level execution plan
      tasks.md                        ← QA-testable Jira slices (final construction gate)
    clarifications/                   ← Q→D→A files (created on demand)
      q-<topic>.md
templates/
  tech-breakdown.md
  state.md
  construction/
  clarifications/question.md
```

Templates are canonical. Copy from `templates/`, never edit in place.

Three phases, not three folders. Design is a single `.md`; construction is a folder of artifacts; execution is the loop of running the codegen plan, transitioning Jira tickets, and updating `state.md` — no folder of its own.

## Bootstrap

Before drafting anything, orient on the work:

1. **Read the Jira ticket** the breakdown is being written against. Pull description, comments, and any linked Confluence pages.
2. **Check for an originating BW Initiative.** If the work sits under one, **run `Skill(navigating-the-initiative-funnel)` first** to pull the shepherd, sibling teams, architecture plan, and PoC PRs. The initiative context feeds the Specification and Cross-team engagement sections of `design.md`.
3. **Identify the owning team** and confirm the breakdown will live in `breakdowns/<team>/`.
4. **Copy `templates/tech-breakdown.md`** into the team's folder, renamed to `<JIRA-KEY>-<short-name>.md` (e.g., `PM-23289-sync-push-notifications.md`).
5. **Delete the template checklist** at the top of the copied file.

## The three phases

The skill runs each phase as a gated loop: draft → clarify (Q→D→A as needed) → request approval → either iterate or advance. Phase boundaries are explicit; gates are explicit.

### Phase 1 — Design

Single file: `breakdowns/<team>/<JIRA-KEY>-<short-name>.md`. Covers Specification, Clarifications Log, Architecture (high-level), Cross-team engagement, Agent Context.

Drafting order:

1. **Specification.** Description, User Value, Functional Requirements, Alternatives, Success Criteria. Don't paste Product spec; link it and frame in the team's voice.
2. **Architecture.** Current State (what exists today in code, with paths), Proposed architecture (prefer Mermaid diagrams over images), Out of Scope, Known Limitations, Prototypes.
3. **Cross-team engagement.** Walk the three subsections — consuming other teams' APIs, changes required in other teams' code, sequencing & ordering. Populate the signoff table. **Hand off to `Skill(coordinating-cross-team-breakdown)`** when chasing signoffs.
4. **Agent Context.** Repos affected (with `CLAUDE.md` pointers), existing patterns to follow, external references, things an agent should not assume. This block is what makes the breakdown useful to future Claude conversations — populate it explicitly, not as an afterthought.
5. **Clarifications Log.** Run an AI clarify pass against the draft _before_ requesting cross-team review. AI-raised questions go in `clarifications/q-<topic>.md` files via the Q→D→A pattern; resolved answers fold back into Spec or Architecture and the log entry becomes a short stub.

**Design Approval Gate.** Sign the gate at the bottom of the design doc to advance from PROPOSED to ACCEPTED. Create the sibling folder, copy `templates/construction/*.md` and `templates/state.md` into it, and initialize `state.md` with the transition.

### Phase 2 — Construction

Five artifacts in the sibling folder, each through its own approval gate:

1. **`functional-design.md` first.** Per-layer changes: data model, server logic, API surface, SDK, client services, UI, background jobs, testing strategy. Fill only the layers this change touches; remove the rest. Each subsection's checklist evaluated explicitly (mark N/A when skipped, don't leave blank).
2. **`non-functional.md` and `infrastructure.md` in parallel** once functional design is approved. NFR covers security, cryptography, observability, operations. Infrastructure covers deployment, environments, feature flagging.
3. **`codegen-plan.md`** — numbered, checkbox-tracked list of every file to create or modify, in execution order. Each file traces back to a construction doc (e.g., "Source: `functional-design.md` § Data model changes"). Sequencing constraints called out explicitly (interfaces before consumers, types before usages).
4. **`tasks.md` — the final construction gate.** Carve the codegen plan into **vertical, QA-testable slices**. Each slice = one Jira ticket. Typical grain: 3-7 tasks per breakdown. For each task: title (the user-observable behavior), scope (which codegen-plan steps), acceptance criteria in Given/When/Then, test scenarios, blocked-on, Jira ID (filled after refinement).
   - ✅ "Web client receives SyncPush and triggers vault refresh" — observable, testable
   - ✅ "API endpoint accepts and validates SyncPush payload" — testable contract
   - ❌ "All data model changes" — horizontal, not testable
   - ❌ "All files in `apps/web/`" — file boundary, not a behavior

Before approving `tasks.md`, two engagements happen — these are gating, not optional:

- **Team refinement session.** The driving engineer/pair walks the whole team (engineers, tech lead, QA, PM as appropriate) through the construction artifacts and the proposed task slicing. This is where the broader team gets read-in, catches what the pair missed, and aligns with QA. Capture session date, attendees, and changes in the Team refinement section of `tasks.md`.
- **QA review.** The responsible QA Engineer reviews tasks and test scenarios (typically as part of refinement). Capture separately so QA ownership is unambiguous.

Each artifact ends with a 2-option approval gate. After each approval, update `state.md` with the artifact name, approval date, and what changed since the last gate.

### Phase 3 — Execution

Not a folder. Once the Tasks gate is signed, execution begins:

1. **Create Jira tickets** from each approved task (carry over AC + test scenarios). Cross-link the breakdown.
2. **Engineer + agent work `codegen-plan.md` file-by-file.** Check off each file as it lands.
3. **Transition the Jira ticket** when all files in its slice are complete. Move it to QA review.
4. **QA validates** against the AC and test scenarios. Ticket closes when QA passes.
5. **Update `state.md`** after every meaningful event — codegen step complete, ticket created, ticket transitioned, ticket closed, QA blocked, clarification surfaced.

Repeat until all tickets are through QA. The breakdown is complete when `state.md` shows all tasks closed.

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

## `state.md` — the bridge

**This file is non-optional.** It is what an agent picking up cold reads first, and what a human (manager, peer team, QA) reads to see status without opening codegen-plan, tasks, and Jira separately. Keep it current.

`state.md` tracks three axes:

1. **Phase progress** — checkboxes per artifact (design → construction artifacts → delivery artifacts) showing what's approved and what's pending.
2. **Execution status** — codegen plan progress (`N of M files complete`), tasks complete (`N of M tickets closed`), active codegen step (which file the agent is touching now, and which task it's part of), tickets in QA, active engineer/pair.
3. **Last gate** — most recent approval gate, date, outcome (Approved and Continue / Request Changes), notes on anything that changed since approval.

**Update `state.md` on every gate transition and every meaningful execution event:**

- Approval gate signed → update Phase progress + Last gate
- Codegen step complete → bump the codegen progress counter
- Task complete → bump the tasks-complete counter and move the ticket to "In QA"
- QA passes → close the ticket and remove from "In QA"
- New clarification file created → add to Open clarifications
- Clarification resolved → remove from Open clarifications

The skill should never advance phases without checking `state.md` is current. If state and reality diverge, fix state first.

## Hard rules (AI-DLC inheritance)

These come from the AI-DLC pattern and are not negotiable:

1. **2-option approval format only.** Each approval gate is "Request Changes" or "Approve and Continue." Never present a 3-option menu. Never invent an emergent navigation pattern.
2. **Never proceed past a gate without explicit approval.** "Looks fine" is not approval. The user must signal Approve and Continue.
3. **Never proceed past open Q→D→A questions.** If a `clarifications/q-*.md` file has unanswered `[Answer]:` tags, the phase work stops.
4. **Update plan checkboxes immediately.** Don't batch. Don't defer. As soon as a file is generated, mark the corresponding `codegen-plan.md` checkbox.
5. **Never overwrite `state.md` or audit content.** Update in place via Edit; don't Write over the whole file.
6. **Always validate content before file creation.** Mermaid diagrams parse, links resolve, file paths exist where claimed.
7. **Always read the canonical templates** before drafting an artifact. Templates evolve; don't work from memory.
8. **Never carve work across teams.** A breakdown is single-team. Cross-team work means multiple breakdowns, one per owning team.

## Cross-references

- **`Skill(coordinating-cross-team-breakdown)`** — the design-phase cross-team signoff workflow. Drives the Cross-team engagement section of `design.md`. Treat blocking signoffs as gates on Design Approval.
- **`Skill(navigating-the-initiative-funnel)`** — load-bearing when the breakdown sits under a BW Initiative. Pulls the shepherd, sibling teams' epics, architecture plan, and PoC PRs that feed Specification, Architecture, and Cross-team engagement.
- **`Skill(architecting-solutions)` (in `bitwarden-tech-lead`)** — the architectural-judgment lens to apply when drafting Architecture and reviewing functional-design.
- **`Skill(bitwarden-security-context)` (in `bitwarden-security-engineer`)** — route through this when `non-functional.md`'s Security section flags cryptographic work or new security definitions.

## Common mistakes

- **Drafting without the Jira ticket and initiative context.** A breakdown drafted in a vacuum diverges from the work that triggered it. Always start from the ticket and (when applicable) the initiative.
- **Treating `state.md` as optional.** Stale state means anyone picking up cold reads codegen-plan, tasks, and Jira separately and reconstructs the picture. The whole point of `state.md` is that they don't have to.
- **Skipping the Q→D→A pattern for "small" questions.** Conversational clarifications get lost. Question files survive the next context reset; chat does not.
- **Slicing tasks horizontally instead of vertically.** "All data model changes" is not a QA-testable slice. Each task must deliver something QA can validate end-to-end.
- **Creating Jira tickets before QA reviews `tasks.md`.** QA's job gets harder when ticket scope/scenarios are baked in without their input. Walk them through first.
- **Carving work across teams within one breakdown.** Cross-team execution means separate breakdowns, linked via the Cross-team engagement section. Trying to track multi-team work in one breakdown's `tasks.md` collapses the model.
- **Editing a template instead of copying it.** Templates are canonical; teams copy them. Editing in place corrupts the next breakdown's starting point.
- **Approving a gate to "save time" without reading the artifact.** Downstream gates treat upstream approvals as authoritative. A rubber-stamped functional-design becomes the source the codegen-plan trusts.
- **Letting `codegen-plan.md` checkboxes lag execution.** Drift between checkboxes and actual files breaks the file-grain ↔ ticket-grain bridge `state.md` depends on.

## Reference

- [bitwarden/tech-breakdowns repo](https://github.com/bitwarden/tech-breakdowns) — canonical templates and team folders.
- [tech-breakdowns README](https://github.com/bitwarden/tech-breakdowns/blob/main/README.md) — three-phase model, layout, workflow.
- [AI-DLC working guide](https://github.com/awslabs/aidlc-workflows/blob/main/docs/WORKING-WITH-AIDLC.md) — upstream inspiration for the Q→D→A pattern, approval gates, and state-tracking discipline.
- [EDD — Evolutionary Database Design](https://contributing.bitwarden.com/contributing/database-migrations/edd) — referenced in `functional-design.md`'s data-model checklist.
