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
  PM-12345-feature-name.md            ← design overview (cold-start entry, Phase 1)
  PM-12345-feature-name/              ← sibling folder, created when design begins
    state.md                          ← breakdown-wide tracker (all phases)
    design/
      functional-design.md            ← per-layer implementation design
      non-functional-design.md        ← security, observability
      infrastructure-design.md        ← deployment, environments, flagging
    construction/
      codegen-plan.md                 ← file-level execution plan
      tasks.md                        ← QA-testable Jira slices (final construction gate)
    clarifications/                   ← Q→D→A files (created on demand)
      q-<topic>.md
templates/
  tech-breakdown.md                   ← design overview template
  state.md
  design/                             ← detailed design artifacts
  construction/                       ← codegen plan + tasks
  clarifications/question.md
```

Templates are canonical. Copy from `templates/`, never edit in place.

Three phases. Design is the overview `.md` plus detailed sub-artifacts in `design/` (each with its own approval sub-gate, rolled up by the Design Approval Gate at the bottom of the overview). Construction is thin — just the codegen plan and task decomposition. Execution is the loop of running the codegen plan, transitioning Jira tickets, and updating `state.md` — no folder of its own.

## Bootstrap

Before drafting anything, orient on the work:

1. **Read the Jira epic** the breakdown is being written against. Pull description, comments, and any linked Confluence pages.
2. **Read all child user stories** under the epic and their acceptance criteria. Stories are **inputs** to the design — they describe user-observable outcomes the breakdown must deliver. If no user stories exist for the epic, **stop and surface this as a blocker**: stories belong to Product and should exist before engineering decomposition begins. Either work with Product to author them, or scope the breakdown to a single existing story.
3. **Check for an originating BW Initiative.** If the work sits under one, **run `Skill(navigating-the-initiative-funnel)` first** to pull the shepherd, sibling teams, architecture plan, and PoC PRs. The initiative context feeds the Specification and Cross-team engagement sections of `design.md`.
4. **Identify the owning team** and confirm the breakdown will live in `breakdowns/<team>/`.
5. **Copy `templates/tech-breakdown.md`** into the team's folder, renamed to `<JIRA-KEY>-<short-name>.md` (e.g., `PM-23289-sync-push-notifications.md`).
6. **Create the sibling folder** with the same name and copy `templates/design/*.md`, `templates/construction/*.md`, and `templates/state.md` into it.
7. **Delete the template checklist** at the top of the overview file.

## The three phases

The skill runs each phase as a gated loop: draft → clarify (Q→D→A as needed) → complete artifacts → request gate approval → either iterate or advance. **Two approval gates total per breakdown**: the Design Approval Gate (rolls up all design work) and the Tasks Approval Gate (rolls up all construction work). Individual artifacts have completion checklists, not per-artifact gates.

### Phase 1 — Design

Two parts: the overview (single file: `breakdowns/<team>/<JIRA-KEY>-<short-name>.md`) and the detailed design artifacts (in the sibling `design/` folder).

**Overview drafting order:**

1. **Specification.** Description, User Value, **User Stories** (list each one with Jira ID, "As a … I want …" line, and AC summary — these are inputs, not authored here), Functional Requirements (each mapped to the story IDs it implements), Alternatives, Success Criteria. Don't paste Product spec; link it and frame in the team's voice.
2. **Architecture (high-level).** Current State (what exists today in code, with paths), Proposed architecture (prefer Mermaid diagrams over images), Out of Scope, Known Limitations, Prototypes. The architecture must cover every user story listed in the Specification. Per-layer detail lives in `design/functional-design.md`, not here.
3. **Cross-team engagement.** Walk the three subsections — consuming other teams' APIs, changes required in other teams' code, sequencing & ordering. Populate the signoff table. **Hand off to `Skill(coordinating-cross-team-breakdown)`** when chasing signoffs.
4. **Agent Context.** Durable reference content for future agent invocations: repos affected (with `CLAUDE.md` pointers), existing patterns to follow, external references, things an agent should not assume. Stable design-phase context only — current-position state (which phase, who's driving, last gate) lives in `state.md`, not here. Populate explicitly, not as an afterthought.
5. **Clarifications Log.** Run an AI clarify pass against the draft _before_ requesting cross-team review. AI-raised questions go in `clarifications/q-<topic>.md` files via the Q→D→A pattern; resolved answers fold back into Spec or Architecture and the log entry becomes a short stub.

**Detailed design artifacts in `design/`.** Each has a completion checklist but no per-artifact gate; they roll up to the overview's Design Approval Gate.

1. **`functional-design.md`** — per-layer changes: data model, server logic, API surface, SDK, client services, UI, background jobs, testing strategy. Fill only the layers this change touches; remove the rest. Each subsection's checklist evaluated explicitly (mark N/A when skipped, don't leave blank).
2. **`non-functional-design.md`** — security, cryptography, observability, operations. Drafted in parallel with step 3 once functional-design is complete.
3. **`infrastructure-design.md`** — deployment, environments, feature flagging strategy. Drafted in parallel with step 2 once functional-design is complete.

**Design Approval Gate.** Sign the gate at the bottom of the overview when all three design artifacts have their completion checklists satisfied AND cross-team signoffs are complete. Status advances PROPOSED → ACCEPTED. Update `state.md` with the transition.

### Phase 2 — Construction

Two artifacts in the sibling `construction/` folder. Each has a completion checklist but no per-artifact gate; both roll up to the single **Tasks Approval Gate**.

1. **`codegen-plan.md`** — numbered, checkbox-tracked list of every file to create or modify, in execution order. Each file traces back to a design artifact (e.g., "Source: `../design/functional-design.md` § Data model changes"). Sequencing constraints called out explicitly (interfaces before consumers, types before usages).
2. **`tasks.md`** — the artifact that carries the Tasks Approval Gate at its bottom. Carve the codegen plan into **engineering tasks**, each a vertical slice of implementation work that delivers (part of) one or more user stories. Typical grain: 3-7 tasks per breakdown, ~1-3 days each.

   Engineering tasks are **not user stories**. The relationship is one-to-many: one story → multiple engineering tasks. Each task has:
   - **Stories served** — Jira IDs from the overview's User Stories section
   - **Scope** — codegen-plan steps it implements
   - **Definition of Done** — engineering-shaped (tests pass, code reviewed, build green), **not** user-AC. Story AC stays on the Jira story; engineering tasks don't duplicate it.
   - **Test scenarios** — edge cases for QA to cross-check (story AC is the user-facing contract)
   - **Blocked on** — prerequisites among the other tasks
   - **Jira ID** — typically created as a sub-task of the parent story

   Include a **Coverage check** subsection mapping every user story from the overview to at least one task. If a story is uncovered, the decomposition is incomplete.

   Slicing principle: vertical implementation slices, not horizontal layer batches.

   Note the exception path: if user stories don't exist (the blocker from bootstrap wasn't resolved), engineering tasks may carry story-shaped AC and become Jira stories rather than sub-tasks. Use sparingly; the right fix is upstream.

Before signing the Tasks Approval Gate, two engagements happen — these are gating, not optional:

- **Team refinement session.** The driving engineer/pair walks the whole team (engineers, tech lead, QA, PM as appropriate) through the construction artifacts and the proposed task slicing. This is where the broader team gets read-in, catches what the pair missed, and aligns with QA. Capture session date, attendees, and changes in the Team refinement section of `tasks.md`.
- **QA review.** The responsible QA Engineer reviews tasks and test scenarios (typically as part of refinement). Capture separately so QA ownership is unambiguous.

After the Tasks Approval Gate is signed, update `state.md` with the transition and proceed to execution.

### Phase 3 — Execution

Not a folder. Once the Tasks gate is signed, execution begins.

**Task "done" and story "done" are different events.** Tasks close on engineering DoD (tests, review, build, behind flag if applicable). Stories close on QA validation against story AC. QA does **not** gate individual task merges; it validates at the story boundary. The flagging path (chosen in `design/infrastructure-design.md`) determines how tasks merge safely without per-task QA.

Execution loop (each step shows the owner):

1. **Create Jira tickets** — **engineer** (or agent via Atlassian MCP, with engineer review) creates a Jira sub-task per engineering task, typically linked to the parent stories. Cross-link the breakdown.
2. **Execute the codegen plan** — **engineer + agent** work `codegen-plan.md` file-by-file. Agent generates each file; engineer reviews the diff and commits. Check off each file as it lands.
3. **Close tasks as they merge** — **engineer** transitions the Jira sub-task to Done when engineering DoD is met (tests, review, build, behind flag if applicable).
4. **Notify QA when a story is ready** — when all tasks serving a story have merged (and the flag is enabled in staging if flagged), **engineer/pair** notifies the QA Engineer.
5. **QA validates** — **QA Engineer** validates the story against its AC (not task DoD). Story closes on pass.
6. **Flag flip (flagged path only)** — once the story is validated in staging, **engineer** coordinates the production flag flip per the team's release process.

**Who updates `state.md`:** the engineer owns it. During an AI-DLC session, the agent updates `state.md` as a side-effect of its work (codegen step complete, gate signed, clarification surfaced) — the agent can only update what it observes in-session. For asynchronous events (a PR merging hours later, QA validating a story a day later, a flag flip), the engineer updates `state.md` directly or asks the agent in the next session to record what's changed. Stale state means anyone picking up cold reconstructs the picture from scratch.

The breakdown is complete when `state.md` shows all stories validated (and all flags flipped, if applicable).

### QA testing process

See the README's QA testing process section for the full model. Skill-level summary:

**Two paths**, decided in `design/infrastructure-design.md`:

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
9. **User stories are inputs, not outputs.** Read them during bootstrap from Jira; reference them in the design's Specification; ensure construction's `tasks.md` covers every story. Don't author stories in this breakdown — they belong to Product and live in Jira. If they're missing, that's a blocker.
10. **Engineering task Definition of Done is not user AC.** Story AC stays on the Jira story. Engineering tasks describe implementation work; their DoD is implementation-shaped (tests pass, code reviewed, build green).

## Cross-references

- **`Skill(coordinating-cross-team-breakdown)`** — the design-phase cross-team signoff workflow. Drives the Cross-team engagement section of `design.md`. Treat blocking signoffs as gates on Design Approval.
- **`Skill(navigating-the-initiative-funnel)`** — load-bearing when the breakdown sits under a BW Initiative. Pulls the shepherd, sibling teams' epics, architecture plan, and PoC PRs that feed Specification, Architecture, and Cross-team engagement.
- **`Skill(architecting-solutions)` (in `bitwarden-tech-lead`)** — the architectural-judgment lens to apply when drafting Architecture and reviewing functional-design.
- **`Skill(bitwarden-security-context)` (in `bitwarden-security-engineer`)** — route through this when `design/non-functional-design.md`'s Security section flags cryptographic work or new security definitions.

## Common mistakes

- **Drafting without the Jira ticket and initiative context.** A breakdown drafted in a vacuum diverges from the work that triggered it. Always start from the ticket and (when applicable) the initiative.
- **Treating `state.md` as optional.** Stale state means anyone picking up cold reads codegen-plan, tasks, and Jira separately and reconstructs the picture. The whole point of `state.md` is that they don't have to.
- **Skipping the Q→D→A pattern for "small" questions.** Conversational clarifications get lost. Question files survive the next context reset; chat does not.
- **Slicing tasks horizontally instead of vertically.** "All data model changes" is not a QA-testable slice. Each task must deliver something QA can validate end-to-end.
- **Creating Jira tickets before QA reviews `tasks.md`.** QA's job gets harder when ticket scope/scenarios are baked in without their input. Walk them through first.
- **Confusing engineering tasks with user stories.** Stories describe user-observable outcomes with Given/When/Then AC, authored by Product, living in Jira. Engineering tasks describe implementation work and reference stories. Duplicating story AC onto engineering tasks creates two sources of truth and confuses QA.
- **Starting design without user stories.** Stories are inputs to the breakdown. Bootstrap should pull them; missing stories is a blocker, not a section to fill in. Engineering doesn't author stories on Product's behalf.
- **Carving work across teams within one breakdown.** Cross-team execution means separate breakdowns, linked via the Cross-team engagement section. Trying to track multi-team work in one breakdown's `tasks.md` collapses the model.
- **Editing a template instead of copying it.** Templates are canonical; teams copy them. Editing in place corrupts the next breakdown's starting point.
- **Approving a gate to "save time" without reading the artifact.** Downstream gates treat upstream approvals as authoritative. A rubber-stamped functional-design becomes the source the codegen-plan trusts.
- **Letting `codegen-plan.md` checkboxes lag execution.** Drift between checkboxes and actual files breaks the file-grain ↔ ticket-grain bridge `state.md` depends on.

## Reference

- [bitwarden/tech-breakdowns repo](https://github.com/bitwarden/tech-breakdowns) — canonical templates and team folders.
- [tech-breakdowns README](https://github.com/bitwarden/tech-breakdowns/blob/main/README.md) — three-phase model, layout, workflow.
- [AI-DLC working guide](https://github.com/awslabs/aidlc-workflows/blob/main/docs/WORKING-WITH-AIDLC.md) — upstream inspiration for the Q→D→A pattern, approval gates, and state-tracking discipline.
- [EDD — Evolutionary Database Design](https://contributing.bitwarden.com/contributing/database-migrations/edd) — referenced in `functional-design.md`'s data-model checklist.
