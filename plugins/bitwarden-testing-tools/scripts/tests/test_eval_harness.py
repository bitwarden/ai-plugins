import importlib
import json
import multiprocessing
import sys
import unittest
from pathlib import Path
from unittest import mock

HARNESS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS_DIR))

import eval_harness  # noqa: E402


class TestEvalConfig(unittest.TestCase):
    def test_config_carries_the_target_token(self):
        cfg = eval_harness.EvalConfig(target_skill_token="my-skill")
        self.assertEqual(cfg.target_skill_token, "my-skill")

    def test_config_defaults_match_the_hardened_policy(self):
        cfg = eval_harness.EvalConfig(target_skill_token="x")
        self.assertEqual(cfg.exec_tools, frozenset({"Bash", "Task"}))
        self.assertIn("gh pr view", cfg.read_only_bash)
        self.assertIn(";", cfg.shell_chains)

    def test_config_is_picklable_for_the_process_pool(self):
        import pickle

        cfg = eval_harness.EvalConfig(target_skill_token="x")
        self.assertEqual(pickle.loads(pickle.dumps(cfg)), cfg)


class TestReadOnlyCarveOut(unittest.TestCase):
    def test_bare_read_only_command_is_scanned_past(self):
        cfg = eval_harness.EvalConfig(target_skill_token="x")
        self.assertTrue(eval_harness.is_read_only_bash("gh pr view 123", cfg))

    def test_chained_command_loses_the_carve_out(self):
        cfg = eval_harness.EvalConfig(target_skill_token="x")
        self.assertFalse(eval_harness.is_read_only_bash("gh api foo && npm test", cfg))

    def test_unlisted_command_is_not_read_only(self):
        cfg = eval_harness.EvalConfig(target_skill_token="x")
        self.assertFalse(eval_harness.is_read_only_bash("npm install", cfg))


class TestSpawnSafety(unittest.TestCase):
    def test_harness_module_is_importable_by_a_spawned_child(self):
        # A spawned child re-imports the entry module. Prove the harness is
        # importable from a bare interpreter given only the sys.path insert,
        # which is what each skill's thin wrapper does at module top level.
        ctx = multiprocessing.get_context("spawn")
        q = ctx.Queue()
        p = ctx.Process(target=_import_in_child, args=(str(HARNESS_DIR), q))
        p.start()
        p.join(30)
        self.assertEqual(p.exitcode, 0)
        self.assertEqual(q.get(timeout=5), "ok")


def _import_in_child(harness_dir, q):
    sys.path.insert(0, harness_dir)
    importlib.import_module("eval_harness")
    q.put("ok")


class _FakeCompletedProcess:
    """A subprocess double that has already exited with canned, complete
    stdout, exercising the "child exited" branch of run_query's poll loop
    without needing a real `claude -p` invocation."""

    def __init__(self, data: bytes):
        self._data = data
        self.stdout = self

    def poll(self):
        return 0

    def read(self):
        return self._data

    def kill(self):
        pass

    def wait(self):
        pass


def _stream(events):
    return ("\n".join(json.dumps(e) for e in events) + "\n").encode()


def _bash_event(command):
    return {"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": "Bash", "input": {"command": command}},
    ]}}


def _skill_event(skill):
    return {"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": "Skill", "input": {"skill": skill}},
    ]}}


def _read_event(file_path):
    return {"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": "Read", "input": {"file_path": file_path}},
    ]}}


def _agent_event(subagent_type, name="Agent"):
    return {"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": name, "input": {"subagent_type": subagent_type}},
    ]}}


