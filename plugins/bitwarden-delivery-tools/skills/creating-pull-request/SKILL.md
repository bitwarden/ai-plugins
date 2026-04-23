---
name: creating-pull-request
description: Pull request creation workflow for Bitwarden repositories. Use when creating PRs, writing PR descriptions, or preparing branches for review. Triggered by "create PR", "pull request", "open PR", "gh pr create", "PR description".
---

# Create Pull Request

## PR Title Format

```
[PM-XXXXX] <type>: <short imperative summary>
```

**Type keywords** (triggers automatic `t:` label via CI):

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

**Examples:**

- `[PM-12345] feat: Add autofill support for passkeys`
- `[PM-12345] fix: Resolve crash during vault sync`
- `[PM-12345] refactor: Simplify authentication flow`

---

## PR Body

**Always follow the repo's PR template at `.github/PULL_REQUEST_TEMPLATE.md`.** Read it and fill in each section. If no template exists, use this fallback:

```markdown
## 🎟️ Tracking

<!-- Paste the link to the Jira or GitHub issue or otherwise describe / point to where this change is coming from. -->

## 📔 Objective

<!-- Describe what the purpose of this PR is, for example what bug you're fixing or new feature you're adding. -->

## 📸 Screenshots

<!-- Required for any UI changes; delete if not applicable. Use fixed width images for better display. -->
```

Delete the Screenshots section entirely if there are no UI changes.

---

## Creating the PR

Before creating, run `perform-preflight` if not already done.

```bash
git push -u origin <branch-name>
gh pr create --draft --title "[PM-XXXXX] feat: Short summary" --body "<fill in from PR template>"
```

**Default to draft PRs.** Only create a non-draft PR if the user explicitly requests it.

---

## AI Review Label

Before running `gh pr create`, **always** use the `AskUserQuestion` tool to ask whether to add an AI review label:

- **Question**: "Would you like to add an AI review label to this PR?"
- **Options**: `ai-review-vnext`, `ai-review`, `No label`

If the user selects a label, include it via the `--label` flag:

```bash
gh pr create --draft --label "ai-review-vnext" --title "..." --body "..."
```
