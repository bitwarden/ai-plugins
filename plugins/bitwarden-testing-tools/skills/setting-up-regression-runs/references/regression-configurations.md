# Regression run configurations (Mobile, Desktop, Extension)

These platforms ship several same-named runs distinguished only by Testmo Configuration. The API can
only create step 1 of each; the step 2 UI pass is explained in the `bitwarden-testmo-tools`
`creating-test-runs` skill's `references/multi-configuration-runs.md`, and each spec's `_comment` gives
its exact pass.

- **Mobile** — 2 runs, both named `Mobile`. Same filters, differing only by which automation type is
  excluded. `config_id` 1 = Android, 3 = iOS.

Desktop and Extension use a **broad + narrow** split: one variant covers the full folder and the rest
are driven by an "essential" tag.

- **Desktop** — 3 runs, all named `Desktop`. Broad = **macOS** (21); narrow = **Windows** (22), **Linux**
  (20), driven by the `desktop-essential` tag (id 15999).
- **Extension** — 4 runs, all named `Extension`. Broad = **`MacOS, Chrome`** (7); narrow =
  **`Windows, Edge`** (15), **`MacOS, Safari`** (10), **`Linux, Firefox`** (5), driven by the
  `extension-essential` tag (id 17190).

Config and tag ids above verified 2026-08-28 via `GET /projects/1/configs` and `GET /projects/1/tags`.

Every variant on both platforms, broad and narrow alike, takes a step 2. The two variant types differ
only in how cases are selected:

|            | Broad                               | Narrow                                       |
| ---------- | ----------------------------------- | -------------------------------------------- |
| Scope      | whole top-level folder + subfolders | the `<platform>-essential` tag (server-side) |
| Test Type  | Smoke + Regression                  | **any** — the tag defines the scope          |
| Case state | Active                              | Active                                       |
| Automation | manual only (exclude 10, 23, 24)    | manual only (exclude 10, 23, 24)             |

Narrow variants deliberately drop the test-type filter, since a tagged case counts regardless of type,
but keep the state and automation-type filters so retired and already-automated cases stay out.
