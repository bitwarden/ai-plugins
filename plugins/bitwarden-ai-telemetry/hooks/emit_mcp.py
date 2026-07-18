#!/usr/bin/env python3
# Reads a PostToolUse hook JSON on stdin and emits one bw.mcp OTLP log record
# recovering the REAL MCP tool name. Native telemetry redacts every MCP call to a
# generic tool_name="mcp_tool"; the hook still receives the true
# "mcp__<server>__<tool>" identifier and re-surfaces it (same recovery pattern as
# emit_identity.py does for agents/skills). Metadata ONLY -- the tool's name, the
# server segment; NEVER arguments or results. NEVER fails the session: every
# error path exits 0.
import json
import os
import sys

from emit import emit  # sibling module; script dir is on sys.path[0]


def _parse_mcp_tool_name(name):
    """Split a native `mcp__<server>__<tool>` tool_name into (server, tool).

    Returns None if `name` isn't an MCP tool identifier. The server segment
    may contain single underscores but never the "__" delimiter, so a plain
    split on "__" is safe; the tool segment is rejoined in case it itself
    contains "__" (e.g. a tool named with a double-underscore).
    """
    name = name or ""
    if not name.startswith("mcp__"):
        return None
    parts = name.split("__")
    server = parts[1] if len(parts) > 1 else ""
    tool = "__".join(parts[2:]) if len(parts) > 2 else ""
    return server, tool


def main():
    try:
        h = json.load(sys.stdin)
    except Exception:
        return
    parsed = _parse_mcp_tool_name(h.get("tool_name", ""))
    if parsed is None:
        return  # not an MCP tool; nothing to recover
    server, tool = parsed
    name = h.get("tool_name", "")
    emit("bw.mcp", {
        "event.name": "bw.mcp",
        "bw.hook": h.get("hook_event_name", ""),
        "bw.mcp_tool": name,          # full mcp__server__tool identifier
        "bw.mcp_server": server,      # the MCP server segment
        "bw.mcp_tool_name": tool,     # the bare tool name
        # No bw.tool here: native telemetry already sets tool_name="mcp_tool" on
        # the co-located invocation event, so the real name only needs to live
        # in bw.mcp_tool / bw.mcp_server / bw.mcp_tool_name above.
        "session.id": h.get("session_id", ""),
        "repo": os.path.basename(h.get("cwd") or ""),
    })


if __name__ == "__main__":
    main()
    sys.exit(0)
