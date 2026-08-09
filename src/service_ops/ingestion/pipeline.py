"""Small, explicit Phase 3 ELT ingestion with audit, watermark, and quarantine handling."""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, cast
from uuid import UUID, uuid4

import psycopg
from psycopg.types.json import Jsonb

from service_ops.generation.generator import Dataset

LOGGER = logging.getLogger(__name__)
SOURCE_NAME = "phase-01-parquet"


@dataclass(frozen=True)
class PipelineResult:
    """Observable outcome of one source batch."""

    run_id: UUID
    batch_id: str
    status: str
    inserted_count: int
    updated_count: int
    quarantined_count: int
    watermark_before: datetime | None
    watermark_after: datetime | None

    def as_dict(self) -> dict[str, object]:
        """Return JSON-safe structured command output."""
        return asdict(self)


def _checksum(record: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(record, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def _json_payload(record: dict[str, Any]) -> dict[str, Any]:
    """Make timestamps and other typed Parquet values safe for JSONB audit storage."""
    return cast(dict[str, Any], json.loads(json.dumps(record, default=str)))


def _ticket_error(ticket: dict[str, Any]) -> tuple[str, str] | None:
    if not ticket.get("ticket_id"):
        return "required_ticket_id", "ticket_id is required"
    created_at = ticket.get("created_at")
    updated_at = ticket.get("updated_at")
    if created_at is None or updated_at is None:
        return "required_timestamp", "created_at and updated_at are required"
    if updated_at < created_at:
        return "ticket_timestamp_order", "updated_at is earlier than created_at"
    return None


def _watermark(conn: psycopg.Connection[Any], source_name: str) -> datetime | None:
    row = conn.execute(
        "SELECT watermark_at FROM audit.pipeline_watermarks WHERE source_name = %s", (source_name,)
    ).fetchone()
    return None if row is None else row[0]


def _record_run_start(
    conn: psycopg.Connection[Any],
    run_id: UUID,
    batch_id: str,
    checksum: str,
    watermark: datetime | None,
) -> None:
    conn.execute(
        "INSERT INTO audit.pipeline_runs(run_id, source_name, batch_id, source_checksum, status, "
        "watermark_before) VALUES (%s, %s, %s, %s, 'running', %s)",
        (run_id, SOURCE_NAME, batch_id, checksum, watermark),
    )
    conn.commit()


def run_records(
    conn: psycopg.Connection[Any], records: Dataset, batch_id: str, source_checksum: str
) -> PipelineResult:
    """Stage valid tickets, quarantine invalid records, and advance the watermark atomically."""
    run_id = uuid4()
    watermark_before = _watermark(conn, SOURCE_NAME)
    _record_run_start(conn, run_id, batch_id, source_checksum, watermark_before)
    quarantined = 0
    valid_tickets: list[dict[str, Any]] = []
    for ticket in records["tickets"]:
        issue = _ticket_error(ticket)
        if issue is None:
            valid_tickets.append(ticket)
            continue
        rule, reason = issue
        conn.execute(
            "INSERT INTO audit.quarantine_records("
            "run_id, source_name, batch_id, record_identifier, rule_name, reason, raw_payload"
            ") VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (
                run_id,
                SOURCE_NAME,
                batch_id,
                ticket.get("ticket_id"),
                rule,
                reason,
                Jsonb(_json_payload(ticket)),
            ),
        )
        quarantined += 1
    conn.commit()

    try:
        with conn.transaction():
            inserted = 0
            updated = 0
            watermark_after = watermark_before
            for ticket in valid_tickets:
                updated_at = ticket["updated_at"]
                if watermark_before is not None and updated_at <= watermark_before:
                    continue
                record_checksum = _checksum(ticket)
                existing = conn.execute(
                    "SELECT record_checksum FROM staging.ticket_ingest WHERE batch_id = %s "
                    "AND ticket_id = %s",
                    (batch_id, ticket["ticket_id"]),
                ).fetchone()
                conn.execute(
                    "INSERT INTO staging.ticket_ingest("
                    "batch_id, ticket_id, source_updated_at, record_checksum, payload"
                    ") VALUES (%s, %s, %s, %s, %s) "
                    "ON CONFLICT (batch_id, ticket_id) DO UPDATE SET "
                    "source_updated_at = EXCLUDED.source_updated_at, "
                    "record_checksum = EXCLUDED.record_checksum, payload = EXCLUDED.payload "
                    "WHERE staging.ticket_ingest.record_checksum <> EXCLUDED.record_checksum",
                    (
                        batch_id,
                        ticket["ticket_id"],
                        updated_at,
                        record_checksum,
                        Jsonb(_json_payload(ticket)),
                    ),
                )
                if existing is None:
                    inserted += 1
                elif existing[0] != record_checksum:
                    updated += 1
                watermark_after = max(filter(None, (watermark_after, updated_at)))
            if watermark_after is not None:
                conn.execute(
                    "INSERT INTO audit.pipeline_watermarks(source_name, watermark_at) "
                    "VALUES (%s, %s) ON CONFLICT (source_name) DO UPDATE SET "
                    "watermark_at = EXCLUDED.watermark_at, "
                    "updated_at = now()",
                    (SOURCE_NAME, watermark_after),
                )
            status = "partial" if quarantined else "succeeded"
            conn.execute(
                "UPDATE audit.pipeline_runs SET status = %s, inserted_count = %s, "
                "updated_count = %s, quarantined_count = %s, watermark_after = %s, "
                "finished_at = now() WHERE run_id = %s",
                (status, inserted, updated, quarantined, watermark_after, run_id),
            )
        LOGGER.info("pipeline_run_completed run_id=%s status=%s", run_id, status)
        return PipelineResult(
            run_id,
            batch_id,
            status,
            inserted,
            updated,
            quarantined,
            watermark_before,
            watermark_after,
        )
    except psycopg.Error as error:
        conn.rollback()
        conn.execute(
            "UPDATE audit.pipeline_runs SET status = 'failed', error_message = %s, "
            "finished_at = now() WHERE run_id = %s",
            (str(error), run_id),
        )
        conn.commit()
        raise


def status(conn: psycopg.Connection[Any]) -> list[dict[str, object]]:
    """Return recent pipeline runs for operational inspection."""
    rows = conn.execute(
        "SELECT run_id, batch_id, status, inserted_count, updated_count, quarantined_count, "
        "watermark_before, watermark_after FROM audit.pipeline_runs "
        "ORDER BY started_at DESC LIMIT 20"
    ).fetchall()
    fields = (
        "run_id",
        "batch_id",
        "status",
        "inserted_count",
        "updated_count",
        "quarantined_count",
        "watermark_before",
        "watermark_after",
    )
    return [dict(zip(fields, row, strict=True)) for row in rows]
