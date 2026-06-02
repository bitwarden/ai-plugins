# Figma Dev Mode MCP Server — Setup & Troubleshooting

The Figma MCP server is not bundled with this plugin. It is Figma's own product, and
the user installs and authenticates it themselves. This reference is for the moments when
something isn't working and a quick check helps unblock the work.

## Two server types

Figma exposes the MCP server in two flavors:

- **Desktop server.** Runs locally alongside the Figma desktop app. Requires a **Dev or Full
  seat on a paid Figma plan**. Some tools (marked "remote only" in the official docs) are
  unavailable on desktop.
- **Remote server.** Hosted by Figma; works in environments that support remote MCP servers
  (Augment Code, Claude Code, Cursor, and others per Figma's compatibility list).

Confirm with the user which one they're using when troubleshooting — the tool surface differs.

## Client compatibility

The client (Claude Code in this plugin's context) must support MCP servers, and the user must
have configured the Figma server in their client's MCP settings. Configuration lives in the
user's environment (not in this plugin) — refer them to Figma's setup guide if the tools are
absent from the session.

## Confirming the server is reachable

Before starting any Figma-dependent work, verify the MCP is present:

- If a `whoami`-style tool is available in the session's MCP list, that confirms the connection
  and tells you which seat type the user has.
- If no Figma tools appear in the session's MCP list at all, stop and ask the user to install
  and authenticate the server before proceeding.

## Common failure modes

- **Write tools unavailable.** The desktop server may not expose write tools that are
  available remotely. If a write call fails on desktop, fall back to a read-only approach or
  surface the limitation to the user.
- **Seat type insufficient.** Some tools require a Dev or Full seat. If a tool returns an
  authorization error, suggest the user check their seat type via `whoami` and escalate to
  their Figma admin if needed.
- **File not in workspace.** If the file is in a personal workspace the authenticated user
  can't access, no MCP tool will reach it. The user must either be granted access or share
  via a different channel.
- **Node ID format mismatch.** URLs use `-`; the MCP expects `:`. Always convert. If a tool
  responds with "node not found", check the ID format first.

## References

- Official guide: `help.figma.com/hc/en-us/articles/32132100833559-Guide-to-the-Dev-Mode-MCP-Server`
- Official tool reference: `developers.figma.com/docs/figma-mcp-server/tools-and-prompts/`
