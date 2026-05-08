---
name: labeling-changes
description: Conventional commit type keywords for PR titles and commit messages. Use when determining the change type for commits or PRs. Triggered by "what type", "label", "change type", "conventional commit", "t: label".
---

# Labeling Changes

PR titles and commit messages must include a conventional commit type keyword. This keyword drives automatic `t:` label assignment via CI (`.github/scripts/label-pr.py` reads `.github/label-pr.json`).

## Format

The type keyword appears after the Jira ticket prefix:

```
[PM-XXXXX] <type>: <imperative summary>
```

## Type Keywords and Selection Guidance

Read `${CLAUDE_PLUGIN_ROOT}/references/change-type-labels.md` for the full table of type keywords, their CI label mappings, and guidance for selecting a type (including ambiguous cases).

The CI labeling script matches `<type>:` or `<type>(` in the lowercased PR title, so the keyword must be followed by a colon or parenthesis. **If the type cannot be confidently determined, ask the user.**
