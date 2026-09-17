# Testmo API and project 1 field reference

Read this when you need an endpoint, a project id, or the numeric id behind a field value —
writing a new spec, or checking one that selects the wrong cases.

## API reference

- **Base:** `https://bitwarden.testmo.net/api/v1`, auth header `Authorization: Bearer $TESTMO_API_KEY`.
- **Projects:** `1` = **Bitwarden** (live: ~13.7k cases), `2` = **Pretend** (sandbox), `11` = Automation -
  Test, `14` = Archive. Every shipped spec targets project `1`. Project `2` is safe for exercising the
  script's write path, but it does **not** mirror project 1's folders, tags, or configurations, so a spec
  cannot be validated there — a dry-run against it proves nothing about the case set the spec will select.
- **Pagination quirk:** `per_page` only accepts specific values (100 works; 5/10 return HTTP 422). Omit
  `per_page` and page with `page=N`; responses carry `next_page`/`last_page`.
- **Read endpoints (GET):** `/projects/{id}/cases`, `/projects/{id}/folders`, `/projects/{id}/milestones`,
  `/projects/{id}/runs`, `/projects/{id}/automation/runs`, and single-run detail at `/runs/{id}`
  (top-level — `/projects/{id}/runs/{id}` 404s).
- **Create run (POST `/projects/{id}/runs`):** body `{name, state_id, include_all:false, cases:[ids],
milestone_id?, config_id?, tags?, note?}`. Run `state_id`s (from `/projects/{id}/states`): 6=New,
  7=In progress, 8=Under review, 9=Rejected, 10=Done. Active runs use `7`.

## Project 1 field reference (captured 2026-07-22 — re-verify via `/projects/1/fields`)

- **Test Type** (`custom_test_type`, multiselect): 18=Functional, 19=Regression, 20=Smoke,
  21=Accessibility, 22=Compatibility.
- **Automation Type** (`custom_automation_type`, single): 8=Not Automating, 11=Ready to Automate,
  9=In Progress, 10=Automated, 23=Automated-Android, 24=Automated-iOS, 12=Blocked. "Manual only" =
  exclude {10, 23, 24}.
- **Case `state_id`**: 4=Active (~94% of cases), 5=(inactive/deprecated), plus legacy strays. Regression
  runs filter to `[4]`.
- **Team** (`custom_team`, multiselect): 25=Admin Console, 26=Auth, 27=Autofill, 28=Billing,
  38=Desktop Native, 29=DIRT, 30=Key Management, 31=Mobile, 37=Passwordless, 32=Platform,
  33=Secrets Manager, 34=Tools, 35=UI Foundation, 36=Vault.
- **Top-level folders**: Web=3136, Extension=2779, Mobile=3010, Desktop=2923, CLI=2858, API=3390,
  Passwordless=3103. (Excluded as junk: "Retired Test Cases"=81330, "Need to be deleted"=371518.)
