---
name: assessing-test-coverage
description: Use when determining what test coverage ALREADY exists for a change — inventorying the tests that currently cover a feature, PR, component, or set of changed paths across Bitwarden's repos, citing each as a stable GitHub permalink, bucketing it by test layer, and flagging behaviors with no observed test as gaps. Distinguishes observed coverage from assumed. Triggers on "what's already tested", "does this PR have tests", "what coverage exists for", "find the existing tests for", "is this component covered", "audit current test coverage". This is the backward-looking inventory that feeds test-stack analysis — it does NOT recommend new tests or assign cheapest-sufficient trophy layers; for that, use analyzing-test-stack.
allowed-tools: "Read, Write, Grep, Glob, AskUserQuestion, Bash(gh pr view:*), Bash(gh pr diff:*), Bash(git rev-parse:*), Bash(git remote get-url:*), Bash(git -C * rev-parse:*), Bash(git -C * remote get-url:*)"
---

# Assessing Test Coverage

Produce an evidence-grounded inventory of what is **already tested** for a change, scoped to the change surface, with every cited test rendered as a stable GitHub permalink and bucketed by test layer. This is a backward-looking, descriptive job: you report what exists, you do **not** recommend what to add or judge whether the shape is right — that is `analyzing-test-stack`'s job, which consumes this inventory.

The output is a **coverage inventory**: a set of permalink records for observed tests plus a list of behaviors/surfaces recorded as gaps (`unverified`). Honesty is the whole point — a behavior with no observed test is a gap, never assumed covered.

## Inputs

You work from a **change surface** and the repos it touches:

- **Change surface** — the changed paths/symbols and the named component(s). Usually supplied by the caller (the agent's evidence fan-out, or an `analyzing-test-stack` run). If you're handed only a Jira key or a PR with no resolved surface, derive a minimal surface from the PR diff (`gh pr diff`) before looking for coverage; the shared `../../references/input-sources.md` (the same intake guide `analyzing-test-stack` uses) covers how to resolve a PR or Epic into its diff paths and linked PRs.
- **Affected repos** — which platform checkouts to inspect, and whether the sibling `test` repo (E2E) is available.
- **Linked/merged PRs** — the PRs that shipped this work; their diffs are the primary, permalink-ready coverage evidence.

A missing input narrows the inventory; it never blocks it. Record what you could not inspect as part of the result.

**Today's date is provided by the caller** — use it for the report filename; do not attempt to read the clock. If no date is supplied, ask via `AskUserQuestion` rather than guessing.

## Workflow

1. **Learn each repo's conventions, config-first.** Before opening any test files, read the repo's Claude config to learn its test tooling and where tests live. Stop as soon as it answers the question. See `references/finding-coverage.md` → _Discovering a repo's test conventions_.

2. **Find existing coverage — PRs first, then a targeted lookup.** Take the tests in the linked/merged PR diffs as primary evidence, then do a lookup **scoped to the change surface** for pre-existing tests. Never a repo-wide grep sweep. For E2E, inspect the sibling `test` repo if available. See `references/finding-coverage.md` → _Finding existing coverage_.

3. **Cite and bucket each observed test.** Render every cited test as a GitHub permalink (commit SHA, not branch), following `references/finding-coverage.md` → _Citing tests as GitHub permalinks_. A test that genuinely cannot be linked is recorded path-only with an explicit reason — never fabricate a URL. Bucket each by apparent layer (unit / integration / E2E); for the layer definitions see the `analyzing-test-stack` skill's `references/testing-trophy.md`. For the per-repo stack/tooling reference, see that skill's `references/monorepo-layout.md`.

4. **Record gaps.** Any behavior or surface in the change with no PR-observed test and no targeted hit is recorded as a coverage gap / `unverified`. Distinguish _observed_ coverage from _assumed_.

5. **Write the coverage report.** Build a single self-contained HTML file (inline CSS, no external/CDN dependencies, no JS required) following `references/coverage-report-template.md`. **Inline the canonical stylesheet from `../../references/report-style-tokens.md` verbatim** — the same plugin-level styling source the test-stack report uses, so the two reports read as one instrument; do not re-pick colors or reintroduce a brand skin. Use the normative section IDs (`#overview`, `#summary`, `#evidence`, `#coverage`, `#gaps`) and write `#overview` yourself as a short synthesis. Write the report to the **current working directory** as `test-coverage-report-<slug>-<date>.html`, where `<slug>` is a short kebab-case identifier for the change and `<date>` is the caller-provided date.

## Output

Two artifacts:

- The **coverage inventory** as structured data — the record shape defined in `references/finding-coverage.md` → _Output contract_: one permalink record per observed test, plus the list of `unverified` gaps. When run under the `bitwarden-test-engineer` agent, return these records for `analyzing-test-stack` to consume as-is.
- The **self-contained HTML coverage report** (step 5), written to the current working directory.

Mirror the report's `#overview` in chat — the observed shape per platform and the top gaps — and point the reader at the report file for the per-test detail.

## Principles

- **Observed vs. assumed.** Never present assumed coverage as verified. "I could not inspect the `test` repo" is a finding, not a failure.
- **Scoped, not swept.** Coverage is established PR-first then scoped to the change surface — never a repo-wide grep.
- **Stable links only.** Permalinks use the commit SHA, not a branch. Unlinkable tests are recorded with a reason; URLs are never fabricated.
- **Backward-looking only.** You inventory what exists. Recommending new tests, assigning cheapest-sufficient layers, and judging trophy shape belong to `analyzing-test-stack` — hand off, don't cross over.
