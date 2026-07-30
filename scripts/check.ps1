[CmdletBinding()]
param(
    [switch]$WithDocker
)

$ErrorActionPreference = 'Stop'
$python = if (Test-Path -LiteralPath '.\.venv\Scripts\python.exe') { '.\.venv\Scripts\python.exe' } else { 'python' }

& $python -c "from service_ops.health import foundation_status; print(foundation_status())"
& $python -m pytest
& $python -m ruff check .
& $python -m mypy src

if ($WithDocker) {
    if (-not (Test-Path -LiteralPath '.env')) {
        Copy-Item -LiteralPath '.env.example' -Destination '.env'
    }
    docker compose config
    docker compose up -d --wait
    docker compose exec postgres sh -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
    docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1 AS connection_ok;"'
    docker compose down
}
