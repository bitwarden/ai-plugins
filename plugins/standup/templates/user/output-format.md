## Output format

Controls where the finished report is delivered and how it is laid out. Edit the
values freely; the choices below are editable defaults, not fixed options.

- Destination: [YOUR-PREFERENCE] — choose one:
  - `local markdown file` — write the report to a markdown file at a path you specify. If you give no path, the report is written to a timestamped file under `~/.claude/standup/reports/`.
  - `stdout to chat` — print the report straight to the conversation, no persistence.
- Section labels: `Last week` / `This week` / `Blockers` (rename these if your team uses different headings; keep the three-section shape so the skill can render it).
- Markdown-link rendering: `on` — render every Jira key as `[PM-#####](url)` and every PR as `[owner/repo#N](url)`. Set to `off` to emit bare keys and PR numbers instead.
- RAG status legend (leading line of the report is one of these emoji plus a one-sentence summary):
  - `:large_green_circle:` — on track.
  - `:large_yellow_circle:` — some risk / needs attention.
  - `:red_circle:` — blocked / off track.
