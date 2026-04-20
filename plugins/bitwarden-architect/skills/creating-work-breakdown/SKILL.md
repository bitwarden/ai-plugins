---
name: creating-work-breakdown
description: This skill should be used when the user asks to "break this plan into tickets", "create a work breakdown", "generate Jira tasks from the plan", "prepare tickets for this feature", or otherwise requests a ticket-ready decomposition of an implementation plan. Converts an implementation plan's phases into discrete, dependency-ordered tasks with file touchpoints and acceptance criteria.
when_to_use: Use after `bitwarden-architect:creating-implementation-plan`, or when an implementation plan already exists and needs to be split into tickets. Preparing work for sprint planning or Jira import, Handing phases off to multiple implementers, Capturing dependencies between tasks explicitly
argument-hints: Path to an existing implementation plan (e.g., ${CLAUDE_PLUGIN_DATA}/plans/pm-32009-new-item-types-server-IMPLEMENTATION-PLAN.md), Jira epic or parent ticket key, Target repository slug, Optional output filename (defaults to {slug}-WORK-BREAKDOWN.md)
---

## Scope

This skill produces one artifact: a work-breakdown document under `${CLAUDE_PLUGIN_DATA}/plans/`. If the user supplies an output filename, use it verbatim. Otherwise default to `{slug}-WORK-BREAKDOWN.md`, reusing the same slug as the corresponding implementation plan so the two files pair up.

It does not do implementation planning. If no plan exists yet, invoke `bitwarden-architect:creating-implementation-plan` first.

## Template

```markdown
# Work Breakdown: [Feature Name]

**Plan:** `{slug}-IMPLEMENTATION-PLAN.md`
**Parent ticket:** [Jira epic or parent, if known]

## Task: [Short imperative title]
**Phase:** [Phase N from the plan]
**Files:** [paths that this task touches]
**Depends on:** [task titles or "none"]
**Acceptance:**
- [ ] [observable, verifiable criterion]
- [ ] [another criterion]
**Notes:** [optional — non-obvious context, risks surfaced during decomposition]

## Task: [next]
...
```

## Decomposition Rules

- **One task, one PR.** If a task is too large to review in a single PR, split it.
- **Order by dependency.** A task that depends on another must come later in the list. Make the dependency explicit in the `Depends on` field.
- **Every task cites files.** "Updates the thing" is not a task. "Updates `src/Foo/Bar.cs:42` and its tests" is.
- **Acceptance criteria are observable.** Prefer "unit test X passes", "endpoint Y returns 200", "flag Z toggles feature" over "works correctly".
- **Preserve the plan's phase boundaries.** A task belongs to exactly one phase. If decomposition reveals a phase that should split, flag it as a plan-level issue rather than papering over it here.
- **Inherit risks from the plan.** Do not re-enumerate plan-level risks per task. If a risk is task-specific (e.g., "depends on external SDK release"), note it in `Notes`.
