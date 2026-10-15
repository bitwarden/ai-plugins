# Changelog

All notable changes to the Bitwarden Community Tools Plugin will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-15

### Added

- `reading-community-forum`: read-only, anonymous access to the public Bitwarden Community forum (community.bitwarden.com, Discourse) through the `bwcommunity.py` wrapper, a single standard-library Python 3.9+ script.
  - **Commands:** `search` (filters for category, tag, user, solved status, dates and title), `thread`, `post`, `latest`, `top`, `categories`, `tags` and `user`.
  - **Long threads:** use Discourse's "best of" selection. `thread --brief` keeps only the first post, the accepted answer, staff posts and the top 3 moderator posts.
  - **Output:** compact Markdown for LLMs, with canonical URLs to cite and `STAFF`, `MOD` and `ACCEPTED ANSWER` markers. Same-thread quotes are collapsed and system posts hidden; `--json` gives pruned JSON.
  - **Read-only contract:** sends GET requests only, needs no credentials, and is throttled to 1 request per second across processes. It retries with backoff that honours `Retry-After`, keeps a 1-hour cache with owner-only permissions, enforces `robots.txt` except for `/search.json`, and documents exit codes 0–4.
  - **Untrusted content:** the skill treats forum content as data that never authorizes an action.
  - **Tests and evals:** offline unit tests and a trigger eval.
