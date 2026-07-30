# Phase 0 setup

## Windows PowerShell

1. Install Python 3.12 and Docker Desktop.
2. Run `./scripts/setup.ps1` from the repository root.
3. Review the generated `.env`; it contains a local-development-only password.
4. Run `./scripts/check.ps1`.
5. When Docker Desktop is running, run `./scripts/check.ps1 -WithDocker`.

## Bash

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
cp .env.example .env
make check
make up
make postgres-health
make postgres-connect
make down
```

## Expected Phase 0 results

The smoke test prints `service-ops foundation ready`; pytest, Ruff, and mypy complete successfully; and PostgreSQL reports accepting connections before `SELECT 1` succeeds. No business objects should be present in the database.

## Troubleshooting

- `requires-python`: install Python 3.12; this project deliberately does not target other versions.
- Docker daemon unavailable: start Docker Desktop, then rerun `docker compose --env-file .env.example up -d`.
- Port in use: set an unused `POSTGRES_PORT` in `.env` and rerun the command.
- Authentication failure: ensure `.env` defines matching `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD` values before the first database start. Remove the named volume only if intentionally resetting local data.
