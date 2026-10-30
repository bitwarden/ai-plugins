# Render Guide

The template at `assets/template.html` uses `{{...}}` placeholders. Most are self-explanatory; this guide covers the HTML shapes to inject for `{{PROJECT_SECTIONS}}`, `{{TIMELINE_EVENTS}}`, `{{TODAY_BANNER}}`, `{{STAT_JIRA_ISSUES}}`, `{{STAT_CONFLUENCE_PAGES}}`, and `{{OPEN_THREADS}}`. The CSS is tuned to the Bitwarden brand palette, so fill placeholders rather than regenerating styles.

## Escape untrusted text

PR titles, review and comment bodies, commit messages, branch names, repository names, session prompts, Jira issue summaries and statuses, transition `from`/`to` names, and Confluence page titles and space keys are free text, and on any shared repository other people author much of it. Before inserting any of it into the page, HTML-escape these five characters:

| Character | Replacement |
| --------- | ----------- |
| `&`       | `&amp;`     |
| `<`       | `&lt;`      |
| `>`       | `&gt;`      |
| `"`       | `&quot;`    |
| `'`       | `&#39;`     |

Escape `&` first so the other replacements are not double-escaped. For example, a PR titled `Fix <input> focus & "Save" button` renders as `Fix &lt;input&gt; focus &amp; &quot;Save&quot; button`. Markup the recap adds itself (`<code>`, `<strong>`, `<a class="pr-ref">`) goes around escaped text, never inside it. Only use `href` values that are `https://github.com/...` URLs, or a Jira/Confluence `url` that begins with that source's `site_url` over `https`. A Jira issue with a `url` of `null` renders its key as plain text, not a link.

The template's Content-Security-Policy is a second line of defense: it lets only the page's own script run and blocks outbound requests other than the brand fonts. Leave the `<script>` block and the policy untouched. The policy pins the script by hash, so an edited script stops running and the filters and Copy button break.

## Placeholders

Self-explanatory: `{{DATE}}`, `{{SUBTITLE}}`, `{{STAT_REPOS}}`, `{{STAT_SESSIONS}}`, `{{STAT_PRS_OPENED}}`, `{{STAT_PRS_APPROVED}}`, `{{STAT_GH_EVENTS}}`, `{{STANDUP_SHIPPED}}`, `{{STANDUP_NEXT}}`, `{{THEME_PARAGRAPHS}}`, `{{GENERATED_AT}}`. `{{DATE}}` appears several times; replace every occurrence.

`{{STAT_JIRA_ISSUES}}` is the length of `jira.issues`; `{{STAT_CONFLUENCE_PAGES}}` is the length of `confluence.pages`. Each is `—` when its source is `null` (not collected), distinct from `0` (collected, nothing found). For a multi-day range, sum each day's count, deduping by issue key for Jira and by page `url` for Confluence.

`{{OPEN_THREADS}}` is a plain-text, HTML-escaped summary of work still open at the end of the window: PRs from `search.json`/`events.json` that are still open (including drafts) and awaiting review or merge, branches from `CreateEvent`/`PushEvent` that have not been merged or deleted, streams whose status is `open` or `deferred`, and Jira issues from `jira.issues` whose `status_category` is not `Done`. Render each as a short phrase — pairing PR numbers with titles per the escaping rules above, quoting branch names in backticks, and pairing a Jira key with its summary — and join them with `; `. Dedupe PRs by URL the same way streams do. Call out any Jira issue with `returned: true` as notable within its phrase (for example "sent back"), since it was moved backward in status within the window. When `jira` is `null`, omit the Jira issues entirely — never leave the whole placeholder empty solely because Jira is unavailable; fill it from the GitHub/session content alone.

`{{PROJECT_CHIPS}}`: one per project:

```html
<button class="chip" data-filter="{slug}">
  {emoji} {label} <span class="count" id="ct-{slug}">0</span>
</button>
```

The script fills in the counts. `{slug}` must match the `data-project` value used on that project's section and timeline events.

`{{TODAY_BANNER}}`: an empty string when step 1 did not gather `today.json` or it holds no events. Otherwise, built from those events:

