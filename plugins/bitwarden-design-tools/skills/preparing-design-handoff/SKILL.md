---
name: preparing-design-handoff
description: Prepare a Bitwarden design handoff — the Figma file in Ready-for-Dev state and the Jira state transitions that go with it. The end-of-In-Design gate / checklist.
when_to_use: Use at the end of the In Design phase before engineering picks the work up. Triggers — "prep handoff", "is this ready to hand off", "what goes in a handoff", "hand this off to engineering", "finish the design phase". Not for Jira-specific state transitions on their own (use `navigating-design-jira-process`); composes that one for the Jira moves and `using-figma` for verifying the Figma file is handoff-ready.
allowed-tools: Skill, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_remote_links, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_issues, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence_cql
---

# Preparing a Design Handoff

This skill is the end-of-In-Design gate. Engineering relies on a consistent set of signals to
know a design is ready to pick up. A handoff missing any of those signals creates downstream
questions and slows the epic into development.

## The handoff is two things, not one

A handoff is finished when both are in place:

1. **The Figma file in Ready-for-Dev state.** Final designs grouped on a single page, with
   sections named to match the engineering stories that will consume them. Sections marked
   "Ready for Dev" in Figma. User-visible strings (toasts, error messages, form verifications,
   email body copy) annotated on the frames. Annotated prototype available.
2. **The Jira state aligned.** Figma file linked in the Epic's "Design" field, sections
   marked Ready for Dev in Figma, and the EM transitions the Epic to `Ready for Dev`. The
   full choreography is in `navigating-design-jira-process`.

If either is missing, the handoff isn't done.

## Prep checklist (before declaring handoff)

- The product initiative or PRD page exists and is current.
- The engineering Epic exists in Jira and the designer is or has been assigned to it.
- Designs have been through critique at 30%, 60%, and 90% and the 90% review has been
  addressed.
- Real-user testing has happened where applicable (this is what 90% is for).
- The Figma file's final-designs page is curated — no scratch pages, no unused frames in the
  Ready-for-Dev surface.
- All user-visible strings are annotated in Figma alongside the frames they apply to.

If any item is missing, surface that before declaring the handoff ready — handoff is not the
moment to discover the 90% review never happened.

## Figma readiness check

Before marking sections Ready for Dev, confirm:

- **Sections aligned to stories.** Each named section maps to a single engineering story.
  Avoid sections that span stories or stories that span multiple sections.
- **Tokens are library-bound.** No raw hex values where a design-system variable exists.
  Compose `using-figma` with `get_variable_defs` to verify.
- **Strings annotated.** Every user-visible string — button labels, error messages, toasts,
  empty states, helper text — is present in the Figma frames or annotations.
- **Edge cases covered.** Empty, error, partial-success, offline, and premium-gated states
  exist on the relevant frames (or are explicitly out of scope and noted).

## Composing with other skills

- **`using-figma`.** Use `get_metadata` to confirm the Ready-for-Dev sections exist with the
  expected names; use `get_variable_defs` to confirm tokens are library-bound rather than raw
  values; use `search_design_system` if a component in the design is suspiciously close to
  one that already exists.
- **`navigating-design-jira-process`.** The Jira moves that go with handoff — link Figma to
  Epic "Design" field, mark Ready for Dev in Figma, EM transitions Epic — live there.
- **`content-style-guide`.** Walk every annotated string through the style guide before
  declaring handoff. Toasts, errors, and form-verification text are the highest-leverage
  place to catch content-style issues before engineering localizes them.

## Common omissions to catch

- **Figma file with no Ready-for-Dev marks.** Engineering can't find what's final. This is
  the most-skipped step.
- **Sections not aligned to stories.** Each story should map to a Figma section whose
  content is _only_ that story. Mismatch creates ambiguity at review time.
- **Missing string annotations.** Engineering will ask for strings the moment they pick the
  Epic up. Annotate them in Figma alongside the frames before declaring handoff — don't
  defer to engineering to invent copy.
- **Edge states absent.** Empty, error, partial-success, offline, premium-gated. If they're
  out of scope, say so explicitly on the frames or in the dev-support comments.

## Output format

When asked to help prep a handoff:

1. **Prep checklist** — what's in place, what's missing.
2. **Figma readiness check** — section-to-story alignment, token binding, string
   annotations, edge states.
3. **Jira moves** — the specific status transitions and Figma links to apply (link to Epic
   "Design" field, mark sections Ready for Dev, EM transitions Epic). Defer to
   `navigating-design-jira-process` for the canonical choreography.

Always end with the explicit go/no-go: _is this handoff actually ready?_
