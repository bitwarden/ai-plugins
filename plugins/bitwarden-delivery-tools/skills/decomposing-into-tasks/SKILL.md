---
name: decomposing-into-tasks
description: Decompose a Bitwarden Tech Breakdown's Plan into Task rows that are ready to become Jira stories or tasks. Use after the Plan section's file and module list is concrete. Phrasings like "decompose into tasks", "break this into stories", "split into Jira tickets", "draft the tasks table".
allowed-tools: Read, Edit, Write, Grep, Glob
---

# Decomposing into Tasks

## Overview

Turn the Plan section of a Bitwarden Tech Breakdown into a Tasks table. Each row is one future Jira story scoped tightly enough that the engineer picking it up can recognize when they are done without re-reading the rest of the breakdown.

## Key Principles

- **One row, one Jira story.** If a row would become multiple stories, split it.
- **Scope to "done is recognizable."** The Ticket Shape must let a stranger see the finish line without re-reading the Plan.
- **Concrete files, not generalities.** Affected files are real paths, directories, or crates — never "various" or "TBD".
- **Stand-alone rows.** Tasks may be picked up out of order; no row may rely on `Similar to Task N` for its content.

## Inputs

- The breakdown's **Plan** section, with a concrete file and module list from the per-layer-impact activity.
- The breakdown's **Specification**, to confirm every What/Why item maps to at least one Task row.

## Output: Task rows

Each unit is a future Jira story, with:

- **Title**
- **Affected files** (or directories / crates)
- **Ticket Shape** — the implementation-level acceptance ("the engineer working this story knows when they're done")
- **Brief description**
- **Dependencies** on other rows

_Captured in the breakdown's **Tasks** section._

## Heuristics

**Row count.** If the count exceeds 10, surface to the user: _"Tasks section has N rows — past the 10-task heuristic. Have you considered splitting along a natural seam (sequential phase, independently shippable subset, interface boundary)?"_ Soft prompt, not a block. Tightly coupled work that genuinely cannot split is allowed.

**No placeholders.** A task row is reviewer-ready only if a stranger could pick it up out of order. These patterns are plan failures; flag and rewrite them:

- `TBD`, `TODO`, "decide later", "figure out during implementation"
- "Add appropriate error handling" or "handle edge cases" without naming which ones
- "Wire up to existing service" without naming the service or file
- "Update tests" without naming which test files or what they should cover
- "Similar to Task N" — restate concretely; tasks may be picked up out of order
- Ticket Shape that restates the Title without naming an implementation-level acceptance
- Affected files listed as "various" or "TBD"

## What this skill does NOT do

- **It does not create Jira stories.** Story creation is `Skill(syncing-tasks-with-jira)`.
- **It does not modify the Plan section.** If decomposition surfaces a gap in the Plan, hand back to `Skill(developing-the-breakdown-plan)` to fill it before continuing.
- **It does not pick task assignees or sprint placement.** Those are refinement-ritual decisions.
