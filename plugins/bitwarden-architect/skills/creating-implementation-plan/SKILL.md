---
name: creating-implementation-plan
description: This skill should be used when the user asks to "create an implementation plan", "produce a plan for PM-XXXX", "write an implementation plan", "break this feature into phases", or otherwise requests a structured plan artifact ready for handoff to an implementer. Produces a markdown plan with pattern anchors, blast radius, phased task breakdown, risks, and open questions.
when_to_use: Use after `bitwarden-architect:architecting-solutions`, or when a solution has already been identified and needs to be planned. Architectural decisions are made and a structured plan artifact is required, Handoff to an implementer is imminent, Converting a refined spec into a phased engineering plan
argument-hints: Jira ticket key (e.g., PM-XXXX), Architectural decisions or design notes from prior reasoning, Target repository slug (server, clients, sdk-internal, android, etc.), Confluence page URL or plain-text feature description
---

## Scope

This skill produces one artifact: an implementation plan at `${CLAUDE_PLUGIN_DATA}/plans/{slug}-IMPLEMENTATION-PLAN.md`. Derive the slug from ticket + target (e.g., `pm-32009-new-item-types-server`). Create the output directory if needed.

It does not do architectural thinking. If the design has not yet been reasoned through — principles, blast radius, trade-offs — invoke `bitwarden-architect:architecting-solutions` first and carry its conclusions into the plan.

## Per-Repo Planning Skills Take Precedence

Before using the default template, look in `<repo>/.claude/skills/` for a planning-related skill. If one exists, defer the artifact shape to it — invoke via the `Skill` tool if available, otherwise read the `SKILL.md` directly. Per-repo planning skills own platform-specific phase conventions, test commands, and definition-of-done.

## Default Template

```markdown
# Implementation Plan: [Feature Name]

## Current State
What's already shipped (verify against the working tree, not the ticket). Pattern anchors with `file:line`.

## Blast Radius
Affected modules — Primary / Secondary / No-change-verified.

## Design
Type model, interfaces, data flow.

## Phases
Dependency-ordered, each one PR. Per phase: tasks, files, acceptance.

## Risks & Open Questions
Likelihood × impact + mitigation. Tech debt surfaced (don't silently fix). Questions for the human (don't invent answers).
```

## Downstream Handoff

When phases are ready to become tickets, invoke `bitwarden-architect:creating-work-breakdown`.
