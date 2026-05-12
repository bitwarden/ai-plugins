# Bitwarden Shepherd Plugin

## Overview

Champion-of-a-technical-strategy agent for Bitwarden. The shepherd is the Staff+ engineer who holds a thesis about something Bitwarden should change in its software, its patterns, its architecture, or its engineering practices — and who takes accountability for shaping that thesis into something the organization can act on, earning the support to pursue it, and seeing it through to durable adoption.

The role spans two connected acts. First, you shepherd a Technical Strategy Idea through Architecture's evaluation — peer review, Stakeholder & Engagement Map, Architecture Council, quarterly prioritization — until it earns intake into the Software Initiative Funnel. Then, you shepherd the resulting initiative through five funnel phases — Identification, Research, Proof of Concept, Scoping & Commitment, Implementation — until the thesis is real, adopted by teams, and durable beyond your involvement. The mechanics — Architectural Assessment, PoC, ADR, High-Level Architecture Plan, child epics, cross-team coordination, leadership reporting — are how the thesis becomes reality. They are not what you are.

This plugin is the symmetric counterpart to `bitwarden-tech-lead`. Tech-lead represents a team inside an initiative; shepherd owns the initiative across teams, and the idea upstream of it. Both compose the agent-neutral delivery-lifecycle skills in `bitwarden-delivery-tools` so the funnel-mechanics and work-transition content lives in one place.

## Agent

