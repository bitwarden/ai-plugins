# bitwarden-ai-telemetry

Claude Code hooks that emit **metadata-only** AI-usage telemetry as [OTLP](https://opentelemetry.io/docs/specs/otlp/) logs. The plugin makes AI-assisted development at Bitwarden observable: which skills, agents, and MCP tools are used, and which repos, branches, files, commits, and PRs a session produces. It **never captures code contents or prompt text**.

## What it does

The plugin registers Claude Code lifecycle hooks (`PostToolUse` and `SubagentStop`) that fire after tool use and subagent completion. Each hook POSTs a single OTLP-JSON log record describing what happened, using metadata only. The hooks emit four event families:

| Event         | Fires on                                           | Recovers                                                                                    |
| ------------- | -------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `bw.identity` | `Task` / `Agent` / `Skill` tool use; subagent stop | Skill and agent names that native telemetry redacts                                         |
| `bw.edit`     | `Edit` / `MultiEdit` / `Write` / `NotebookEdit`    | Repo slug, branch, base SHA, and the edited file **path**                                   |
| `bw.commit`   | `Bash` running `git commit`                        | Repo slug, branch, and the resulting commit **SHA**                                         |
| `bw.pr`       | `Bash` running `gh pr create`                      | Repo slug, branch, and the **PR number**                                                    |
| `bw.mcp`      | Any `mcp__*` tool                                  | The real `mcp__<server>__<tool>` name that native telemetry redacts to a generic identifier |

## What it collects

Metadata only. Specifically:

- Repository slug (`owner/name`) and current branch
- File **paths** relative to the repo root (never file contents)
- Commit SHAs and PR numbers
- Tool, skill, agent, and MCP server/tool **names**
- The Claude Code session id

**It never collects:**

- File contents or diffs
- Prompt text or model responses
- Tool arguments or tool results

It does not intentionally collect credentials or secrets — branch and file names are captured as-is, so an unusual name that happens to embed a token or codename passes through.

## Fail-open by design

Telemetry is best-effort and must never interfere with a working session. Every hook is guarded: the shared emitter swallows all errors, git and network calls are time-boxed, and each hook always exits `0`. If the destination is unreachable, misconfigured, or slow, the session proceeds unaffected and the record is dropped.

## Configuration

The OTLP destination is supplied at deploy time via the `BW_TELEMETRY_OTLP` environment variable (normally set org-wide through managed-settings.json's `env` block), and is not hardcoded anywhere in the plugin.

`BW_TELEMETRY_OTLP` has no default. If it isn't set, the hooks emit nothing.

The value must be an `https` URL whose host is `bitwarden.pw` or a subdomain of it (e.g. `https://ait.bitwarden.pw/v1/logs`). Anything else (`http://`, a different domain, a malformed URL) is treated exactly like an unset variable: the hooks emit nothing, with no error or log line to distinguish "not configured" from "configured but rejected."

## Requirements

- **Python 3** must be available on `PATH` (the hooks invoke `python3`). The hooks use only the Python standard library; no third-party packages are required.
- Git and the GitHub CLI (`gh`) are used opportunistically for git-linkage events; if they are absent, those events are skipped (fail-open).

## Installation

```bash
/plugin install bitwarden-ai-telemetry@bitwarden-marketplace
```

Restart Claude Code after installing so the hooks and any `env` configuration load at startup.

## Questions

For questions about this plugin, what it collects, or how to configure the destination, reach out in the **`#team-eng-ai`** Slack channel.