```html
<div class="today-banner">
  <div class="today-banner-content">
    <div class="today-banner-title">
      Since the recap · Fresh today · {today date}
    </div>
    <ul>
      <li>
        <span class="ts">{HH:MM}</span><span class="new-tag">{Tag}</span>{event}
      </li>
    </ul>
  </div>
</div>
```

Tags: `New Repo`, `Sweep`, `Merged`, `Approval`.

## Stream card

```html
<div class="stream" data-status="{completed|open|deferred}">
  <div class="stream-header">
    <div class="stream-title">
      <span class="stream-toggle">▾</span><span>Stream title</span>
    </div>
    <span class="badge badge-{completed|open|deferred}">● Status</span>
  </div>
  <div class="stream-body">
    <ul>
      <li>
        Bullet with <code>file paths</code>,
        <a class="pr-ref" href="https://github.com/{owner}/{repo}/pull/1234"
          >#1234</a
        >
        PR title
      </li>
    </ul>
  </div>
</div>
```

Other bullet shapes, same `<li>` wrapper, escaped text per the rules above:

```html
<li>
  <a class="pr-ref" href="{url}">{KEY}</a> {summary} · {status}
  <!-- involvement and transitions, summarized in plain text -->
  (transitioned, In Review → In Progress)
</li>
```

```html
<li>
  <a class="pr-ref" href="{url}">{title}</a> · {space_key} · {created|edited} ·
  {N} versions
</li>
```

A Jira issue with a `null` `url` renders `{KEY}` as plain text instead of the link. Status semantics: `completed` means the work landed (PR merged, decision made, fix shipped). `open` means work in progress, not pushed or merged, or pending review. `deferred` means intentionally postponed. A Jira issue counts as `completed` when its `status_category` is `Done`, otherwise `open`.

Each Jira issue carries a `returned` boolean: `true` when one of its `transitions` in the window moved it backward (for example In Review → In Progress), `false` otherwise. When `true`, note it in the issue's bullet in plain text (for example "(transitioned, In Review → In Progress, sent back)"), the same way involvement and transitions are already summarized there.

Search PRs merge into the existing PR bullets, deduped by PR URL, with no separate section or stat; a PR whose title or branch carries a matching Jira key shares a stream with that issue.

## Project section

```html
<section class="project" data-project="{slug}">
  <div class="project-header">
    <div class="project-icon">{emoji}</div>
    <div class="project-title">{org/repo or theme}</div>
    <div class="project-meta">{N sessions · M streams}</div>
  </div>
  <!-- one or more .stream blocks -->
</section>
```

## Timeline event

```html
<div
  class="tl-event evt-{merged|opened|push|review|comment|create}"
  data-project="{slug}"
>
  <div>
    <span class="tl-time">{HH:MM}</span
    ><span class="tl-type t-{kind}">{Label}</span>
  </div>
  <div class="tl-event-body"><span class="repo">{repo}</span> · {body}</div>
  <!-- optional inline quote (review comment body) -->
  <div class="tl-quote">{body excerpt}</div>
  <!-- optional cross-reference back to a session stream -->
  <div class="tl-link-session">Session: {stream title}</div>
</div>
```

Show times in the user's local timezone, matching the window's `timezone` label. `data-project` lets the project chips filter the timeline; use the slug of the project the event belongs to.

Each Jira transition is one timeline event at its `at` timestamp, body `{KEY} {from} → {to}` (escaped), label `Jira`. Use class `evt-merged`/`t-merged` when `to` is a Done-category status, that is, the issue's current `status_category` is `Done` and `to` equals the issue's current `status`; otherwise use `evt-review`/`t-review`. No new CSS classes. Confluence pages carry no per-version timestamps, so they appear only in streams, never in the timeline.

Events after midnight but before the cutoff hour still belong to the recap's workday. Insert this divider in the timeline before them:

```html
<div
  style="margin: 28px 0 18px; padding: 8px 0; border-top: 1px dashed var(--border); color: var(--text-muted); font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase;"
>
  🌙 After Midnight · Late-night tail (still this workday)
</div>
```
