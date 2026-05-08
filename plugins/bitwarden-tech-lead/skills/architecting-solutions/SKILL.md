---
name: architecting-solutions
description: Framework for architecting solutions inside a team's domain while staying coherent with Bitwarden's holistic architecture. Covers security mindset, blast radius assessment, architectural judgment, Bitwarden-specific constraints, working with the architecture group, and working with initiative shepherds. Use when planning a solution, reviewing architecture within a team's scope, assessing blast radius, evaluating trade-offs, or deciding whether a choice needs architecture-group input.
allowed-tools: Skill, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_remote_links, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_issues, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence_cql
---

## Security Mindset

Bitwarden is a password manager — security isn't a feature, it's the product. Every design decision is a security decision.

- **Threat model early.** Before approving an approach, ask: what can an attacker reach from here? A dedicated threat-modeling skill exists for deep analysis — use it for complex features.
- **Classify data touch points.** Know which fields are encrypted, which are plaintext, and which cross trust boundaries. Never add a new path for sensitive data without encryption at rest and in transit.
- **Audit trail by default.** Sensitive operations must be observable after the fact. If it can't be audited, it shouldn't ship.
- **Fail closed.** When a security check is ambiguous or a dependency is unavailable, deny access. Never default to permissive.

## Before Advocating for a Design

- **Map the blast radius:** Which clients, services, and databases does this change touch?
- **Read first:** Verify existing patterns before introducing new ones. The codebase already solved many problems — find those solutions first.
- **Ask "who else?"** Other teams, other clients, self-hosted customers, open-source contributors — all are affected by shared code changes.
- **Survivability test:** Would this design hold up in a production incident review? If not, simplify.
- **When requirements are ambiguous, clarify.** Don't invent requirements to fill gaps — ask the human.

## Architectural Judgment

- **Prefer boring technology** for critical paths. Proven and predictable beats clever and novel.
- **Match complexity to scope.** Don't build a framework for a feature. Three similar lines of code beat a premature abstraction.
- **Design for the team.** Code lives longer than context — optimize for the next engineer reading this, not the one writing it.
- **Document tech debt, don't silently fix it.** Unscoped refactors create unwanted risk. Identify the finding and report it to the human.
- **Complement existing patterns.** New code should work alongside what's already there. When proposing new approaches, show how they coexist with current patterns — DO NOT force a rewrite to adopt them.

## Bitwarden-Specific Principles

- **Multi-client reality:** Changes ripple across web, browser, desktop, CLI, and self-hosted deployments. Shared code must work for all clients — including headless ones with different runtime constraints.
- **Dual data-access parity:** Every database change requires parallel implementations across database backends. Never ship one without the other.
- **Open-source stewardship:** Code is public. Architectural decisions, commit messages, and PR discussions are visible to the community. Write them with that audience in mind.
- **Self-hosted constraint:** Features must degrade gracefully for self-hosted customers who may run older versions or different database backends.
- **Version matrix (V +/- 2):** The server must support clients up to 2 major versions behind — and this is enforced by blocking outdated clients. Every API change must be additive: new fields are optional, responses degrade gracefully, and nothing breaks for a client that hasn't updated yet.
- **No formal API versioning:** Breaking changes are actively discouraged. Without URL-path versioning in place, API models trend toward optional-everywhere to preserve backwards compatibility. Design new endpoints with this constraint in mind — don't add required fields to existing endpoints.

## Working with the Architecture Group (Holistic Coherence)

Teams have autonomy over decisions inside their domain. Architecture doesn't gate-keep team-level work. What Architecture does is maintain the holistic view — the portfolio of cross-cutting initiatives, the patterns that span teams, the decisions that will be expensive to change later. The job at the team level is to recognize when a choice has implications that benefit from that wider view, and pull Architecture in before — not after — the team ships.

Watch for the five signals that warrant Architecture involvement (from the [Architecture / Engineering Operating Model](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/1286963201)):

- **Interface or contract definition.** The work defines an API, event schema, SDK surface, or pattern that other teams will build against or adopt.
- **Structural decisions costly to change later.** Data model choices, service boundaries, protocol selection, auth integration — decisions whose cost compounds if they're wrong.
- **Overlap with an existing initiative.** Architecture is already shepherding something adjacent, even if the connection isn't obvious. A quick check against the Now / Next / Later portfolio can save months of rework.
- **New precedent.** Doing something Bitwarden hasn't done before in a way that will likely be repeated by others.
- **External-facing output.** CLIs, SDKs, or public APIs that customers or integrators will interact with directly.

If none of those apply, decide inside the team and move. If any of them apply, surface it — through the team's EM into the monthly Architecture/Platform sync, by attending Architecture Council, or by filing a Technical Strategy Idea (see `Skill(contributing-to-technical-strategy)`).

The framing to hold: Architecture's role is input and portfolio tracking, not approval. Pulling them in early is cheaper for everyone than letting them discover the work downstream.

## Working with the Initiative Shepherd

When a team is receiving an initiative epic, the shepherd is the team's counterpart. They are typically a Staff+ engineer who has owned the initiative since Identification — they wrote the Architectural Assessment, built the PoC, drafted the ADR, and got executive commitment. For smaller-scope initiatives that live largely inside one team's domain or extend only to a single adjacent team, the tech lead may be the shepherd; in that case the principles below describe the role being filled for the receiving team, not someone else's role being operated alongside. What the shepherd does **not** do — regardless of who fills the role — is write the receiving team's stories or run their implementation.

The clean division during Scoping & Commitment and Implementation (from the [Software Initiative Funnel](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/584515614)):

- **The shepherd owns:** the initiative vision, the ADR, the epic definition, cross-team consistency, leadership reporting, and the decision to pause/pivot the whole effort.
- **The team owns:** story breakdown, acceptance criteria, sizing, implementation sequencing, and the team's PRs.

Expect and insist on the handoff meeting: shepherd presents PoC findings and architecture plan, team does Q&A, team commits to a breakdown date. After that, the team does the breakdown — not the shepherd. The shepherd is available for approach questions, reviews 1–2 early PRs from the team for alignment with the PoC pattern, and surfaces cross-team dependencies. Everything else belongs to the team.

Two failure modes to avoid:

- **The shepherd writes the team's stories.** Stories the team didn't write are stories the team won't own. Insist on a handoff meeting and a team breakdown session.
- **The team drifts from the PoC pattern without flagging it.** Drift across teams is exactly what the shepherd is there to prevent. If deviation emerges, tell the shepherd before merging, not after.

`Skill(navigating-the-initiative-funnel)` covers the phase-by-phase mechanics in depth. This section is the working principle.

## Red Flags to Surface

- Over-engineering for hypothetical requirements (YAGNI)
- Mixing concerns across architectural boundaries (e.g., UI logic in services, data access in controllers)
- Silent behavior changes in shared libraries (`libs/common`, `src/Core`)
- Missing test coverage for new code paths
- Security shortcuts in the name of velocity
- Refactors bundled with feature work without explicit scope approval
- Work that should have been a Technical Strategy Idea slipping in as team-level scope because surfacing it feels like overhead
- Accepting an initiative epic without capacity explicitly allocated by the team's EM and engineering leadership
