---
name: compiling-test-report
description: Compile an HTML test report from Playwright agent results for Bitwarden web tests. Use after executing web tests to produce a structured report with per-test-case pass/fail status, screenshot links, and issue summaries. Uses templates/report-template.html. Returns the HTML document as text — the caller persists it.
---
Given the Playwright agent results and services-tested list, produce the complete HTML report document as your output. You do not write any files and you do not name the file — the caller persists the content you return.

The test results, screenshot paths, and pass/fail data all come from the `executing-web-tests` skill output — use them directly.

## HTML Report

Use the structure in `${CLAUDE_SKILL_DIR}/templates/report-template.html`. Fill in:

- **Header**: date, plan file path, services tested (with ports), base URL
- **Summary table**: total / passed / failed / errors counts
- **Test Results section**: one subsection per test case. Parse each `--- TEST CASE N: <name> ---` block (see "Rendering steps and screenshots" below) and render: status, URL (derived from the first navigate step), **Setup Steps** and **Test Steps** as two separate numbered lists, each step's screenshot inline, notes, and a suggested fix for any failure
- **Issues Summary**: bullet list of all failures and errors
- **Recommendations**: follow-up actions (Fix, Investigate, Re-test)

Screenshot paths in the report use relative paths from the report file location — just `screenshots/filename.png`, not the full absolute path.

Each screenshot is rendered as a linked thumbnail, placed inline inside its step's `<li>` (see "Rendering steps and screenshots" below):

```html
<a class="screenshot-link" href="screenshots/filename.png" target="_blank">
  <img src="screenshots/filename.png" alt="description">
</a>
```

The `.screenshot-link img` CSS rule in the template sets `width: 50%` — do not add inline `style` attributes to the `<img>` tags. Thumbnails link to the full-size image in a new tab.

## Rendering steps and screenshots

Each test case block has an optional `Setup Steps:` label and a `Test Steps:` label, each followed by lines like `Step N: <text> — <outcome>`. Render them as two separate numbered lists, each under its own header:

```html
<p><strong>Setup Steps</strong>:</p>
<ol>
  <li>Navigate to … — PASS</li>
</ol>
<p><strong>Test Steps</strong>:</p>
<ol>
  <li>Click Tools dropdown — PASS</li>
</ol>
```

- Omit the Setup Steps header and its list entirely when the block has no `Setup Steps:` section.
- An indented `  Screenshot: <filename>` line belongs to the step on the line directly above it. Render the thumbnail **inside that step's `<li>`**, after the step text:

```html
<li>Click Tools dropdown — PASS
  <a class="screenshot-link" href="screenshots/test-case-1-step-3-….png" target="_blank">
    <img src="screenshots/test-case-1-step-3-….png" alt="test-case-1-step-3">
  </a>
</li>
```

- The URL shown in the test case header comes from the first step whose text begins `Navigate to`.
- Do not emit a separate Screenshots section.
- A step line beginning with `[HUMAN]` renders as `<li class="human-step">…</li>`.

## Adaptive status rendering

When a test case has `PASS (adaptive)` status:

- Render its status line as `⚠️ PASS (adaptive)` — use the amber warning symbol, not the green ✅
- Do NOT include it in the Issues Summary section (it is a pass, not a failure)
- In the Recommendations section, add a bullet for each adaptive test case:
  `Update test plan: TC<N> asserted <what was specified> — actual rendering is <what was found>. Update the assertion in the test plan to match.`

When there are no adaptive test cases, omit any mention of them from the Recommendations section.

## Output

Return a single fenced ```html``` block containing the full HTML document (populated from `${CLAUDE_SKILL_DIR}/templates/report-template.html`). No other text — the entire response is the fenced block.
