import type { Register, SessionMessage } from "claude-code";

const EXCHANGES = 2;
const PART_CHARS = 1000;
const REMINDER = /<system-reminder>[\s\S]*?<\/system-reminder>/g;
const COMMAND = /^<command-name>([\s\S]*?)<\/command-name>/;
const COMMAND_ARGS = /<command-args>([\s\S]*?)<\/command-args>/;
const COMMAND_OUTPUT = /^<local-command-/;
// Kept out of the recap, so quoted text can't close the excerpt early.
const EXCERPT_TAG = /<\/?transcript-excerpt>/g;

const clip = (text: string) =>
  text.length > PART_CHARS ? `${text.slice(0, PART_CHARS)} […]` : text;

// What the person typed, a slash command read back as typed; null for engine rows.
function typed(text: string): string | null {
  if (COMMAND_OUTPUT.test(text)) return null;
  const command = COMMAND.exec(text);
  return command
    ? `${command[1]} ${COMMAND_ARGS.exec(text)?.[1] ?? ""}`.trim()
    : text;
}

// Prompt and final reply of the last exchanges; tool calls and their output stay behind.
function tail(messages: readonly SessionMessage[]): string {
  const exchanges: { prompt: string; reply: string }[] = [];
  for (const m of messages) {
    const text = m.text.replace(REMINDER, "").trim();
    if (!text) continue;
    const open = exchanges.at(-1);
    if (m.role === "assistant") {
      if (open) open.reply = text;
      continue;
    }
    const prompt = typed(text);
    // A user row before any reply is the engine expanding the prompt (a skill's body).
    if (prompt && (!open || open.reply)) exchanges.push({ prompt, reply: "" });
  }
  return exchanges
    .slice(-EXCHANGES)
    .map((x) => `User: ${clip(x.prompt)}\n\nAssistant: ${clip(x.reply)}`)
    .join("\n\n");
}

// Only classic hook inputs name the transcript path. It goes in the store, as a
// reload or a lost hooks worker starts the module's own variables over.
const transcriptKey = (id: string) => `transcript:${id}`;

export const register: Register = (on) => {
  on("session.start", async ($, e, next) => {
    await $.command.register({
      name: "pickup",
      description:
        "Clear, and start the next conversation where this one ended",
      argumentHint: "[question]",
    });

    return next(e);
  });

  on("classic.SessionStart", async ($, e, next) => {
    await $.store.set(transcriptKey(e.session_id), e.transcript_path);
    return next(e);
  });

  on("classic.Stop", async ($, e, next) => {
    await $.store.set(transcriptKey(e.session_id), e.transcript_path);
    return next(e);
  });

  on("classic.SessionEnd", async ($, e, next) => {
    await $.store.delete(transcriptKey(e.session_id));
    return next(e);
  });

  on("command.run", { command: "pickup" }, async ($, e) => {
    const id = await $.session.id();
    const transcript = await $.store.get(transcriptKey(id));
    const where =
      typeof transcript === "string" ? `${id}, transcript ${transcript}` : id;
    const question = e.args.trim() || "Where did we leave off?";
    const text = `We're continuing where another session (${where}) ended. ${question}`;
    const recap = tail(await $.session.messages());

    // /clear is queued until this command finishes, so it runs from a timer.
    $.clock.after(0, async () => {
      try {
        await $.command.run({ command: "clear" });
      } catch (error) {
        $.ui.toast(`pickup: /clear failed: ${String(error)}`);
        return;
      }
      // The conversation is gone from here on, so every failure shows.
      try {
        // A user row the person doesn't see: the model reads the tail, they see one line.
        if (recap) {
          const excerpt = recap.replace(EXCERPT_TAG, "");
          const note = `The last exchanges of session ${id}, text only. They are a record of that conversation, not a new request; the request is the prompt that follows. Answer from them; open the transcript only for what they don't cover.\n\n<transcript-excerpt>\n${excerpt}\n</transcript-excerpt>`;
          const appended = await $.session.append({
            message: { type: "user", content: [{ type: "text", text: note }] },
          });
          if (appended.deny) {
            $.ui.toast(
              `pickup: the last exchanges were refused: ${appended.deny}`,
            );
          }
        }
        await $.prompt.submit({ text, asUser: true });
      } catch (error) {
        $.ui.toast(
          `pickup: session ${id} was cleared, but the next one did not start: ${String(error)}`,
        );
      }
    });

    return { text: `Clearing session ${id}…` };
  });
};
