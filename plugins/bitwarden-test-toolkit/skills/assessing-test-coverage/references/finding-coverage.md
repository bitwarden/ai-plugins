# Finding and citing existing test coverage

How to determine what a change is **already** tested by, scoped to the change surface, and how to cite each observed test as a stable link. This is the repo-reading half of test engineering — inventorying what exists. It does not recommend which layer a behavior _should_ live at.

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
   back to the per-repo stack/tooling table in `test-layers-and-repos.md` and **state the
   assumption** in the result.

This tier governs _conventions_ — what the tooling is and where tests live. Finding which
behaviors are _already covered_ is the next job, below.

## Finding existing coverage (PRs first, then a targeted lookup)

Reliably establishing what is **already tested** does not require grepping a whole repo. Work
two ordered moves, and record anything still unfound as a gap rather than dropping it:

1. **Merged/linked PRs are the backbone.** The PRs hanging off the Jira issue and its epic
   children (surfaced by the `researching-jira-issues` skill's PR links → `gh pr view`/`gh pr diff`) are the reliable record of
   the tests that shipped with this work, and are already permalink-ready via the PR head SHA.
   Take the tests observed in those PR diffs as primary coverage evidence.
2. **Targeted repo lookup for pre-existing tests.** Tests written _before_ this ticket won't
   appear in those PRs. Find them with a lookup **scoped to the change surface** — the files
   and symbols the PRs/diff touch, and the component named in the ticket — not a repo-wide
   sweep. Confirm conventions from config (above) so the lookup targets the right paths.

For end-to-end coverage, inspect the dedicated sibling `test` repo if it is checked out (see
`test-layers-and-repos.md` → _Where each layer lives_) and cite specific files; if it is not
available, record E2E coverage as `unverified`.

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

Cite every test as a commit-SHA permalink, never a branch link:
`https://github.com/<owner>/<repo>/blob/<SHA>/<path>#L<start>-L<end>`

- **SHA** — PR-sourced: the PR head (`gh pr view <pr> --json headRefOid`). Local: `git -C <repo> rev-parse HEAD`; if the tree is dirty, use HEAD and say so in Evidence.
- **owner/repo** — from the PR URL, or `git -C <repo> remote get-url origin`.
- **Line range** — best available: the full test block, else its declaration line, else file-only. Avoid file-only for newly authored tests.

Never fabricate a permalink. When an ingredient is genuinely unavailable, use the unlinkable fallback below.

### When a test cannot be linked

When the commit isn't reachable as a public permalink, record the test as `path — unlinkable: <reason>` rather than fabricating a URL

### Output contract

Return **one record per behavior** (not per test), carrying its layer, an approximate count,
1–3 representative tests as evidence, and — when the behavior was extracted from a Jira item —
the originating `source_issue` (`key` + browse `url`) so the report can link the behavior back to
its requirement (see `input-sources.md` → _Citing Jira issues as links_). The
`source_issue` is **carried through from intake** with the behavior — it is provenance recorded
when the behavior was extracted, not something coverage discovery determines; echo it through when
present. A behavior with no Jira source (e.g. found only in a PR diff) omits `source_issue`.

```
{
  "behavior": "bank account item type round-trips through import/export",
  "platform": "server",
  "layer": "integration",
  "status": "covered",
  "count": 21,
  "source_issue": {
    "key": "PM-32009",
    "url": "https://bitwarden.atlassian.net/browse/PM-32009"
  },
  "representative": [
    {
      "path": "test/Core.Test/Vault/.../CipherItemTypeTests.cs",
      "start_line": 42,
      "end_line": 89,
      "owner_repo": "bitwarden/server",
      "sha": "a1b2c3d4e5f6…",
      "permalink": "https://github.com/bitwarden/server/blob/a1b2c3d4e5f6…/test/Core.Test/Vault/.../CipherItemTypeTests.cs#L42-L89"
    }
  ]
}
```

A representative test that cannot be linked is recorded path-only with a reason inside
`representative` (`{ "path": "…", "unlinkable_reason": "no remote for local checkout" }`) —
never fabricate a URL. Behaviors/surfaces with no observed test are returned as gaps:

```
{ "behavior": "organization policy can restrict the Driver License item type", "platform": "server", "status": "unverified" }
```

Keep `representative` to at most three permalinks per behavior; the `count` conveys breadth
without listing every test. These records populate the report's **Tests (linked)** column
(rendering the representative permalinks) and the _Coverage gaps_ section.
