# applying-bitwarden-branding — evals

A small regression harness for the branding skill. It exercises both jobs the
skill does — **applying** brand to a deliverable and **reviewing** a deliverable
for brand compliance — against fixed mock subjects, and grades the outputs
deterministically where it can.

## Fixtures are mock-only

`inputs/` contains **only fabricated artifacts** — no real Bitwarden data,
metrics, or internal decks. Keep it that way. If a fixture needs to feel
realistic, invent the content.

- `inputs/offbrand-deck.html` — deliberately off-brand (Big Shoulders / IBM Plex
  fonts, invented slate/green palette, no official lockup, sub-36px radii).
- `inputs/onbrand-control.html` — substantially on-brand (Inter, Bitwarden
  palette, 36px radius, official shield embedded) with brand-silent defensible
  choices (a Deep-Blue-derived dark surface, data-viz series) and exactly one
  genuine fault (an off-palette orange CTA hover).

## Files

| File          | Purpose                                                                      |
| ------------- | ---------------------------------------------------------------------------- |
| `evals.json`  | The eval definitions: prompt, input files, expected output.                  |
| `rubric.json` | Pre-registered objective assertions and ground truth.                        |
| `grade.py`    | Deterministic grader. Reads palette + logo signatures live from `../assets`. |
| `inputs/`     | Mock subject artifacts.                                                      |

## Running an eval

1. For each eval in `evals.json`, run the skill against its `prompt` (with the
   listed `files` available). For a baseline measurement, run the same prompt
   with the skill disabled.
2. Save each run's deliverable under `runs/<eval-name>/outputs/`:
   - apply evals → the produced `.html`
   - review evals → the review as `.md`
3. Grade:
   ```
   ./grade.py            # defaults to ./runs
   ./grade.py /path/to/runs
   ```
   It writes `grading.json` into each run dir and prints a summary table.

`runs/` is scratch — do not commit it.

## What is graded deterministically vs. not

`grade.py` covers only the **context-free** checks, because those are the ones a
script does reliably:

- **apply**: loads Inter, uses Bitwarden Blue / Deep Blue, embeds the official
  lockup (not redrawn), applies a 36px radius, is valid self-contained HTML, and
  — for the deck — drops the off-brand fonts. Also reports an off-palette hex
  count (lower is better).
- **review (true-positive)**: detects the off-brand fonts, palette, missing
  logo, and non-36px radii in the off-brand deck.

The **judgment** dimensions are deliberately left to a blind LLM grader, because
they are exactly what a script gets wrong (we tried; it over-flagged sanctioned
Deep-Blue-derived dark ramps as violations):

- **review specificity** (`cites_specific_values`): does the review cite actual
  values/locations rather than generic advice?
- **review false-positives** (`affirms_correct_core`, `false_positive_count`):
  on the on-brand control, does the review affirm the correct core, treat the
  dark surface and data-viz series as judgment calls, and flag only the genuine
  orange fault? Over-flagging defensible choices is the failure mode.

Grade the judgment dimensions with independent, blind LLM passes (no access to
the expected-output text) and score against `rubric.json`'s ground truth.
