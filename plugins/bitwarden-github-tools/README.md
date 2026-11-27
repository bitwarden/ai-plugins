# bitwarden-github-tools

GitHub tools for Bitwarden — cross-repo code and feature discovery across the bitwarden organization, directly from Claude Code.

## Overview

Bitwarden's codebase spans many repositories (`clients`, `server`, `sdk-internal`, `passkey-rs`, mobile apps, and more). This plugin provides GitHub-focused skills, starting with cross-repo search that finds where code and features live across the entire organization.

## Skills

| Skill                       | Description                                                      |
| --------------------------- | ---------------------------------------------------------------- |
| `searching-bitwarden-repos` | Search across all bitwarden org repos by code, feature, or topic |

## Usage

Ask Claude Code to search the Bitwarden organization:

- "Where is passkey related code in Bitwarden?"
- "Which repo has the CipherService?"
- "Find where WebAuthn login is implemented"
- "What repos use bitwarden-fido?"

The skill uses `gh search code`, `gh search repos`, `gh repo view`, and `gh api` to scan the organization and presents results grouped by repository with file paths and direct GitHub URLs.

## Installation

```bash
/plugin install bitwarden-github-tools@bitwarden-marketplace
```

### Prerequisites

- **GitHub CLI (`gh`)** installed and authenticated
- Access to the `bitwarden` GitHub organization

## How It Works

1. Searches across all bitwarden org repos using GitHub code search
2. Groups results by repository
3. Fetches repo metadata (description, language, topics) for context
4. Presents a structured table with repos, paths, and summaries
5. Includes direct GitHub URLs for quick navigation

For well-known features (e.g., passkeys), the skill includes curated mappings that guide the search to the right repos first, then confirms each path with a live query before presenting it.
