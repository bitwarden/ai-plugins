---
name: facilitating-design-critique
description: Run or participate in a Bitwarden design critique session — the weekly team critique and one-off product design reviews — grounded in the team's published etiquette guide and the Product Design Review Guidelines.
when_to_use: Use when the task is about the *meeting itself* rather than the substance of the feedback. Triggers — "facilitate critique", "run a design review", "present at critique", "prep for design critique", "set up a design review meeting". Not for the substance of feedback (use `design-review`).
allowed-tools: Skill, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence_cql
---

# Facilitating Design Critique

This skill grounds the _facilitation_ of design critique in two Bitwarden sources of truth:
the [Weekly Design Critique & Etiquette Quick Guide](https://bitwarden.atlassian.net/wiki/spaces/PROD/pages/2329542659)
and the [Product Design Review Guidelines](https://bitwarden.atlassian.net/wiki/spaces/PROD/pages/469925913).
Read the Confluence pages directly when prepping a real session — the `get_confluence_page` MCP
tool fetches them. This skill is the practitioner's quick reference, not a replacement for
those pages.

> **Cross-plugin dependency.** When the design under discussion lives in a Figma file, this
> skill composes `using-figma` from the `bitwarden-design-tools` plugin — install it
> alongside `bitwarden-designer` for the full composition to work.

## Pick the right mode

Bitwarden runs two distinct kinds of critique. Treat them differently.

- **Weekly Design Critique.** Recurring team session. Presenter sets context for a piece of
  work-in-progress; the room asks clarifying questions, then gives feedback. Lightweight
  cadence, peer-to-peer, the presenter decides what to apply.
- **Product Design Review.** Stakeholder review for a specific design proposal. Invites
  product, engineering, research as relevant. Heavier facilitation: scope, criteria, briefing,
  walkthrough, structured feedback collection.

Ask which mode the user means before suggesting a structure. The roles, prep, and time
investment differ.

## Roles in the room

- **Presenter.** Sets context: the goal of the design, the constraints, the open questions,
  and **what kind of feedback they want.** The presenter owns what they apply.
- **Facilitator.** Shepherds the session: redirects when discussion drifts, holds a "parking
  lot" for side issues that aren't central to the scope, and protects the presenter's stated
  feedback ask. In weekly critique this is usually a rotating role; in product design reviews
  it's an explicit appointment.
- **Participants.** Ask before judging. Share observations, concerns, and ideas. Tied to user
  and product goals, not personal preference. Don't dominate.

The Weekly Design Critique Quick Guide reduces this to: **critique the work, support the
person, improve the product.**

## Session shape

Both modes share the same arc; the depth differs.

1. **Presenter sets context.** Goal, constraints, open questions, the kind of feedback wanted.
   In product design reviews, this also covers background and the "why" — relevant
   documentation, early iterations, user research findings, business goals, end-user goals.
2. **Clarifying questions.** Ask before judging or suggesting. The room doesn't critique
   what it doesn't yet understand.
3. **Walkthrough and feedback.** Presenter walks the design. Participants share feedback tied
   to user impact, product goals, standards, or technical constraints.
4. **Wrap-up.** Key takeaways and next steps. In product design reviews, document feedback for
   future reference in a preferred format and prioritize issues.

## Feedback etiquette — do and don't

**Do**

- Be specific and constructive.
- Explain _why_ something works or doesn't.
- Ask questions to understand intent.
- Call out what's working, not just issues.
- Respect time and stay on topic.

**Don't**

- Make it personal.
- Give vague opinions like "I don't like it."
- Dominate the conversation.
- Jump to solutions without context.
- Design on the spot — describe the gap, let the designer solve.

A useful set of opening phrases when the room stalls:

- "What problem is this solving for the user?"
- "I'm unclear about [blank] — could you explain?"
- "Have we considered [blank] as an alternative?"
- "This part feels strong because [blank]."

## Common participation traps

- **"I don't like it."** Not feedback. Tie the observation to a user need, business need,
  standard, convention, or technical constraint — or skip it.
- **"You are not the user."** Personal bias presented as universal experience. Surface it as
  bias, not as a finding.
- **Asking _why_ badly.** "Why did you do that?" puts the designer on the defensive. "What
  are you trying to achieve by doing X?" gets at the same thing without the edge.
- **Solutioning during the review.** A well-meaning suggestion can cascade through a design.
  Describe the gap. Let the designer weigh the fix offline.
- **Negative-only feedback.** Designers move in the direction of what's working as much as
  away from what isn't. Lead with strengths, then issues.
- **The unconsidered consequence.** "Could we just…" requests often spiral. When a suggestion
  feels simple, name the cascading effects you can see and let the designer decide.

## Facilitator playbook for product design reviews

When facilitating (not just participating):

- **Before the review.** Pick a method to collect feedback. Identify and invite the right
  stakeholders. Confirm the presenter has the briefing material ready (goals, background,
  early iterations, user research, business and end-user goals).
- **During the review.** Define scope. Set feedback expectations. Surface the "why." Run the
  walkthrough. Open the floor with the scope and criteria already named. Document feedback in
  the agreed format. Hold the parking lot for off-scope discussion.
- **After the review.** Prioritize the issues raised. Confirm next steps with the presenter.

## Composing with other skills

- **`design-review`.** During the session, the _substance_ of feedback runs through
  `design-review` — the 30/60/90 framework, the Code of Conduct, and (at 60%/90%) the
  `content-style-guide`. This skill shapes the room; `design-review` shapes what's said.
- **`using-figma`.** When the presentation is from a Figma file, use `using-figma` to bring
  the design context into the discussion (screenshot, metadata, variables) without
  context-bombing the room.

## Output format

When asked to help prep or run a critique:

1. **Mode** — Weekly Critique or Product Design Review.
2. **Roles** — who's facilitating, who's presenting, who's participating.
3. **Presenter's setup** — goal, constraints, open questions, the feedback ask.
4. **Agenda / arc** — context → clarifying questions → walkthrough → feedback → wrap-up.
5. **Watch-outs for the room** — the specific etiquette traps likely to come up given the
   work being presented.

Always end with the wrap-up question explicit: _what is the presenter going to do next?_
