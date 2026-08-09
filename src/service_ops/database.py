"""Phase 2 local PostgreSQL initialisation and idempotent sample loading."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import psycopg
from psycopg import sql

from service_ops.generation.io import REQUIRED_DATASETS, read_committed_sample
from service_ops.generation.validation import validate_dataset

ROOT = Path(__file__).resolve().parents[2]
SAMPLE = ROOT / "data" / "sample" / "phase-01"
DDL = ROOT / "sql" / "ddl"

TABLES = {
    "teams": "teams",
    "agents": "agents",
    "customers": "customers",
    "categories": "categories",
    "subcategories": "subcategories",
    "sla_rules": "sla_rules",
    "tickets": "tickets",
    "ticket_status_history": "ticket_status_history",
}


def connection() -> psycopg.Connection[Any]:
    """Connect using only local environment configuration."""
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "service_ops"),
        user=os.getenv("POSTGRES_USER", "service_ops_app"),
        password=os.getenv("POSTGRES_PASSWORD", "change-me-local-only"),
    )


def initialise(conn: psycopg.Connection[Any]) -> None:
    """Execute ordered repeatable local PostgreSQL DDL scripts."""
    with conn.cursor() as cursor:
        for path in sorted(DDL.glob("00[1-9]_*.sql")):
            cursor.execute(path.read_text(encoding="utf-8"))
    conn.commit()


def load_sample(
    conn: psycopg.Connection[Any], directory: Path = SAMPLE
) -> dict[str, dict[str, int]]:
    """Validate and load typed sample Parquet in one transaction with conflict-safe inserts."""
    records, manifest = read_committed_sample(directory)
    if validate_dataset(records)["overall_result"] != "pass":
        raise ValueError("Sample records failed independent validation")
    results: dict[str, dict[str, int]] = {}
    with conn.transaction():
        with conn.cursor() as cursor:
            for dataset in REQUIRED_DATASETS:
                rows = records[dataset]
                if not rows:
                    results[dataset] = {"inserted": 0, "existing": 0}
                    continue
                columns = list(rows[0])
                statement = sql.SQL(
                    "INSERT INTO raw.{table} ({columns}) VALUES ({values}) ON CONFLICT DO NOTHING"
                ).format(
                    table=sql.Identifier(TABLES[dataset]),
                    columns=sql.SQL(",").join(map(sql.Identifier, columns)),
                    values=sql.SQL(",").join(sql.Placeholder() for _ in columns),
                )
                inserted = 0
                for row in rows:
                    cursor.execute(statement, [row[column] for column in columns])
                    inserted += cursor.rowcount
                results[dataset] = {"inserted": inserted, "existing": len(rows) - inserted}
            cursor.execute(
                "INSERT INTO audit.sample_loads (generated_batch_id, manifest_checksum) "
                "VALUES (%s,%s) ON CONFLICT DO NOTHING",
                (manifest["generated_batch_id"], manifest["reproducibility_checksum"]),
            )
    return results


def validate_database(conn: psycopg.Connection[Any]) -> dict[str, int]:
    """Return row counts for all raw tables after database-side constraint enforcement."""
    with conn.cursor() as cursor:
        counts: dict[str, int] = {}
        for name, table in TABLES.items():
            row = cursor.execute(
                sql.SQL("SELECT count(*) FROM raw.{table}").format(table=sql.Identifier(table))
            ).fetchone()
            if row is None:
                raise RuntimeError(f"Could not count raw.{table}")
            counts[name] = int(row[0])
        return counts


def run_validation(conn: psycopg.Connection[Any]) -> dict[str, int]:
    """Run all SQL validation checks and fail the CLI when any check has violations."""
    checks: dict[str, int] = {}
    with conn.cursor() as cursor:
        for statement in (
            (ROOT / "sql" / "validation" / "phase_02_validation.sql")
            .read_text(encoding="utf-8")
            .split(";")
        ):
            if statement.strip():
                row = cursor.execute(statement).fetchone()
                if row is None:
                    continue
                checks[str(row[0])] = int(row[1])
    if any(checks.values()):
        raise ValueError(f"Database validation failed: {checks}")
    return checks
