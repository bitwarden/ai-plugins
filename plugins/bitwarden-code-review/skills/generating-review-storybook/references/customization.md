# Storybook Customization

The bundled template ships Bitwarden-branded with a small set of reasonable defaults. Customize via the config or by editing the template.

## Brand Override

The template's color palette lives in `assets/template/assets/styles.css` as CSS custom properties scoped to `:root` and `[data-theme="dark"]`. If you need a non-Bitwarden palette:

1. Don't edit `styles.css` in the bundled template (changes carry to every storybook generated thereafter).
2. Either:
   - Run `scaffold.py` with the default output, then post-edit the generated `assets/styles.css`. Quickest path; not reproducible.
   - Or maintain a fork of the skill's template under your own plugin. Add `bw-shield.svg` replacement, palette overrides, and font swaps there. Reproducible.

Every shield in the storybook comes from `assets/template/assets/bw-shield.svg`: the favicon links to it, and `scaffold.py` copies its paths inline into the header lockup and the cover so `styles.css` can theme them for light and dark. To use a different mark, replace that one file. Keep the `shield-fill` and `shield-glyph` classes on its paths and the `viewBox="0 0 24 28"`, because `styles.css` colors and sizes against them.

## Language Imports for Code Highlighting

Prism is vendored under `assets/template/assets/vendor/prism/` so the storybook loads nothing from the network. `index.html.tmpl` loads `prism-core` first, then the language components in dependency order: `clike` (also the fallback `detectLanguage` returns for unknown extensions), `markup` (HTML, XML, plist), `json`, `swift`, `kotlin`, `csharp`, `javascript`, and `typescript`.

To highlight another language:

1. Copy `components/prism-<lang>.min.js` from the same `prismjs` release recorded in `vendor/prism/README.md` into `vendor/prism/`, along with any component it requires (Prism's `components.json` lists each component's `require` and `modify` dependencies).
2. Add a `<script>` for it in `index.html.tmpl` after every component it requires or modifies.
3. Extend `detectLanguage()` in `app.js.tmpl` with the file extension to language mapping.

`detectLanguage` is intentionally simple — it inspects the file path's extension only. If you need fancier detection (shebangs, content sniffing), do it in `data.js` at scaffold time and store the resolved language alongside the diff. That keeps `app.js` deterministic.

## Storage-Prefix Hygiene

Every `localStorage` key the storybook writes is namespaced with `STORAGE_PREFIX`. **Use a different prefix per stack.** Otherwise opening two storybooks in the same browser shares state — comments from stack A leak into stack B's diffs at the same line keys.

Convention: `<jira-or-tag>-storybook-v1`, e.g. `pm32009-storybook-v1`. Keep the `-v1` suffix; if you ever change the storage shape, bump to `-v2` so old reviewers don't read incompatible state on resume.

## Output-Directory Convention

`scaffold.py --output-root <root>` writes to `<root>/<slug>-<timestamp>/`, and the skill passes the plugin data directory's `storybooks/` as the root. The timestamp suffix lets the same stack regenerate cleanly (e.g. after fresh review verdicts arrive) without clobbering an open browser tab. `--output <dir>` writes to that exact directory instead. With neither option, the script uses `$CLAUDE_PLUGIN_DATA/storybooks` as the root when that variable is set in its environment, and otherwise exits with an error rather than guessing a location.

Don't override unless the user has a specific reason — keeping artifacts under the plugin data directory prevents stray storybooks from accumulating in working directories or PR branches.
