# Bitwarden Community Forum Tools Plugin

Reads the public Bitwarden Community forum ([community.bitwarden.com](https://community.bitwarden.com)) for product research through a read-only CLI wrapper.

## Overview

Product questions often start with what users are already saying: which feature requests have the most votes, whether a bug keeps coming back, what workaround people found, and what Bitwarden staff replied. WebSearch indexes forum threads poorly. This plugin gives Claude direct, read-only access to the forum's Discourse JSON API through the `bwcommunity.py` wrapper. The wrapper returns compact Markdown with citable URLs and keeps token use low.

## Skills

| Skill                     | What It Does                                                                                                                                            |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `reading-community-forum` | Searches the forum and reads threads, feature-request votes, staff and moderator replies, accepted answers, and user activity through `bwcommunity.py`. |

## Read-only contract

- **Anonymous GETs only:** the wrapper sends anonymous GET requests and never posts, replies, votes or logs in. Any write capability would ship as a separate script and skill, never as a new wrapper subcommand.
- **Credentials:** none are needed or sent. `BW_COMMUNITY_URL`, used for testing against another Discourse instance, must be an `https` origin.

## Being a good API client

- **Rate:** at most 1 request per second, shared across processes. 429 and 5xx responses are retried with exponential backoff, and `Retry-After` is honoured.
- **Cache:** responses are cached for 1 hour in `~/.cache/bwcommunity`. The directory is set to 0700 on every run and files are 0600. Pass `--no-cache` to bypass it.
- **`robots.txt`:** enforced for every path except `/search.json`. The site disallows `/search` for all agents. `search` is exempt by default because it is an on-demand lookup made for a user, not a crawl. Pass `--strict-robots` to refuse instead.

## Token budget

- **Measured:** `thread 158 --brief` reduces the 571-post auto-type feature request to about 700 tokens. A 15-hit search is about 1.7k tokens.
- **Long threads:** use Discourse's "best of" selection, and the first post and the accepted answer are always kept.
- **Quotes:** a quote of a post in the same thread collapses to one line.
- **Hidden noise:** system posts, link previews, avatars and the near-universal `server:default-cloud` tag are left out.

## Prerequisites

- **Python 3.9+.** There are no dependencies.

## Installation

```bash
/plugin install bitwarden-community-forum-tools@bitwarden-marketplace
```

## Usage

The skill activates on natural-language requests:

```
What are the most-voted feature requests on the community forum this year?
```

```
Is there a known workaround for autofill not working in Brave? What did staff say?
```

## Tests

```bash
python3 -m unittest discover plugins/bitwarden-community-forum-tools/skills/reading-community-forum/scripts/tests
```

The tests run offline and make no network calls.

## References

- [Bitwarden Community forum](https://community.bitwarden.com)
- [Discourse API](https://docs.discourse.org)
- [Claude Code Skills](https://code.claude.com/docs/en/skills)
