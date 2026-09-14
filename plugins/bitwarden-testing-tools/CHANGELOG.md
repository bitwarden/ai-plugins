# Changelog

All notable changes to the Bitwarden Testing Tools Plugin will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1] - 2026-09-14

### Changed

- Consolidated the per-skill eval runners into a single shared engine at `evals/run_real_eval.py`. The `assessing-test-coverage` and `recommending-test-layers` skills previously each shipped a byte-identical copy of the runner that differed only in a hardcoded skill token, so every engine fix had to be hand-applied to both. The shared runner resolves the target skill token from `--skill`, or infers it from the eval-set path when the flag is omitted, so a skill's `evals/` directory now holds only its data (`trigger-eval.json`, `baseline.json`) and a short README. Adding evals for a new skill no longer requires copying the engine.

### Fixed

- Restored the `SKILL.md` guard in the shared runner's trigger detection. The consolidated engine matched a bare skill-token substring, so an exploratory `Read` of the skill's own `evals/` directory (the eval's working directory) counted as a trigger and inflated should-trigger rates, and the streaming path matched the token anywhere in a `Skill` or `Read` input's partial JSON. Detection now counts only a plugin-qualified `Skill` invocation (`<plugin>:<skill>`) or a `Read` of the skill's own `SKILL.md`; the plugin token is resolved from `--plugin` or inferred from the eval-set path.
- Tightened the `recommending-test-layers` description so its `Do NOT use it to...` clause disclaims layer-worded inventory phrasings ("or which layers they land at"), which were cannibalizing the sibling `assessing-test-coverage` skill's dual-intent triggers.
- Re-recorded both `baseline.json` files with the tightened runner and description; the previous baselines were recorded with the looser detection, so this supersedes the 1.2.0 baselines. `recommending-test-layers` now passes 10/10 should-trigger and 10/10 should-not-trigger. `assessing-test-coverage` passes 9/10 should-trigger and 10/10 should-not-trigger: its `does the autofill refactor PR ... which layers do they land at` query recovered from below threshold to a pass now that the sibling no longer cannibalizes it, leaving `audit the current test coverage on the feat/cipher-key-rotation branch` (2/7) as the single recorded below-threshold should-trigger query, documented in `skills/assessing-test-coverage/evals/README.md`.

## [1.2.0] - 2026-09-11

### Added

- `recommending-test-layers` skill: a forward-looking counterpart to `assessing-test-coverage` that recommends which tests a change needs and at which layer each belongs, following minimumCD's testing model. From a Jira key, Testmo CSV, an `assessing-test-coverage` report, a PR, or a feature description, it places each behavior at its lowest sufficient deterministic layer (static, unit, component, contract) to form a fast, fully controlled pre-merge gate, then grades criticality against Bitwarden's Defect Severity Classification Guide fetched live from Confluence when reachable (marking criticality `unverified` and noting the missing guide when it is not, rather than stopping) to decide which critical journeys additionally earn a smoke or E2E test, then routes a doubled external boundary to integration, an SLO-bound journey to synthetic monitoring, and irreducibly uncertain behavior to exploratory (each a post-deploy addition, never a substitute for deterministic coverage), and writes a markdown recommendation report under `${CLAUDE_PLUGIN_DATA}/recommending-test-layers/`. Ships an `evals/` trigger harness, kept in step with the `assessing-test-coverage` harness, so the two forward/backward coverage skills do not cannibalize each other's triggers. See the plugin README for details.

### Changed

- Both eval harnesses aligned with the `bitwarden-delivery-tools` runner pattern: the bespoke read-only `gh`/`git` allowlist and real-work bail path (a ~95-line quote-aware shell parser) were removed in favor of detecting the target skill token as it streams into a `Skill`/`Read` tool input. The adversarial should-not-trigger queries are now contained by launching each subprocess with `--allowedTools Skill Read`, so they can't clone repos or run build/test toolchains, with `--timeout` bounding anything that stalls. This drops each `run_real_eval.py` from 324 to 187 lines and removes the shell-parsing guard that accumulated most of the review churn while never shipping. To stop the runner from exhausting memory, each `claude -p` subprocess (a ~1GB Node process with its own child tree) now runs in its own session and is reaped as a process group on trigger, completion, or timeout — `process.kill()` had reaped only the parent and orphaned the Node children until they piled up — and the default `--num-workers` was lowered from 5 to 3 to cap peak memory. Both harnesses now default to `--model claude-sonnet-5`, and `baseline.json` was re-recorded on that model.

## [1.1.0] - 2026-08-12

### Added

- `writing-manual-test-cases` skill: authors new manual Gherkin test cases from a Jira ticket, PR, or feature description and delivers a paired `.txt` and Testmo-importable `.csv` under `${CLAUDE_PLUGIN_DATA}/writing-manual-test-cases/`, keeping generated files out of the repo under test so they cannot be committed by accident. Ported from the `bitwarden/test` repository so it is available org-wide rather than only to that repo's contributors. See the plugin README for details.

### Changed

- Ported skill standardizes the Automation Type for `Functional` cases on `Not Automating`. The original skill named both `None` and `Not Automating` in different sections, which produced inconsistent CSV exports between runs.

## [1.0.0] - 2026-07-24

### Added

- Initial release of the `bitwarden-testing-tools` plugin.
- `assessing-test-coverage` skill: an evidence-grounded inventory of what a change is already tested by. See the plugin README for details.
