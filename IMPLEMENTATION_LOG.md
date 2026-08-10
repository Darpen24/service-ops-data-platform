# Implementation log

## 2026-07-31 — Phase 0: Project Foundation

### Completed work

- Read the complete `PROJECT_SPEC.md` before making changes.
- Added the Phase 0 directory layout, repository governance, local setup documentation, Python package/tooling, PostgreSQL Compose service, PowerShell scripts, and GitHub templates.
- Preserved the sole existing project file, `PROJECT_SPEC.md`.

### Important files

`AGENTS.md`, `PLANS.md`, `DECISIONS.md`, `README.md`, `PROJECT_SETUP.md`, `pyproject.toml`, `docker-compose.yml`, `scripts/setup.ps1`, `scripts/check.ps1`, `src/service_ops/`, and `docs/learning/phase-00-foundation.md`.

### Decisions made

See `DECISIONS.md` ADR-001 through ADR-011. The local path uses PostgreSQL and ELT later; cloud implementations remain optional and Terraform apply is manual-approval-only.

### Commands executed

- `python --version` (host)
- `python -m venv .venv` and `.venv\\Scripts\\python.exe -m pip install -e '.[dev]'` (host)
- `docker run --rm --mount "type=bind,source=<repository>,target=/app" --workdir /app python:3.12-slim sh -lc "python --version && pip install --no-cache-dir -e '.[dev]' && python -c 'from service_ops.health import foundation_status; print(foundation_status())' && pytest && ruff check . && mypy src"`
- `docker compose --env-file .env.example config`
- `docker compose --env-file .env.example up -d --wait`
- `docker compose --env-file .env.example exec -T postgres pg_isready -U service_ops_app -d service_ops`
- `docker compose --env-file .env.example exec -T postgres psql -U service_ops_app -d service_ops -c 'SELECT 1 AS connection_ok;'`
- `docker compose --env-file .env.example down`

### Passed checks

- Docker Compose configuration validation: passed.
- PostgreSQL image pull, startup with health wait, health check, authenticated `SELECT 1`, and shutdown: passed.
- Isolated Python 3.12.13 package installation: passed.
- Python import smoke test: printed `service-ops foundation ready`.
- pytest: `1 passed in 0.28s`.
- Ruff: `All checks passed!`.
- mypy: `Success: no issues found in 2 source files`.

### Failed and blocked checks

- Native package installation on this workstation is blocked: the available `python` is `Python 3.14.0`, while `pyproject.toml` correctly requires `>=3.12,<3.13`. Pip reported: `Package 'service-ops-data-platform' requires a different Python: 3.14.0 not in '<3.13,>=3.12'`.
- Native smoke, pytest, Ruff, and mypy therefore could not run from `.venv`; the failed installation meant those tools were unavailable. A Python 3.12 container completed the same validation successfully.
- `py -0p` listed only Python 3.14 and 3.10; install Python 3.12 and rerun `./scripts/setup.ps1` for native Windows validation.

### Problems encountered and resolution

- PostgreSQL was initially queried immediately after container start, before it accepted connections. The Compose start command and PowerShell validation script now use `up -d --wait`; the final lifecycle validation passed.
- The host did not provide Python 3.12. An isolated official Python 3.12 container was used to validate installation, import, pytest, Ruff, and mypy without weakening the required Python version.

### Final review validation — 2026-07-31

The Phase 0 work was reviewed against `PROJECT_SPEC.md`, `AGENTS.md`, and the Phase 0 acceptance criteria. The review added explicit ADR coverage for the planned star schema and Power BI's future curated-mart connection; no later-phase implementation was added.

- GitHub authentication: confirmed for `Darpen24` with `repo` and `workflow` token scopes.
- Python environment: official `python:3.12-slim` container reported `Python 3.12.13`.
- Dependency installation: `pip install --no-cache-dir -e '.[dev]'` passed in the Python 3.12 container.
- Import smoke test: passed; output `service-ops foundation ready`.
- pytest: passed; `1 passed in 0.23s`.
- Ruff: passed; `All checks passed!`.
- mypy: passed; `Success: no issues found in 2 source files`.
- Docker Compose configuration: passed with `docker compose --env-file .env.example config`.
- PostgreSQL: `up -d --wait` reached healthy state; `pg_isready` reported `accepting connections`; authenticated `SELECT 1 AS connection_ok;` returned one row.
- Docker shutdown: passed with `docker compose --env-file .env.example down`.

