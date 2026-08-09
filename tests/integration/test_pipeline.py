"""Phase 3 pipeline integration tests against disposable PostgreSQL schemas."""

from __future__ import annotations

import os
from copy import deepcopy
from datetime import timedelta

import psycopg
import pytest

from service_ops import database
from service_ops.generation.io import read_committed_sample
from service_ops.ingestion import pipeline


@pytest.fixture()
def conn() -> psycopg.Connection[tuple[object, ...]]:
    """Provide a reset local schema only when integration configuration exists."""
    if not os.getenv("POSTGRES_HOST"):
        pytest.skip("PostgreSQL integration environment is not configured")
    connection = database.connection()
    connection.execute((database.DDL / "999_reset.sql").read_text(encoding="utf-8"))
    connection.commit()
    database.initialise(connection)
    yield connection
    connection.execute((database.DDL / "999_reset.sql").read_text(encoding="utf-8"))
    connection.commit()
    connection.close()


def test_pipeline_is_idempotent_and_tracks_watermark(
    conn: psycopg.Connection[tuple[object, ...]],
) -> None:
    """A repeated batch has no staged duplicates and does not advance the watermark."""
    records, manifest = read_committed_sample(database.SAMPLE)
    first = pipeline.run_records(
        conn, records, "pipeline-test", manifest["reproducibility_checksum"]
    )
    second = pipeline.run_records(
        conn, records, "pipeline-test", manifest["reproducibility_checksum"]
    )
    assert first.status == "succeeded"
    assert first.inserted_count == 25
    assert second.inserted_count == 0
    assert second.watermark_after == first.watermark_after
    assert conn.execute("SELECT count(*) FROM staging.ticket_ingest").fetchone() == (25,)


def test_invalid_record_is_quarantined_and_late_record_is_updated(
    conn: psycopg.Connection[tuple[object, ...]],
) -> None:
    """Bad timestamps are quarantined while a corrected late ticket is accepted later."""
    records, manifest = read_committed_sample(database.SAMPLE)
    invalid = deepcopy(records)
    invalid["tickets"][0]["updated_at"] = invalid["tickets"][0]["created_at"] - timedelta(minutes=1)
    partial = pipeline.run_records(
        conn, invalid, "pipeline-invalid", manifest["reproducibility_checksum"]
    )
    assert partial.status == "partial"
    assert partial.quarantined_count == 1
    assert conn.execute("SELECT count(*) FROM audit.quarantine_records").fetchone() == (1,)

    late = deepcopy(records)
    late["tickets"][0]["updated_at"] = records["tickets"][0]["updated_at"] + timedelta(days=1)
    corrected = pipeline.run_records(
        conn, late, "pipeline-late", manifest["reproducibility_checksum"]
    )
    assert corrected.watermark_after is not None
    assert corrected.inserted_count >= 1
