# Test results JSON contract

The `playwright-test-runner` emits run results as JSON. The orchestrator assembles segments into the canonical `test-results-<timestamp>.json` with `merge_results.py` and renders it with `render_report.py`. Concrete examples live in `examples/`; they are the producer's reference and the scripts' golden test fixtures.

## Run object

| Field                 | Type   | Notes                                                                                                                 |
| --------------------- | ------ | --------------------------------------------------------------------------------------------------------------------- |
| `run_status`          | string | `complete`, `paused` (segment only), or `aborted`                                                                     |
| `abort_reason`        | string | Present only when `run_status` is `aborted`                                                                           |
| `need_user_input`     | string | Present only on a `paused` segment; the resume question                                                               |
| `need_user_input_url` | string | Optional, and only on a `paused` segment; a link the user opens to do the human step, such as a Stripe Dashboard page |
| `totals`              | object | `{ total, passed, adaptive, failed, errored }`; derived on merge                                                      |
| `cases`               | array  | Case objects, in order; empty for an aborted run only if it aborted before any case completed                         |

Totals are derived from the per-case `status` values by `merge_results.py`. The runner does not emit totals. `total = passed + adaptive + failed + errored` and `len(cases) == total` hold by construction.

An `aborted` run MAY carry `cases` and `totals` alongside `abort_reason`. Any abort that lands after at least one test case completed takes this shape, and two paths reach it. A run may have split into segments at a `[HUMAN]` pause with a later segment aborting, most often because the resumed runner could not re-authenticate. Or a single-segment run may have hit an environment fault partway through, such as Mailcatcher becoming unreachable between cases, in which case the aborting segment carries its own completed cases. Either way the completed cases are preserved by `merge_results.py` and the report renders them under an abort banner. An `aborted` run with an empty or absent `cases` array means the run aborted before any test case completed, that is, setup or authentication failed, and no report is produced.

## Case object

| Field         | Type   | Notes                                                                                                                                                                                        |
| ------------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `number`      | int    | 1-based                                                                                                                                                                                      |
| `name`        | string |                                                                                                                                                                                              |
| `status`      | string | `PASS`, `PASS (adaptive)`, `FAIL`, or `ERROR`                                                                                                                                                |
| `url`         | string | Optional; the page under test                                                                                                                                                                |
| `setup_steps` | array  | Step objects; omit or use `[]` when there are none                                                                                                                                           |
| `test_steps`  | array  | Step objects                                                                                                                                                                                 |
| `notes`       | string | Optional                                                                                                                                                                                     |
| `adaptive`    | object | `{ specified, found }`; present only when status is `PASS (adaptive)`                                                                                                                        |
| `account`     | object | Optional; `{ email, password }` for an account the case created. The password is a disposable local-dev credential, written to `test-results-*.json` in cleartext, so never commit that file |

## Step object

| Field           | Type   | Notes                                                                                                                       |
| --------------- | ------ | --------------------------------------------------------------------------------------------------------------------------- |
| `text`          | string | Step description                                                                                                            |
| `outcome`       | string | `PASS`, `FAIL`, or `COMPLETED (User: <answer>)` for a human step                                                            |
| `observed`      | string | Optional; what was actually observed on an assertion step                                                                   |
| `screenshot`    | string | Optional; bare filename, rendered relative as `screenshots/<name>`                                                          |
| `human`         | bool   | Optional; `true` for a `[HUMAN]` step                                                                                       |
| `error_details` | array  | Optional; one entry per 4xx/5xx API response the step caused, on any step type. Diagnostic only: it never changes `outcome` |

## Error details entry

Each `error_details` entry describes one failed API response, in the server's own words. The report renders it red on a failed step and amber otherwise, with the stack trace collapsed.

| Field                     | Type   | Notes                                                                                                      |
| ------------------------- | ------ | ---------------------------------------------------------------------------------------------------------- |
| `request`                 | string | Required; method and path, with no origin or query string, such as `POST /api/organizations`               |
| `status`                  | int    | Optional; absent for an `external_trigger.py` call, whose output carries no status                         |
| `status_text`             | string | Optional; such as `Internal Server Error`                                                                  |
| `count`                   | int    | Optional; present only when the same request failed more than once in the step                             |
| `message`                 | string | Optional; the response's `message`, capped at 2,000 characters                                             |
| `validation_errors`       | object | Optional; field name to a list of messages, from the response's `validationErrors`                         |
| `exception_message`       | string | Optional; the response's `exceptionMessage`, capped at 2,000 characters                                    |
| `inner_exception_message` | string | Optional; the response's `innerExceptionMessage`, capped at 2,000 characters                               |
| `stack_trace`             | string | Optional; the response's `exceptionStackTrace`, trimmed to 15 frames with a final `… N more` line when cut |

The renderer skips an entry that is not an object or has no string `request`, and never fails a run over one.

## Invariants enforced in code

- `run_status` is a known value.
- Every case `status` is a known enum value.
- Derived totals are internally consistent and `len(cases) == total`.
- Malformed JSON, a missing required field, or an unknown enum is a loud, non-zero-exit failure naming the offending field or case.
