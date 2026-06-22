# Finding and citing existing test coverage

How to determine what a change is **already** tested by, scoped to the change surface, and how to cite each observed test as a stable link. This is the repo-reading half of test engineering; the layer-mapping half (which layer a behavior _should_ live at) is in the `analyzing-test-stack` skill.

## Discovering a repo's test conventions (config-first)

Test conventions, tooling, and where tests live are usually documented in a repo's Claude
config — read it **before** opening any test files, and stop as soon as it answers the
question. This keeps token spend low on large repos. Work the tiers in order:

1. **Config first.** Read the repo's root `CLAUDE.md`, its `.claude/` directory (rules and
   settings), and any **nested `CLAUDE.md`** in the subdirectories the change touches (e.g.
   `clients/apps/<app>/CLAUDE.md`). Extract the test tooling, the test-file layout/naming, and
   any stated layer conventions.
2. **Test files as fallback — only for gaps config leaves.** If config is silent on a
   convention you need, read a _few representative_ test files near the change surface to
   confirm it. Do **not** sweep the repo.
3. **Generic stack table as last resort.** When neither config nor local tests answer, fall
   back to the per-repo stack/tooling table in the `analyzing-test-stack` skill's
   `references/monorepo-layout.md` and **state the assumption** in the result.

This tier governs _conventions_ — what the tooling is and where tests live. Finding which
behaviors are _already covered_ is the next job, below.

## Finding existing coverage (PRs first, then a targeted lookup)

Reliably establishing what is **already tested** does not require grepping a whole repo. Work
two ordered moves, and record anything still unfound as a gap rather than dropping it:

1. **Merged/linked PRs are the backbone.** The PRs hanging off the Jira issue and its epic
   children (`mcp__bitwarden-atlassian__get_issue_remote_links` → `gh pr view`/`gh pr diff`) are the reliable record of
   the tests that shipped with this work, and are already permalink-ready via the PR head SHA.
   Take the tests observed in those PR diffs as primary coverage evidence.
2. **Targeted repo lookup for pre-existing tests.** Tests written _before_ this ticket won't
   appear in those PRs. Find them with a lookup **scoped to the change surface** — the files
   and symbols the PRs/diff touch, and the component named in the ticket — not a repo-wide
   sweep. Confirm conventions from config (above) so the lookup targets the right paths.

For end-to-end coverage, inspect the dedicated sibling `test` repo if it is checked out (see
the `analyzing-test-stack` skill's `references/monorepo-layout.md` → _Where each layer lives_)
and cite specific files; if it is not available, record E2E coverage as `unverified`.

A behavior with no PR-observed test and no targeted hit is recorded as a coverage gap /
`unverified` — never silently assumed covered.

### Establish coverage per behavior, not per test — stop as soon as it's confirmed

The inventory is keyed to the **change's testable behaviors**, not to every test method in the
repo. For each behavior, find _whether and at what layer_ it is covered, capture **1–3
representative tests** plus an approximate **count** at that layer, then **move on** — do not
enumerate every test in a covered area. A behavior backed by 40 unit tests is recorded as
`{ count: ~40, representative: [3 permalinks] }`, not 40 records. This is the dominant cost control
on large repos: two or three confirming tests prove a behavior is covered; cataloguing the rest
burns tool calls, bloats the downstream report, and adds cost, not confidence.

## Citing tests as GitHub permalinks

Every test cited as **current coverage** must be rendered as a clickable
GitHub permalink so a reader can jump to the actual test. The link form is:

```
https://github.com/<owner>/<repo>/blob/<SHA>/<path>#L<start>-L<end>
```

Use the **commit SHA**, not a branch name. Branch links rot under rebase and
force-push; SHA links are stable.

### Acquiring the four ingredients

1. **`owner/repo`** — from the remote URL.
   - PR-sourced: parse from the PR URL (e.g. `gh pr view <pr> --json url`).
   - Local checkout: `git -C <repo> remote get-url origin` and parse the
     `github.com[:/]<owner>/<repo>(\.git)?` segment.
2. **Commit SHA**.
   - PR-sourced: `gh pr view <pr> --json headRefOid` returns the PR head SHA. This is
     the SHA the diff was computed against and is the right anchor for any
     tests-in-PR or tests-on-the-PR-branch references.
   - Local checkout: `git -C <repo> rev-parse HEAD` for the working-tree SHA. If the
     working tree is dirty (uncommitted changes), still use HEAD and note in the
     evidence that links point to HEAD, not the working tree.
3. **Path** — repo-relative path of the test file (no leading slash). The same path
   you'd pass to `Read`, minus the repo root.
4. **Line range** — start line through end line of the test declaration. Acceptable
   resolutions, in descending preference:
   - Full block: from the `it(`/`test(`/`Test(`/`func Test…(` declaration line through
     the matching closing brace.
   - Declaration only: the single line where the test name is declared (`#L42`).
   - File only (`#L1`) — accept reluctantly, and only when grep cannot localize the
     test. Avoid for newly authored tests.

### When a test cannot be linked

If any of the four ingredients is missing — no remote (`git remote get-url origin`
returns empty), detached HEAD with no remote, private fork the session cannot reach,
or the file exists only in a local working tree never pushed — record the test as
**unlinkable** with the reason. Never fabricate a URL. Both this skill's coverage report
(`coverage-report-template.md`) and the downstream `analyzing-test-stack` test-stack report
render these as `<span class="unlinkable">path — unlinkable: &lt;reason&gt;</span>`.

### Output contract

Return **one record per behavior** (not per test), carrying its layer, an approximate count,
1–3 representative tests as evidence, and — when the behavior was extracted from a Jira item —
the originating `source_issue` (`key` + browse `url`) so the report can link the behavior back to
its requirement (see `../../../references/input-sources.md` → _Citing Jira issues as links_). The
`source_issue` is **carried through from intake** with the behavior — it is provenance recorded
when the behavior was extracted, not something coverage discovery determines; echo it through when
present. A behavior with no Jira source (e.g. found only in a PR diff) omits `source_issue`.

```
{
  "behavior": "per-phase price resolution on schedule activation",
  "platform": "server",
  "layer": "integration",
  "status": "covered",
  "count": 21,
  "source_issue": {
    "key": "PM-1234",
    "url": "https://bitwarden.atlassian.net/browse/PM-1234"
  },
  "representative": [
    {
      "path": "test/Billing/.../ScheduleHandlerTests.cs",
      "start_line": 42,
      "end_line": 89,
      "owner_repo": "bitwarden/server",
      "sha": "a1b2c3d4e5f6…",
      "permalink": "https://github.com/bitwarden/server/blob/a1b2c3d4e5f6…/test/Billing/.../ScheduleHandlerTests.cs#L42-L89"
    }
  ]
}
```

A representative test that cannot be linked is recorded path-only with a reason inside
`representative` (`{ "path": "…", "unlinkable_reason": "no remote for local checkout" }`) —
never fabricate a URL. Behaviors/surfaces with no observed test are returned as gaps:

```
{ "behavior": "tier downgrade preserves seat count", "platform": "server", "status": "unverified" }
```

Keep `representative` to at most three permalinks per behavior; the `count` conveys breadth
without listing every test. The `analyzing-test-stack` recommender consumes these records as-is
to populate the report's Evidence (linked) column (rendering the representative permalinks) and
to seed its gap analysis.
