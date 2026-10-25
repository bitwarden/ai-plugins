# Bitwarden Feature Flag Unwinder Plugin

Autonomous worker for the back end of the [Feature Flags Lifecycle](https://bitwarden.atlassian.net/wiki/spaces/EN/pages/1152417888). An agent that lives inside each target repo (`bitwarden/clients`, `bitwarden/server`, `bitwarden/ios`, `bitwarden/android`) and executes one lifecycle step for one flag in that repo — removing flagged code, opening one draft PR, and commenting the URL back on the originating Jira task.

A thin biweekly conductor queries Jira and dispatches `repository_dispatch` events to each per-repo workflow. The agent never clones other repos and never touches more than the one it's invoked inside.

## Shape of the system

```
┌─────────────────────────────┐         ┌─────────────────────────────┐
│  Conductor workflow         │         │  per-repo workflow          │
│  (ops repo, biweekly cron)  │  ─────▶ │  (bitwarden/clients)        │  ──▶ draft PR
│                             │         │  checks out self + agent    │
│  queries Jira:              │         └─────────────────────────────┘
│    ready-for-cleanup AND    │         ┌─────────────────────────────┐
│    (flagged-logic-removal   │  ─────▶ │  per-repo workflow          │
│     OR server-flag-removal) │         │  (bitwarden/server)         │  ──▶ draft PR
│                             │         └─────────────────────────────┘
│  Step 1: dispatch to all 4  │         ┌─────────────────────────────┐
│  Step 2: dispatch to server │  ─────▶ │  per-repo workflow          │
│  via repository_dispatch    │         │  (bitwarden/ios)            │  ──▶ draft PR
└─────────────────────────────┘         └─────────────────────────────┘
                                        ┌─────────────────────────────┐
                                   ───▶ │  per-repo workflow          │
                                        │  (bitwarden/android)        │  ──▶ draft PR
                                        └─────────────────────────────┘
```

This matches the pattern used by `bitwarden/clients/.github/workflows/sdk-update.yml`: workflow lives in the target repo, checks out self, mints a GH App installation token from Azure Key Vault at runtime, commits as `bw-ghapp[bot]`, and uses a reusable branch guarded against human edits.

## What the agent handles

| Step | Scope                                           | Repos dispatched              | Automation state      |
| ---- | ----------------------------------------------- | ----------------------------- | --------------------- |
| 1    | Remove flagged logic + per-repo flag definition | clients, server, ios, android | Automated             |
| 2    | Remove flag key from server `FeatureFlagKeys`   | server (with clients sidecar) | Automated (gated)     |
| 3    | Archive flag in LaunchDarkly                    | n/a                           | Manual — out of scope |

Step 2 is gated on the backward-compat rule: three major non-web client releases must ship between Step 1 and Step 2 unless the flag was web-only. The server workflow mounts a read-only sidecar checkout of `bitwarden/clients` so the `computing-backward-compatibility` skill can compute the compat window from the clients tag history. If the gate isn't clear, the agent comments the gap on the Jira ticket and stops.

Every PR the agent opens is pre-verified against the target repo's canonical build + test commands. If verification fails after the removal, the agent iterates on fixes within a bounded budget; if it still can't make the branch green, no PR is opened and the Jira comment carries the failure output.

## Jira ticket conventions the agent reads

The agent expects cleanup tasks under a `[Follow Up]` epic (see [PM-45032](https://bitwarden.atlassian.net/browse/PM-45032) as the canonical shape):

- **Feature flags field** (`customfield_12076`): the kebab-case flag key, e.g. `pm-18612-otp-6-digits`.
- **Step label** (exactly one):
  - `flagged-logic-removal` → Step 1
  - `server-flag-removal` → Step 2
- **Trigger label**: `ready-for-cleanup` when the task is actionable. The conductor queries for the intersection of `ready-for-cleanup` and a step label.

Step 3 tasks intentionally carry no step label. Tickets missing the flag field, missing the step label, or carrying both step labels cause the agent to abort and comment the specific gap on the ticket.

## Guards against human-in-the-loop state

Each agent run reuses the branch `flag-cleanup/<flag-key>-step-<N>` across runs (same pattern as `sdlc/sdk-update`). Before touching the branch:

- If the branch exists on the remote and the tip commit author isn't `bw-ghapp[bot]`, the agent refuses to overwrite manual edits and links the existing PR on Jira.
- If the open PR carries a `stop-cleanup` label, the agent bails and links the PR on Jira.

Removing the `stop-cleanup` label resumes the automated updates on the next dispatch.

## Installation

Available through Bitwarden's Claude Code marketplace:

```bash
/plugin marketplace add https://github.com/bitwarden/ai-plugins
/plugin install bitwarden-feature-flag-unwinder@bitwarden-marketplace
```

Dependencies the agent assumes are installed:

- `bitwarden-atlassian-tools` — for the Atlassian MCP server used to read the Jira task and comment back.
- `bitwarden-delivery-tools` — for `applying-pr-conventions`, `managing-feature-flags`, and `perform-preflight` skills.

## Deploying the automation

Two workflow templates ship in [`examples/`](examples/):

- **[`per-repo-workflow.yml`](examples/per-repo-workflow.yml)** — copy into **each** target repo at `.github/workflows/feature-flag-unwinder.yml`. Edit the single `_REPO:` line to match the current repo name (`clients`, `server`, `ios`, or `android`). The rest is identical across repos. Each repo's workflow is independently triggered via `repository_dispatch: feature-flag-unwinder` and operates only on itself.
- **[`conductor-workflow.yml`](examples/conductor-workflow.yml)** — copy into an ops repo you control at `.github/workflows/feature-flag-unwinder-conductor.yml`. Runs every other Wednesday at 15:00 UTC (even ISO weeks, matching sprint cadence), queries Jira, and fans out `repository_dispatch` events to each target repo. Does not touch target-repo code itself.

### Required Azure KV secrets (keyvault `gh-org-bitwarden`)

The templates follow the standard Bitwarden secret-retrieval pattern (`azure-login` → `get-keyvault-secrets` → `azure-logout`) rather than storing secrets directly on GitHub.

| Secret              | Used by           | Purpose                                                           |
| ------------------- | ----------------- | ----------------------------------------------------------------- |
| `BW-GHAPP-ID`       | both workflows    | Bitwarden GH App installation ID                                  |
| `BW-GHAPP-KEY`      | both workflows    | Bitwarden GH App private key                                      |
| `ANTHROPIC-API-KEY` | per-repo workflow | Claude API key for `anthropics/claude-code-base-action`           |
| `JIRA-EMAIL`        | both workflows    | Atlassian account email (conductor: for JQL; agent: for comments) |
| `JIRA-API-TOKEN`    | both workflows    | Atlassian API token with read + comment permissions               |

### Required GH App installation permissions

The Bitwarden GH App needs installing on `bitwarden/clients`, `bitwarden/server`, `bitwarden/ios`, and `bitwarden/android` with:

- `contents: write` — commit, push to the flag-cleanup branch; `repository_dispatch` fan-out from the conductor
- `pull-requests: write` — open or edit the draft PR
- `actions: read` — read workflow run metadata

## Running the agent manually

For local development and testing — invoke the agent against an already-checked-out repo:

```text
Unwind the flag per PM-45033 — this is the clients repo. Operate on the current working directory.
```

The agent treats cwd as the target repo. Set `JIRA_ISSUE_KEY` and `REPO` env vars (and for Step 2 server runs, `CLIENTS_REPO` to a path with full tag history).

## Why biweekly

Agent PRs still need human review and merge. Firing every Wednesday would stack unmerged PRs on top of each other. Every other Wednesday matches typical sprint cadence, giving reviewers time to clear each batch before the next arrives. Change the cron and the ISO-week gate to taste.

## Out of scope

- Operational / kill-switch flags.
- LaunchDarkly writes (segment hygiene, archival).
- Picking the winning variation when it isn't obvious. The agent assumes `true` for launched flags; override by adding `winning-variation: false` to the Jira task description.
- Cross-repo PR linking in titles. All four Step 1 PRs land in Jira as separate comments as the agents complete.
