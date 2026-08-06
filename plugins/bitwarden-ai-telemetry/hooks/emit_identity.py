#!/usr/bin/env python3
# Reads hook JSON on stdin, emits one bw.identity OTLP log record recovering the
# skill/agent identity that native telemetry redacts. Never fails the session:
# every error path exits 0.
import json
import os
import sys

from emit import emit  # sibling module; script dir is on sys.path[0]

EXPANSION_HOOK = "UserPromptExpansion"
SLASH_EXPANSION = "slash_command"
SKILL_TOOL = "Skill"


def _slash_skill(h):
    """The skill name from a slash invocation, or "" if this isn't one.

    A slash-invoked skill (`/plugin:skill`) never produces a Skill tool call —
    Claude Code expands it into the prompt instead — so PostToolUse never fires
    and `tool_input.skill` does not exist. UserPromptExpansion is the only event
    that carries the name, in `command_name`. Verified empirically 2026-07-30;
    this path was previously invisible to telemetry entirely.
    """
    if h.get("expansion_type") != SLASH_EXPANSION:
        return ""
    return h.get("command_name") or ""


def _should_emit(h):
    """UserPromptExpansion fires for expansion types beyond slash commands.

    Only slash expansions carry a skill identity; emitting for the others would
    add content-free bw.identity rows (every bw.* field empty and therefore
    dropped by emit()), which already pollute counts of @event.name:bw.identity.
    """
    if h.get("hook_event_name") == EXPANSION_HOOK:
        return bool(_slash_skill(h))
    return True


def _build_identity_attrs(h):
    """Reduce one hook-invocation dict to the bw.identity attrs.

    agent_type prefers the top-level `agent_type` (set on SubagentStop) over
    `tool_input.subagent_type` (set on a Task|Agent PostToolUse dispatch) —
    the two hooks fire for different event shapes, never both populated at
    once in practice, but SubagentStop's is the more authoritative of the two
    when both exist. skill comes from tool_input.skill (a Skill dispatch) or,
    for a slash invocation, from UserPromptExpansion's command_name.

    A slash expansion reports bw.tool = "Skill" even though no tool ran, so it
    joins the same `@bw.tool:Skill` queries as the tool path; bw.hook preserves
    the true origin ("UserPromptExpansion" vs "PostToolUse") for anyone who
    needs to tell the two apart. Note command_name may name a plugin *command*
    rather than a skill — the two are deliberately not distinguished.
    """
    tin = h.get("tool_input") or {}
    slash_skill = _slash_skill(h)
    return {
        "event.name": "bw.identity",
        "bw.hook": h.get("hook_event_name", ""),
        "bw.agent_type": h.get("agent_type") or tin.get("subagent_type") or "",
        "bw.skill": tin.get("skill") or slash_skill,
        "bw.tool": h.get("tool_name") or (SKILL_TOOL if slash_skill else ""),
        "session.id": h.get("session_id", ""),
        "repo": os.path.basename(h.get("cwd") or ""),
    }


def main():
    try:
        h = json.load(sys.stdin)
    except Exception:
        return
    if not _should_emit(h):
        return
    emit("bw.identity", _build_identity_attrs(h))


if __name__ == "__main__":
    main()
    sys.exit(0)
