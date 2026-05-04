# Storybook Customization

The bundled template ships Bitwarden-branded with a small set of reasonable defaults. Customize via the config or by editing the template.

## Brand Override

The template's color palette lives in `assets/template/assets/styles.css` as CSS custom properties scoped to `:root` and `[data-theme="dark"]`. If you need a non-Bitwarden palette:

1. Don't edit `styles.css` in the bundled template (changes carry to every storybook generated thereafter).
2. Either:
   - Run `scaffold.py` with the default output, then post-edit the generated `assets/styles.css`. Quickest path; not reproducible.
   - Or maintain a fork of the skill's template under your own plugin. Add `bw-shield.svg` replacement, palette overrides, and font swaps there. Reproducible.

The header lockup uses an inline SVG defined in `index.html.tmpl`. Swap the `path d="..."` values to drop in a different mark. Keep the `viewBox="0 0 24 28"` — `styles.css` sizes against it.

## Language Imports for Code Highlighting

The bundled `index.html.tmpl` loads Prism components for:

- `prism-core` (always required)
- `prism-clike` (C-style fallback used by `detectLanguage` for unknown extensions)
- `prism-swift`
- `prism-markup` (HTML / XML / plist)
- `prism-json`

If your stack uses a language Prism does not yet load (TypeScript, Kotlin, Rust, etc.):

1. Add a `<script>` for `prism-<lang>.min.js` in `index.html.tmpl` next to the others.
2. Extend `detectLanguage()` in `app.js.tmpl` with the file extension → language mapping.

Available components: <https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/>

`detectLanguage` is intentionally simple — it inspects the file path's extension only. If you need fancier detection (shebangs, content sniffing), do it in `data.js` at scaffold time and store the resolved language alongside the diff. That keeps `app.js` deterministic.

## Storage-Prefix Hygiene

Every `localStorage` key the storybook writes is namespaced with `STORAGE_PREFIX`. **Use a different prefix per stack.** Otherwise opening two storybooks in the same browser shares state — comments from stack A leak into stack B's diffs at the same line keys.

Convention: `<jira-or-tag>-storybook-v1`, e.g. `pm32009-storybook-v1`. Keep the `-v1` suffix; if you ever change the storage shape, bump to `-v2` so old reviewers don't read incompatible state on resume.

## Output-Directory Convention

`scaffold.py` defaults to `$CLAUDE_PLUGIN_DATA/storybooks/<slug>-<timestamp>/`. The timestamp suffix lets the same stack regenerate cleanly (e.g. after fresh review verdicts arrive) without clobbering an open browser tab.

Don't override unless the user has a specific reason — keeping artifacts under `CLAUDE_PLUGIN_DATA` prevents stray storybooks from accumulating in working directories or PR branches.

## Re-Running Against an Existing Output

The block sentinels (`<!-- __BW_BLOCK_START__ ... -->`) are preserved in the rendered `index.html` and `app.js`. This means you can point `scaffold.py` at an existing output directory and re-render only the parts that changed (cover, pages, merge plan, stack-config). The sentinels make the rendered files idempotent — re-running with the same config produces an identical output.
