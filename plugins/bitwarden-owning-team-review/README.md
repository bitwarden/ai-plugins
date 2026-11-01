# Bitwarden Owning-Team Review Plugin

Classifies whether a pull request needs review from the team that owns the code it changes.

## Overview

`CODEOWNERS` says which team owns every file, and a repository ruleset requires that team on domain critical paths. This plugin answers the remaining question for every other changed file: does the change need the owning team, or is approval from any engineer enough?

Three inputs decide the answer:

- **Global change kinds.** [`change-kinds.md`](./agents/owning-team-classifier/references/change-kinds.md) defines routine work the same way for every file. Fixes, and changes that follow a pattern the module's intent keeps, need any engineer. Everything else needs the owning team.
- **The module's `INTENT.md`.** It says what the module is for, where it is going, and what it may depend on. A change that contradicts it needs the owning team. Intent only raises a change to the owning team, never lowers one. See [`intent-format.md`](./agents/owning-team-classifier/references/intent-format.md).
- **Fail shut.** Any engineer is enough only when a signal the agent can evaluate says so. Without one, the change needs the owning team.

A module without an `INTENT.md` gets the global policy. The `INTENT.md` is optional, and holds only what differs from it.

The plugin classifies and nothing else. The agent never posts, approves, requests reviewers, or sets a status. The `owning-team-review` workflow acts on the result in CI.

## Why the agent does not post

**The agent reads untrusted input, so it does not hold the token that controls a merge gate.** The workflow posts everything, in evaluation mode and when enforcing.

- **It contains prompt injection.** The PR author writes the diff the agent reads. With no write grants, a successful injection can produce at most a wrong classification for that one PR. It cannot post a passing status, approve the PR, dismiss a review, or act on another PR. Read-only does not prevent a manipulated classification. The mechanical indicators and the fail-shut rule address that risk.
- **Most posts need no judgment.** The workflow updates the status on every review event by checking team membership, with no LLM run. The status must come from one pinned GitHub App so that nobody can fake it, and that App's token stays out of any session that reads contributor content. The workflow also posts the failure status when the agent crashes or times out, which the agent cannot do for itself.
- **The same agent is safe to run locally.** A backtest runs the agent against merged PRs and other teams' PRs. With no write grants, a local run cannot post to them.

## Feedback in the PR

**The workflow renders the agent's result into one sticky comment on the PR, with one section per team that needs to review.** It updates the comment on every push and every review. The comment has two readers:

- **The author** sees which teams the PR waits on, what in the change needs each team, why, and what to do next. That can be a question to take to a team, or files to split into a routine PR.
- **Each owning-team reviewer** reads only their team's section: what to look for, with links to the exact diff lines.

The agent groups its result by owner and writes each team's content for that team's reviewer. The workflow controls the format. The workflow renders a fixed template, writes the team handles itself from `CODEOWNERS`, links each `evidence` location at the head commit, and escapes the agent's text so it cannot add mentions, links, or HTML. Example:

```markdown
## Owning-team review

This PR needs review from **2 teams**: Platform, Key Management.
Admin Console's files are routine and need only any engineer.

---

### Platform (@bitwarden/team-platform-dev): waiting

**Why:** Structural. Conflicts with the module's intent: "Platform code does not
depend on feature code." ([client-managed-state.ts:5](link))

The change imports an Admin Console mapper into platform SDK state. Platform would
then depend on Admin Console code and have to move with it.

**For the author:** Ask Platform whether the mapper can register itself through the
existing repository registration point.

**For the reviewer, check:**

- Whether platform needs to know about this mapper, or can be handed it.

<details><summary>Was this classification right?</summary>

- [ ] Correct
- [ ] Didn't need us: this was routine for our module
- [ ] Should have needed us: we'd want to see this kind of change

</details>

---

### Key Management (@bitwarden/team-key-management-dev): approved by @reviewer

(The same structure, collapsed once the team approves.)

---

<details><summary>Any engineer: 3 files in Admin Console</summary>

`organization-sdk-mapper.ts`: pattern-following. These files could merge as their
own PR without waiting on Platform.

</details>
```

- **One comment, not one per team.** The author sees the whole picture in one place, and each team's status updates in place as approvals arrive.
- **Notifications come from review requests.** The workflow requests each required team, so the comment needs no mentions to reach them.
- **Long comments stay readable.** Approved teams and the "any engineer" files collapse, so the open part shows only the teams still being waited on. A PR that needs four or more teams is a signal that preflight's split suggestion was skipped.

In evaluation mode, the workflow posts the same comment under an "Evaluation mode, owning-team review is still required by CODEOWNERS" banner. The owning team still reviews every PR in evaluation mode, so a "Should have needed us" tick on an "any engineer" result is a direct report of a miss.

## Pull requests with several owning teams

**Each file is judged on its own, and each team approves only the files that need it.**

