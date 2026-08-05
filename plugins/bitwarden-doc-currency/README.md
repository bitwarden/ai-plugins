# bitwarden-doc-currency

Enforces the [documentation standard's](https://contributing.bitwarden.com/contributing/documentation) requirement that docs and diagrams update in the same change as the code they describe. Changes that invalidate out-of-repo docs get called out at review.

## Design

Four layers. Each layer covers the weakness of the one before it.

### Layer 1: instruction fragment

A `SessionStart` hook injects the [base documentation obligations](./hooks/doc-currency-instructions.md) into every session.

The fragment closes with a pointer to the published standard. This layer is prevention, so most sessions never reach the gate.

### Layer 2: Stop hook

A [deterministic tripwire](./hooks/doc-currency-check.sh) on the session-end event. The hook's scope is in-repo documentation only, since a file-path tripwire can only see the tree; out-of-repo docs belong to the CI face.

The hook blocks once per session and its message directs the agent to run the verification skill.

### Layer 3: semantic verification skill

`verifying-doc-currency` is the intelligence the hook invokes, also invocable on demand: read the diff, then read the documentation at every documented ancestor of the change, since references may occur at any level.

The outcome, per documented scope, is either an update or an explicit attestation that nothing documented there drifted.

### Layer 4: CI face

The same skill logic run as a PR reviewer through the existing ai-review workflow, covering human-authored changes that no in-session layer sees. This layer also owns out-of-repo discovery. Search terms are derived from the diff and used to search contributing-docs for references that need to be addressed. The callout triggers the standard's external-docs flow: a work item before merge and a stale marker on the page.

## Installation

```bash
/plugin install bitwarden-doc-currency@bitwarden-marketplace
```

Restart Claude Code after installing so the hooks load.

## Usage

The plugin needs no invocation in normal work: the fragment loads at session start, and the Stop hook fires only when the trigger rule matches. When the hook blocks, follow its message and run the skill. To verify documentation currency on demand:

```text
Do I need to update any docs for my current changes?
```

## Requirements

- `bash`, `git`, and `jq` on `PATH`. The hooks fail open: when a requirement is missing or the working directory is not a git repository, sessions proceed unaffected.
