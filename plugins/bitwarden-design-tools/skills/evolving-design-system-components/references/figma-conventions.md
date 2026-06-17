# Figma Conventions for Component Library Work

These conventions govern Figma-side work in the Bitwarden Tailwind Component Library. They are
the design-team-facing surface of the CL API design docs at
`bitwarden.atlassian.net/wiki/spaces/EN/pages/619511828/Establish+common+language` — when in
doubt, that engineering-side page wins.

## Branch naming

Name the branch after the component or pattern being added or modified. Match the kebab-case
used in the engineering-side Tailwind component name if it exists (e.g., `segmented-control`,
`badge`, `bit-toast`).

## Page placement

**New core components.** Create a new page named after the component. Pages in the "Pages"
section are kept alphabetical — drop the new page in at the right slot.

**Modifications.** Use the existing component's page; do not create a new page for a
modification.

**Recipes / Snowflakes.** Add to the "Templates" page at the bottom of the Pages section, not
to its own page.

## Required interactive states

For interactive components, include at minimum:

- default
- hover
- focus
- active (when applicable)
- disabled (when applicable)

Missing states create handoff ambiguity. Default to including more rather than fewer.

## Property order — the load-bearing convention

Figma property order is **not arbitrary**. Designers using the library scan properties from
the top of the panel; consistent order across components makes the library usable. From the
Creating-new-design-patterns Confluence page:

1. **Variant**
2. **Size**
3. **Icon / Element**
4. **Misc / Block / Position / Quantity**
5. **Expanded**
6. **Selected / Active**
7. **State**

The two anchors that matter most: **Variant first**, **State last**. If a property doesn't
obviously fit one of these slots, look at adjacent components for precedent before inventing
a new ordinal.

## Property naming

Property names come from the
[CL API design docs](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/619511828/Establish+common+language).
When the engineering-side name already exists, match it exactly. When introducing a new name,
walk it through the docs first — coined-on-the-spot names diverge from the engineering API and
create translation pain at code-mapping time.

## Component documentation frame

Every component (and every modified component, for documentation updates) gets a documentation
frame next to its main component. The pattern:

- Copy an existing component's docs frame as a starting point — preserves the layout, the
  variable bindings, and the dark-theme variable swap.
- Replace all content with the new component's content. Sections: usage, behavior, variants,
  accessibility.
- Create the docs frame as a component, named `.<component-name>-docs` (note the leading dot
  to keep it sorted at the bottom of the components list).
- Update the docs component's variables to use the **dark** theme. This is intentional and
  matches every other component's docs.
- Place the docs component next to the main component.
- Group the main component and its docs component together. Name the group `<component-name> -
storybook link don't ungroup`. The "don't ungroup" is literal — Storybook uses the group as
  the link target.

## Comments on modifications

For modifications, leave a Figma comment on each changed component noting what changed.
Comments survive the branch merge and give downstream designers context for what's new.

## Warning badges on early-merge components

When the exception path is taken (Figma merges ahead of engineering), add a warning badge to
the component's docs frame indicating engineering state. Remove the badge once engineering has
caught up. Pair the badge with a message in `#team-eng-ui-foundation`.

## Recipe / Snowflake annotations

Recipes don't get the full docs frame, but they should still carry:

- Variants defined in the design file (states, sizes, configurations).
- Annotations for component behavior and accessibility (focus order, ARIA roles, keyboard
  shortcuts).
- Property naming per the same conventions above, even though the recipe lives on the
  Templates page.

Work with the feature team's tech lead on the engineering build plan for a recipe — recipes
are owned by the feature team, not by UI Foundation, so the Jira stories live in the feature
team's project, not the Component Library project.
