#!/usr/bin/env python3
"""PreToolUse hook: confine the planning agents' Bash and Skill use.

For each restricted planning agent:

- a Bash command other than `<plugin root>/scripts/repo-diff.sh <one path>` is
  blocked. The scoper and mapper list plain `Bash` in `tools:` because a
  script-scoped grant does not work there; this is what narrows it.
- a Skill call other than the agent's own skill is blocked, because a skill
  that runs in a forked context executes its Bash as a different agent type,
  outside this check.

A block exits 2, which Claude Code applies before permission rules are
evaluated. Every other agent, and the main session, passes through (exit 0).

A plugin subagent's `agent_type` has been observed as `plugin:agent` (installed
from a marketplace) and `plugin:agent:agent` (loaded with --plugin-dir), so the
caller is matched on its first and last `:`-separated segments.
"""
import json
import os
import re
import sys

PLUGIN_NAME = "bitwarden-testing-tools"
# Each restricted agent, mapped to the one plugin-qualified skill it may invoke.
AGENT_SKILLS = {
    "playwright-application-context-scoper": "bitwarden-testing-tools:scoping-playwright-application-context",
    "services-under-test-mapper": "bitwarden-testing-tools:mapping-services-under-test",
    "playwright-test-context-gatherer": "bitwarden-atlassian-tools:researching-jira-issues",
}
BASH_BLOCK_MESSAGE = (
    "Only repo-diff.sh may run through Bash in this agent (bitwarden-testing-tools "
    "policy), as <plugin root>/scripts/repo-diff.sh <one repo path>: one repo per "
    "call, the script path single-quoted if it contains any character other than "
    "ASCII letters, digits, and ._/+@:-, and no cd, redirects, pipes, or chaining. "
    "If your command differed, retry once in exactly that form; otherwise report "
    "this step as an obstacle."
)
SKILL_BLOCK_TEMPLATE = (
    "Only the {skill} skill may be invoked in this agent (bitwarden-testing-tools "
    "policy). If you invoked it under a different name, retry once as exactly "
    "{skill}; otherwise report this step as an obstacle."
)
# One path argument: bare (POSIX, or a Windows path written with forward
# slashes), single-quoted, or double-quoted with no expansion.
PATH_ARG = r"""(?:[A-Za-z0-9._/~+@:-]+|'[^'\n]*'|"[^"$`\\\n]*")"""
# A plugin root made only of these characters is safe to leave unquoted.
SAFE_ROOT = re.compile(r"[A-Za-z0-9._/+@:-]+")
# Only the whitespace bash also ignores around a command. str.strip() would also
# drop characters such as U+00A0 and CR that bash treats as part of the command word.
OUTER_WHITESPACE = " \t\n"


def restricted_agent(agent_type):
    """Return the restricted agent's name, or None if agent_type is not one."""
    if not isinstance(agent_type, str):
        return None
    segments = agent_type.split(":")
    if len(segments) >= 2 and segments[0] == PLUGIN_NAME and segments[-1] in AGENT_SKILLS:
        return segments[-1]
    return None


def script_path_forms(plugin_root):
    """Regexes for the script path as the shell passes it through intact.

    Unquoted only when the root needs no quoting; single-quoted unless the root
    holds a `'`; double-quoted unless it holds a character the shell expands or
    escapes inside double quotes.
    """
    script = plugin_root + "/scripts/repo-diff.sh"
    forms = []
    if SAFE_ROOT.fullmatch(plugin_root):
        forms.append(re.escape(script))
    if "'" not in plugin_root:
        forms.append(re.escape("'" + script + "'"))
    if not any(c in plugin_root for c in '"$`\\'):
        forms.append(re.escape('"' + script + '"'))
    return forms


def is_allowed_command(command, plugin_root):
    """True only for `<root>/scripts/repo-diff.sh <one path>` and nothing else."""
    if not isinstance(command, str) or not plugin_root:
        return False
    forms = script_path_forms(plugin_root)
    if not forms:
        return False
    pattern = "(?:" + "|".join(forms) + ") " + PATH_ARG
    return re.fullmatch(pattern, command.strip(OUTER_WHITESPACE)) is not None


def is_allowed_skill(skill, allowed):
    """True only for the exact plugin-qualified skill, ignoring outer spaces and one leading '/'."""
    if not isinstance(skill, str):
        return False
    name = skill.strip()
    if name.startswith("/"):
        name = name[1:]
    return name == allowed


def block_message(tool, agent):
    if tool == "Skill":
        return SKILL_BLOCK_TEMPLATE.format(skill=AGENT_SKILLS[agent])
    return BASH_BLOCK_MESSAGE


def decide(payload, env):
    """Return (exit code, stderr message) for one hook invocation."""
    agent = restricted_agent(payload.get("agent_type"))
    if agent is None:
        return 0, ""
    tool = payload.get("tool_name")
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        tool_input = {}
    if tool == "Bash":
        if is_allowed_command(tool_input.get("command"), env.get("CLAUDE_PLUGIN_ROOT", "")):
            return 0, ""
        return 2, block_message(tool, agent)
    if tool == "Skill":
        if is_allowed_skill(tool_input.get("skill"), AGENT_SKILLS[agent]):
            return 0, ""
        return 2, block_message(tool, agent)
    return 0, ""


def main(stdin, env):
    try:
        payload = json.loads(stdin)
    except ValueError:
        return 0
    except RecursionError:
        # No Bash or Skill input is nested this deeply. Block if it could come
        # from a restricted agent rather than let the crash exit 1 and fail open.
        agent = next((a for a in AGENT_SKILLS if PLUGIN_NAME in stdin and a in stdin), None)
        if agent is None:
            return 0
        print(block_message(None, agent), file=sys.stderr)
        return 2
    if not isinstance(payload, dict):
        return 0
    try:
        code, message = decide(payload, env)
    except Exception:
        # Fail closed for the agents this hook exists to restrict.
        agent = restricted_agent(payload.get("agent_type"))
        if agent is None:
            return 0
        code, message = 2, block_message(payload.get("tool_name"), agent)
    if code == 2:
        print(message, file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.stdin.buffer.read().decode("utf-8", "replace"), os.environ))
