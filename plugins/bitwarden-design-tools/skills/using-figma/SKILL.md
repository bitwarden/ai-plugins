---
name: using-figma
description: >
  This skill should be used when the user shares a Figma URL, asks to "look at this design",
  "extract tokens from Figma", "what variables does this use", "what's in this Figma file",
  "compare these two Figma frames", "inspect this component", or any task that reads design
  context from Figma without generating production code. Selects the right Figma Dev Mode MCP
  tool, parses Figma URLs into fileKey and nodeId, and turns design context into useful input
  for critique, copy review, handoff prep, and Design System work. Stops at extracted context;
  framework-bound code generation belongs in repo-specific skills like `figma-to-angular` in
  the clients repo (external, not bundled).
---

# Using Figma via the Dev Mode MCP Server

This skill grounds the designer in the Figma Dev Mode MCP server — Figma's official MCP that
exposes design context, variables, screenshots, metadata, and design-system search to Claude.
Apply it whenever a task needs to _read_ a Figma design — extract structure, tokens,
screenshots, or strings. Composing skills like `design-review`, `content-style-guide`,
`preparing-design-handoff`, and `evolving-design-system-components` call into here whenever a
Figma file is referenced. Write tools (creating files, uploading assets, generating diagrams,
mapping Code Connect) exist on the MCP server and are documented below for completeness, but
this skill's center of gravity is read.

## Prerequisite: the MCP server must be installed

The Figma Dev Mode MCP server is not bundled with this plugin. It is Figma's own product and
the user installs and authenticates it themselves — either the desktop server (which requires
a Dev or Full seat on a paid Figma plan) or the remote server. If the Figma MCP tools are not
available in the session, stop and tell the user to install and authenticate the Figma MCP
server before continuing.

Detailed setup notes live in `references/setup.md`.

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

### Code Connect tools

These map Figma components to their code counterparts. Mostly relevant inside
`evolving-design-system-components`; rarely needed for critique or copy review.

- `get_code_connect_map` — returns existing mappings, source files, and snippets for selected
  instances.
- `get_code_connect_suggestions` — suggested mappings for selected components.
- `get_context_for_code_connect` — property definitions and variant options for a component.
- `add_code_connect_map` — writes a Figma-node-to-code mapping. **Write tool — confirm first.**
- `send_code_connect_mappings` — submits confirmed mappings.

### Write tools

All write tools modify Figma state. Confirm scope and target with the user before invoking,
and report exactly what was created or changed.

- `use_figma` — generic create / modify / delete on Figma objects.
- `create_new_file` — creates a new Design or FigJam file.
- `upload_assets` — uploads PNG/JPG/GIF/WebP images (max 10 MB) as fills or new frames.
- `generate_figma_design` — sends UI code into Figma as design layers.
- `generate_diagram` — generates a FigJam diagram from Mermaid syntax or natural language.

Per-tool parameters and full output shape are in `references/figma-mcp-tools.md`.

## Decision rules

- **Don't reach for `get_design_context` by reflex.** It returns code and screenshots even when
  the question is "what color is this background" — `get_variable_defs` answers that in a
  fraction of the context.
- **Start with `get_metadata` for orientation.** When the goal is "tell me what's in this
  frame", the metadata XML is cheaper than full context and usually enough to pick the next
  move.
- **Use `get_screenshot` for human reference, `get_metadata` for machine reasoning.** Don't
  load both unless both are needed.
- **Write tools require confirmation.** `use_figma`, `upload_assets`, `create_new_file`,
  `generate_figma_design`, and `generate_diagram` modify Figma. Confirm scope and target with
  the user before calling.
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
- **`preparing-design-handoff`.** Use `get_metadata` to verify the file has the expected page
  structure (Userflows page, Annotated Prototype, "Ready for Dev" sections). Use
  `get_variable_defs` to confirm tokens are library-bound rather than raw hex.
- **`evolving-design-system-components`.** Use `search_design_system` and `get_libraries`
  before proposing a new pattern — most "we need this new thing" cases turn out to be
  "this thing exists in the library and we didn't know." Use the Code Connect tools when the
  question crosses into how a Figma component maps to its code counterpart.

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

- **`references/figma-mcp-tools.md`** — per-tool parameter and output reference, drawn from
  Figma's official MCP documentation.
- **`references/setup.md`** — installing and authenticating the Figma Dev Mode MCP server
  (desktop vs. remote), seat-type requirements, and troubleshooting unavailable tools.
