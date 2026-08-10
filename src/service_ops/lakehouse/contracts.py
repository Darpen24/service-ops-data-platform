"""Pure-Python contracts shared by optional Spark Bronze, Silver, and Gold jobs."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def bronze_record(record: dict[str, Any], batch_id: str) -> dict[str, Any]:
    """Preserve source values while adding ingestion metadata for Bronze."""
    return {**record, "_batch_id": batch_id, "_source_format": "parquet"}


def silver_ticket(record: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    """Standardise a ticket or return a quarantine reason before writing Silver."""
    if not record.get("ticket_id"):
        return None, "required_ticket_id"
    created_at = record.get("created_at")
    updated_at = record.get("updated_at")
    if not isinstance(created_at, datetime) or not isinstance(updated_at, datetime):
        return None, "required_timestamp"
    if updated_at < created_at:
        return None, "ticket_timestamp_order"
    return {**record, "priority": str(record["priority"]).upper()}, None


def gold_priority_metrics(records: list[dict[str, Any]]) -> list[dict[str, object]]:
    """Return one Gold metric row per priority, matching PostgreSQL SLA semantics."""
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        grouped.setdefault(str(record["priority"]), []).append(record)
    return [
        {
            "priority": priority,
            "ticket_count": len(items),
            "breached_ticket_count": sum(
                int(
                    item.get("resolution_minutes") is not None
                    and item["resolution_minutes"] > item["sla_target_hours"] * 60
                )
                for item in items
            ),
        }
        for priority, items in sorted(grouped.items())
    ]


def deduplicate_ticket_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep the deterministic latest version of each ticket for Silver MERGE input."""
    latest: dict[str, dict[str, Any]] = {}
    for record in records:
        ticket_id = str(record["ticket_id"])
        if ticket_id not in latest or record["updated_at"] > latest[ticket_id]["updated_at"]:
            latest[ticket_id] = record
    return [latest[key] for key in sorted(latest)]
