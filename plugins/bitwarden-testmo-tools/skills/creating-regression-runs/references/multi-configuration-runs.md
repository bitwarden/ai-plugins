# Multi-configuration runs (Mobile, Desktop, Extension)

Read this before creating or reviewing any spec that carries a `config_id`. These runs need a
manual Testmo UI pass after the script finishes, and the pass is mandatory.

Some platforms ship **several same-named runs distinguished only by Testmo Configuration**. Each variant
is its own spec file with the same `run_name` and a different `config_id`.

Testmo's `/cases` API **cannot filter by configuration** and exposes no per-case config assignment, so
these are always **two-step runs**: the spec reproduces step 1, and removing the non-target
configuration's cases is a manual UI pass. Each affected spec documents its own step 2 in `_comment`.

- **Mobile** — 2 runs, both named `Mobile`. Same filters, differing only by which automation type is
  excluded. `config_id` 1 = Android, 3 = iOS.

Desktop and Extension instead use a **broad + narrow** split, where one variant covers the full folder and
the rest are driven by an "essential" tag:

- **Desktop** — 3 runs, all named `Desktop`. Broad = **macOS** (21); narrow = **Windows** (22), **Linux**
  (20), driven by the `desktop-essential` tag (id 15999).
- **Extension** — 4 runs, all named `Extension`. Broad = **`MacOS, Chrome`** (7); narrow =
  **`Windows, Edge`** (15), **`MacOS, Safari`** (10), **`Linux, Firefox`** (5), driven by the
  `extension-essential` tag (id 17190).

Config and tag ids above verified 2026-08-28 via `GET /projects/1/configs` and `GET /projects/1/tags`.

Every variant on both platforms — broad and narrow alike — takes a step 2. The two variant types differ
only in how cases are selected:

|            | Broad                               | Narrow                                       |
| ---------- | ----------------------------------- | -------------------------------------------- |
| Scope      | whole top-level folder + subfolders | the `<platform>-essential` tag (server-side) |
| Test Type  | Smoke + Regression                  | **any** — the tag defines the scope          |
| Case state | Active                              | Active                                       |
| Automation | manual only (exclude 10, 23, 24)    | manual only (exclude 10, 23, 24)             |

Narrow variants deliberately drop the **test-type** filter — a tagged case counts regardless of type — but
they keep the **state** and **automation-type** filters so retired and already-automated cases stay out.

Verify tag names against `GET /projects/1/tags` before trusting a narrow spec: it has no folder or type
filter to constrain it, so a wrong or duplicated tag name silently yields the wrong case set rather than
erroring.

**`"config_id": null` is a deliberate placeholder** meaning "this run needs a Configuration that has not
been looked up yet." Dry-runs still work so case counts can be validated, but `--create` is refused —
otherwise the variants would be indistinguishable from each other. Fill it in from
`GET /projects/{id}/configs`.
