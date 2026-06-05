---
name: evolving-design-system-components
description: Propose a new UI pattern or modify an existing Design System component per Bitwarden's published governance process — design-team alignment, Core vs. Recipe/Snowflake decision with UI Foundation, Figma branching and property conventions, review gates, merge timing.
when_to_use: Use when a task touches the Component Library or its Figma source of truth. Triggers — "add a component", "create a new design pattern", "modify a component", "should this be in the Component Library", "make this a core component", "is this a snowflake", "Figma component properties". Composes `using-figma` for searching and inspecting the library. Not for handoff prep on a specific project (use `preparing-design-handoff`).
allowed-tools: Skill, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_issue_remote_links, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_issues, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__get_confluence_page_comments, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence, mcp__plugin_bitwarden-atlassian-tools_bitwarden-atlassian__search_confluence_cql
---

# Evolving Design System Components

This skill grounds Component Library work in two Bitwarden governance pages:
[Creating new design patterns](https://bitwarden.atlassian.net/wiki/spaces/PROD/pages/665780251)
and
[Modifying an existing Design System component](https://bitwarden.atlassian.net/wiki/spaces/PROD/pages/1804206168).
Read the canonical pages via `get_confluence_page` before driving a real proposal — they evolve
faster than this skill, and they link to template Figma files and engineering processes
referenced below. Figma conventions (property ordering, naming) live in
`references/figma-conventions.md`.

## The two paths

There are two governance flows. They share a beginning but diverge.

- **Creating a new pattern.** A pattern that doesn't yet exist. Path forks at "is this a
  Core Component, or a Recipe/Snowflake?" based on use cases and complexity.
- **Modifying an existing component.** A pattern that already exists. Always passes through
  the UI Foundation team because instances across the product are affected.

The skill walks both. Confirm which one applies before recommending steps — they have different
review gates.

## Step 1: Search first, then propose

Before either path, check whether the pattern already exists. The most common false-positive
of "we need a new component" is "this already exists in the library and the designer hadn't
found it."

Use `search_design_system` and `get_libraries` from `using-figma`. If a near match is found,
the question becomes whether to use it as-is, modify it (path B), or propose a new variant
under it. If no match, proceed.

## Step 2: Identify the need with the team

For both paths, the design team aligns first — before engineering is involved. From the
Confluence pages:

- The designer identifies the need and creates a draft of the new or modified pattern in a
  feature file.
- The designer shares with the design team — group iteration or independent draft followed
  by team critique, depending on timeline.
- The design team reviews against three or four questions, depending on the path:

**For a new pattern:**

- What existing patterns have been considered? Why don't they work?
- What value does the new pattern bring?
- Does it follow existing design / brand guidelines?
- What are other use cases? Can it be used in multiple places?

**For a modification:**

- Does it improve visual appeal?
- Does it expand the use cases for the component?
- Is it in line with other UI patterns?
- How will it affect instances of the component across the product?
- What other components or patterns might be affected?

The team aligns on whether to move forward before the proposal goes further. There is a
[Figma template for new pattern discussion](https://www.figma.com/board/Z9fDCjQkUmV1pRBkBJ2gW2/Template---New-Pattern-Proposal)
linked from the Creating-new-design-patterns page; surface it when the proposer doesn't have a
discussion structure of their own.

## Step 3 (new patterns only): Core vs. Recipe/Snowflake

This decision is made with the UI Foundation team — never unilaterally by the proposing
designer.

- **Core Component Library candidate.** Many use cases, or too complex for a single feature
  team to maintain. Becomes a first-class library component owned by UI Foundation.
- **Recipe / Snowflake.** Few use cases, or specific to a feature surface. Owned by the
  feature team that built it. Still added to the Figma library so other designers can find it.

Schedule the conversation with UI Foundation. Walk the use cases. Defer to their call on
ownership. The Confluence page references the engineering side at
[Creating a New Component](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/181109127/Creating+a+New+Component) —
read that page when the Core path is taken.

## Step 4: Build it in the Figma library

The Figma side of the process is opinionated. The conventions — property ordering, naming,
required states, documentation pattern — are in `references/figma-conventions.md`. The
high-level moves:

- Open the Tailwind Component Library Figma file.
- Create a new branch named after the component / pattern.
- Add the new (or modified) UI pattern as a Figma Component, on a dedicated page for new
  components or in the existing component's page for modifications.
- For interactive components, ensure at minimum: default, hover, focus, active (where
  applicable), disabled (where applicable).
- Name Figma properties per the [CL API design docs](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/619511828/Establish+common+language)
  and existing Figma property patterns. **Property order matters** — see
  `references/figma-conventions.md`.
- Create a component-documentation frame next to the component with usage, behavior, variants,
  and accessibility notes. Convention is to copy and adapt an existing component's docs
  rather than build from scratch.
- For modifications, leave a Figma comment on each changed component noting what changed.

## Step 5: Review gates

- **New patterns.** Send the branch to the Design team for review.
- **Modifications.** Send the branch to the Design team **AND** review during a team sync.
  **At least 2 other designers must approve** before merging.
- Review changes with the UI Foundation engineering team during a team sync.
- Create a Jira issue on the Component Library board if not already created. Prioritize with
  UI Foundation engineering in the next sync.

## Step 6: Merge timing — Figma vs. code

The default is **wait to merge the Figma branch until engineering has updated the code** so
designers don't see UI in Figma that doesn't yet exist in product. But there are exceptions:

- **Designers need the changes now.** Add a warning badge to the component's docs in Figma
  noting the engineering state, merge the Figma branch, and send an update to engineering
  teams in `#team-eng-ui-foundation`.
- **Branch maintenance is too unwieldy.** Same exception applies — merge with a warning and
  announce.

Default to the disciplined order. Use the exception sparingly.

## Composing with other skills

- **`using-figma`.** `search_design_system` and `get_libraries` for the pre-proposal search;
  `get_metadata` and `get_variable_defs` for inspecting existing components; the Code Connect
  tools (`get_code_connect_map`, `add_code_connect_map`, `get_context_for_code_connect`) for
  the design-to-code linkage when promoting a pattern to a Core Component.
- **`facilitating-design-critique`.** The design team's alignment step in Step 2 is a critique
  session, not a one-off message. When the proposer needs help structuring it, dispatch into
  the critique-facilitation skill.
- **`navigating-design-jira-process`.** The Component Library Jira board lives inside the
  larger Product and Design Jira workflow. When the proposal generates engineering work,
  dispatch into the Jira-process skill for the right state moves.

## Common traps

- **Skipping the pre-proposal search.** `search_design_system` first. Always.
- **Designer-unilateral Core/Recipe call.** The UI Foundation conversation is required for
  this decision. Don't pre-decide.
- **Property names that don't match the CL API conventions.** Inconsistent naming breaks the
  library's usability across the team. Read the CL API design doc rather than improvising.
- **Skipping the warning badge on early merges.** When the exception path is taken, the
  warning badge in Figma plus the `#team-eng-ui-foundation` message is required, not optional.
- **Merging Figma changes ahead of engineering with no comms.** Designers downstream see UI
  that doesn't exist in product and build on top of it.

## Output format

When asked to help propose a pattern or modify a component:

1. **Path** — new pattern or modification.
2. **Search results** — what already exists in the library that's adjacent or overlapping.
3. **Design team alignment plan** — what to bring to critique, what questions the team should
   weigh.
4. **Core vs. Recipe call (new patterns only)** — the UI Foundation conversation framing.
5. **Figma plan** — branch name, page placement, required states, property order, docs frame.
6. **Review path** — designer approvals required, UI Foundation review, Component Library
   Jira issue.
7. **Merge timing** — default or exception, with the warning-badge and comms steps if
   exception.
