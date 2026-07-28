# Changelog

All notable changes to the standup plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-28

### Added

- Initial plugin scaffold: `.claude-plugin/plugin.json` manifest, README, and the `skills/`, `commands/`, and `templates/` directory layout, plus marketplace registration. The report-generation command arrives in a subsequent release.
- Activity collectors (`gather.py`, `collect_github.py`, `collect_jira.py`, `collect_confluence.py`, `lib/`) ported as the `generate-standup-report` skill, with all paths abstracted to `${CLAUDE_PLUGIN_ROOT}` and identity/workspace kept strictly environment-driven.
- `/standup:init` guided preferences command: an interactive Q&A that captures identity, workspace, output-format, and output-style preferences and writes them to a dedicated, load-on-demand file at `~/.claude/standup/preferences.md` (never `~/.claude/CLAUDE.md`, never auto-loaded). Retains the init-user safety flow — unified diff preview, timestamped backup, and explicit Apply confirmation — retargeted at the dedicated file.
- `templates/user/` preference modules (`identity.md`, `output-format.md`, `output-style.md`, `recurring-responsibilities.md`) that `/standup:init` renders into the preferences file. The highlighted-item cap is a configurable preference rather than a fixed value.
- Finalized extraction of all output-style preferences into `templates/user/output-style.md` (highlighted-item cap, select→enrich→collapse pipeline, routine-tail collapse, editable RAG thresholds, kudos-only name discipline, optional voice-correction pass) as parameterized rules, and defined the load-on-demand preferences contract (ADR-084) in the `generate-standup-report` skill: a runner Reads `~/.claude/standup/preferences.md` at run start to supply identity/workspace args and env vars and to apply the output-format/output-style knobs when synthesizing the report.
- `deliver-standup-report` skill: delivers the finished report to a single first-match destination (org-roam memory, local markdown file, or stdout) via optional pluggable backends with graceful fallback (org-roam → local markdown → stdout), plus optional voice-correction gating. Personal-only skills (`create_memory`, `correct-document-voice`) are detected at runtime and degrade quietly when absent.
- `/standup:generate` report-generation command: a thin dispatcher that invokes the `standup-report-generator` orchestration agent to run the collect → synthesize → deliver pipeline. The agent reads the preferences file, preflights credentials, then chains `generate-standup-report` (collect activity as JSON), the new `synthesize-standup-report` skill (RAG-status heuristic, select→enrich→collapse pipeline, problem-first bullets, and self-lint gate producing report markdown), and `deliver-standup-report` (output routing). An optional argument passes a target user or time window through to the agent; otherwise it falls back to the preferences file.

### Changed

- Renamed the plugin from `standup-report` to `standup` so the preferences command is namespaced `/standup:init`. The bundled `generate-standup-report` skill keeps its name.
- Added example output to README illustrating the RAG-status report format, section labels, and markdown-link rendering.
- `deliver-standup-report` skill no longer references personal skill names (`create_memory`, `correct-document-voice`) in its definitions; destination routing and voice-correction gating are now described in capability-agnostic terms, driven entirely by user preferences.
- `standup-report-generator` agent description collapsed from multi-example block format to a single inline trigger-phrase description matching the repo's established agent pattern; removed `## Expected Inputs` and `## Expected Outputs` sections (the input/output contract belongs to the skills, not the agent).
- `templates/user/output-format.md` no longer offers `org-roam memory` as a destination during `/standup:init` — this is a personal-only capability not available in a standard marketplace session; the deliver skill still supports it if added manually to the preferences file.
- `templates/user/output-style.md` no longer prompts for a highlighted-item cap; the synthesis skill treats an absent cap as no ceiling. Users who want a cap can add `Highlighted-item cap: N` to their preferences file manually.
- `/standup:init` Q&A updated to match: removed org-roam destination option, removed cap question, clarified section labels are user-defined rather than defaulting to "Last week / This week / Blockers".
- `deliver-standup-report` skill no longer implements voice correction as a first-class pipeline step; delivery is now pure transport. Voice correction (when `Voice-correction pass: on` in output-style preferences) is applied as a final pass inside `synthesize-standup-report` before the report is returned.
- Voice correction removed as a named feature from all skill instructions and preference templates. Users who want a voice or register pass describe it freely in their `## Output style` preferences; the synthesize skill applies whatever output-style rules it receives.
- `/standup:init` identity Q&A tightened: Atlassian display name and GitHub username are always asked with no suggestions (handles can be anything); Atlassian email offers exactly two derived suggestions from the display name (`firstinitiallastname@bitwarden.com` and `firstname@bitwarden.com`) plus Other — no other guesses.
