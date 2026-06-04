---
name: using-figma
description: Read and inspect Figma designs via the Dev Mode MCP server — selects the right tool, parses Figma URLs into fileKey and nodeId, and turns design context into useful input for critique, copy review, handoff prep, and Design System work.
when_to_use: Use when a task reads design context from Figma without generating production code or modifying Figma state. Triggers — Figma URL shared, "look at this design", "extract tokens from Figma", "what variables does this use", "what's in this Figma file", "compare these two Figma frames", "inspect this component". Not for framework-bound code generation (use `figma-to-angular` in the clients repo, external — not bundled), and not for Figma mutations (this skill's `allowed-tools` is read-only).
allowed-tools: Skill, mcp__figma__get_design_context, mcp__figma__get_metadata, mcp__figma__get_screenshot, mcp__figma__get_variable_defs, mcp__figma__get_libraries, mcp__figma__search_design_system, mcp__figma__get_figjam, mcp__figma__whoami, mcp__figma__get_code_connect_map, mcp__figma__get_code_connect_suggestions, mcp__figma__get_context_for_code_connect
---

# Using Figma via the Dev Mode MCP Server

This skill grounds the designer in the Figma Dev Mode MCP server — Figma's official MCP that
exposes design context, variables, screenshots, metadata, and design-system search to Claude.
Apply it whenever a task needs to _read_ a Figma design — extract structure, tokens,
screenshots, or strings. Composing skills like `design-review`, `content-style-guide`,
`preparing-design-handoff`, and `evolving-design-system-components` call into here whenever a
Figma file is referenced.

The Figma MCP server also exposes write tools (creating files, uploading assets, generating
diagrams, mapping Code Connect, mutating Figma objects). Those are intentionally **out of
scope** for this skill — its `allowed-tools` is read-only. If a task genuinely needs a Figma
mutation, invoke the underlying MCP tool directly with explicit user consent rather than
extending this skill's surface.

## Prerequisite: the MCP server must be installed

The Figma Dev Mode MCP server is not bundled with this plugin. It is Figma's own product and
the user installs and authenticates it themselves — either the desktop server (which requires
a Dev or Full seat on a paid Figma plan) or the remote server. If the Figma MCP tools are not
available in the session, stop and tell the user to install and authenticate the Figma MCP
server before continuing.

Some MCP tools are remote-only and unavailable on the desktop server; check Figma's docs when
a tool isn't where you expect it. Detailed setup notes live in `references/setup.md`.

## Anatomy of a Figma URL

Every interaction starts from a Figma URL. The two pieces that matter are the **fileKey** and
the **nodeId**.

```
https://www.figma.com/design/<fileKey>/<fileName>?node-id=<nodeIdWithDashes>&...
```

Conversion: the URL's node-id uses `-` as the separator (`123-456`), but the MCP server expects
`:` (`123:456`). Convert before passing it into a tool.

If the user pastes a URL without a `node-id`, the URL points at the whole file. Ask which frame
they mean before extracting anything — operating on the whole file is rarely what's wanted and
returns far too much context.

## The read tools, by job to be done

The Figma MCP server exposes many tools. Pick the smallest one that answers the question.

| Job to be done                                               | Tool                   | Notes                                                                                 |
| ------------------------------------------------------------ | ---------------------- | ------------------------------------------------------------------------------------- |
| Read a frame's design context (code + screenshot + metadata) | `get_design_context`   | Most common entry point. Accepts a framework parameter; defaults to React + Tailwind. |
| Get just the structural outline                              | `get_metadata`         | Sparse XML of layer IDs, names, types, positions, sizes. Cheap.                       |
| Get just the rendered image                                  | `get_screenshot`       | Visual reference without the code or token noise.                                     |
| Extract design tokens used in selection                      | `get_variable_defs`    | Variables and styles — colors, spacing, typography.                                   |
| Discover available libraries on the file                     | `get_libraries`        | Shows which subscribed/available design libraries are linked.                         |
| Find a component in the design system                        | `search_design_system` | Text query against components, variables, styles.                                     |
| Inspect a FigJam board                                       | `get_figjam`           | Same role as `get_metadata` but for FigJam content.                                   |
| Identify the authenticated Figma user                        | `whoami`               | Useful when permission / seat type matters.                                           |

### Code Connect tools (read-only)

These map Figma components to their code counterparts. Mostly relevant inside
`evolving-design-system-components`; rarely needed for critique or copy review.

- `get_code_connect_map` — returns existing mappings, source files, and snippets for selected
  instances.
- `get_code_connect_suggestions` — suggested mappings for selected components.
- `get_context_for_code_connect` — property definitions and variant options for a component.

(The two write Code Connect tools — `add_code_connect_map` and `send_code_connect_mappings` —
are out of scope for this skill. Invoke them directly with explicit user consent if needed.)

## Decision rules

- **Don't reach for `get_design_context` by reflex.** It returns code and screenshots even when
  the question is "what color is this background" — `get_variable_defs` answers that in a
  fraction of the context.
- **Start with `get_metadata` for orientation.** When the goal is "tell me what's in this
  frame", the metadata XML is cheaper than full context and usually enough to pick the next
  move.
- **Use `get_screenshot` for human reference, `get_metadata` for machine reasoning.** Don't
  load both unless both are needed.
- **Don't generate code from this skill.** Production code generation belongs in repo-specific
  output skills like `figma-to-angular` in the clients repo. This skill stops at extracted
  design context.

## Composing with other skills

- **`design-review`.** When critiquing a design, start with `get_screenshot` + `get_metadata`
  to orient. Pull `get_variable_defs` if tokens are part of the critique (off-system colors,
  inconsistent spacing). Only escalate to `get_design_context` when the code-shape itself is
  the question.
- **`content-style-guide`.** Use `get_design_context` or `get_metadata` to surface every
  user-visible string in a frame, then walk each string through the style guide. Do not
  rewrite Figma copy from inside this skill — return findings with proposed alternatives and
  let the designer apply.
- **`preparing-design-handoff`.** Use `get_metadata` to verify the file has the expected
  Ready-for-Dev sections with names aligned to engineering stories. Use `get_variable_defs`
  to confirm tokens are library-bound rather than raw hex.
- **`evolving-design-system-components`.** Use `search_design_system` and `get_libraries`
  before proposing a new pattern — most "we need this new thing" cases turn out to be
  "this thing exists in the library and we didn't know." Use the Code Connect read tools when
  the question crosses into how a Figma component maps to its code counterpart.

## Asking the user before extracting

Before fetching, surface what you're about to ask for and why:

> "I'll pull `get_metadata` for that frame first to see the layer structure, then
> `get_variable_defs` for the tokens it uses — that should answer the spacing question without
> loading the full design context. OK?"

This is faster than apologizing for an over-broad call later and helps the designer learn
which MCP tool answers their kind of question.

## Output format for Figma extractions

When reporting what's in a Figma file, structure the response as:

1. **Frame and stage** — file name, frame name, stage if known (30/60/90).
2. **Structure** — layer outline at the level relevant to the question (don't paste raw XML).
3. **Tokens and library bindings** — what's bound to the design system vs. what's a raw value.
4. **User-visible strings** (when copy is part of the task) — flagged with content-style-guide
   findings.
5. **Open questions** — anything ambiguous in the file that the designer should clarify before
   the work moves forward.

## Additional resources

- **`references/setup.md`** — installing and authenticating the Figma Dev Mode MCP server
  (desktop vs. remote), seat-type requirements, and troubleshooting unavailable tools.
- **Figma's canonical per-tool reference:**
  [`developers.figma.com/docs/figma-mcp-server/tools-and-prompts/`](https://developers.figma.com/docs/figma-mcp-server/tools-and-prompts/) —
  the source of truth for tool parameters, return shapes, and desktop-vs-remote availability.
