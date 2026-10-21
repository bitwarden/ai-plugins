import { expect, test } from "claude-code/testing";

const BEADS = [
  {
    id: "demo-2",
    title: "Wire the parser",
    status: "open",
    priority: 2,
    issue_type: "task",
  },
  {
    id: "demo-1",
    title: "Fix the login flow",
    status: "in_progress",
    priority: 1,
    issue_type: "bug",
  },
  {
    id: "demo-3",
    title: "Waiting on review",
    status: "blocked",
    priority: 0,
    issue_type: "task",
  },
];

const RUN = {
  command: "beads-pane",
  args: "",
  origin: { kind: "composer" },
  presentation: { isFullscreen: true, columns: 160 },
} as const;

const PANE = {
  component: "Pane",
  requestId: "beads",
  props: {
    title: "Beads",
    isFocused: false,
    bodyColumns: 60,
    placement: "dock",
    scroll: { offset: 0, bodyRows: 20 },
    view: {},
  },
} as const;

test("the beads command lists beads by status", async ($, on) => {
  const statuses: (string | undefined)[] = [];
  on("session.cwd", () => ({ value: "/work/demo" }));
  on("process.run", () => ({
    value: {
      exitCode: 0,
      stdout: JSON.stringify(BEADS),
      stderr: "",
      isStdoutTruncated: false,
      isStderrTruncated: false,
    },
  }));
  on("ui.status", ($, e) => {
    statuses.push(e.text);

    return { value: undefined };
  });
  on("ui.open", () => ({ value: { isPlaced: true } }));

  const ran = await $.command.run(RUN);
  expect(JSON.stringify(ran)).toContain(
    "beads: 1 in progress, 1 blocked, 1 open",
  );
  expect(statuses).toContain("beads: 1 in progress, 1 blocked, 1 open");

  for (const surface of ["terminal", "desktop"] as const) {
    const ui = await $.ui.mount({
      plugin: "bitwarden-beads-tools",
      surface,
      ...PANE,
    });
    expect(await ui.find({ text: /In progress \(1\)/ })).toBeDefined();
    expect(await ui.find({ text: /Fix the login flow/ })).toBeDefined();
    expect(await ui.find({ text: /Blocked \(1\)/ })).toBeDefined();
    await ui.unmount();
  }
});

test("bd 1.3 output wrapped in an issues object is read", async ($, on) => {
  on("session.cwd", () => ({ value: "/work/demo" }));
  on("process.run", () => ({
    value: {
      exitCode: 0,
      stdout: JSON.stringify({ issues: BEADS }),
      stderr: "",
      isStdoutTruncated: false,
      isStderrTruncated: false,
    },
  }));
  on("ui.status", () => ({ value: undefined }));
  on("ui.open", () => ({ value: { isPlaced: true } }));

  const ran = await $.command.run(RUN);
  expect(JSON.stringify(ran)).toContain(
    "beads: 1 in progress, 1 blocked, 1 open",
  );
});

test("outside a beads project the command says so", async ($, on) => {
  on("session.cwd", () => ({ value: "/work/plain" }));
  on("process.run", () => ({
    value: {
      exitCode: 1,
      stdout: "",
      stderr: "no beads database found",
      isStdoutTruncated: false,
      isStderrTruncated: false,
    },
  }));
  on("ui.status", () => ({ value: undefined }));

  const ran = await $.command.run(RUN);
  expect(JSON.stringify(ran)).toContain("No beads project here");
});