class TestRunQueryDecisionLogic(unittest.TestCase):
    """Drives run_query's bail-out and carve-out decisions against synthetic
    stream-json event sequences instead of real agents, so a future edit that
    silently breaks the bail-out (the mechanism that stops adversarial
    should-not-trigger queries from cloning repos and exhausting memory) is
    caught for free and fast, not only by a live eval run."""

    def _run(self, events):
        cfg = eval_harness.EvalConfig(target_skill_token="assessing-test-coverage")
        data = _stream(events)
        with mock.patch.object(eval_harness.subprocess, "Popen", return_value=_FakeCompletedProcess(data)):
            return eval_harness.run_query("dummy query", 30, "claude-opus-4-8", cfg)

    def test_non_allowlisted_bash_before_skill_is_a_non_trigger_and_terminates(self):
        events = [
            _bash_event("npm test"),
            _skill_event("bitwarden-testing-tools:assessing-test-coverage"),
        ]
        result = self._run(events)
        self.assertFalse(result["triggered"])
        self.assertEqual(result["first_skill"], "Bash (bailed: real-work tool)")

    def test_read_only_gh_pr_view_is_scanned_past_not_bailed(self):
        events = [
            _bash_event("gh pr view 123"),
            _skill_event("bitwarden-testing-tools:assessing-test-coverage"),
        ]
        result = self._run(events)
        self.assertTrue(result["triggered"])

    def test_read_only_prefix_with_shell_chain_loses_the_carve_out(self):
        events = [
            _bash_event("gh api foo && npm test"),
            _skill_event("bitwarden-testing-tools:assessing-test-coverage"),
        ]
        result = self._run(events)
        self.assertFalse(result["triggered"])
        self.assertEqual(result["first_skill"], "Bash (bailed: real-work tool)")

    def test_target_skill_before_any_exec_tool_is_a_trigger(self):
        events = [
            _skill_event("bitwarden-testing-tools:assessing-test-coverage"),
            _bash_event("npm test"),
        ]
        result = self._run(events)
        self.assertTrue(result["triggered"])

    def test_read_of_skill_md_containing_the_token_is_a_trigger(self):
        # Implementation (eval_harness.py): a Read only counts when it opens
        # the skill's own SKILL.md (`name == "Read" and
        # config.target_skill_token in fp and fp.rstrip().endswith("SKILL.md")`):
        # both the token AND the SKILL.md suffix are required.
        events = [_read_event("/plugins/bitwarden-testing-tools/skills/assessing-test-coverage/SKILL.md")]
        result = self._run(events)
        self.assertTrue(result["triggered"])

    def test_read_of_token_path_not_ending_in_skill_md_is_not_a_trigger(self):
        events = [
            _read_event("/plugins/bitwarden-testing-tools/skills/assessing-test-coverage/evals/README.md"),
        ]
        result = self._run(events)
        self.assertFalse(result["triggered"])


class TestAgentDispatchDetection(unittest.TestCase):
    """The agent non-trigger suite passes an agent name as the target token.
    A direct dispatch surfaces as an Agent (or legacy Task) tool_use carrying
    subagent_type; an inspection surfaces as a Read of the agent's AGENT.md.
    Both must count as triggers, and neither may move a skill suite's counts."""

    def _run(self, token, events):
        cfg = eval_harness.EvalConfig(target_skill_token=token)
        data = _stream(events)
        with mock.patch.object(eval_harness.subprocess, "Popen", return_value=_FakeCompletedProcess(data)):
            return eval_harness.run_query("dummy query", 30, "claude-opus-4-8", cfg)

    def test_agent_dispatch_naming_the_target_is_a_trigger(self):
        result = self._run("playwright-test-context-gatherer", [_agent_event("playwright-test-context-gatherer")])
        self.assertTrue(result["triggered"])
        self.assertEqual(result["first_skill"], "playwright-test-context-gatherer")

    def test_legacy_task_dispatch_naming_the_target_is_a_trigger(self):
        result = self._run("playwright-test-context-gatherer", [_agent_event("playwright-test-context-gatherer", name="Task")])
        self.assertTrue(result["triggered"])

    def test_read_of_agent_md_containing_the_token_is_a_trigger(self):
        result = self._run("playwright-test-context-gatherer", [
            _read_event("/plugins/bitwarden-testing-tools/agents/playwright-test-context-gatherer/AGENT.md"),
        ])
        self.assertTrue(result["triggered"])

    def test_agent_dispatch_not_naming_the_target_bails_as_real_work(self):
        result = self._run("playwright-test-context-gatherer", [_agent_event("services-under-test-mapper")])
        self.assertFalse(result["triggered"])
        self.assertEqual(result["first_skill"], "Agent (bailed: real-work tool)")

    def test_skill_target_is_inert_to_agent_dispatch(self):
        result = self._run("assessing-test-coverage", [_agent_event("playwright-test-context-gatherer")])
        self.assertFalse(result["triggered"])
        self.assertEqual(result["first_skill"], "Agent (bailed: real-work tool)")

    def test_skill_target_is_inert_to_agent_md_read(self):
        result = self._run("assessing-test-coverage", [
            _read_event("/plugins/bitwarden-testing-tools/agents/playwright-test-context-gatherer/AGENT.md"),
        ])
        self.assertFalse(result["triggered"])


if __name__ == "__main__":
    unittest.main()
