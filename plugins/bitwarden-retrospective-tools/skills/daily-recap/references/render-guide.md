# Render Guide

The template at `assets/template.html` uses `{{...}}` placeholders. Most are self-explanatory; this guide covers the HTML shapes to inject for `{{PROJECT_SECTIONS}}`, `{{TIMELINE_EVENTS}}`, and `{{TODAY_BANNER}}`. The CSS is tuned to the Bitwarden brand palette, so fill placeholders rather than regenerating styles.

## Escape untrusted text

PR titles, review and comment bodies, commit messages, branch names, repository names, and session prompts are free text, and on any shared repository other people author much of it. Before inserting any of it into the page, HTML-escape these five characters:

| Character | Replacement |
| --------- | ----------- |
| `&`       | `&amp;`     |
| `<`       | `&lt;`      |
| `>`       | `&gt;`      |
| `"`       | `&quot;`    |
| `'`       | `&#39;`     |

Escape `&` first so the other replacements are not double-escaped. For example, a PR titled `Fix <input> focus & "Save" button` renders as `Fix &lt;input&gt; focus &amp; &quot;Save&quot; button`. Markup the recap adds itself (`<code>`, `<strong>`, `<a class="pr-ref">`) goes around escaped text, never inside it. Only use `https://github.com/...` URLs in `href` attributes.

The template's Content-Security-Policy is a second line of defense: it lets only the page's own script run and blocks outbound requests other than the brand fonts. Leave the `<script>` block and the policy untouched. The policy pins the script by hash, so an edited script stops running and the filters and Copy button break.

## Placeholders

Self-explanatory: `{{DATE}}`, `{{SUBTITLE}}`, `{{STAT_*}}`, `{{STANDUP_SHIPPED}}`, `{{STANDUP_NEXT}}`, `{{THEME_PARAGRAPHS}}`, `{{OPEN_THREADS}}`, `{{GENERATED_AT}}`. `{{DATE}}` appears several times; replace every occurrence.

`{{PROJECT_CHIPS}}`: one per project:

```html
<button class="chip" data-filter="{slug}">
  {emoji} {label} <span class="count" id="ct-{slug}">0</span>
</button>
```

The script fills in the counts. `{slug}` must match the `data-project` value used on that project's section and timeline events.

`{{TODAY_BANNER}}`: an empty string when nothing happened after today's cutoff hour. Otherwise:

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

Status semantics: `completed` means the work landed (PR merged, decision made, fix shipped). `open` means work in progress, not pushed or merged, or pending review. `deferred` means intentionally postponed.

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

Events after midnight but before the cutoff hour still belong to the recap's workday. Insert this divider in the timeline before them:

```html
<div
  style="margin: 28px 0 18px; padding: 8px 0; border-top: 1px dashed var(--border); color: var(--text-muted); font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase;"
>
  🌙 After Midnight · Late-night tail (still this workday)
</div>
```
