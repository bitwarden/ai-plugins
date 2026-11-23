# Multi-configuration runs

Read this before creating or reviewing any spec that carries a `config_id`. These runs need a manual
Testmo UI pass after the script finishes, and the pass is mandatory.

Some platforms ship **several same-named runs distinguished only by Testmo Configuration** (for example
one `Mobile` run per OS). Each variant is its own spec file with the same `run_name` and a different
`config_id`. Look config ids up via `GET /projects/{id}/configs`.

Testmo's `/cases` API **cannot filter by configuration** and exposes no per-case config assignment, so
these are always **two-step runs**:

1. **Step 1 (the script):** create the run with the spec's case set and `config_id`.
2. **Step 2 (manual, Testmo UI):** remove the cases that belong to the other configurations. Each spec
   documents its own step 2 in `_comment`.

Until step 2 is done the run holds the wrong case set. The script lists every affected run under
`MANUAL STEP 2 REQUIRED`; pass that list on to the user.

A common split is **broad + narrow**: one variant covers a whole folder, and the others are driven by a
tag that marks the essential cases. A narrow, tag-only spec has no folder or test-type filter behind it,
so verify the tag against `GET /projects/{id}/tags` before trusting it — a wrong or duplicated tag name
yields the wrong case set rather than an error.

**`"config_id": null` is a deliberate placeholder** meaning "this run needs a Configuration that has not
been looked up yet." Dry-runs still work so case counts can be validated, but `--create` refuses, since
the variants would be indistinguishable.
