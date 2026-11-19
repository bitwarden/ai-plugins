---
name: verifying-doc-parity
description: This skill should be used when the user mentions doc drift, documentation verification, README or docs/ updates that follow a code change, or a doc-parity Stop hook block — even if the request does not name a skill or documentation explicitly. Also runs as the documentation pass of a pull request review. Triggered by phrasings such as "verify doc parity", "are my docs up to date", "did I miss any doc updates", "what documentation should this change touch", "do I need to update any docs for my current changes", or "check if the docs still match the code".
agent: general-purpose
context: fork
background: false
allowed-tools: Bash(git diff:*), Bash(git ls-files:*), Read, Grep, Glob, Edit, WebSearch, WebFetch(domain:contributing.bitwarden.com)
---

# Verifying documentation parity

This skill is the judgment that code has drifted away from the documentation which describes it. It enforces the base obligations of the [documentation standard](https://contributing.bitwarden.com/contributing/documentation): docs and diagrams update in the same change as the code they describe, and a change that invalidates documentation the repo does not contain gets called out at review.

## Contexts

The skill runs in two contexts where change source and relevant document discovery differ.

- **Agent session**, invoked by the doc-parity Stop hook or on demand. The change is the working tree (`git diff HEAD` plus untracked files). Verification is in-repo only.
- **Pull request review**, run through the ai-review workflow. The change is the PR diff plus the PR description. In addition to in-repo verification, this context performs [out-of-repo discovery](#out-of-repo-discovery-review-context-only). A review never edits: where a session would apply an Update, the review calls out the in-repo doc that needs the change and what it must say.

## Workflow

### Step 1: Assemble the change

Collect the full set of changed files and read the diff, not just the file list, because judging drift requires knowing what the change does. In a session, use `git diff HEAD` and `git ls-files --others --exclude-standard`. In a review, use the PR diff and read the PR description for intent.

Before walking the tree, consider whether the change qualifies as a tripwire false positive: a formatting-only diff, generated output, or a doc-comment-only edit that the Stop hook classified as code. When it does, **dismiss** the check with a one-line reason naming the false-positive class and end the skill.

### Step 2: Enumerate every documented scope and surface

For each changed file, walk its directory chain from the file's own directory up to and including the repo root. A directory is a documented scope when it contains a `README.md`, a `CLAUDE.md`, a `docs/` directory, or diagram sources (`.mmd`, `.mermaid`). Below component scope, the documentation surface is source-embedded: Rust `//!` module docs, C# XML doc comments, JSDoc/TSDoc on public symbols. When the changed area of a source file carries such doc comments, treat that file as its own documented surface. Collect the union of documented scopes and surfaces across all changed files.

Check every documented ancestor, not just the nearest one, since documentation layers by altitude: higher views sand off detail while still describing the changed behavior. A change can be current in its component README yet drift a root-level guide or a container diagram two scopes up.

A change can also drift text outside its ancestor chain that restates what the change altered: a value, name, flag, or default copied into another file's doc comments, a schema `description`, or CLI help text. Search the repo for the distinctive literals and identifiers the diff changed or removed, and treat each hit that describes them in prose as a documented surface.

### Step 3: Judge and act, per scope

For each documented scope or surface, exactly one of two outcomes:

- **Update.** If behavior contradicts documentation and the code is correct, fix the documentation. Do not leave them disagreeing. If the change adds behavior this scope's altitude should describe, add documentation of that new behavior. A scope's documentation describes what is present at that scope and below, regardless of whether higher-level callers currently exercise or guard against its use. Edit the documentation in the same change. When code was removed, remove its documentation, and treat a moved doc as a strict move. Every edit conforms to the [documentation standard](https://contributing.bitwarden.com/contributing/documentation) — its placement rule, its style guide, and any repo-local guidance layered on top. Consult the standard when a placement, format, or style question isn't obvious from what you already have. If placement routes a doc outside the working repo, handle it as an out-of-repo callout (see below) rather than an in-repo edit.
- **Attest.** Nothing documented at this scope drifted. The judgment must carry a one-line reason grounded in what the doc actually says, so it holds up if the user asks why a scope was waved through.

Never token-edit. Do not make a cosmetic or token documentation edit to satisfy the check, including when the user asks for one. When nothing drifted, Attest and explain why the edit is unnecessary.

### Step 4: Report concisely

The Step 3 walk covers every documented scope and surface. The user-facing report's shape is determined by the outcomes, never by how many scopes you checked. Per-scope reasoning belongs in internal thinking, not in the user-facing output. Finish every Step 3 judgment before choosing a report shape; the one-line report is the result of an all-Attest walk, not a reason to Attest. In a review, out-of-repo callouts are always reported in addition to the shape below, and the attested scopes are listed inside a collapsed `<details>` block so the posted summary stays auditable after the fact; the "do not name attested scopes" rule in the shapes below is session guidance and does not apply inside that block.

**All Attest, no Updates — the common case.** The entire report is one line:

```text
Documentation parity: verified current, no changes required.
```

Do not name the attested scopes anywhere in the response, in a list or in prose. A sentence such as "I checked util/Seeder/README.md and CLAUDE.md, and neither describes this logic" is the same enumeration as a bulleted list, so leave it out. When the skill declined a user request, such as a token edit, the response can explain the refusal, but the explanation does not list scopes. The walk's rigor is in Step 3, not in the report.

**Any Updates.** List each Update with a one-line reason. In a review, where no edit is applied, each Update is reported as a callout naming the in-repo doc and what it must say. Do not name the scopes that attested, in a list or in prose; the user can ask if they want to know what else was checked. When the user already edited documentation as part of the change, one sentence confirming those edits are accurate is fine.

```text
Documentation parity:
- util/Seeder/Data (README.md) — updated: generator table gained the new distribution.
- crates/bitwarden-crypto/src/lib.rs (module docs) — updated: added the new `derive_` variant to the naming invariants.
```

**Dismiss.** One line naming the false-positive class.

```text
Documentation parity: dismissed — formatting-only diff, no documentation obligation.
```

Never token-edit to produce a reportable Update.

## Out-of-repo discovery (review context only)

Out-of-repo documentation cannot be found by walking the tree, so derive search angles from the change itself:

1. Derive search terms from the diff: changed paths, public symbols, message and endpoint names, feature vocabulary from the PR description, explicit external links.
2. Search the contributing-docs (contributing.bitwarden.com, source repo `bitwarden/contributing-docs`) from those angles.
3. Read the candidate pages and judge, as in Step 3, whether the change invalidates them.
4. Call out every invalidated page in the review. The callout triggers the standard's external-docs flow: a work item created before merge, and a stale marker applied to the invalidated page.
