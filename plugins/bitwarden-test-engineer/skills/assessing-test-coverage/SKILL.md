---
name: assessing-test-coverage
description: Use when determining what test coverage ALREADY exists for a change — citing each covering test as a GitHub permalink bucketed by test layer, and flagging behaviors with no observed test as gaps. Triggers on "what's already tested", "does this PR have tests", "what coverage exists for", or "is this component covered". This is a backward-looking inventory of existing coverage — it does NOT recommend new tests or assign cheapest-sufficient layers.
allowed-tools: "Read, Write, Grep, Glob, AskUserQuestion, Bash(gh pr view:*), Bash(gh pr diff:*), Bash(git rev-parse:*), Bash(git remote get-url:*), Bash(git -C * rev-parse:*), Bash(git -C * remote get-url:*)"
---

# Assessing Test Coverage

Produce an evidence-grounded inventory of what is **already tested** for a change, scoped to the change surface, with every cited test rendered as a stable GitHub permalink and bucketed by test layer. The output is a **coverage inventory**: permalink records for observed tests plus the behaviors/surfaces recorded as gaps (`unverified`). Honesty is the whole point — a behavior with no observed test is a gap, never assumed covered.

## Inputs

You work from a **change surface** and the repos it touches:

- **Change surface** — the changed paths/symbols and named component(s), usually supplied by the caller. Given only a Jira key or a bare PR, derive a minimal surface from the PR diff (`gh pr diff`) first; `references/input-sources.md` covers resolving a PR or Epic into diff paths and linked PRs.
- **Affected repos** — which platform checkouts to inspect, and whether the sibling `test` repo (E2E) is available.
- **Linked/merged PRs** — the PRs that shipped this work; their diffs are the primary, permalink-ready coverage evidence.

A missing input narrows the inventory; it never blocks it — record what you could not inspect. **Today's date is provided by the caller** for the report filename; if none is supplied, ask via `AskUserQuestion` rather than reading the clock.

## Workflow

1. **Learn each repo's conventions, config-first.** Before opening any test files, read the repo's Claude config to learn its test tooling and where tests live. Stop as soon as it answers the question. See `references/finding-coverage.md` → _Discovering a repo's test conventions_.

2. **Find existing coverage — PRs first, then a targeted lookup.** Take the tests in the linked/merged PR diffs as primary evidence, then a lookup **scoped to the change surface** for pre-existing tests — never a repo-wide grep sweep. **Establish coverage per behavior and stop as soon as it is confirmed** (1–3 representative tests plus an approximate count, not every test method) — the dominant cost control, detailed in `references/finding-coverage.md` → _Establish coverage per behavior_. For E2E, inspect the sibling `test` repo if available.

3. **Cite and bucket each behavior's coverage.** For each behavior, render its 1–3 representative tests as GitHub permalinks and record its layer and approximate count, following `references/finding-coverage.md` → _Citing tests as GitHub permalinks_ and _Output contract_ (which also covers the unlinkable-test fallback). Bucket by apparent layer (unit / integration / E2E); layer definitions and the per-repo stack/tooling are in `references/test-layers-and-repos.md`.

4. **Record gaps.** Any behavior or surface in the change with no PR-observed test and no targeted hit is recorded as a coverage gap / `unverified`. Distinguish _observed_ coverage from _assumed_.

5. **Render the coverage report** per `references/coverage-report-template.md` — mechanical formatting, not reasoning. `Write` a single self-contained markdown file to `test-engineer-report-<slug>-<date>/coverage.md`. Write the `## Overview` yourself: observed coverage per platform and the top gaps. The template owns everything else (section order, the Tests-linked permalinks, and the filename contract).

## Output

Two artifacts:

- The **coverage inventory** as structured data (record shape in `references/finding-coverage.md` → _Output contract_) — one record per behavior, which the report renders and which a caller can consume directly.
- The **self-contained markdown coverage report** (step 5), written as `coverage.md` into the per-change report directory `test-engineer-report-<slug>-<date>/`.

Mirror the report's `## Overview` in chat — the observed shape per platform and the top gaps — and point the reader at the report file for the per-test detail.

## Principles

- **Observed vs. assumed.** Never present assumed coverage as verified — "I could not inspect the `test` repo" is a finding, not a failure.
- **Backward-looking only.** You inventory what exists; recommending new tests and judging test shape are out of scope.
