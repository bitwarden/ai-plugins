# Outbound payload reference

Every hook invocation that has something to report sends one HTTPS `POST` to `BW_TELEMETRY_OTLP` with `Content-Type: application/json` and a one-second timeout. The body is a single OTLP-JSON log record. The collector address must be `https` on `bitwarden.pw` or one of its subdomains; any other value is treated as unset and nothing is sent.

## Envelope

The envelope is identical for every event. Only `body` and `attributes` vary.

```json
{
  "resourceLogs": [
    {
      "resource": {
        "attributes": [
          {
            "key": "service.name",
            "value": { "stringValue": "bitwarden-ai-telemetry" }
          },
          { "key": "service.version", "value": { "stringValue": "1.5.0" } }
        ]
      },
      "scopeLogs": [
        {
          "scope": { "name": "bw.telemetry.hooks", "version": "1.5.0" },
          "logRecords": [
            {
              "timeUnixNano": "1790000000000000000",
              "body": { "stringValue": "bw.edit" },
              "attributes": [
                { "key": "event.name", "value": { "stringValue": "bw.edit" } },
                {
                  "key": "session.id",
                  "value": { "stringValue": "<session uuid>" }
                },
                {
                  "key": "bw.repo_full",
                  "value": { "stringValue": "bitwarden/ai-plugins" }
                },
                { "key": "bw.branch", "value": { "stringValue": "main" } },
                {
                  "key": "bw.base_sha",
                  "value": { "stringValue": "<40-char sha>" }
                },
                {
                  "key": "bw.file",
                  "value": {
                    "stringValue": "plugins/bitwarden-ai-telemetry/README.md"
                  }
                },
                { "key": "bw.tool", "value": { "stringValue": "Edit" } },
                { "key": "bw.hook", "value": { "stringValue": "PostToolUse" } },
                {
                  "key": "event.timestamp",
                  "value": { "stringValue": "2026-09-29T17:04:12.345Z" }
                },
                {
                  "key": "user.email",
                  "value": { "stringValue": "someone@bitwarden.com" }
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

Every attribute value is sent as a `stringValue`, including SHAs and PR numbers. An attribute whose value is empty is omitted from the record rather than sent blank, so a consumer should treat any key below as optional.

`body` and `event.name` always carry the same value, the event family.

The plugin's version is sent as the resource attribute `service.version` and as the scope `version`, the same two places native Claude Code telemetry carries its own. It is read from the plugin's `plugin.json` at run time, and both are omitted if the manifest can't be read.

## Attributes on every record

| Key               | Value                                                                                                                                                                                                |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `event.name`      | The event family, one of the six below                                                                                                                                                               |
| `event.timestamp` | Client time as ISO-8601 UTC with millisecond precision, matching the shape of native Claude Code's `event.timestamp` so both streams bucket on the same clock                                        |
| `user.email`      | `oauthAccount.emailAddress` from Claude Code's `.claude.json` (under `CLAUDE_CONFIG_DIR` when set, otherwise the home directory). Absent for a bare API key, `apiKeyHelper`, or third-party provider |
| `session.id`      | The Claude Code session id                                                                                                                                                                           |
| `bw.hook`         | The Claude Code hook event that fired (`SessionStart`, `PostToolUse`, `SubagentStop`, `UserPromptExpansion`)                                                                                         |

## Repository identity

Two different keys name a repository, and they are not interchangeable.

`repo` is the basename of the session's working directory. It is cheap and always present when the session has a cwd, but it names a folder, not a repository: a worktree or a renamed clone reports whatever its directory is called.

`bw.repo_full` is the `owner/name` slug parsed from the `origin` remote of the repository that owns the file or command, matching GitHub's own slug. The git events (`bw.edit`, `bw.commit`, `bw.pr`) carry it instead of `repo`, and are dropped entirely when no slug can be resolved, because a SHA, PR number or file path means nothing without the repository it belongs to.

## Event families

### `bw.session`

Sent once on `SessionStart`, so every session produces at least one record naming who ran it.

| Key    | Value                                       |
| ------ | ------------------------------------------- |
| `repo` | Basename of the session's working directory |

### `bw.identity`

Recovers the skill and agent names that native telemetry redacts. Sent on `PostToolUse` for `Task`, `Agent` and `Skill`, on `SubagentStop`, and on `UserPromptExpansion` when the expansion is a slash command. Other expansion types send nothing.

| Key             | Value                                                                                                                                                                 |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bw.agent_type` | The agent type, from `agent_type` on `SubagentStop` or `tool_input.subagent_type` on a `Task`/`Agent` dispatch                                                        |
| `bw.skill`      | The skill name, from `tool_input.skill` on a `Skill` dispatch or `command_name` on a slash expansion. A slash expansion may name a plugin command rather than a skill |
| `bw.tool`       | The tool that ran. A slash expansion reports `Skill` so it joins the same queries as the tool path; `bw.hook` tells the two apart. Absent on `SubagentStop`           |
| `repo`          | Basename of the session's working directory                                                                                                                           |

### `bw.edit`

Sent on `PostToolUse` for `Edit`, `MultiEdit`, `Write` and `NotebookEdit` when the edited file sits in a repository with an `origin` remote. The git context comes from the file's own repository, not the session's cwd.

| Key            | Value                                                                              |
| -------------- | ---------------------------------------------------------------------------------- |
| `bw.repo_full` | `owner/name` slug of the file's repository                                         |
| `bw.branch`    | Current branch (`rev-parse --abbrev-ref HEAD`)                                     |
| `bw.base_sha`  | Full SHA of `HEAD` at the time of the edit                                         |
| `bw.file`      | Path relative to the repository root, the shape GitHub uses for `files[].filename` |
| `bw.tool`      | The editing tool                                                                   |

### `bw.commit`

Sent on `PostToolUse` for a `Bash` call that ran a successful `git commit`. Dry runs, failed commits, and cases where the resolved `HEAD` does not match the SHA git printed send nothing.

| Key             | Value                                                                      |
| --------------- | -------------------------------------------------------------------------- |
| `bw.repo_full`  | `owner/name` slug of the committed repository                              |
| `bw.branch`     | The branch git reported for the commit, falling back to the current branch |
| `bw.commit_sha` | Full SHA of the new commit                                                 |

### `bw.pr`

Sent on `PostToolUse` for a `Bash` call that ran a successful `gh pr create` and printed the new PR's URL on stdout. A failed call that names an existing PR sends nothing.

| Key            | Value                                                                                |
| -------------- | ------------------------------------------------------------------------------------ |
| `bw.repo_full` | `owner/name` slug from the PR URL, or from the `origin` remote when the URL has none |
| `bw.branch`    | Current branch of the directory the command ran in                                   |
| `bw.pr_number` | The new PR's number                                                                  |

### `bw.mcp`

Sent on `PostToolUse` for any `mcp__*` tool. Native telemetry reports every MCP call as `mcp_tool`; this record carries the real name. It has no `bw.tool`, since the co-located native event already sets one.

| Key                | Value                                       |
| ------------------ | ------------------------------------------- |
| `bw.mcp_tool`      | The full `mcp__<server>__<tool>` identifier |
| `bw.mcp_server`    | The `<server>` segment                      |
| `bw.mcp_tool_name` | The `<tool>` segment                        |
| `repo`             | Basename of the session's working directory |
