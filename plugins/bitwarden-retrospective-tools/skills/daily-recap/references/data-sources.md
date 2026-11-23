# Data Sources

Field schema for `gather-atlassian.sh`'s output, moved out of `SKILL.md` step 1 to keep that file's word count in check as more sources get added (see `render-guide.md` for the same split applied to rendering).

`gather-atlassian.sh [YYYY-MM-DD]` collects Jira and Confluence activity for one workday only, so a range runs it once per day, like `gather-gh-events.sh`. It emits `{"jira": ..., "confluence": ...}`.

`jira` holds `account_id`, `site_url`, `window`, `complete`, and `issues` (`key`, `summary`, `status`, `status_category`, `url`, `involvement`, `transitions` with `from`/`to`/`at`, `comment_count`, `returned`). `returned` is `true` when one of the issue's `transitions` in the window moved it backward in status (for example In Review → In Progress), `false` otherwise.

`confluence` holds `account_id`, `site_url`, `window`, `complete`, and `pages` (`title`, `space_key`, `space_id`, `created`, `version_count`, `url`).

Each service's `complete` is `false`, same as `gather-gh-search.sh`'s `search_complete`, when that service's search hit its page safety cap before exhausting all pages; when either is `false`, say in the recap that some Jira issues or Confluence pages may be missing.

Credentials come from `ATLASSIAN_CLOUD_ID`, `ATLASSIAN_EMAIL`, `ATLASSIAN_JIRA_READ_ONLY_TOKEN`, and `ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN` (the same variables bitwarden-atlassian-tools uses).
