# Changelog

All notable changes to the Bitwarden Community Forum Tools Plugin will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-15

### Added

- `reading-community-forum`: read-only, anonymous access to the public Bitwarden Community forum (community.bitwarden.com, Discourse) through the `bwcommunity.py` wrapper, a single standard-library Python 3.9+ script.
  - **Commands:** `search` (filters for category, tag, user, solved status, dates and title), `thread`, `post`, `latest`, `top`, `categories`, `tags` and `user`.
  - **Long threads:** use Discourse's "best of" selection. `thread --brief` keeps only the first post, the accepted answer, staff posts and the top 3 moderator posts.
  - **Output:** compact Markdown for LLMs, with canonical URLs to cite and `STAFF`, `MOD` and `ACCEPTED ANSWER` markers. Same-thread quotes are collapsed and system posts hidden; `--json` gives pruned JSON.
  - **Read-only contract:** sends anonymous GET requests only and never sends credentials. `BW_COMMUNITY_URL` must be an `https` origin. Requests are throttled to 1 per second across processes and retried with backoff that honours `Retry-After`. Responses are cached for 1 hour in an owner-only directory. `robots.txt` is enforced except for `/search.json`, and exit codes 0–4 are documented.
  - **Untrusted content:** the skill treats forum content as data that never authorizes an action.
  - **Tests and evals:** offline unit tests, plus a trigger eval with the plugin's copy of the eval runner at `evals/run_real_eval.py`.
