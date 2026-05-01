# Render Guide — daily-recap template

The template at `assets/template.html` uses `{{...}}` placeholders. Most are self-explanatory; this guide covers the HTML shapes you need to inject for `{{PROJECT_SECTIONS}}`, `{{TIMELINE_EVENTS}}`, and `{{TODAY_BANNER}}`. CSS is already tuned to the Bitwarden brand palette — don't regenerate.

## Placeholders

Self-explanatory: `{{DATE}}`, `{{SUBTITLE}}`, `{{STAT_*}}`, `{{STANDUP_SHIPPED}}`, `{{STANDUP_NEXT}}`, `{{THEME_PARAGRAPHS}}`, `{{OPEN_THREADS}}`, `{{GENERATED_AT}}`. The interesting ones below.

`{{PROJECT_CHIPS}}` — one per project: `<button class="chip" data-filter="{slug}">{emoji} {label} <span class="count" id="ct-{slug}">0</span></button>`

`{{TODAY_BANNER}}` — empty string if no events past today's cutoff hour (local time). Otherwise:

```html
<div class="today-banner">
  <div class="today-banner-content">
    <div class="today-banner-title">
      Since the recap · Fresh today · {today date}
    </div>
    <ul>
      <li>
        <span class="ts">{HH:MMZ}</span
        ><span class="new-tag">{Tag}</span>{event}
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
        <a class="pr-ref" href="...">#1234</a>
      </li>
    </ul>
  </div>
</div>
```

Status semantics: `completed` = work landed (PR merged, decision made, fix shipped). `open` = WIP, not pushed/merged, pending review. `deferred` = intentionally postponed.

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
<div class="tl-event evt-{merged|opened|push|review|comment|create}">
  <div>
    <span class="tl-time">{HH:MM:SSZ}</span
    ><span class="tl-type t-{kind}">{Label}</span>
  </div>
  <div class="tl-event-body"><span class="repo">{repo}</span> · {body}</div>
  <!-- optional inline quote (review comment body) -->
  <div class="tl-quote">{body excerpt}</div>
  <!-- optional cross-reference back to a session stream -->
  <div class="tl-link-session">Session: {stream title}</div>
</div>
```

For "today" events that fall before today's cutoff hour (local time) — those belong to yesterday's workday — insert this divider in the timeline before them:

```html
<div
  style="margin: 28px 0 18px; padding: 8px 0; border-top: 1px dashed var(--border);
            color: var(--text-muted); font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase;"
>
  🌙 After Midnight · Late-Night Tail (still yesterday's workday)
</div>
```
