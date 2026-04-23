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

## Type Keywords

| Type           | Label               | Use for                                    |
| -------------- | ------------------- | ------------------------------------------ |
| `feat`         | `t:feature`         | New features or functionality              |
| `fix`          | `t:bug`             | Bug fixes                                  |
| `refactor`     | `t:tech-debt`       | Code restructuring without behavior change |
| `chore`        | `t:tech-debt`       | Maintenance, cleanup, minor tweaks         |
| `test`         | `t:tech-debt`       | Adding or updating tests                   |
| `perf`         | `t:tech-debt`       | Performance improvements                   |
| `docs`         | `t:docs`            | Documentation changes                      |
| `ci` / `build` | `t:ci`              | CI/CD and build system changes             |
| `deps`         | `t:deps`            | Dependency updates                         |
| `llm`          | `t:llm`             | LLM/Claude configuration changes           |
| `breaking`     | `t:breaking-change` | Breaking changes requiring migration       |
| `misc`         | `t:misc`            | Changes that do not fit other categories   |

## Selecting a Type

Infer the type from the task description and changes made. **If the type cannot be confidently determined, ask the user.**

The CI labeling script matches `<type>:` or `<type>(` in the lowercased PR title, so the keyword must be followed by a colon or parenthesis. CI also accepts additional aliases (e.g., `revert`, `bugfix`, `cleanup`). See `.github/label-pr.json` for the full mapping.

### Examples

Ambiguous cases where type selection is non-obvious:

- Refactor that incidentally fixes a bug → use the **primary intent**: `fix:` if the bug was the goal, `refactor:` if the restructuring was the goal
- Adding tests for existing untested code → `test:` (not `chore:`)
- Updating a dependency to fix a vulnerability → `deps:` (not `fix:`)
- Changing Claude/LLM configuration files → `llm:` (not `chore:`)
- Removing dead code → `refactor:` (not `chore:` — it changes the codebase structure)
