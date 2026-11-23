# Weekly Recap Skill

A thin wrapper around daily-recap. It builds the same recap page over a Monday-to-Friday workweek instead of a single day.

## What It Inherits

Everything: scripts, template, and references. It calls daily-recap's files by their absolute plugin path, not a relative `../daily-recap/` path, since Claude Code installs the whole plugin tree and `SKILL.md` is read as plain text with no variable substitution:

- `${CLAUDE_PLUGIN_ROOT}/skills/daily-recap/scripts/`
- `${CLAUDE_PLUGIN_ROOT}/skills/daily-recap/assets/`
- `${CLAUDE_PLUGIN_ROOT}/skills/daily-recap/references/`

See [daily-recap's README](../daily-recap/README.md) for configuration, requirements, and privacy details — they all apply here unchanged.

## What Differs

- **Window**: Monday through Friday. "Last week" or no time given means the most recently completed workweek. "This week" means Monday through today.
- **Output file**: `recap-week-YYYY-MM-DD.html`, named by that week's Monday, instead of daily-recap's `recap-YYYY-MM-DD.html`.
