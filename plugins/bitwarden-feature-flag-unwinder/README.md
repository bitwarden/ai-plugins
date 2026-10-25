# Bitwarden Feature Flag Unwinder Plugin

Autonomous worker for the back end of the Feature Flags Lifecycle. An agent that executes one lifecycle step for one flag in one target repo (`bitwarden/clients`, `bitwarden/server`, `bitwarden/ios`, or `bitwarden/android`) — removing flagged code and opening one PR. All it needs is a flag key and a step. A Jira ticket is optional: with one, the PR links it and the agent comments the outcome on it.

Engineers can dispatch it from their own checkout (see [Dispatching cleanup yourself](#dispatching-cleanup-yourself)), and a single workflow in `bitwarden/ai-plugins` runs it once per (flag, repo) pair as a matrix job, either biweekly from Jira or on demand from a flag and step. Each job checks out exactly one target repo and mints a GH App token scoped to that repo only, so the agent never touches more than the one repo it runs against.

## Shape of the system

```
┌─────────────────────────────┐         ┌─────────────────────────────┐
│  find-tasks job             │         │  unwind job (clients)       │
│  (ai-plugins, biweekly cron)│  ─────▶ │  checks out one repo        │  ──▶ open PR
│                             │         │  + runs agent               │
│  queries Jira:              │         └─────────────────────────────┘
│    ready-for-cleanup AND    │         ┌─────────────────────────────┐
│    (flagged-logic-removal   │  ─────▶ │  unwind job (server)        │
│     OR server-flag-removal) │         │  + clients tags for Step 2  │  ──▶ open PR
│                             │         └─────────────────────────────┘
│  Step 1: one job per repo   │         ┌─────────────────────────────┐
│  Step 2: server job only    │  ─────▶ │  unwind job (ios)           │  ──▶ open PR
│                             │         │                             │
└─────────────────────────────┘         └─────────────────────────────┘
                                        ┌─────────────────────────────┐
                                   ───▶ │  unwind job (android)       │  ──▶ open PR
                                        └─────────────────────────────┘
```

Each `unwind` job follows the conventions of `bitwarden/clients/.github/workflows/sdk-update.yml`: it mints a GH App installation token from Azure Key Vault at runtime, commits as `bw-ghapp[bot]`, and uses a reusable branch guarded against human edits. The difference is that the workflow lives in one place instead of being copied into every target repo.

## What the agent handles

| Step | Scope                                           | Repos                         | Automation state      |
| ---- | ----------------------------------------------- | ----------------------------- | --------------------- |
| 1    | Remove flagged logic + per-repo flag definition | clients, server, ios, android | Automated             |
| 2    | Remove flag key from server `FeatureFlagKeys`   | server (reads clients tags)   | Automated (gated)     |
| 3    | Archive flag in LaunchDarkly                    | n/a                           | Manual — out of scope |

Step 2 is gated on the backward-compat rule: three major non-web client releases must ship between Step 1 and Step 2, unless the flag was web-only or server-only. Server runs also read the history and release tags of `bitwarden/clients`, `ios`, and `android` so the `computing-backward-compatibility` skill can compute the window. If the gate isn't clear, the agent reports the gap, on the ticket too if there is one, and stops.

**Steps 1 and 2 combine when the gate already passes.** A server Step 1 run checks the gate after removing the flagged logic. If it passes, the run also removes the `FeatureFlagKeys` constant in the same PR. That happens for a server-only flag (it never appeared in clients, ios, or android, so no client release depends on it), a web-only flag, or a flag whose client cleanup shipped long enough ago. Otherwise the constant stays for a later Step 2. Any PR that removes the constant carries a **Backward-compatibility validation** section: the commits each repo was searched at and, for a flag clients used, a table of each client's removal commit and PR, last release with the flag, first release without it, and the server version it became safe from.

Every PR the agent opens is pre-verified against the target repo's canonical build + test commands. If verification fails after the removal, the agent iterates on fixes within a bounded budget; if it still can't make the branch green, no PR is opened and the run reports the failure output, on the ticket too if there is one.

## Jira ticket conventions the scheduled run reads

Only the biweekly run depends on Jira, because Jira is how it finds work. Manual runs need no ticket, labels, or status. The scheduled run looks for cleanup tasks under a `[Follow Up]` epic (see [PM-45032](https://bitwarden.atlassian.net/browse/PM-45032) as the canonical shape):

- **Feature flags field** (`customfield_12076`): the kebab-case flag key, e.g. `pm-18612-otp-6-digits`.
- **Step label** (exactly one):
  - `flagged-logic-removal` → Step 1
  - `server-flag-removal` → Step 2
- **Trigger label**: `ready-for-cleanup` when the task is actionable. The workflow queries for the intersection of `ready-for-cleanup` and a step label.

Step 3 tasks intentionally carry no step label. The workflow skips tickets with a missing or malformed flag field, or with both step labels, and logs a warning for each in the run. It passes each remaining ticket to the agent along with its flag and step, so the PRs link it and the agent comments on it.

## Guards against human-in-the-loop state

Each agent run reuses the branch `flag-cleanup/<flag-key>-step-<N>` across runs (same pattern as `sdlc/sdk-update`). Before touching the branch:

- If the branch exists on the remote and the tip commit author isn't the agent's own git identity (`git config user.email`, which is `bw-ghapp[bot]` in CI), the agent refuses to overwrite manual edits and reports the existing PR.
- If the open PR carries a `stop-cleanup` label, the agent stops and reports the PR.

Removing the `stop-cleanup` label resumes the automated updates on the next run.

## Installation

Available through Bitwarden's Claude Code marketplace:

```bash
/plugin marketplace add https://github.com/bitwarden/ai-plugins
/plugin install bitwarden-feature-flag-unwinder@bitwarden-marketplace
```

Dependencies the agent assumes are installed:

- `bitwarden-atlassian-tools` — for the Atlassian MCP server, used only when a run has a ticket.
- `bitwarden-delivery-tools` — for `applying-pr-conventions`, `managing-feature-flags`, and `perform-preflight` skills.

## Deploying the automation

The automation is one workflow in this repo: [`.github/workflows/feature-flag-unwinder.yml`](../../.github/workflows/feature-flag-unwinder.yml). Nothing is installed in the target repos.

1. **`find-tasks`** runs every other Wednesday at 15:00 UTC (even ISO weeks, matching sprint cadence). It queries Jira and builds a matrix with one entry per (task, repo): four entries for each Step 1 task, one server entry for each Step 2 task.
2. **`unwind`** runs once per matrix entry. It mints a GH App token scoped to that single repo, checks the repo out at the workspace root, sets up that repo's toolchain to match its own `test.yml`, installs the plugins from this marketplace, and runs the agent. iOS jobs run on a macOS runner, the rest on Ubuntu.
3. **`workflow_dispatch`** runs on demand without Jira. Pass `flag` and `step` (both required for a manual run), optionally `jira_issue_key` to link a ticket, `draft` to open draft PRs, and `repo` to limit the run to one target repo. Leaving `flag` empty runs the scheduled Jira query instead.

Scheduled runs open PRs ready for review. Set the repository variable `FLAG_UNWINDER_DRAFT_PRS` to `true` to make them drafts.

### Required Azure KV secrets (keyvault `gh-org-bitwarden`)

The workflow follows the standard Bitwarden secret-retrieval pattern (`azure-login` → `get-keyvault-secrets` → `azure-logout`) rather than storing secrets directly on GitHub.

| Secret              | Used by                | Purpose                                                       |
| ------------------- | ---------------------- | ------------------------------------------------------------- |
| `BW-GHAPP-ID`       | `unwind`               | Bitwarden GH App installation ID                              |
| `BW-GHAPP-KEY`      | `unwind`               | Bitwarden GH App private key                                  |
| `ANTHROPIC-API-KEY` | `unwind`               | Claude API key for `anthropics/claude-code-action`            |
| `JIRA-EMAIL`        | `find-tasks`, `unwind` | Atlassian account email (JQL query, agent reads and comments) |
| `JIRA-API-TOKEN`    | `find-tasks`, `unwind` | Atlassian API token with read + comment permissions           |

The Atlassian cloud ID is resolved at runtime from `bitwarden.atlassian.net/_edge/tenant_info`, so it needs no secret.

### Required GH App installation permissions

The Bitwarden GH App needs installing on `bitwarden/clients`, `bitwarden/server`, `bitwarden/ios`, and `bitwarden/android` with:

- `contents: write` — commit, push to the flag-cleanup branch
- `pull-requests: write` — open or edit the PR
- `actions: read` — read workflow run metadata

Each `unwind` job requests a token for its one target repo only, so a job can't push to any other repo even though the app is installed on all four.

## Dispatching cleanup yourself

Engineers don't have to wait for the biweekly run.

### Across every repo

In any Claude Code session, ask:

```text
clean up feature flag pm-18612-otp-6-digits
run step 2 cleanup for pm-18612-otp-6-digits
clean up pm-18612-otp-6-digits step 1 for PM-45033 as draft PRs
```

The `dispatching-flag-cleanup` skill needs a flag key and a step. It asks for the step, whether the PRs should be drafts or ready for review, and a cleanup ticket, if you didn't say. The ticket is optional (answer "no ticket"), and if you name one instead of a flag, the skill reads the flag from its Feature flags field. It then works out the repos (all four for Step 1, server for Step 2), finds your local checkouts, shows you the plan, and after you confirm launches one background unwinder session per repo. Follow them with `claude agents`, and attach with `claude attach <id>` to watch one or approve a permission prompt. Run `claude` once in each repo before your first dispatch so it's trusted: background sessions won't start in an untrusted directory. The first session in clients also stops to ask about that repo's project MCP servers, which the agent doesn't need.

It finds each checkout from `CLIENTS_REPO`, `SERVER_REPO`, `IOS_REPO`, or `ANDROID_REPO` if set, otherwise as a sibling under one root (`BITWARDEN_REPOS_ROOT`, else the parent of the bitwarden checkout you're in, else the current directory). If it still can't find one, it asks you for the path. Each repo's build and tests run on your machine. The skill checks each repo's toolchain first, and if one is missing (say, no Xcode for iOS), it asks whether to proceed for that repo with CI validation: the agent skips the local build and tests, opens the PR anyway, and the PR's CI checks validate it.

### In a single repo

From the root of your own checkout of the target repo, give the agent the flag and step:

```bash
# Interactive: watch it work
claude --agent bitwarden-feature-flag-unwinder:feature-flag-unwinder "Unwind pm-18612-otp-6-digits step 1"

# Background: keep working, check on it with `claude agents`
claude --bg --agent bitwarden-feature-flag-unwinder:feature-flag-unwinder "Unwind pm-18612-otp-6-digits step 1 for PM-45033 as a draft PR"
```

It runs the same procedure as the scheduled workflow and ends with a summary: the PR URL, the branch, and whether it commented on the ticket. Behavior to expect:

- **Your identity.** It uses your `gh` auth and commits as your git identity. It treats your earlier commits on the `flag-cleanup/*` branch as its own, so you can re-run it on the same flag. If you later want the scheduled workflow to take a branch over, delete the branch first, because the bot treats your commits as human edits and won't overwrite them.
- **Repo from the checkout.** It reads the target repo from `origin`, which must be `bitwarden/clients`, `server`, `ios`, or `android`. It won't run from a fork.
- **Your checkout is left alone.** It works in its own git worktree next to your checkout (`<repo>-worktrees/flag-cleanup-<flag>-step-<N>`), created from a freshly fetched `origin/main` with its own dependency install. Your branch and uncommitted work are untouched, and you can keep working while it runs. The agent removes the worktree when the run succeeds, and keeps it when a run stops partway (failed verification, a denied push) so you can pick up the work. The summary gives its path and the cleanup commands.
- **Skips repos with nothing to remove.** It searches `origin/main` for the flag key first and stops without a branch or PR if there's nothing there.
- **Server runs need sibling checkouts.** For any server run it reads history and release tags from `clients`, `ios`, and `android`. It looks for them in `../clients`, `../ios`, and `../android`, or in `CLIENTS_REPO`, `IOS_REPO`, and `ANDROID_REPO` if you set them.
- **Real side effects.** It pushes a branch, opens a PR in the real repo, and, with a ticket, comments on it.

Setup, once:

1. Install this plugin plus `bitwarden-atlassian-tools` and `bitwarden-delivery-tools`.
2. To use tickets, the agent needs Jira access that can read and comment, typically an Atlassian MCP server: the hosted one (`mcp.atlassian.com`, signed in with OAuth) or `bitwarden-atlassian-tools` configured as its README describes. Runs without a ticket don't need it.
3. Make sure `gh auth status` succeeds with push access to the target repo, and that you have the target repo's toolchain installed so the build and tests can run.

## Why biweekly

Agent PRs still need human review and merge. Firing every Wednesday would stack unmerged PRs on top of each other. Every other Wednesday matches typical sprint cadence, giving reviewers time to clear each batch before the next arrives. Change the cron and the ISO-week gate to taste.

## Out of scope

- Operational / kill-switch flags.
- LaunchDarkly writes (segment hygiene, archival).
- Picking the Flag branch maintained when it isn't obvious. The agent assumes `true` for launched flags. Override it in the request (`flag branch maintained false`) or with `flag-branch-maintained: false` in the ticket's description.
- Cross-repo PR linking in titles. With a ticket, all four Step 1 PRs land on it as separate comments as the agents complete.
