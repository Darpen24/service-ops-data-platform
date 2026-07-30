# Phase 00: Foundation refresher

## Why this structure matters

This repository separates source code (`src/`), tests (`tests/`), configuration (`config/`), storage boundaries (`data/`), SQL, documentation, and delivery assets. That makes ownership and change impact visible: a future loading change should not silently alter a Power BI artifact or raw input. Empty directories are retained only where the planned repository shape itself matters.

## Why use a src layout

`src/service_ops` is not importable merely because the repository root happens to be on the path. Installing the project is therefore part of the testable workflow, which catches packaging mistakes earlier than a flat layout. The tiny `foundation_status` function is deliberately a package smoke boundary, not application functionality.

## Dependency isolation and configuration

The `.venv` environment isolates project libraries from the system Python. `pyproject.toml` constrains Python to 3.12 and centralises build, test, lint, and type-check configuration. `.env` separates environment-specific values from code; `.env.example` documents safe values but is not a secret store.

## Docker, images, containers, and volumes

Docker avoids a host PostgreSQL installation. The `postgres:16.4-alpine` image is a versioned template; the running PostgreSQL service is a container; `service_ops_postgres_data` is a named volume that persists database files when the container is recreated. The Compose health check runs `pg_isready`, so a started container is not mistaken for a ready database.

## Secrets and generated data

`.gitignore` excludes `.env` and generated raw/processed data. This prevents accidental credential leakage and avoids storing reproducible output as source code. The example password is explicitly local-only and must not be reused.

## What the checks validate

- **pytest** checks declared behavioural expectations; currently the public smoke marker.
- **Ruff** finds formatting-adjacent, import, and common correctness problems quickly.
- **mypy** checks static type consistency before code runs.
- **Docker Compose config** resolves the service definition and variables.
- **pg_isready** verifies PostgreSQL accepts connections; `SELECT 1` verifies an authenticated SQL connection.

Independent phases make failures, review, rollback, and interview explanations much clearer: Phase 0 should be explainable and runnable without needing Phase 1 data or later cloud tools.

## Interview questions and concise answers

### Git

1. **Why ignore `.env`?** It contains environment-specific credentials; this repository commits only `.env.example` with non-sensitive local documentation.
2. **Why small conventional commits?** A commit such as `chore: initialise project foundation` communicates one reviewable intent and is easy to revert.
3. **How do you prevent accidental generated-data commits?** Ignore `data/raw` and `data/processed` while retaining their directory markers.
4. **What belongs in a pull request template?** Context, tests, security/data impact, documentation, screenshots, and rollback planning—the fields used here.
5. **Why document decisions in the repository?** ADRs preserve the reasoning behind PostgreSQL, ELT, and optional cloud paths when contributors change.

### Docker

1. **Image versus container?** The image is the versioned PostgreSQL template; the container is its running instance.
2. **Why a named volume?** It preserves local PostgreSQL state independently of the container lifecycle.
3. **Why pin PostgreSQL 16.4?** A precise version improves reproducibility and avoids unreviewed behavioural changes from a floating tag.
4. **Why use a health check?** A process can start before it accepts SQL connections; `pg_isready` identifies readiness.
5. **Why use Compose variables?** Ports and credentials vary by environment without changing the Compose file.

### Project structure

1. **Why keep `src` and `tests` separate?** It prevents test-only import paths from hiding packaging faults.
2. **Why is Docker configuration in the root?** `docker-compose.yml` is the conventional local-service entry point; environment values stay in `.env`.
3. **Why not create dbt models now?** The plan keeps Phase 0 independently reviewable; dbt belongs to Phase 4.
4. **Why include pandas and pyarrow already?** They are planned data-foundation dependencies and pin the compatible local environment; no data logic is added yet.
5. **Why separate SQL, docs, and notebooks?** It keeps executable warehouse logic, human explanation, and exploratory work from becoming an untraceable monolith.
