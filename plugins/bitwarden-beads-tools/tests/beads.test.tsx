import { expect, mock, test } from "claude-code/testing";

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
      stdout: JSON.stringify({ issues: BEADS }),
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

test("output that is not JSON reads as an error in the status line", async ($, on) => {
  const statuses: (string | undefined)[] = [];
  on("session.cwd", () => ({ value: "/work/demo" }));
  on("process.run", () => ({
    value: {
      exitCode: 0,
      stdout: "not json",
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
  expect(JSON.stringify(ran)).toContain("beads: error reading bd list");
  expect(statuses).toContain("beads: error reading bd list");
});

test("a project with no open beads clears the status line", async ($, on) => {
  const statuses: (string | undefined)[] = [];
  let issues: unknown[] = [];
  on("session.cwd", () => ({ value: "/work/demo" }));
  on("process.run", () => ({
    value: {
      exitCode: 0,
      stdout: JSON.stringify({ issues }),
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

  await $.command.run(RUN);
  expect(statuses).toEqual([undefined]);

  issues = BEADS;
  await $.command.run(RUN);
  expect(statuses).toEqual([
    undefined,
    "beads: 1 in progress, 1 blocked, 1 open",
  ]);
});

test("a headless session neither runs bd nor opens the pane", async ($, on) => {
  let runs = 0;
  let opens = 0;
  const clock = mock.clock(on);
  on("command.register", () => ({ value: { command: "beads-pane" } }));
  on("session.start", (_, e) => ({ cwd: e.cwd }));
  on("session.cwd", () => ({ value: "/work/demo" }));
  on("process.run", () => {
    runs += 1;

    return {
      value: {
        exitCode: 0,
        stdout: JSON.stringify({ issues: BEADS }),
        stderr: "",
        isStdoutTruncated: false,
        isStderrTruncated: false,
      },
    };
  });
  on("ui.status", () => ({ value: undefined }));
  on("ui.open", () => {
    opens += 1;

    return { value: { isPlaced: true } };
  });

  await $.session.start({
    cwd: "/work/demo",
    surface: null,
    isInteractive: false,
  });
  await clock.advance(30_000);
  expect(runs).toBe(0);
  expect(opens).toBe(0);
});

test("an interactive session outside a beads project does not poll bd", async ($, on) => {
  let runs = 0;
  const clock = mock.clock(on);
  on("command.register", () => ({ value: { command: "beads-pane" } }));
  on("session.start", (_, e) => ({ cwd: e.cwd }));
  on("session.cwd", () => ({ value: "/work/plain" }));
  on("process.run", () => {
    runs += 1;

    return {
      value: {
        exitCode: 1,
        stdout: "",
        stderr: "no beads database found",
        isStdoutTruncated: false,
        isStderrTruncated: false,
      },
    };
  });
  on("ui.status", () => ({ value: undefined }));

  await $.session.start({
    cwd: "/work/plain",
    surface: "terminal",
    isInteractive: true,
  });
  await clock.advance(90_000);
  expect(runs).toBe(1);
});

test("the poll starts once a refresh finds a beads project", async ($, on) => {
  let runs = 0;
  let exitCode = 1;
  const clock = mock.clock(on);
  on("command.register", () => ({ value: { command: "beads-pane" } }));
  on("session.start", (_, e) => ({ cwd: e.cwd }));
  on("session.cwd", () => ({ value: "/work/demo" }));
  on("process.run", () => {
    runs += 1;

    return {
      value: {
        exitCode,
        stdout: exitCode === 0 ? JSON.stringify({ issues: BEADS }) : "",
        stderr: "",
        isStdoutTruncated: false,
        isStderrTruncated: false,
      },
    };
  });
  on("ui.status", () => ({ value: undefined }));
  on("ui.open", () => ({ value: { isPlaced: true } }));

  await $.session.start({
    cwd: "/work/demo",
    surface: "terminal",
    isInteractive: true,
  });
  await clock.advance(30_000);
  expect(runs).toBe(1);

  exitCode = 0;
  await $.command.run(RUN);
  await $.command.run(RUN);
  expect(runs).toBe(3);

  await clock.advance(30_000);
  expect(runs).toBe(4);
});

test("a refresh that a newer one overtook does not overwrite it", async ($, on) => {
  const statuses: (string | undefined)[] = [];
  let entered: () => void = () => {};
  const started = new Promise<void>((resolve) => {
    entered = resolve;
  });
  let release: () => void = () => {};
  const held = new Promise<void>((resolve) => {
    release = resolve;
  });
  let calls = 0;
  on("session.cwd", () => ({ value: "/work/demo" }));
  on("process.run", async () => {
    calls += 1;

    if (calls === 1) {
      entered();
      await held;

      return {
        value: {
          exitCode: 0,
          stdout: JSON.stringify({ issues: [] }),
          stderr: "",
          isStdoutTruncated: false,
          isStderrTruncated: false,
        },
      };
    }

    return {
      value: {
        exitCode: 0,
        stdout: JSON.stringify({ issues: BEADS }),
        stderr: "",
        isStdoutTruncated: false,
        isStderrTruncated: false,
      },
    };
  });
  on("ui.status", ($, e) => {
    statuses.push(e.text);

    return { value: undefined };
  });
  on("ui.open", () => ({ value: { isPlaced: true } }));

  const older = $.command.run(RUN);
  await started;
  await $.command.run(RUN);
  release();
  await older;

  expect(statuses).toEqual(["beads: 1 in progress, 1 blocked, 1 open"]);

  const ui = await $.ui.mount({
    plugin: "bitwarden-beads-tools",
    surface: "terminal",
    ...PANE,
  });
  expect(await ui.find({ text: /Fix the login flow/ })).toBeDefined();
  await ui.unmount();
});

test("the pane reads the beads again after /clear", async ($, on) => {
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
  let refreshed: () => void = () => {};
  const done = new Promise<void>((resolve) => {
    refreshed = resolve;
  });
  on("ui.status", () => {
    refreshed();

    return { value: undefined };
  });
  on("classic.SessionStart", () => ({}));

  await $.classic.SessionStart({ source: "clear" });
  await done;

  const ui = await $.ui.mount({
    plugin: "bitwarden-beads-tools",
    surface: "terminal",
    ...PANE,
  });
  expect(await ui.find({ text: /Fix the login flow/ })).toBeDefined();
  await ui.unmount();
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
