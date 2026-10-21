import { atom, read, update } from "claude-code";
import type { EngineInterface, Register } from "claude-code";

import type { Bead, BeadsSnapshot, BeadStatus } from "../types";

const PANE = "beads";
const POLL_MS = 30_000;
const STATUSES: readonly BeadStatus[] = ["in_progress", "blocked", "open"];
const LABELS: Record<BeadStatus, string> = {
  in_progress: "In progress",
  blocked: "Blocked",
  open: "Open",
};
const COLORS: Record<BeadStatus, "warning" | "error" | "suggestion"> = {
  in_progress: "warning",
  blocked: "error",
  open: "suggestion",
};

const snapshot = atom(
  { plugin: "bitwarden-beads-tools", key: "snapshot" } as const,
  null,
);

// A null snapshot means the session's directory is not a beads project, so
// the pane and status line stay out of the way.
async function refresh($: EngineInterface): Promise<BeadsSnapshot | null> {
  const next = await load($);
  await update($, snapshot, () => next);
  $.ui.status(next === null ? undefined : summary(next));

  return next;
}

async function load($: EngineInterface): Promise<BeadsSnapshot | null> {
  const cwd = await $.session.cwd();
  const argv = [
    "bd",
    "list",
    "--json",
    "--brief",
    "--skip-labels",
    "-n",
    "0",
    "--status",
    STATUSES.join(","),
  ];
  const ran = await $.process
    .run(argv, { cwd, timeoutMs: 10_000 })
    .catch(() => null);

  if (ran === null || ran.exitCode !== 0) {
    return null;
  }

  try {
    // bd 1.3 wraps the list as { issues: [...] }; older releases print a bare array.
    const parsed: unknown = JSON.parse(ran.stdout || "[]");
    const rows = Array.isArray(parsed)
      ? parsed
      : (parsed as { issues?: unknown } | null)?.issues;

    return {
      beads: Array.isArray(rows) ? rows.map(toBead).filter(isBead) : [],
    };
  } catch {
    return { beads: [], error: "bd list returned output that is not JSON" };
  }
}

function toBead(row: unknown): Bead | null {
  if (typeof row !== "object" || row === null) {
    return null;
  }

  const { id, title, status, priority, issue_type } = row as Record<
    string,
    unknown
  >;

  if (typeof id !== "string" || !STATUSES.includes(status as BeadStatus)) {
    return null;
  }

  return {
    id,
    title: typeof title === "string" ? title : "",
    status: status as BeadStatus,
    priority: typeof priority === "number" ? priority : 4,
    type: typeof issue_type === "string" ? issue_type : "task",
  };
}

function isBead(bead: Bead | null): bead is Bead {
  return bead !== null;
}

export function summary({ beads }: BeadsSnapshot): string {
  const counts = STATUSES.map(
    (status) =>
      [status, beads.filter((bead) => bead.status === status).length] as const,
  );
  const parts = counts
    .filter(([, n]) => n > 0)
    .map(([status, n]) => `${n} ${LABELS[status].toLowerCase()}`);

  return `beads: ${parts.length === 0 ? "none open" : parts.join(", ")}`;
}

function clip(text: string, width: number): string {
  return text.length <= width
    ? text
    : text.slice(0, Math.max(0, width - 3)) + "...";
}

export const register: Register = (on) => {
  on("session.start", async ($, e, next) => {
    await $.command.register({
      name: "beads-pane",
      description: "Show this project's beads in a pane",
    });

    void refresh($).then((found) => {
      if (found !== null) {
        void $.ui.open({ id: PANE, title: "Beads" });
      }
    });
    $.clock.every(POLL_MS, () => void refresh($));

    return next(e);
  });

  on("command.run", { command: "beads-pane" }, async ($) => {
    const found = await refresh($);

    if (found === null) {
      return { text: "No beads project here (bd list found nothing to read)." };
    }

    await $.ui.open({ id: PANE, title: "Beads" });

    return { text: `Beads pane opened. ${summary(found)}` };
  });

  on("tool.call", { tool: "Bash" }, async ($, e, next) => {
    const ran = await next(e);

    if (/(^|[\s;&|(])bd\s/.test(e.command)) {
      void refresh($);
    }

    return ran;
  });

  on("classic.CwdChanged", async ($, e, next) => {
    const ran = await next(e);
    void refresh($);

    return ran;
  });

  on("ui.render", { component: "Pane", requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e);
    const current = await read($, snapshot);
    const width = Math.max(20, e.props.bodyColumns);

    if (current === null) {
      return <Text dimColor>No beads project in this directory.</Text>;
    }

    if (current.error !== undefined) {
      return <Text color="error">{current.error}</Text>;
    }

    if (current.beads.length === 0) {
      return <Text dimColor>No open beads.</Text>;
    }

    const groups = STATUSES.map((status) => ({
      status,
      beads: current.beads
        .filter((bead) => bead.status === status)
        .sort((a, b) => a.priority - b.priority || a.id.localeCompare(b.id)),
    })).filter((group) => group.beads.length > 0);

    return (
      <Box flexDirection="column">
        {groups.map((group) => (
          <Box key={group.status} flexDirection="column" marginBottom={1}>
            <Text bold color={COLORS[group.status]}>
              {LABELS[group.status]} ({group.beads.length})
            </Text>
            {group.beads.map((bead) => {
              const head = `P${bead.priority} ${bead.id} `;

              return (
                <Text key={bead.id}>
                  <Text dimColor>{head}</Text>
                  {clip(bead.title, width - head.length)}
                </Text>
              );
            })}
          </Box>
        ))}
      </Box>
    );
  });
};