### Known limitations

No synthetic data, database business objects, dbt models, CI workflow, cloud implementation, Airflow, or Power BI artifact has been created. Phase 0 validation may be constrained by local Python or Docker availability.

### Recommended next step

Install Python 3.12 for native Windows use, review and approve the Phase 0 foundation, then begin Phase 1 only after that approval.

## 2026-07-31 — Phase 1: Python synthetic data and Parquet

### Completed work

- Added deterministic generation of teams, agents, customers, categories, subcategories, SLA rules, tickets, and ticket status history.
- Added JSON, CSV, and Snappy-compressed Parquet writers, a manifest/checksum, `argparse` commands, and independent data validation.
- Added an explicit defect mode that writes invalid ticket copies separately; default output remains clean.
- Added a committed 25-ticket sample and ignored larger validation outputs.

### Important files

`src/service_ops/generation/`, `src/service_ops/__main__.py`, `tests/unit/test_generation.py`, `tests/integration/test_output_formats.py`, `data/sample/phase-01/`, `docs/data_dictionary/phase-01-source-data.md`, and `docs/learning/phase-01-python-parquet.md`.

### Commands executed and exact results

- Python 3.12.13 container package installation: passed.
- `pytest`: `9 passed in 1.05s`.
- `pytest --cov=service_ops --cov-report=term-missing`: `9 passed in 2.17s`; total coverage `77%`.
- `ruff format --check .`: `27 files already formatted`.
- `ruff check .`: `All checks passed!`.
- `mypy src`: `Success: no issues found in 8 source files`.
- Small generation: 25 tickets, 108 status-history records, 12 agents, 4 teams, 4 customers, 4 categories, 8 subcategories, and 4 SLA rules; clean validation passed.
- Temporary larger generation: 250 tickets and 1,082 status-history records; clean validation passed.
- Defect validation: 6 explicitly injected records produced `overall_result=fail` when combined with clean tickets; the clean source files remained valid.
- JSON, CSV, and Parquet round trips: passed in `tests/integration/test_output_formats.py` for every dataset.
- Git ignore check: `data/raw/phase-01-validation/tickets.parquet` and `data/raw/phase-01-defects/invalid_tickets.json` are ignored by `data/raw/*`.

### Decisions and known limitations

See ADR-012 and ADR-013. The sample models realistic but deliberately compact support operations. CSV round trips preserve schema and row count but values are strings when read with the standard library; typed analytical consumers should use Parquet. Native host validation remains blocked until Python 3.12 is installed; all Phase 1 checks ran in an isolated Python 3.12.13 container.

### Recommended next step

Review Phase 1 and begin PostgreSQL business schemas only in Phase 2 after approval.

## 2026-08-03 — Phase 2: PostgreSQL and SQL

### Completed work

- Created `raw`, `staging`, `analytics`, and `audit` schemas; source-shaped raw tables; audit
  load tracking; keys, references, lifecycle/status/value checks; and targeted indexes.
- Added transactional, typed-Parquet loading from the committed Phase 1 sample. It validates the
  manifest and source data, loads parents before children, and is idempotent through stable keys
  and `ON CONFLICT DO NOTHING`.
- Added analytical dimensions/facts as views, twenty executable business SQL questions, and SQL
  validation for relational, lifecycle, SLA, history, and cross-row agent/team rules.
- Added PostgreSQL integration tests for schema/view creation, full and repeat load counts,
  idempotency, constraints, lifecycle ordering, final status, checksum rejection, cross-row
  validation, controlled average/median calculation, and guarded reset behaviour.
- Added SQLFluff configuration plus Phase 2 architecture, data-dictionary, learning, and LinkedIn
  draft documentation. Updated the Phase boundary, delivery plan, decisions, and README.

### Files created or modified

- Created `.sqlfluff`, `src/service_ops/database.py`, `sql/ddl/`, `sql/analysis/`,
  `sql/validation/`, `tests/integration/test_postgresql.py`,
  `docs/architecture/phase-02-postgresql.md`,
  `docs/data_dictionary/phase-02-postgresql.md`,
  `docs/learning/phase-02-postgresql-sql.md`, `docs/learning/phase-02-sql.md`, and
  `docs/linkedin/phase-02-postgresql-sql.md`.
- Modified `pyproject.toml`, `src/service_ops/__main__.py`, `AGENTS.md`, `PLANS.md`,
  `DECISIONS.md`, `README.md`, and this log.

