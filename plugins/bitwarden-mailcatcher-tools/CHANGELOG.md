# Changelog

All notable changes to the Bitwarden Mailcatcher Tools Plugin will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-07

### Added

- `reading-mailcatcher-api`, reading Bitwarden emails through the Mailcatcher REST API for verification links, magic links, and other action links. Its `read_mailcatcher.py` script pins Mailcatcher to `http://localhost:1080`, never follows redirects, and returns only URLs on a local dev host allowlist that `MAILCATCHER_ALLOWED_HOSTS` can extend. A second script, `get_admin_email.py`, prints the dev admin address from `server/dev/secrets.json` and nothing else from that file. Its `Read` grant covers only the skill's own `references/`, so a session that invokes it gains no wider file access. Includes a trigger eval recorded as an on-demand prose reading, and a copy of the trigger-eval runner at `evals/run_real_eval.py`.
