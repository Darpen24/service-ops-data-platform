"""Small, explicit Phase 3 ELT ingestion with audit, watermark, and quarantine handling."""

from __future__ import annotations

import hashlib
import json
import logging
from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any, cast
from uuid import UUID, uuid4

import psycopg
from psycopg.types.json import Jsonb

from service_ops.generation.generator import Dataset

LOGGER = logging.getLogger(__name__)
SOURCE_NAME = "phase-01-parquet"
TICKET_TIMESTAMP_FIELDS = (
    "created_at",
    "updated_at",
    "first_response_at",
    "in_progress_at",
    "resolved_at",
    "closed_at",
)


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
        json.dumps(record, sort_keys=True, separators=(",", ":"), default=_json_default).encode()
    ).hexdigest()


def _json_default(value: object) -> str:
    if isinstance(value, datetime):
        return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
    return str(value)


def _json_payload(record: dict[str, Any]) -> dict[str, Any]:
    """Make timestamps and other typed Parquet values safe for JSONB audit storage."""
    return cast(dict[str, Any], json.loads(json.dumps(record, default=_json_default)))


def parse_timestamp(value: object, field_name: str, *, nullable: bool = False) -> datetime | None:
    """Return a UTC-aware timestamp from the Phase 1 ISO contract or a datetime input."""
    if value is None:
        if nullable:
            return None
        raise ValueError(f"{field_name} is required")
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as error:
            raise ValueError(f"{field_name} must be an ISO-8601 timestamp") from error
    else:
        raise ValueError(f"{field_name} must be a timestamp string or datetime")
    if parsed.tzinfo is None:
        raise ValueError(f"{field_name} must include a timezone")
    return parsed.astimezone(UTC)


def normalise_pipeline_records(records: Dataset) -> Dataset:
    """Return a copied pipeline input with all lifecycle timestamps as UTC datetimes."""
    normalised = deepcopy(records)
    for ticket in normalised["tickets"]:
        for field_name in TICKET_TIMESTAMP_FIELDS:
            ticket[field_name] = parse_timestamp(
                ticket.get(field_name),
                field_name,
                nullable=field_name in {"resolved_at", "closed_at"},
            )
    for event in normalised["ticket_status_history"]:
        event["changed_at"] = parse_timestamp(event.get("changed_at"), "changed_at")
    return normalised


def _normalise_ticket(ticket: dict[str, Any]) -> dict[str, Any]:
    """Normalise one ticket so bad source values can be quarantined independently."""
    normalised = deepcopy(ticket)
    for field_name in TICKET_TIMESTAMP_FIELDS:
        normalised[field_name] = parse_timestamp(
            normalised.get(field_name),
            field_name,
            nullable=field_name in {"resolved_at", "closed_at"},
        )
    return normalised


def _ticket_error(ticket: dict[str, Any]) -> tuple[str, str] | None:
    if not ticket.get("ticket_id"):
        return "required_ticket_id", "ticket_id is required"
    created_at = ticket.get("created_at")
    updated_at = ticket.get("updated_at")
    if not isinstance(created_at, datetime) or not isinstance(updated_at, datetime):
        return "required_timestamp", "created_at and updated_at must be UTC-aware datetimes"
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
    for source_ticket in records["tickets"]:
        issue: tuple[str, str] | None
        try:
            ticket = _normalise_ticket(source_ticket)
            issue = _ticket_error(ticket)
        except ValueError as error:
            ticket = source_ticket
            issue = "invalid_timestamp", str(error)
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
