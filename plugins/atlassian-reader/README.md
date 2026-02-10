# Atlassian Reader Plugin

Read-only access to Jira and Confluence from Atlassian Cloud. Mention a Jira ticket, ask about a sprint, or reference a Confluence page — the skill fetches and summarizes the data. No scripts, no MCP servers, just curl templates in a single SKILL.md.

## Prerequisites

### Environment Variables

| Variable                               | Purpose                                                           |
| -------------------------------------- | ----------------------------------------------------------------- |
| `ATLASSIAN_CLOUD_ID`                   | Cloud ID from `https://bitwarden.atlassian.net/_edge/tenant_info` |
| `ATLASSIAN_EMAIL`                      | Atlassian account email                                           |
| `ATLASSIAN_JIRA_READ_ONLY_TOKEN`       | Scoped Jira view-only API token                                   |
| `ATLASSIAN_CONFLUENCE_READ_ONLY_TOKEN` | Scoped Confluence view-only API token                             |

Two separate tokens are required because Atlassian scoped tokens are per-product. Create them at [Atlassian API tokens](https://id.atlassian.com/manage-profile/security/api-tokens) with **view-only** scope.

### Dependencies

- `curl`
- `jq` (`brew install jq` or `apt-get install jq`)

## Installation

```bash
/plugin marketplace add bitwarden/ai-marketplace

/plugin install atlassian-reader@bitwarden-marketplace
```

## Usage

```
Read PROJ-123
What's in the current sprint for PROJ?
Search Confluence for "API rate limiting" in the Engineering space
```

## Security

- **Scoped read-only tokens**: View-only permissions enforced server-side by Atlassian's API gateway. Tokens cannot modify data.
- **Per-product isolation**: Separate Jira and Confluence tokens. A compromised token for one product cannot access the other.
- **No stored credentials**: Tokens read from environment variables at runtime.
- **Restricted tool access**: Only `curl` commands are permitted.
