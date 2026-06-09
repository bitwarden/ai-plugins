# Edge Cases

Load this reference when an unusual condition surfaces during Triage or Execute — it carries the per-condition response patterns.

The parent SKILL.md keeps the main flow (CREATE / MATCH-AND-SYNC / UPDATE-from-breakdown / UPDATE-from-jira / NO-CHANGE / CONFLICT / ORPHANED). When you hit one of the conditions below, load this file and follow the matching subsection.

## The epic key in the filename does not match the Status block

Ask the user which is correct. Filename is canonical; Status block should match. Do not guess.

## A row has no story key but a story exists with a very similar title

Treat as MATCH-AND-SYNC if confidence is high (verbatim title match with or without prefix); otherwise surface to the user as a manual-pair candidate.

## Existing story has substantive content already (first-creation case)

If the existing story has populated `Technical breakdown` (not a placeholder), ask before overwriting: _"PM-XXXXX already has content in `Technical breakdown`. Append the breakdown details below it, replace it entirely, or skip this row?"_ Default to appending.

## The Jira project requires fields not in the breakdown

Use the engineer's Jira authoring tool to check required fields for the issue type. If any required field has no source in the breakdown, ask the user for values before creating. Do not guess.

## The team uses a non-standard Tasks column layout

Read the breakdown's Tasks section as-is and ask the user to clarify column mappings. Do not assume.

## Jira refinement pulled a change that affects a cross-team-signed-off interface

Surface at the end of Phase 5 with the lifecycle-reset flag. Recommend moving the breakdown back to `Proposed` and re-running affected signoffs. This skill does not flip status; it surfaces the requirement so the user can invoke the lifecycle skill that handles transitions.
