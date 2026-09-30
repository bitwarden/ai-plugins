#!/usr/bin/env python3
"""PreToolUse hook: confine the planning agents' Skill use.

A Skill call from a restricted planning agent, other than the agent's own skill,
is blocked, because a skill that runs in a forked context executes its Bash as a
different agent type, outside the agent's `tools:` allowlist.

A block exits 2, which Claude Code applies before permission rules are
evaluated. Every other agent, and the main session, passes through (exit 0).

The caller is matched on the first and last `:`-separated segments of its
`agent_type`.
"""
import json
import sys

PLUGIN_NAME = "bitwarden-testing-tools"
# Each restricted agent, mapped to the one plugin-qualified skill it may invoke.
AGENT_SKILLS = {
    "playwright-application-context-scoper": "bitwarden-testing-tools:scoping-playwright-application-context",
    "services-under-test-mapper": "bitwarden-testing-tools:mapping-services-under-test",
    "playwright-test-context-gatherer": "bitwarden-atlassian-tools:researching-jira-issues",
    "playwright-test-case-writer": "bitwarden-testing-tools:writing-playwright-test-cases",
}
SKILL_BLOCK_TEMPLATE = (
    "Only the {skill} skill may be invoked in this agent (bitwarden-testing-tools "
    "policy). If you invoked it under a different name, retry once as exactly "
    "{skill}; otherwise report this step as an obstacle."
)


def restricted_agent(agent_type):
    """Return the restricted agent's name, or None if agent_type is not one."""
    if not isinstance(agent_type, str):
        return None
    segments = agent_type.split(":")
    if len(segments) >= 2 and segments[0] == PLUGIN_NAME and segments[-1] in AGENT_SKILLS:
        return segments[-1]
    return None


def is_allowed_skill(skill, allowed):
    """True only for the exact plugin-qualified skill, ignoring outer spaces and one leading '/'."""
    if not isinstance(skill, str):
        return False
    name = skill.strip()
    if name.startswith("/"):
        name = name[1:]
    return name == allowed


def block_message(agent):
    return SKILL_BLOCK_TEMPLATE.format(skill=AGENT_SKILLS[agent])


def decide(payload):
    """Return (exit code, stderr message) for one hook invocation."""
    agent = restricted_agent(payload.get("agent_type"))
    if agent is None:
        return 0, ""
    tool = payload.get("tool_name")
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        tool_input = {}
    if tool == "Skill" and not is_allowed_skill(tool_input.get("skill"), AGENT_SKILLS[agent]):
        return 2, block_message(agent)
    return 0, ""


def main(stdin):
    try:
        payload = json.loads(stdin)
    except ValueError:
        return 0
    except RecursionError:
        # No Skill input is nested this deeply. Block if it could come
        # from a restricted agent rather than let the crash exit 1 and fail open.
        agent = next((a for a in AGENT_SKILLS if PLUGIN_NAME in stdin and a in stdin), None)
        if agent is None:
            return 0
        print(block_message(agent), file=sys.stderr)
        return 2
    if not isinstance(payload, dict):
        return 0
    try:
        code, message = decide(payload)
    except Exception:
        # Fail closed for the agents this hook exists to restrict.
        agent = restricted_agent(payload.get("agent_type"))
        if agent is None:
            return 0
        code, message = 2, block_message(agent)
    if code == 2:
        print(message, file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.stdin.buffer.read().decode("utf-8", "replace")))
