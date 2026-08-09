"""Phase 2 integration tests; run with a disposable PostgreSQL service."""

import json
import os
import shutil
from pathlib import Path

import psycopg
import pytest

from service_ops import database
from service_ops.__main__ import main


@pytest.fixture()
def conn() -> psycopg.Connection[tuple[object, ...]]:
    """Create an isolated schema state and remove it after each test."""
    if os.getenv("POSTGRES_HOST") is None:
        pytest.skip("PostgreSQL integration environment is not configured")
    connection = database.connection()
    with connection.cursor() as cursor:
        cursor.execute((database.DDL / "999_reset.sql").read_text(encoding="utf-8"))
    connection.commit()
    database.initialise(connection)
    yield connection
    with connection.cursor() as cursor:
        cursor.execute((database.DDL / "999_reset.sql").read_text(encoding="utf-8"))
    connection.commit()
    connection.close()


def test_schema_load_idempotency_and_views(conn: psycopg.Connection[tuple[object, ...]]) -> None:
    """Schemas/views exist and the committed sample loads only once."""
    first = database.load_sample(conn)
    second = database.load_sample(conn)
    assert first["tickets"]["inserted"] == 25
    assert second["tickets"]["inserted"] == 0
    assert database.validate_database(conn)["ticket_status_history"] == 110
    with conn.cursor() as cursor:
        assert cursor.execute("SELECT count(*) FROM analytics.fct_tickets").fetchone() == (25,)
        assert (
            cursor.execute(
                "SELECT count(*) FROM analytics.fct_tickets "
                "WHERE status NOT IN ('resolved','closed')"
            ).fetchone()[0]
            >= 0
        )
        assert (
            cursor.execute(
                "SELECT count(*) FROM analytics.fct_ticket_status_events h "
                "JOIN raw.tickets t USING (ticket_id) "
                'WHERE h."sequence" = (SELECT max("sequence") FROM raw.ticket_status_history '
                "WHERE ticket_id = h.ticket_id) AND h.status = t.status"
            ).fetchone()[0]
            == 25
        )
        averages = cursor.execute(
            "SELECT avg(value), percentile_cont(0.5) WITHIN GROUP (ORDER BY value) "
            "FROM (VALUES (10::numeric), (20::numeric), (90::numeric)) AS fixture(value)"
        ).fetchone()
        assert averages == (pytest.approx(40), 20.0)


def test_constraints_and_validation(conn: psycopg.Connection[tuple[object, ...]]) -> None:
    """Keys and constraints reject invalid Phase 2 records; clean validation succeeds."""
    database.load_sample(conn)
    with pytest.raises(psycopg.errors.UniqueViolation):
        with conn.transaction():
            conn.execute(
                "INSERT INTO raw.teams(team_id,team_name,region) VALUES ('team-app','x','DE')"
            )
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        with conn.transaction():
            conn.execute(
                "INSERT INTO raw.agents(agent_id,agent_name,team_id) VALUES ('bad','bad','missing')"
            )
    with pytest.raises(psycopg.errors.CheckViolation):
        with conn.transaction():
            conn.execute("UPDATE raw.tickets SET priority='P0' WHERE ticket_id='ticket-000001'")
    with pytest.raises(psycopg.errors.CheckViolation):
        with conn.transaction():
            conn.execute(
                "UPDATE raw.tickets SET first_response_at = created_at - interval '1 minute' "
                "WHERE ticket_id = 'ticket-000001'"
            )
    assert all(value == 0 for value in database.run_validation(conn).values())


def test_validation_detects_cross_row_and_checksum_problems(
    conn: psycopg.Connection[tuple[object, ...]], tmp_path: Path
) -> None:
    """Cross-row mismatches and a corrupt manifest block a clean load/validation result."""
    database.load_sample(conn)
    conn.execute(
        "UPDATE raw.tickets AS t SET assigned_team_id = (SELECT team_id FROM raw.teams "
        "WHERE team_id <> t.assigned_team_id LIMIT 1) WHERE ticket_id = 'ticket-000001'"
    )
    with pytest.raises(ValueError, match="agent_team_mismatch"):
        database.run_validation(conn)
    conn.rollback()

    copied = tmp_path / "phase-01"
    shutil.copytree(database.SAMPLE, copied)
    manifest_path = copied / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["reproducibility_checksum"] = "not-the-real-checksum"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="checksum"):
        database.load_sample(conn, copied)


def test_reset_is_protected() -> None:
    """The destructive CLI reset requires an explicit acknowledgement."""
    assert main(["database", "reset"]) == 2
