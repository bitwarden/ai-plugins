# bitwarden-repo-search

Search across all repositories in the Bitwarden GitHub organization to find where specific code, features, or topics live — directly from Claude Code.

## Overview

Bitwarden's codebase spans many repositories (`clients`, `server`, `sdk-internal`, `passkey-rs`, mobile apps, and more). This plugin eliminates the need to manually browse GitHub by providing a single skill that searches across the entire organization and returns structured, grouped results.

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

The skill uses `gh search code`, `gh repo list`, and `gh api` to scan the organization and presents results grouped by repository with file paths and direct GitHub URLs.

## Prerequisites

- **GitHub CLI (`gh`)** installed and authenticated
- Access to the `bitwarden` GitHub organization

## How It Works

1. Searches across all bitwarden org repos using GitHub code search
2. Groups results by repository
3. Fetches repo metadata (description, language, topics) for context
4. Presents a structured table with repos, paths, and summaries
5. Includes direct GitHub URLs for quick navigation

For well-known features (e.g., passkeys), the skill includes curated mappings that provide instant answers without needing to hit the GitHub API.
