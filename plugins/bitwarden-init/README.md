# Bitwarden Init Plugin

Generates CLAUDE.md files at three scopes — repository, workspace, and user — using Bitwarden's templates.

## What It Does

Claude Code reads `CLAUDE.md` files by walking up the directory tree from the current working directory and concatenating every file it finds. That makes three scopes useful:

| Scope          | Path                                 | Applies to                                  |
| -------------- | ------------------------------------ | ------------------------------------------- |
| **User**       | `~/.claude/CLAUDE.md`                | Every project, every conversation           |
| **Workspace**  | `<bw-source-root>/.claude/CLAUDE.md` | Every Bitwarden repo cloned under that root |
| **Repository** | `<repo>/CLAUDE.md`                   | One specific repo                           |

This plugin has commands for all three.

## Installation

```bash
/plugin install bitwarden-init@bitwarden-marketplace
```

Restart Claude Code after installation.

## Commands

### Repository scope

#### `/bitwarden-init:init`

Generates a new repository-level `CLAUDE.md`. Runs both phases automatically:

1. Anthropic's `/init` analyzes the codebase.
2. `/enhance` restructures and extends the output using the 11-section project template (see below).

#### `/bitwarden-init:enhance`

Enhances an existing repository-level `CLAUDE.md`. Reads the current file, performs supplementary codebase research, and reorganizes content into the 11 project sections.

### User scope

#### `/bitwarden-init:init-user`

Walks you through a Q&A to assemble `~/.claude/CLAUDE.md` from opt-in behavioral modules (intellectual honesty, simplicity, surgical changes, code-review mutation lockdown, …). The modules are a starting point assembled from one engineer's preferences — pick what fits you and edit freely.

#### `/bitwarden-init:enhance-user`

Detects which behavioral modules are already present in `~/.claude/CLAUDE.md` and offers to append any that are missing.

### Workspace scope

#### `/bitwarden-init:init-workspace`

Walks you through a Q&A to assemble `<workspace-root>/.claude/CLAUDE.md` for the folder where you keep all your locally-cloned Bitwarden repos. Auto-detects the workspace root by walking up from `cwd` looking for an ancestor with two or more sibling git repositories. Always asks for confirmation before writing. Modules include the zero-knowledge invariant, security principles P01–P06, core vocabulary, and operating defaults like worktrees and plan mode.

#### `/bitwarden-init:enhance-workspace`

Detects which Bitwarden domain modules are already present in the workspace-level file and offers to append any that are missing.

### Safety guardrails for user / workspace scopes

Both new init and enhance flows for the user and workspace scopes:

- Show a unified diff preview before any write.
- Require an explicit `Apply` confirmation.
- Create a timestamped `*.bak-<ISO-timestamp>` copy of the existing file before overwriting.
- Surface the backup path in the success message.

## Usage

Typical first-time setup, in order:

```text
# 1. Set up your user-level CLAUDE.md (applies to every project)
/bitwarden-init:init-user

# 2. From any directory under the folder where you keep your cloned Bitwarden repos
/bitwarden-init:init-workspace

# 3. In each repo, set up the repo-level CLAUDE.md
/bitwarden-init:init
```

Later, to refresh a CLAUDE.md after the plugin adds new modules:

```text
/bitwarden-init:enhance-user        # append any missing user-scope modules
/bitwarden-init:enhance-workspace   # append any missing workspace-scope modules
/bitwarden-init:enhance             # refresh a repo CLAUDE.md against the 11-section template
```

All four user/workspace commands open an interactive Q&A: pick the modules you want, review a unified diff against the existing file (if any), then confirm `Apply`. A timestamped `*.bak-<...>` is written before any overwrite.

## Repository Template Structure

The generated CLAUDE.md includes these sections:

- **Overview** - Project purpose, key concepts
- **Architecture & Patterns** - System diagrams, code organization, implementation patterns
- **Development Guide** - Step-by-step instructions with code templates
- **Data Models** - Types, validation schemas, domain entities
- **Security & Configuration** - Security rules, authentication, environment variables
- **Testing** - Test structure, writing tests, running tests
- **Code Style & Standards** - Formatting, naming conventions, pre-commit hooks
- **Anti-Patterns** - DO/DON'T lists
- **Deployment** - Build and deployment instructions
- **Troubleshooting** - Common issues and solutions
- **References** - Documentation links

## Requirements

- `claude` CLI in PATH
- Write permissions for CLAUDE.md

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

See [LICENSE.txt](../../LICENSE.txt).
