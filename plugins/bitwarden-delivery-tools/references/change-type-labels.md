# Change Type Labels

Conventional commit type keywords used in commit messages and PR titles. Each keyword drives automatic `t:` label assignment via CI (`.github/scripts/label-pr.py` reads `.github/label-pr.json`). CI matches `<type>:` or `<type>(` in the lowercased title.

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

CI also accepts additional aliases (e.g., `revert`, `bugfix`, `cleanup`). See `.github/label-pr.json` for the full mapping.

## Selecting a Type

Infer the type from the task description and changes made. **If the type cannot be confidently determined, ask the user.**

### Ambiguous Cases

- Refactor that incidentally fixes a bug → use the **primary intent**: `fix:` if the bug was the goal, `refactor:` if the restructuring was the goal
- Adding tests for existing untested code → `test:` (not `chore:`)
- Updating a dependency to fix a vulnerability → `deps:` (not `fix:`)
- Changing Claude/LLM configuration files → `llm:` (not `chore:`)
- Removing dead code → `refactor:` (not `chore:` — it changes the codebase structure)
