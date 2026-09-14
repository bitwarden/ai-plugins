# Changelog

All notable changes to the Bitwarden Testing Tools Plugin will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-09-14

### Added

- `recommending-test-layers` skill: a forward-looking counterpart to `assessing-test-coverage` that recommends which tests a change needs and at which layer each belongs, following minimumCD's testing model. From a Jira key, Testmo CSV, an `assessing-test-coverage` report, a PR, or a feature description, it places each behavior at its lowest sufficient deterministic layer (static, unit, component, contract) to form a fast, fully controlled pre-merge gate, then grades criticality against Bitwarden's Defect Severity Classification Guide fetched live from Confluence when reachable (marking criticality `unverified` and noting the missing guide when it is not, rather than stopping) to decide which critical journeys additionally earn a smoke or E2E test, then routes a doubled external boundary to integration, an SLO-bound journey to synthetic monitoring, and irreducibly uncertain behavior to exploratory (each a post-deploy addition, never a substitute for deterministic coverage), and writes a markdown recommendation report under `${CLAUDE_PLUGIN_DATA}/recommending-test-layers/`. Ships an `evals/` trigger harness, kept in step with the `assessing-test-coverage` harness, so the two forward/backward coverage skills do not cannibalize each other's triggers. See the plugin README for details.

### Changed

- Replaced the per-skill eval runner with a single shared engine at `evals/run_real_eval.py` and a single shared `evals/README.md`. Previously `assessing-test-coverage` shipped a bespoke runner — a ~95-line quote-aware shell parser backing a read-only `gh`/`git` allowlist and real-work bail path — with its own README. The shared engine detects a trigger from streamed `stream-json` events, counting only a plugin-qualified `<plugin>:<skill>` `Skill` invocation or a `Read` of the skill's own `SKILL.md` (never a bare token substring), and resolves the target skill and plugin from `--skill`/`--plugin` or infers them from the eval-set path. Adversarial should-not-trigger queries are contained with `--allowedTools Skill Read` so they cannot clone repos or run build/test toolchains; `--timeout` bounds anything that stalls, recording a timed-out run as a non-trigger with a stderr warning; and each `claude -p` subprocess runs in its own session, reaped as a process group so its ~1GB Node child tree cannot pile up. Defaults are `--model claude-sonnet-5` and `--num-workers 3`. The runner writes the recording model into a top-level `model` field of its JSON summary, so a baseline updated by copying a run output carries the model it was measured on and the regression check fails a diff against a baseline recorded on a different model. A skill's `evals/` directory now holds only its data — `trigger-eval.json` and `baseline.json` — so adding evals for a new skill no longer requires copying the engine.
- Tightened the `recommending-test-layers` description so its `Do NOT use it to...` clause disclaims layer-worded inventory phrasings, which were cannibalizing the sibling `assessing-test-coverage` skill's dual-intent triggers.
- Recorded both `baseline.json` files on `claude-sonnet-5`: `recommending-test-layers` passes 10/10 should-trigger and 10/10 should-not-trigger; `assessing-test-coverage` passes 9/10 and 10/10, with `audit the current test coverage on the feat/cipher-key-rotation branch` (2/7) the single recorded below-threshold should-trigger query, documented in `evals/README.md`.

## [1.1.0] - 2026-08-12

### Added

- `writing-manual-test-cases` skill: authors new manual Gherkin test cases from a Jira ticket, PR, or feature description and delivers a paired `.txt` and Testmo-importable `.csv` under `${CLAUDE_PLUGIN_DATA}/writing-manual-test-cases/`, keeping generated files out of the repo under test so they cannot be committed by accident. Ported from the `bitwarden/test` repository so it is available org-wide rather than only to that repo's contributors. See the plugin README for details.

### Changed

- Ported skill standardizes the Automation Type for `Functional` cases on `Not Automating`. The original skill named both `None` and `Not Automating` in different sections, which produced inconsistent CSV exports between runs.

## [1.0.0] - 2026-07-24

### Added

- Initial release of the `bitwarden-testing-tools` plugin.
- `assessing-test-coverage` skill: an evidence-grounded inventory of what a change is already tested by. See the plugin README for details.
