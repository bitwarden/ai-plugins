# Changelog

All notable changes to the Bitwarden Eval Tools plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-17

### Added

- Initial release of the `bitwarden-eval-tools` plugin.
- `running-trigger-evals` skill: guidance for running reproducible trigger-rate
  evals against a skill's description / when_to_use text; the standard tool for
  Triggering evals (use skill-creator for Structure and Behavior).
- `trigger_eval.py` runner (stdlib-only) supporting two modes:
  - **installed**: watches an already plugin-registered skill token; a
    parameterized port of `creating-pull-request/evals/run_real_eval.py`.
  - **isolated**: evaluates a not-yet-installed skill via a throwaway
    slash-command file carrying the skill's real description, always cleaned up.
    Both modes scan tolerantly past unrelated `Skill` / `Read` tool_use calls so
    session-init skills firing first do not register as false negatives.
- Reliability-aware reporting: alongside the blended `should_trigger_pass_rate`
  and `should_not_trigger_pass_rate` (threshold 0.5, field names kept for
  continuity), a `reliability` block derived from a per-case `all_runs_agree`
  pass^k signal.
- Balance warning: a non-blocking stderr warning when the should_trigger /
  should_not_trigger split is skewed by more than ~20%.
- Opt-in baseline regression check (`--check-regression`): matches cases by
  query string, flags hard regressions and reliability regressions, exits `1`
  on either, and always prints the full JSON summary.
- Report-only sibling-exclusion field (`--exclude-skill`): records whether
  named sibling skill tokens also fired, for catching skill-vs-sibling
  triggering overlap without changing pass/fail semantics.
- Reference documentation (`references/cli-reference.md`,
  `references/authoring-eval-sets.md`) and worked examples
  (`examples/sample-eval-set.json`, `examples/sample-report.json`).

---

## Version Format

Plugin version tracks eval-runner and skill changes:

- **Major version**: Breaking changes to the CLI, report schema, or skill structure.
- **Minor version**: New flags, report fields, or reference documentation.
- **Patch version**: Bug fixes, clarifications, documentation improvements.
