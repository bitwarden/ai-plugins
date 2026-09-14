"""Unit coverage for the trigger-eval runner's scan decisions.

These drive `_scan_process` against synthetic `stream-json` event sequences
rather than real agents, so an edit that silently breaks the real-work bail
(the mechanism stopping an adversarial should-not-trigger query from cloning
repositories until it exhausts memory) is caught here, fast, instead of only
showing up as a mysteriously slow live eval run.

The process double reports itself already exited, which also exercises the
child-exit branch of the poll loop: a trigger arriving in the final chunk has
to survive it.
"""

import json
import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_DIR))

import trigger_eval  # noqa: E402

TARGET = "running-trigger-evals"


class _FakeExitedProcess:
    """A subprocess double that has already exited with canned, complete stdout."""

    def __init__(self, data: bytes):
        self._data = data
        self.stdout = self

    def poll(self):
        return 0

    def read(self):
        return self._data

    def kill(self):  # pragma: no cover - never reached, the child has exited
        pass

    def wait(self):  # pragma: no cover
        pass


def _stream(events):
    return ("\n".join(json.dumps(e) for e in events) + "\n").encode()


def _tool(name, inp):
    return {"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": name, "input": inp},
    ]}}


def _bash(command):
    return _tool("Bash", {"command": command})


def _skill(skill):
    return _tool("Skill", {"skill": skill})


def _read(file_path):
    return _tool("Read", {"file_path": file_path})


def _agent(subagent_type, name="Agent"):
    return _tool(name, {"subagent_type": subagent_type})


def _scan(events, target=TARGET, exclude=()):
    return trigger_eval._scan_process(
        _FakeExitedProcess(_stream(events)), target, list(exclude), 30
    )


class TestReadOnlyCarveOut(unittest.TestCase):
    def test_bare_read_only_command_is_scanned_past(self):
        self.assertTrue(trigger_eval.is_read_only_bash("gh pr view 1234"))

    def test_chained_command_loses_the_carve_out(self):
        self.assertFalse(trigger_eval.is_read_only_bash("gh api repos/x && npm test"))
        self.assertFalse(trigger_eval.is_read_only_bash("git remote -v; rm -rf /"))

    def test_unlisted_command_is_not_read_only(self):
        self.assertFalse(trigger_eval.is_read_only_bash("npm test"))


class TestNamesTarget(unittest.TestCase):
    def test_skill_call_naming_the_target(self):
        self.assertTrue(trigger_eval.names_target(
            "Skill", {"skill": f"bitwarden-eval-tools:{TARGET}"}, TARGET))

    def test_agent_dispatch_naming_the_target(self):
        self.assertTrue(trigger_eval.names_target(
            "Agent", {"subagent_type": TARGET}, TARGET))

    def test_legacy_task_dispatch_naming_the_target(self):
        self.assertTrue(trigger_eval.names_target(
            "Task", {"subagent_type": TARGET}, TARGET))

    def test_read_of_the_definition_counts(self):
        for leaf in ("SKILL.md", "AGENT.md"):
            self.assertTrue(trigger_eval.names_target(
                "Read", {"file_path": f"plugins/p/skills/{TARGET}/{leaf}"}, TARGET))

    def test_read_of_a_sibling_file_under_the_same_token_does_not_count(self):
        for path in (
            f"plugins/p/skills/{TARGET}/references/cli-reference.md",
            f"plugins/p/skills/{TARGET}/evals/trigger-eval.json",
        ):
            self.assertFalse(trigger_eval.names_target("Read", {"file_path": path}, TARGET))

    def test_a_bash_command_carrying_the_token_is_never_a_trigger(self):
        self.assertFalse(trigger_eval.names_target(
            "Bash", {"command": f"grep -r {TARGET} ."}, TARGET))


class TestClassifyToolUse(unittest.TestCase):
    def test_target_naming_call_is_a_trigger(self):
        self.assertEqual(trigger_eval.classify_tool_use(
            "Skill", {"skill": TARGET}, TARGET), "trigger")

    def test_real_work_tool_bails(self):
        self.assertEqual(trigger_eval.classify_tool_use(
            "Bash", {"command": "npm test"}, TARGET), "bail")

    def test_read_only_bash_continues(self):
        self.assertEqual(trigger_eval.classify_tool_use(
            "Bash", {"command": "gh pr view 1"}, TARGET), "continue")

    def test_agent_not_naming_the_target_bails(self):
        self.assertEqual(trigger_eval.classify_tool_use(
            "Agent", {"subagent_type": "general-purpose"}, TARGET), "bail")

    def test_unrelated_skill_continues(self):
        self.assertEqual(trigger_eval.classify_tool_use(
            "Skill", {"skill": "some:other-skill"}, TARGET), "continue")