### Final executed validation — 2026-08-03

- Python 3.12.13 container CLI import smoke: `python -m service_ops --help` passed.
- `pytest`: `17 passed in 2.91s`.
- `pytest --cov=service_ops --cov-report=term-missing`: `17 passed in 4.38s`; total coverage
  `85%` (471 statements, 61 missed, 154 branches, 25 partial branches).
- `ruff format --check .`: `34 files already formatted`.
- `ruff check .`: `All checks passed!`.
- `mypy src`: `Success: no issues found in 9 source files`.
- `sqlfluff lint sql/` with PostgreSQL dialect: `All Finished!` (exit code 0).
- `docker compose --env-file .env.example config`: passed.
- PostgreSQL lifecycle: `docker compose --env-file .env.example up -d --wait` reached healthy;
  `pg_isready` returned `accepting connections`; authenticated `SELECT 1 AS connection_ok` returned
  one row; `docker compose --env-file .env.example down` passed.
- `database initialise`: passed. First `database load-sample` inserted 4 teams, 12 agents,
  4 customers, 4 categories, 8 subcategories, 4 SLA rules, 25 tickets, and 110 history events.
  The immediate repeat inserted zero rows and reported all those rows as existing.
- `database validate`: passed with zero violations in all 16 checks. `database query-summary`
  returned the expected counts above. The committed sample validator passed and matched checksum
  `13563ac43159119f0ada365c208b3585aed69ebcbec919cee5a90c30dce2d683`.
- All 20 statements in `sql/analysis/service_operations.sql` executed through PostgreSQL `psql`
  successfully.
- `EXPLAIN (ANALYZE, BUFFERS)` for the grouped open-backlog query passed. On the 25-ticket sample,
  PostgreSQL selected a sequential scan (`Execution Time: 0.136 ms`), which is expected at this
  small volume despite the supporting indexes.

### Failed or blocked checks

- Two earlier combined PowerShell/Docker convenience commands failed because PowerShell removed
  nested Python quoting (`SyntaxError`/`NameError`) before their intended smoke fragment ran. They
  did not change repository or database state; the equivalent final checks above were run
  independently and passed.
- Native host Python remains 3.14 rather than the required 3.12. All Python validation therefore
  ran in the official Python 3.12.13 container. No Phase 2 check is otherwise blocked.

### Decisions, limitations, and next step

- See ADR-014 and ADR-015. The committed sample is intentionally tiny, so `EXPLAIN` may choose a
  sequential scan even where an index exists; query-plan claims must be reassessed on realistic
  volume. `staging` is created but intentionally unused until Phase 3, and dbt is intentionally
  deferred to Phase 4.
- Recommended next step: review the Phase 2 draft pull request. Begin Phase 3 only after Phase 2
  is accepted and merged.

### Phase 2 acceptance review

| Criterion | Result | Evidence |
| --- | --- | --- |
| Schemas, typed tables, constraints, audit and indexes | Pass | `sql/ddl/` and PostgreSQL integration tests |
| Safe, idempotent committed-Parquet load | Pass | loader tests; first/repeat load results |
| Analytics views and twenty business questions | Pass | `004_analytics_views.sql`; 20 statements executed |
| SQL and Python validation | Pass | zero database violations; 17 tests; Ruff, mypy, SQLFluff |
| Documentation and learning material | Pass | Phase 2 docs, dictionary, architecture, README, ADRs |
| Later phases avoided | Pass | no Phase 3 ETL/ELT, dbt, cloud, Airflow, or Power BI implementation |

## 2026-08-09 — Phase 3: ETL, ELT, and data quality

### Completed work

- Corrected Phase 2 to complete/merged and set the active boundary to Phase 3.
- Added audited, watermark-driven typed-Parquet ticket staging, deterministic record checksums,
  partial-run quarantine, transaction rollback handling, and operational CLI commands.
- Added integration coverage for repeat batches, watermark stability, quarantine, and corrected
  late-arriving records. See `docs/learning/phase-03-etl-elt.md` and ADR-016/017.

### Commands and actual results

- Native Python 3.12.10: `ruff format --check .` — `38 files already formatted`.
- `ruff check .` — `All checks passed!`.
- `mypy src` — `Success: no issues found in 11 source files`.
- `pytest` — `14 passed, 5 skipped, 1 warning in 1.22s`. The warning is an upstream
  `dateutil` deprecation warning. PostgreSQL integration tests were skipped because no integration
  environment was configured.