| Agent                | What It Does                                                                                                                                                                                                                                                                                                                                                                                                                            |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bitwarden-shepherd` | Champion of a technical strategy. Shepherds a Technical Strategy Idea through Architecture's evaluation into the Software Initiative Funnel, then drives the resulting initiative across all five funnel phases to adoption. Produces the Architectural Assessment, PoC, ADR, High-Level Architecture Plan, and child epics; coordinates cross-team consistency; reports to leadership — while teams own their breakdown and execution. |

## Skills

| Skill                                      | What It Does                                                                                                                                                                                                                                                                                                                                               |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `championing-a-strategy-idea`              | Primary-Owner playbook for the pre-funnel arc — taking accountability for a specific Technical Strategy Idea, pairing with a peer reviewer, completing the Stakeholder & Engagement Map honestly, presenting at Architecture Council, earning funnel intake at quarterly prioritization, and running the Adoption Retrospective at Implementation handoff. |
| `shepherding-an-initiative`                | End-to-end umbrella playbook covering all five funnel phases, effort budgets, decision gates, and shepherd-vs-team ownership boundaries. Picks up after an idea has earned funnel intake. Dispatches into the four phase-deep skills.                                                                                                                      |
| `running-an-architectural-assessment`      | Phase 2 (Research) deep dive — stakeholder interviews, current-state analysis with quantified impact, generating 2–4 solution options, drafting the Architectural Assessment, socializing with stakeholders.                                                                                                                                               |
| `running-a-proof-of-concept`               | Phase 3 (PoC) deep dive — choosing a representative-but-contained PoC area in coordination with the owning team, building the framework and example implementations, Architecture Council walkthrough, drafting the ADR.                                                                                                                                   |
| `scoping-and-handing-off-to-teams`         | Phase 4 (Scoping & Commitment) deep dive — High-Level Architecture Plan, child epics, per-team handoff meeting structure, holding the line against shepherd-written stories, leadership commitment, operational prioritization with capacity.                                                                                                              |
| `coordinating-implementation-across-teams` | Phase 5 (Implementation) deep dive — communication channels, kickoff, review-for-consistency vs. detailed code review, drift detection, progress reporting cadence, knowledge transfer, retrospective, post-implementation impact measurement.                                                                                                             |
| `curating-the-strategy-ideas-backlog`      | Peer-Reviewer and portfolio-curator side of the TSI Shepherding Model — serving as constructive challenge function for someone else's idea, weekly triage, monthly score updates, mid-quarter backlog management, quarterly prioritization with engineering leadership.                                                                                    |

## Cross-Plugin Integration

| Plugin                        | How It's Used                                                                                                                                                                                                                                                                                    |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `bitwarden-delivery-tools`    | Composed (not duplicated). `navigating-the-initiative-funnel` for the agent-neutral phase-by-phase boundary view; `running-work-transitions` for the Phase 4→5 handoff mechanics on the originating side (Preparation, Sessions, Support Period, Pulse Check, Retrospective, Closure).           |
| `bitwarden-tech-lead`         | Team-side counterpart. Use `architecting-solutions` for team-scope architectural judgment when an initiative lands inside a team's codebase. Use `contributing-to-technical-strategy` to understand the team-contributor perspective on TSIs (this plugin covers the Architecture-curator side). |
| `bitwarden-security-engineer` | `bitwarden-security-context` for P01–P06 principles, `reviewing-security-architecture` for architecture pattern validation, `threat-modeling` for initiatives touching crypto, auth, or zero-knowledge boundaries.                                                                               |
| `bitwarden-atlassian-tools`   | Jira issue research and Confluence page access for the funnel, the Work Transition Playbook, the Operating Model, the TSI backlog, and the Idea-Based Initiatives pages this plugin's skills reference throughout.                                                                               |

All cross-plugin skills are required because the plugin relies on them for a complete shepherd workflow.

## Installation

```bash
/plugin install bitwarden-shepherd@bitwarden-marketplace
```

Install `bitwarden-delivery-tools` alongside it (the funnel-mechanics and work-transition skills live there):

```bash
/plugin install bitwarden-delivery-tools@bitwarden-marketplace
```

## Usage

The shepherd agent activates when championing a Technical Strategy Idea, driving an approved initiative through any phase of the funnel, running an architectural assessment or PoC, drafting an ADR, handing off epics to teams, coordinating an in-flight initiative across teams, or curating the upstream TSI backlog:

```
I think Bitwarden should standardize observability instrumentation across services. I want to take this on. Walk me through the championing arc — how do I file, who do I pair with, what does the Stakeholder & Engagement Map need to look like before this can go to Research?
```

```
I just got assigned to shepherd ARCH-123. Walk me through Phase 1 — what do I produce, and what do I avoid pre-scoping?
```

```
We're at the end of Research for the observability initiative. Help me structure the Architectural Assessment and prep for the leadership review.
```

```
Phase 4 handoff with the Vault team is tomorrow. Help me build the agenda and the per-team architecture-plan section.
```

```
TypeScript migration is 60% through Implementation and two teams are interpreting the error pattern differently. How do I surface this without taking over their code review?
```

```
I'm reviewing a new TSI a tech lead just filed. The Stakeholder & Engagement Map's friction-points field is empty. What do I push back on?
```

## Related Plugins

- **`bitwarden-tech-lead`** — the team-side counterpart of this role. Use that plugin when representing a team inside an initiative (receiving the epic, breaking it down, running it in the team's roadmap). Use this plugin when owning the initiative across teams.
- **`bitwarden-delivery-tools`** — required. Provides the agent-neutral funnel and work-transition skills that this plugin composes.

## References

- [Software Initiative Funnel](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/584515614)
- [Work Transition Playbook](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2521038855)
- [Architecture / Engineering Operating Model](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/1286963201)
- [Technical Strategy Ideas](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2344517656)
- [Idea-Based Initiatives](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/2785181779)
- [Architecture Council](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/751698031)
- [Bitwarden ADR Template](https://contributing.bitwarden.com/architecture/adr/)
- [Bitwarden Security Definitions](https://contributing.bitwarden.com/architecture/security/definitions)
- [Bitwarden Security Principles](https://contributing.bitwarden.com/architecture/security/principles/)
- [Bitwarden Contributing Guidelines](https://contributing.bitwarden.com/contributing/)
