# bitwarden-devops-engineer

BRE tooling for GitHub Actions workflow compliance and security auditing.

## Installation

```bash
claude plugin install bitwarden/ai-plugins#bitwarden-devops-engineer
```

## Commands

### `/bre-workflow-fix [file-or-dir] | --repos <repo1,repo2,...>`

Fix GitHub Actions workflow linter findings in one or more repos.

Runs `bwwl lint` against the target workflow files, applies mechanical fixes automatically (capitalization, permissions, runner pins, action hash pins, output naming), and asks for direction on judgment calls (unapproved actions, complex actionlint findings). Creates a draft PR per repo when done.

**Examples:**

```
/bre-workflow-fix
/bre-workflow-fix .github/workflows/build.yml
/bre-workflow-fix --repos server,clients,android,ios
```

### `/bre-action-audit [action-name] [--mode incident|audit] [--replace <new-action>]`

Audit and remediate GitHub Actions action usage across the Bitwarden org.

Searches the org via `gh search code`, reports all usages with their pin status, resolves a safe hash with a verification link, and creates draft PRs per repo after confirmation.

**Modes:**

- `incident` (default when action name is provided): Targeted search for a specific action.
- `audit` (default when no action name): Sweep all workflow files for unpinned action references.

**Examples:**

```
/bre-action-audit tj-actions/changed-files
/bre-action-audit tj-actions/changed-files --replace actions/changed-files
/bre-action-audit --mode audit
```

## Skills

### `bitwarden-workflow-linter-rules`

Reference knowledge for all 10 Bitwarden workflow linter rules, their triggers, and correct fixes. Used internally by `/bre-workflow-fix` but also available to any agent that needs to reason about workflow compliance.