### Blocked validation and limitation

- `docker compose` and Docker-based PostgreSQL validation were blocked because Docker Desktop was
  not running: `open //./pipe/docker_engine: The system cannot find the file specified.` No
  PostgreSQL pipeline integration result is claimed for this run. Start Docker Desktop and rerun
  `pytest` with `POSTGRES_HOST` configured to exercise the five skipped integration tests.

### Next phase

Phase 4 will add dbt models to the Phase 3 raw/staging contract; no dbt code was added here.

## 2026-08-09 — Phase 4: dbt transformations and analytics marts

### Completed work

- Added a dbt-postgres project with sources/freshness, staging, intermediate lifecycle/SLA/team
  models, dimensions, facts, daily/team/SLA/category marts, a snapshot, macro, tests, and exposure.
- Kept dbt outputs in `dbt_analytics` to coexist with Phase 2's `analytics` views.

### Commands and actual results

- Installed optional `dbt-postgres`; `dbt --version` reported Core 1.12.0 and postgres 1.11.0.
- `dbt parse --no-partial-parse --project-dir dbt/service_ops --profiles-dir dbt/service_ops`
  passed.

### Blocked validation

- `dbt debug`, seed, snapshot, build, test, and docs generation require the local PostgreSQL
  service. Docker Desktop remains unavailable (`//./pipe/docker_engine` missing), so none of those
  commands were represented as successful.

## 2026-08-09 — Phase 5: CI/CD

### Completed work

- Added a GitHub Actions quality workflow for Python, PostgreSQL-backed integration, SQLFluff,
  Compose, dbt parse/build, coverage artifact upload, and Gitleaks secret scanning.
- Kept workflow permissions least-privilege and did not add Terraform before Phase 8.

### Validation and limitation

- Workflow YAML was reviewed locally. Remote GitHub Actions execution is pending after push and is
  not claimed as passed. Docker Desktop remains unavailable for local service-container validation.

### Secret-scan history correction — 2026-08-10

- Gitleaks failed on pull request #9 without reporting a secret because its shallow checkout could
  not resolve the historical pull-request range. The `secret-scan` checkout now uses
  `fetch-depth: 0`, retaining Gitleaks and its default findings policy unchanged. Remote execution
  is required to confirm the corrected job result.

## 2026-08-09 — Phase 6: optional Snowflake adapter

- Added credential-free Snowflake SQL and dbt profile examples covering roles/grants, a small
  auto-suspending warehouse, file format/stage, COPY guidance, VARIANT, stream, and suspended task.
- No Snowflake credentials were available. No Snowflake SQL, COPY, task, Time Travel, clone, or
  cloud resource operation was executed or claimed as executed.

## 2026-08-09 — Phase 7: Databricks and Delta Lake

- Added optional Bronze/Silver/Gold contracts, a Databricks notebook design, and an opt-in small
  job resource with an auto-terminating cluster definition.
- Local PySpark/Delta and Databricks deployment were not run because no runtime or credentials are
  available. The pure Python contract is covered by the ordinary test suite.
### Timestamp contract correction — 2026-08-10

- The committed Parquet reader returned Phase 1 ISO-8601 timestamp strings in the live Python
  environment. Phase 3 had incorrectly compared them directly with PostgreSQL `datetime`
  watermarks. Added a single UTC-aware pipeline normalization boundary that accepts strings or
  datetimes, rejects malformed/naive values, and canonicalises timestamps for checksums and JSON
  audit payloads.
- Live PostgreSQL validation with `POSTGRES_HOST=127.0.0.1` and port `55432`: `pytest -ra` —
  `19 passed in 3.05s`; coverage — `19 passed in 3.87s`, total `83%`; Ruff formatting/lint and
  mypy passed.

### Phase 1 lifecycle correction — 2026-08-03

- Replaced history's final `updated_at` use with explicit `in_progress_at` and regenerated the committed sample.
- Extended independent ticket/history validation for full chronological transitions, continuous sequences, final status consistency, unresolved null handling, manifest checks, and corrupted/reordered history detection.
- Final validation: `13 passed in 2.35s`; coverage `79%`; Ruff formatting/lint and mypy passed. Ruff format initially reported two new test files and was corrected before final rerun.
- Committed-sample validation read Parquet files under `data/sample/phase-01/`, matched all manifest counts and checksum `13563ac43159119f0ada365c208b3585aed69ebcbec919cee5a90c30dce2d683`, and returned `overall_result=pass`.