1. The classifier judges every file against its own module's `INTENT.md`. It never names a team.
2. The workflow looks up each required file's owner in the base commit's `CODEOWNERS`, and builds the set of teams whose approval is needed. A team whose files are all routine is not in the set.
   - **A file the base gives no owner uses the PR's own `CODEOWNERS` assignment.** That covers a new library the PR adds and assigns. It is safe because the ruleset requires approval for every `CODEOWNERS` change, so the assignment is itself reviewed.
   - **A file with no owner on either commit has no team to require.** The comment lists it as unowned, so the author and reviewers can see the ownership gap.
3. The `owning-team-review` status passes when every team in the set has an approval on the head commit from a member other than the author. GitHub's one required approval still applies.
4. A file that `CODEOWNERS` assigns to several teams follows GitHub's own rule: an approval from any one of them counts.
5. The author's own team follows the same rule as everyone else. A Platform engineer's change that needs Platform needs a different Platform engineer's approval.

A change that crosses an ownership boundary is flagged on the side whose intent it affects. When platform code imports an Admin Console mapper, the Platform file is flagged, because "platform never depends on feature code" is Platform's statement to enforce. The Admin Console file is judged on its own merits.

## Feedback loop

**Owning-team reviewers label each classification from the PR comment, and the workflow records the label.** The checkboxes at the end of the comment are the capture point.

### What a tick does

1. Ticking a box edits the comment, which fires an `issue_comment` `edited` event with the sender and the previous body.
2. The workflow compares the previous and new body to find which box changed.
3. The workflow checks which team's section the box is in, and who ticked it. A tick from a member of that team is a label for that team's classification. A tick from the author is recorded as author disagreement. Ticks from anyone else, including members of other required teams, are ignored.
4. The workflow appends one feedback record to the feedback log.
5. When the label disagrees with the classification, the workflow replies with one optional question: what made the change routine, or what should have flagged it.

### Rules

- **A tick is not an override.** It never changes the `owning-team-review` status. An owner who wants the PR to merge approves it, which already satisfies the gate.
- **One label per reviewer per head commit.** The latest tick wins.
- **A push resets the boxes.** A push produces a new classification, so the workflow re-renders the comment with empty boxes. Earlier labels stay attached to the earlier commit.
- **The workflow ignores its own edits.** It drops `edited` events sent by its own GitHub App, so re-rendering the comment does not trigger it again.

### Feedback record

The workflow writes one record per label. It stamps the versions itself, because the agent cannot reliably report the plugin version it runs as.

```json
{
  "pr": 18231,
  "head_sha": "<HEAD_SHA>",
  "base_sha": "<BASE_SHA>",
  "classifier_version": "0.1.0",
  "model": "<model ID>",
  "result": "owning-team-review",
  "entries": ["<the agent's entries for the labeled team>"],
  "label": "not-needed",
  "labeled_by": "<GitHub login>",
  "labeled_by_role": "owning-team",
  "reason": null,
  "labeled_at": "<ISO 8601 timestamp>"
}
```

- `label` is `correct`, `not-needed`, or `should-have-needed`.
- `base_sha` pins the intent, because the agent reads every `INTENT.md` from the base commit. Together with `classifier_version` and `model`, it identifies exactly what produced the classification.
- `reason` holds the answer to the follow-up question, when there is one.

### Where the labels go

A confirmed disagreement has one of two causes, and each feeds a different fix:

- **The module's intent was incomplete or stale.** The fix is an `INTENT.md` change: a new statement, a new trigger or "do not need" entry, or a different change kind default. The ruleset requires the owning team for every `INTENT.md` change.
- **The classifier misjudged the change kind.** The PR becomes an eval fixture, with its base commit and the expected kind and result. A change to the agent or to `change-kinds.md` must pass every fixture.

## Authoring layer

The same change kinds and `INTENT.md` reach the author before the PR exists, at three points:

| Point         | Where                                                                                                   | What it does                                                                                                                                                                                                                    |
| ------------- | ------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Plan          | `architecting-solutions` in `bitwarden-delivery-tools`, and `bitwarden-software-engineer`'s orient step | Reads the `INTENT.md` of every module the plan changes, and raises a non-routine or intent-contradicting change with the owning team before code is written.                                                                    |
| Edit          | The `inject-intent.sh` hook in this plugin                                                              | Attaches the governing `INTENT.md` to the first Read of a file in the module, which arrives before any edit. When an edit comes first, as when Write creates a new file, it pauses that one edit with the intent as the reason. |
| Before the PR | `perform-preflight` and `creating-pull-request` in `bitwarden-delivery-tools`                           | Runs this plugin's classifier on the branch with `classify-owning-team-review local`, and carries its findings into the PR body.                                                                                                |

Context that a PreToolUse hook adds reaches the agent only after the tool runs, which is too late to stop an edit. So the hook delivers the intent with a Read, which Claude Code requires before an edit, and pauses an edit only when no Read came first. It never pauses a second edit in the same module. The hook reads `INTENT.md` from the working tree, because it advises the author while they work. The classifier reads it from the base commit, because its result gates a merge.

## Components

