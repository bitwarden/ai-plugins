import type { SessionMessage } from "claude-code";
import { expect, mock, test } from "claude-code/testing";

type On = Parameters<typeof mock.clock>[0];

const SESSION = "0b6f3c2e-old-session";
const TRANSCRIPT = "/projects/demo/0b6f3c2e-old-session.jsonl";
const TYPED = {
  origin: { kind: "composer" },
  presentation: { isFullscreen: true, columns: 120 },
} as const;

const user = (text: string): SessionMessage => ({
  role: "user",
  text,
  toolUses: [],
});
const assistant = (text: string, toolOutput = ""): SessionMessage => ({
  role: "assistant",
  text,
  toolUses: toolOutput
    ? [{ tool_use_id: "t1", tool: "Bash", input: {}, text: toolOutput }]
    : [],
});
const toolResult = (text: string): SessionMessage => ({
  role: "user",
  text: "",
  toolUses: [],
  toolResults: [{ tool_use_id: "t1", text, isError: false }],
});

type Submitted = {
  text: string;
  notes: string[];
  asUser?: boolean;
  isAfterClear: boolean;
};

// Stands in for the engine: the old session, /clear, and the new session's prompt.
function engine(on: On, messages: SessionMessage[] = []) {
  const session = mock.session(on);
  mock.store(on);
  const seen: { isCleared: boolean; submitted?: Submitted } = {
    isCleared: false,
  };
  on("session.id", () => ({ value: SESSION }));
  on("session.messages", () => ({ value: messages }));
  on("command.run", { command: "clear" }, () => {
    seen.isCleared = true;
    return {};
  });
  on("prompt.submit", (_, e) => {
    seen.submitted = {
      text: e.text,
      // The rows appended before the prompt, as the model will read them.
      notes: session
        .appended()
        .map((row) =>
          row.message.content
            .map((block) => (block.type === "text" ? block.text : ""))
            .join(""),
        ),
      asUser: e.origin.kind === "plugin" ? e.origin.asUser : undefined,
      isAfterClear: seen.isCleared,
    };
    return { text: e.text };
  });
  return seen;
}

test("clears, then submits where the cleared session ended as the user", async ($, on) => {
  const clock = mock.clock(on);
  const seen = engine(on);
  on("classic.Stop", () => ({}));

  await $.classic.Stop({
    session_id: SESSION,
    transcript_path: TRANSCRIPT,
    stop_hook_active: false,
  });
  await $.command.run({ ...TYPED, command: "pickup", args: "" });
  await clock.settle();

  expect(seen.submitted).toEqual({
    text: `We're continuing where another session (${SESSION}, transcript ${TRANSCRIPT}) ended. Where did we leave off?`,
    notes: [],
    asUser: true,
    isAfterClear: true,
  });
});

test("a question after the command replaces the default one", async ($, on) => {
  const clock = mock.clock(on);
  const seen = engine(on);

  await $.command.run({
    ...TYPED,
    command: "pickup",
    args: "Is the test fixed?",
  });
  await clock.settle();

  expect(seen.submitted?.text).toEndWith("ended. Is the test fixed?");
});

test("the transcript is left out when no hook has named it for this session", async ($, on) => {
  const clock = mock.clock(on);
  const seen = engine(on);
  on("classic.SessionStart", () => ({}));

  await $.classic.SessionStart({
    source: "startup",
    session_id: "another-session",
    transcript_path: TRANSCRIPT,
  });
  await $.command.run({ ...TYPED, command: "pickup", args: "" });
  await clock.settle();

  expect(seen.submitted?.text).toStartWith(
    `We're continuing where another session (${SESSION}) ended.`,
  );
});

test("only the last two exchanges ride along, as a hidden row before the prompt", async ($, on) => {
  const clock = mock.clock(on);
  const seen = engine(on, [
    user("first prompt"),
    assistant("first reply"),
    user("second prompt"),
    assistant("Checking the logs.", "TOOL OUTPUT"),
    toolResult("TOOL RESULT"),
    assistant("second reply"),
    user(
      "<command-name>/simplify</command-name>\n<command-message>simplify</command-message>\n<command-args>the parser</command-args>",
    ),
    user("Base directory for this skill: SKILL BODY"),
    assistant("third reply"),
    user("<local-command-stdout>COMMAND OUTPUT</local-command-stdout>"),
  ]);

  await $.command.run({ ...TYPED, command: "pickup", args: "" });
  await clock.settle();

  const context = seen.submitted?.notes.join("\n") ?? "";
  expect(seen.submitted?.notes).toHaveLength(1);
  expect(context).toContain("User: second prompt\n\nAssistant: second reply");
  expect(context).toContain(
    "User: /simplify the parser\n\nAssistant: third reply",
  );
  for (const left of [
    "first",
    "Checking the logs",
    "TOOL",
    "SKILL BODY",
    "COMMAND OUTPUT",
  ]) {
    expect(context).not.toContain(left);
  }
});

test("a long message is cut", async ($, on) => {
  const clock = mock.clock(on);
  const long = "x".repeat(5000);
  const seen = engine(on, [user("prompt"), assistant(long)]);

  await $.command.run({ ...TYPED, command: "pickup", args: "" });
  await clock.settle();

  const context = seen.submitted?.notes[0] ?? "";
  expect(context).toContain(" […]");
  expect(context.length).toBeLessThan(long.length / 2);
});

test("a plain /clear submits nothing", async ($, on) => {
  const clock = mock.clock(on);
  const seen = engine(on);
  on("classic.SessionEnd", () => ({}));

  await $.classic.SessionEnd({
    reason: "clear",
    session_id: SESSION,
    transcript_path: TRANSCRIPT,
  });
  await clock.settle();

  expect(seen.submitted).toBeUndefined();
});

test("a session that ended leaves no transcript behind", async ($, on) => {
  const clock = mock.clock(on);
  const seen = engine(on);
  on("classic.Stop", () => ({}));
  on("classic.SessionEnd", () => ({}));

  await $.classic.Stop({
    session_id: SESSION,
    transcript_path: TRANSCRIPT,
    stop_hook_active: false,
  });
  await $.classic.SessionEnd({
    reason: "clear",
    session_id: SESSION,
    transcript_path: TRANSCRIPT,
  });
  await $.command.run({ ...TYPED, command: "pickup", args: "" });
  await clock.settle();

  expect(seen.submitted?.text).toStartWith(
    `We're continuing where another session (${SESSION}) ended.`,
  );
});