class TestScanDecisions(unittest.TestCase):
    def test_target_skill_is_a_trigger(self):
        self.assertTrue(_scan([_skill(f"bitwarden-eval-tools:{TARGET}")])["triggered"])

    def test_unrelated_skill_is_scanned_past_before_the_target(self):
        result = _scan([_skill("other:session-init"), _skill(TARGET)])
        self.assertTrue(result["triggered"])

    def test_real_work_before_the_target_is_a_non_trigger(self):
        result = _scan([_bash("npm test"), _skill(TARGET)])
        self.assertFalse(result["triggered"])
        self.assertIn("bailed", result["first_skill"])

    def test_read_only_lookup_is_scanned_past(self):
        result = _scan([_bash("gh pr view 1234"), _skill(TARGET)])
        self.assertTrue(result["triggered"])

    def test_read_only_prefix_with_a_shell_chain_bails(self):
        result = _scan([_bash("gh api repos/x && npm test"), _skill(TARGET)])
        self.assertFalse(result["triggered"])

    def test_agent_dispatch_naming_the_target_is_a_trigger(self):
        self.assertTrue(_scan([_agent(TARGET)])["triggered"])

    def test_legacy_task_dispatch_naming_the_target_is_a_trigger(self):
        self.assertTrue(_scan([_agent(TARGET, name="Task")])["triggered"])

    def test_agent_dispatch_elsewhere_bails(self):
        result = _scan([_agent("general-purpose"), _skill(TARGET)])
        self.assertFalse(result["triggered"])

    def test_read_of_the_definition_is_a_trigger(self):
        self.assertTrue(_scan([_read(f"skills/{TARGET}/SKILL.md")])["triggered"])

    def test_read_of_a_sibling_file_is_not_a_trigger(self):
        result = _scan([
            _read(f"skills/{TARGET}/references/cli-reference.md"),
            {"type": "result", "subtype": "success"},
        ])
        self.assertFalse(result["triggered"])

    def test_a_trigger_in_the_final_chunk_survives_child_exit(self):
        # The regression this guards: the poll loop used to append the last
        # bytes to the buffer and then break without parsing them, discarding
        # any trigger event that arrived in that final read.
        result = _scan([
            {"type": "system", "subtype": "init"},
            _skill(f"bitwarden-eval-tools:{TARGET}"),
        ])
        self.assertTrue(result["triggered"])

    def test_a_clean_exit_is_not_reported_as_a_timeout(self):
        self.assertFalse(_scan([_skill(TARGET)])["timed_out"])

    def test_sibling_fires_are_recorded(self):
        result = _scan(
            [_skill("other:writing-manual-test-cases"), _skill(TARGET)],
            exclude=("writing-manual-test-cases",),
        )
        self.assertTrue(result["triggered"])
        self.assertTrue(result["sibling_fires"]["writing-manual-test-cases"])


class TestPartialMessageScanning(unittest.TestCase):
    """The partial-JSON path detects a trigger before the assistant message
    completes, which is what lets a killed child still be scored correctly."""

    @staticmethod
    def _blocks(tool_name, partials):
        events = [{"type": "stream_event", "event": {
            "type": "content_block_start",
            "content_block": {"type": "tool_use", "name": tool_name},
        }}]
        for part in partials:
            events.append({"type": "stream_event", "event": {
                "type": "content_block_delta",
                "delta": {"type": "input_json_delta", "partial_json": part},
            }})
        events.append({"type": "stream_event", "event": {"type": "content_block_stop"}})
        return events

    def test_target_skill_detected_mid_stream(self):
        events = self._blocks("Skill", ['{"skill": "bitwarden-eval-', f'tools:{TARGET}"}}'])
        self.assertTrue(_scan(events)["triggered"])

    def test_a_bash_command_carrying_the_token_does_not_trigger_mid_stream(self):
        events = self._blocks("Bash", ['{"command": "grep -r ', f'{TARGET} ."}}'])
        result = _scan(events)
        self.assertFalse(result["triggered"])
        self.assertIn("bailed", result["first_skill"])

    def test_a_read_of_a_sibling_file_does_not_trigger_mid_stream(self):
        events = self._blocks(
            "Read", ['{"file_path": "skills/', f'{TARGET}/references/cli-reference.md"}}'])
        self.assertFalse(_scan(events)["triggered"])


if __name__ == "__main__":
    unittest.main()
