# Changelog

All notable changes to the Bitwarden Stripe Tools Plugin will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-07

### Added

- `using-stripe-cli`, read-only Stripe test-mode data queries, a preview of a subscription's next invoice (`POST /v1/invoices/create_preview`, which creates nothing, because `GET /v1/invoices/upcoming` is deprecated), and the single permitted write of advancing an already-attached test clock, through the `stripe_cli.py` wrapper. The wrapper refuses any key that is not a test key before calling the CLI. Its `Read` grant covers only the skill's own `references/`, so a session that invokes it gains no wider file access. Includes a trigger eval and advice-only behavior evals, both recorded as on-demand prose readings, and a copy of the trigger-eval runner at `evals/run_real_eval.py`.
