# Bitwarden Mailcatcher Tools Plugin

Reads emails from the local Bitwarden Mailcatcher inbox.

## Overview

Bitwarden's local dev environment delivers every outgoing email to Mailcatcher. This plugin finds a message by recipient and subject through Mailcatcher's REST API and returns the action link from its body, so a local testing or debugging session can follow email-driven flows such as account verification, Admin Portal magic-link login, trial activation, organization invites, and emergency access without opening the Mailcatcher UI.

## Skills

| Skill                     | What It Does                                                                                                                                                                                                                                            |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `reading-mailcatcher-api` | Reads a Bitwarden email from Mailcatcher by recipient and subject and returns its verification link, magic link, or other action link. Extracted URLs are limited to local dev hosts. Also prints the dev Admin Portal address for the magic-link flow. |

## Prerequisites

- **Python 3** on `PATH`. The skill's scripts are invoked directly and rely on their shebang.
- **Mailcatcher running** at `http://localhost:1080`: the `mail` service in `bitwarden/server`'s `dev/docker-compose.yml`, started with `docker compose --profile mail up -d mail` from `server/dev/`.
- **Optional:** if your environment's emails link to a local hostname other than `localhost`, `127.0.0.1`, `::1`, or `bitwarden.test`, add it to the comma-separated `MAILCATCHER_ALLOWED_HOSTS` environment variable in your shell. It extends the allowlist and never replaces it.

## Installation

```bash
/plugin install bitwarden-mailcatcher-tools@bitwarden-marketplace
```

## Usage

The skill activates on natural-language requests:

```
Grab the verification link from the email Mailcatcher just received for qa+trial@example.com.
```

```
Log me into the Admin Portal with the magic link from Mailcatcher.
```

## References

- [Mailcatcher](https://mailcatcher.me/)
- [Claude Code Skills](https://code.claude.com/docs/en/skills)
