import json
import sys
import unittest
from pathlib import Path
from unittest import mock

ENGINE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_DIR))

import run_real_eval  # noqa: E402

PLUGIN = "bitwarden-testing-tools"


class _FakeCompletedProcess:
    """A subprocess double that has already exited with canned, complete
    stdout, exercising the "child exited" branch of run_query's poll loop
    without needing a real `claude -p` invocation."""

    returncode = 0

    def __init__(self, data: bytes):
        self._data = data
        self.stdout = self

    def poll(self):
        return 0

    def read(self):
        return self._data


def _stream(events):
    return ("\n".join(json.dumps(e) for e in events) + "\n").encode()


def _tool_use(name, tool_input):
    return {"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": name, "input": tool_input},
    ]}}


def _skill_event(skill):
    return _tool_use("Skill", {"skill": skill})


def _read_event(file_path):
    return _tool_use("Read", {"file_path": file_path})


def _agent_event(subagent_type, name="Agent"):
    return _tool_use(name, {"subagent_type": subagent_type})


def _run(token, events):
    data = _stream(events)
    with mock.patch.object(run_real_eval.subprocess, "Popen", return_value=_FakeCompletedProcess(data)):
        return run_real_eval.run_query("dummy query", 30, "claude-opus-4-8", token, PLUGIN)


class TestSkillTriggerDetection(unittest.TestCase):
    def test_plugin_qualified_skill_invocation_is_a_trigger(self):
        result = _run("assessing-test-coverage", [_skill_event(f"{PLUGIN}:assessing-test-coverage")])
        self.assertTrue(result["triggered"])

    def test_unrelated_skill_before_the_target_is_scanned_past(self):
        result = _run("assessing-test-coverage", [
            _skill_event("superpowers:using-superpowers"),
            _skill_event(f"{PLUGIN}:assessing-test-coverage"),
        ])
        self.assertTrue(result["triggered"])

    def test_read_of_the_skill_md_is_a_trigger(self):
        result = _run("assessing-test-coverage", [
            _read_event(f"/plugins/{PLUGIN}/skills/assessing-test-coverage/SKILL.md"),
        ])
        self.assertTrue(result["triggered"])

    def test_read_of_another_file_under_the_skill_is_not_a_trigger(self):
        result = _run("assessing-test-coverage", [
            _read_event(f"/plugins/{PLUGIN}/skills/assessing-test-coverage/evals/trigger-eval.json"),
        ])
        self.assertFalse(result["triggered"])


class TestAgentDispatchDetection(unittest.TestCase):
    """The agent non-trigger suite passes an agent name as the target token.
    A direct dispatch surfaces as an Agent (or legacy Task) tool_use carrying
    subagent_type; an inspection surfaces as a Read of the agent's AGENT.md.
    Both must count as triggers, and neither may move a skill suite's counts."""

    def test_agent_dispatch_naming_the_target_is_a_trigger(self):
        result = _run("playwright-test-context-gatherer", [
            _agent_event(f"{PLUGIN}:playwright-test-context-gatherer"),
        ])
        self.assertTrue(result["triggered"])

    def test_legacy_task_dispatch_naming_the_target_is_a_trigger(self):
        result = _run("playwright-test-context-gatherer", [
            _agent_event(f"{PLUGIN}:playwright-test-context-gatherer", name="Task"),
        ])
        self.assertTrue(result["triggered"])

    def test_read_of_the_agent_md_is_a_trigger(self):
        result = _run("playwright-test-context-gatherer", [
            _read_event(f"/plugins/{PLUGIN}/agents/playwright-test-context-gatherer/AGENT.md"),
        ])
        self.assertTrue(result["triggered"])

    def test_agent_dispatch_naming_another_agent_is_not_a_trigger(self):
        result = _run("playwright-test-context-gatherer", [
            _agent_event(f"{PLUGIN}:services-under-test-mapper"),
        ])
        self.assertFalse(result["triggered"])

    def test_skill_target_is_inert_to_agent_dispatch(self):
        result = _run("assessing-test-coverage", [
            _agent_event(f"{PLUGIN}:playwright-test-context-gatherer"),
        ])
        self.assertFalse(result["triggered"])

    def test_skill_target_is_inert_to_agent_md_read(self):
        result = _run("assessing-test-coverage", [
            _read_event(f"/plugins/{PLUGIN}/agents/playwright-test-context-gatherer/AGENT.md"),
        ])
        self.assertFalse(result["triggered"])


class TestTargetResolution(unittest.TestCase):
    def _args(self, **kw):
        defaults = {"eval_set": f"/x/{PLUGIN}/skills/start-playwright-test/evals/trigger-eval.json",
                    "skill": None, "agent": None}
        defaults.update(kw)
        return mock.Mock(**defaults)

    def test_agent_flag_overrides_path_inference(self):
        args = self._args(agent="playwright-test-runner")
        self.assertEqual(run_real_eval.resolve_skill_token(args), "playwright-test-runner")

    def test_skill_token_is_inferred_from_the_eval_set_path(self):
        self.assertEqual(run_real_eval.resolve_skill_token(self._args()), "start-playwright-test")


if __name__ == "__main__":
    unittest.main()