| Component                                                                      | Type  | Purpose                                                                                                                                                                               |
| ------------------------------------------------------------------------------ | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`owning-team-classifier`](./agents/owning-team-classifier/AGENT.md)           | Agent | Classifies one PR. Writes `owning-team-review-<PR>.json`.                                                                                                                             |
| [`inject-intent.sh`](./hooks/inject-intent.sh)                                 | Hook  | Injects the governing `INTENT.md` before the first edit in a module, once per session.                                                                                                |
| [`classify-owning-team-review`](./skills/classify-owning-team-review/SKILL.md) | Skill | Runs the agent on the current branch (`local`) or on one or more PRs, and reports a table. Use it before opening a PR, to check an open PR, or to backtest intent against merged PRs. |

## How the classifier decides

The agent gives every change one of eight kinds, then decides whether the kind needs the owning team. See [`change-kinds.md`](./agents/owning-team-classifier/references/change-kinds.md) for definitions and examples.

| Kind                | Default needs the owning team |
| ------------------- | ----------------------------- |
| `fix`               | No                            |
| `pattern-following` | No                            |
| `debt-extending`    | Yes                           |
| `pattern-breaking`  | Yes                           |
| `special-case`      | Yes                           |
| `structural`        | Yes                           |
| `api-additive`      | Yes                           |
| `api-breaking`      | Yes                           |

Size is not a kind. A one-line rename of a public method is `api-breaking`.

The agent checks mechanical indicators before it judges anything. A removed export, a new `index.ts` export, or a new import from another owner's code sets a minimum kind that judgment cannot lower. Judgment covers four questions: is the change a fix or a behavior change, does it follow a pattern the module keeps or break it, is it general or for one consumer, and does it move toward the module's direction or away from it.

The first rule that applies decides:

| Signal            | When                                                                                         | Needs the owning team            |
| ----------------- | -------------------------------------------------------------------------------------------- | -------------------------------- |
| `change-trigger`  | The diff matches one of the module's change triggers.                                        | Yes                              |
| `intent-conflict` | The diff contradicts a specific statement in the module's `INTENT.md`, quoted in the result. | Yes                              |
| `do-not-need`     | An entry in the module's "do not need" list describes the change exactly.                    | No                               |
| `kind-default`    | None of the above. The kind's default applies, after the module's overrides.                 | Depends on the kind              |
| `ambiguous`       | The evidence did not settle the kind, so the agent chose the more serious one.               | Depends on the more serious kind |

**Domain critical paths and `INTENT.md` files are protected by a repository ruleset, not by the agent.** The agent classifies those files like any other file, and the workflow renders its explanation and review focus for them. The owning team is required when either the ruleset or the agent requires it.

## Usage

Check the current branch before opening a PR, check one PR, or backtest a module's intent against several merged PRs, from the root of a checkout of the PRs' repository:

```
/bitwarden-owning-team-review:classify-owning-team-review local
/bitwarden-owning-team-review:classify-owning-team-review local --base origin/rc
/bitwarden-owning-team-review:classify-owning-team-review 18231
/bitwarden-owning-team-review:classify-owning-team-review 17702 17840 17911
```

In CI, the workflow invokes the agent directly with the prompt `TARGET: PR #<number>`, then reads `owning-team-review-<number>.json`.

## Security

- **Intent comes from the PR's base commit.** A PR cannot change the intent it is judged by, and the ruleset requires the owning team for any `INTENT.md` change.
- **The PR title, body, and diff are untrusted.** The agent does not read the title or body. Text in the diff that addresses the agent has no effect on the result.
- **Inputs are validated before they reach a command.** The PR number, commit SHAs, and file paths are checked against strict patterns.
- **The agent is read-only on GitHub.** Its grants are `gh pr view`, `gh pr diff`, and the read-only `git` commands `diff`, `grep`, `merge-base`, `rev-parse`, and `show`, `Read` for its own reference files, and `Write` for its result file. `.claude/settings.json` denies GitHub and git write commands.
- **The workflow fails closed.** It treats a `no-verdict` result, a missing file, or an unparseable file as needing the owning team.

## Directory structure

```
bitwarden-owning-team-review/
├── .claude/
│   └── settings.json
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   └── owning-team-classifier/
│       ├── AGENT.md
│       └── references/
│           ├── change-kinds.md
│           └── intent-format.md
├── hooks/
│   ├── hooks.json
│   └── inject-intent.sh
├── evals/
│   ├── README.md                     # Corpus, scoring, and how to run
│   ├── classification-eval.json      # Synthetic pull requests and expected results
│   ├── real-pr-eval.json             # Real bitwarden/clients pull requests and hand labels
│   ├── fixtures/
│   │   ├── setup.sh                  # Builds each synthetic case's repository and canned PR
│   │   ├── setup-real.sh             # Replays a real PR on a base with draft INTENT.md files
│   │   ├── intent/                   # Draft INTENT.md files for the real-PR replay
│   │   └── gh-stub/gh                # Serves the canned PR in place of gh
│   ├── run-eval.sh
│   ├── score.sh
│   ├── score.jq
│   └── aggregate.sh
├── skills/
│   └── classify-owning-team-review/
│       └── SKILL.md
├── CHANGELOG.md
└── README.md
```
