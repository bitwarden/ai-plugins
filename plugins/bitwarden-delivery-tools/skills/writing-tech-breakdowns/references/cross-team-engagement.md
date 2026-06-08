# Cross-team Engagement — Subsections, Models, and Signoff Table

Load this reference when working through the Cross-team engagement section of a breakdown — identifying affected teams, walking the three template subsections, proposing collaboration models, and building the signoff table. The parent SKILL.md keeps the lifecycle spine; this file carries the per-impact mechanics.

## The three cross-team engagement subsections

The template splits cross-team work into three explicit subsections. Walk each before considering the section complete.

**Consuming other teams' APIs.** For each external service or component used: name the team, the interface, the assumed behavior, and any known constraints or roadmap risk on the providing team's side. Check publicly visible tech debt indicators, recent incidents, or planned deprecations on the providing team. If concerns exist, surface them as Clarifications Log entries. If the consumption requires changes or extensions to the owning team's API, **propose a collaboration model** (see below) — pure consumption of an unchanged API is the one case where no model is needed.

**Changes required in other teams' code.** For each file or module outside the team's domain that needs to change: name the team, the file or module, the change, the **proposed collaboration model**, and the Jira items. Two specific rules:

- **Mobile changes** must be defined as separate Jira Tasks/Stories on the Mobile team's board. Mobile parity is almost always File a Ticket; the Mobile team writes its own breakdown for the screens.
- **Components, services, or files outside the team's domain** — post on the owning team's public Slack channel (not DMs, tagging the human TL/EM) to evaluate impact before adding them to the signoff table. Surprise signoff requests don't work well. If a sibling team's breakdown for related work already exists, link it.

**Cross-team sequencing & ordering.** If this change delivers an API or service for another team, follow the **interface-first pattern**:

- Define the interface early so the consuming team can code against it while implementation is in flight.
- Consult the consuming team twice — once at design (after the interface is defined in the breakdown), and again at PR (after the implementation lands). Both touchpoints belong on the signoff list.
- **Propose a collaboration model** for landing the interface in the owning team's code (often Internal Open-Source, but let the change shape pick).

If the order matters in the other direction (the team needs another team's work to land first), capture it in Coordination notes so the dependency is explicit.

## Collaboration models per impact

Every cross-team impact that involves work must name a **collaboration model** — File a Ticket, Internal Open-Source, or Embedded Expert (the three Bitwarden-adopted patterns from Pete Hodgson's cross-team collaboration patterns). The model determines who writes the code, who carries the planning load, and how the request flows; leaving it implicit defers the question to signoff or, worse, mid-implementation. Pure consumption of an existing, unchanged API is the one case where no model is required.

**Use `Skill(choosing-collaboration-model)` to pick a model for each impact.** That skill walks the change shape through a depth/familiarity/history evaluation, scans the owning team's in-flight breakdowns and open PRs for collision risk, surfaces escape hatches, and outputs a recommendation with reasoning, a runner-up, and the velocity findings. This section consumes the recommendation; it doesn't re-derive it.

Two rules on top of the chooser:

- **The model is a joint decision.** The driving team proposes the model in the breakdown; the owning team confirms or counter-proposes during signoff. A model that lands in `Accepted` without owning-team confirmation isn't a working agreement, it's a guess. Treat counter-proposals as material design changes — update the breakdown and re-circulate to anyone who has already signed off.
- **File a Ticket transfers planning load, not just execution.** If the owning team accepts a File a Ticket impact, they take the work into their own domain — their own breakdown if it warrants one, their own epic and stories. The driving team's roadmap looks lighter; the owning team's gets heavier. Confirm absorption before defaulting to File a Ticket.

Surface the proposed model in the signoff table's `Interface` cell with reasoning. Once signoff lands, mark the row as confirmed (e.g., `Model: Internal Open-Source — confirmed @platform-tl, 2026-05-15`).

## The signoff table

A worked example with both in-flight and fully-signed-off shapes lives at `examples/signoff-table.md`. Use it as a shape reference for what good cells look like and what a healthy table looks like at `Proposed` versus `Accepted`.

The template's five columns:

| Column                   | What goes in it                                                                                                                                                                                                                                                                                                                                                            |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Team**                 | The owning team's name. One row per team — combine sub-interfaces under that row's `Interface` cell.                                                                                                                                                                                                                                                                       |
| **Interface**            | What this breakdown asks of the other team, the **proposed collaboration model**, and brief reasoning. Specific enough that an engineer on the other team can react without re-reading the whole breakdown. The model is a proposal until signoff lands; mark it confirmed once it does. Pure consumption of an unchanged API is the one case where the model is optional. |
| **Associated breakdown** | Link to the sibling breakdown if the other team is producing their own. Empty when they aren't (common for FYI-level rows).                                                                                                                                                                                                                                                |
| **Signoff**              | Named human + date. Not "the team" — a specific person. The template renders this as a checkbox; capture the human + date inline.                                                                                                                                                                                                                                          |

Every row in the table is a signoff the breakdown needs before moving to `Accepted`. If a team only needs to be informed and doesn't need to sign off on the design, they don't belong in the table; mention them in Coordination notes or post an FYI in their public Slack channel instead.

## Coordination notes

The template's free-form `Coordination notes` subsection captures anything about the cross-team seams that isn't obvious from the table:

- Which team's PR lands first.
- Whether a temporary API stub is needed.
- Whether one team's work needs to land in a feature branch.
- Sequencing constraints outside the standard interface-first pattern.
- Counter-proposals from owning teams on the collaboration model.
- Collisions surfaced by the in-flight scan and how the sequencing accounts for them.

Empty is fine when the table is self-explanatory; vague is not.
