---
name: verifying-doc-parity
description: Use this skill whenever the user mentions doc drift, documentation verification, README or docs/ updates that follow a code change, or a doc-parity Stop hook block — even if the request does not name a skill or documentation explicitly. Also use as the documentation pass of a pull request review. Verifies or updates documentation at every documented ancestor scope of a code change; in review context, also discovers out-of-repo documentation the change invalidates. Triggered by phrasings such as "verify doc parity", "are my docs up to date", "did I miss any doc updates", "what documentation should this change touch", "do I need to update any docs for my current changes", or "check if the docs still match the code".
agent: general-purpose
context: fork
allowed-tools: WebFetch(domain:contributing.bitwarden.com)
---

# Verifying documentation parity

This skill is the judgment that code has drifted away from the documentation which describes it. It enforces the base obligations of the [documentation standard](https://contributing.bitwarden.com/contributing/documentation): docs and diagrams update in the same change as the code they describe, and a change that invalidates documentation the repo does not contain gets called out at review.

## Contexts

The skill runs in two contexts where change source and relevant document discovery differ.

- **Agent session**, invoked by the doc-parity Stop hook or on demand. The change is the working tree (`git diff HEAD` plus untracked files). Verification is in-repo only.
- **Pull request review**, run through the ai-review workflow. The change is the PR diff plus the PR description. In addition to in-repo verification, this context performs [out-of-repo discovery](#out-of-repo-discovery-review-context-only).

## Workflow

### Step 1: Assemble the change

Collect the full set of changed files and read the diff, not just the file list, because judging drift requires knowing what the change does. In a session, use `git diff HEAD` and `git ls-files --others --exclude-standard`. In a review, use the PR diff and read the PR description for intent.

Before walking the tree, consider whether the change qualifies as a tripwire false positive: a formatting-only diff, generated output, or a doc-comment-only edit that the Stop hook classified as code. When it does, **dismiss** the check with a one-line reason naming the false-positive class and end the skill.

### Step 2: Enumerate every documented ancestor scope

For each changed file, walk its directory chain from the file's own directory up to and including the repo root. A directory is a documented scope when it contains a `README.md`, a `docs/` directory, or diagram sources. Below component scope, the documentation surface is source-embedded: Rust `//!` module docs, C# XML doc comments, JSDoc/TSDoc on public symbols. When the changed area of a source file carries such doc comments, treat that file as its own documented surface. Collect the union of documented scopes and surfaces across all changed files.

Check every documented ancestor, not just the nearest one, since documentation layers by altitude: higher views sand off detail while still describing the changed behavior. A change can be current in its component README yet drift a root-level guide or a container diagram two scopes up.

### Step 3: Judge and act, per scope

For each documented scope or surface, exactly one of two outcomes:

- **Update.** If behavior contradicts documentation and the code is correct, fix the documentation. Do not leave them disagreeing. If the change adds behavior this scope's altitude should describe, add documentation of that new behavior. A scope's documentation describes what is present at that scope and below, regardless of whether higher-level callers currently exercise or guard against its use. Edit the documentation in the same change. When code was removed, remove its documentation, and treat a moved doc as a strict move. Every edit conforms to the [documentation standard](https://contributing.bitwarden.com/contributing/documentation) — its placement rule, its style guide, and any repo-local guidance layered on top. Consult the standard when a placement, format, or style question isn't obvious from what you already have. If placement routes a doc outside the working repo, handle it as an out-of-repo callout (see below) rather than an in-repo edit.
- **Attest.** Nothing documented at this scope drifted. State that explicitly, with a one-line reason grounded in what the doc actually says.

### Step 4: Report with per-scope attestation

Close with an explicit per-scope list so the user, or the PR review summary, can audit the judgment:

```text
Documentation parity:
- util/Seeder/Data (README.md) — updated: generator table gained the new distribution.
- util/Seeder (README.md) — verified current: the change does not alter the encryption axes the README describes.
- crates/bitwarden-crypto/src/lib.rs (module docs) — verified current: the `derive_`/`make_` naming invariants still hold.
- repo root (README.md) — verified current: no root-level behavior described there changed.
```

Every documented scope and surface from Step 2 appears in the list. A scope missing from the list means the verification is incomplete.

When the check exits early via Dismiss, the report is a single line naming the false-positive class:

```text
Documentation parity: dismissed — formatting-only diff, no documentation obligation.
```

## Out-of-repo discovery (review context only)

Out-of-repo documentation cannot be found by walking the tree, so derive search angles from the change itself:

1. Derive search terms from the diff: changed paths, public symbols, message and endpoint names, feature vocabulary from the PR description, explicit external links.
2. Search the contributing-docs (contributing.bitwarden.com, source repo `bitwarden/contributing-docs`) from those angles.
3. Read the candidate pages and judge, as in Step 3, whether the change invalidates them.
4. Call out every invalidated page in the review. The callout triggers the standard's external-docs flow per the documentation standard.
