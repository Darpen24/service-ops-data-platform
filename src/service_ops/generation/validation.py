"""Independent validation rules for generated service-operations records."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Any

from service_ops.generation.generator import PRIORITIES, STATUSES, Dataset

Record = dict[str, Any]


def _parse_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else None


def _summary(name: str, rows: list[Record], primary_key: str) -> dict[str, Any]:
    values = [row.get(primary_key) for row in rows]
    duplicate_count = sum(count - 1 for count in Counter(values).values() if count > 1)
    null_counts = (
        {key: sum(row.get(key) is None for row in rows) for key in rows[0]} if rows else {}
    )
    return {
        "dataset_name": name,
        "record_count": len(rows),
        "duplicate_count": duplicate_count,
        "null_counts": null_counts,
        "invalid_value_count": 0,
        "timestamp_failures": 0,
        "referential_integrity_failures": 0,
    }


def validate_dataset(records: Dataset) -> dict[str, Any]:
    """Validate relationships, allowed values, lifecycle timestamps, and ranges."""
    summaries = {
        "teams": _summary("teams", records["teams"], "team_id"),
        "agents": _summary("agents", records["agents"], "agent_id"),
        "customers": _summary("customers", records["customers"], "customer_id"),
        "categories": _summary("categories", records["categories"], "category_id"),
        "subcategories": _summary("subcategories", records["subcategories"], "subcategory_id"),
        "sla_rules": _summary("sla_rules", records["sla_rules"], "sla_rule_id"),
        "tickets": _summary("tickets", records["tickets"], "ticket_id"),
        "ticket_status_history": _summary(
            "ticket_status_history", records["ticket_status_history"], "status_event_id"
        ),
    }
    team_ids = {row["team_id"] for row in records["teams"]}
    agent_teams = {row["agent_id"]: row["team_id"] for row in records["agents"]}
    category_ids = {row["category_id"] for row in records["categories"]}
    subcategory_categories = {
        row["subcategory_id"]: row["category_id"] for row in records["subcategories"]
    }
    customer_ids = {row["customer_id"] for row in records["customers"]}
    sla_targets = {row["priority"]: row["target_hours"] for row in records["sla_rules"]}
    ticket_ids = {row["ticket_id"] for row in records["tickets"]}

    for agent in records["agents"]:
        if agent["team_id"] not in team_ids:
            summaries["agents"]["referential_integrity_failures"] += 1
    for subcategory in records["subcategories"]:
        if subcategory["category_id"] not in category_ids:
            summaries["subcategories"]["referential_integrity_failures"] += 1
    for ticket in records["tickets"]:
        ticket_summary = summaries["tickets"]
        if ticket.get("priority") not in PRIORITIES or ticket.get("status") not in STATUSES:
            ticket_summary["invalid_value_count"] += 1
        if ticket.get("sla_target_hours") != sla_targets.get(ticket.get("priority")):
            ticket_summary["invalid_value_count"] += 1
        satisfaction = ticket.get("satisfaction_score")
        if satisfaction is not None and (
            not isinstance(satisfaction, int) or not 1 <= satisfaction <= 5
        ):
            ticket_summary["invalid_value_count"] += 1
        references_valid = (
            ticket.get("assigned_team_id") in team_ids
            and agent_teams.get(ticket.get("assigned_agent_id")) == ticket.get("assigned_team_id")
            and ticket.get("customer_id") in customer_ids
            and subcategory_categories.get(ticket.get("subcategory_id"))
            == ticket.get("category_id")
        )
        if not references_valid:
            ticket_summary["referential_integrity_failures"] += 1
        created = _parse_timestamp(ticket.get("created_at"))
        response = _parse_timestamp(ticket.get("first_response_at"))
        updated = _parse_timestamp(ticket.get("updated_at"))
        resolved = (
            _parse_timestamp(ticket.get("resolved_at")) if ticket.get("resolved_at") else None
        )
        closed = _parse_timestamp(ticket.get("closed_at")) if ticket.get("closed_at") else None
        valid_lifecycle = False
        if created is not None and response is not None and updated is not None:
            valid_lifecycle = created <= response <= updated
        if resolved is not None and created is not None:
            valid_lifecycle = valid_lifecycle and created <= resolved <= (closed or resolved)
        if closed:
            valid_lifecycle = valid_lifecycle and resolved is not None and resolved <= closed
        if ticket.get("resolution_minutes") is not None and int(ticket["resolution_minutes"]) < 0:
            valid_lifecycle = False
        if not valid_lifecycle:
            ticket_summary["timestamp_failures"] += 1
    for event in records["ticket_status_history"]:
        event_summary = summaries["ticket_status_history"]
        if event.get("ticket_id") not in ticket_ids:
            event_summary["referential_integrity_failures"] += 1
        if event.get("status") not in STATUSES or _parse_timestamp(event.get("changed_at")) is None:
            event_summary["invalid_value_count"] += 1
    overall_result = all(
        summary[metric] == 0
        for summary in summaries.values()
        for metric in (
            "duplicate_count",
            "invalid_value_count",
            "timestamp_failures",
            "referential_integrity_failures",
        )
    )
    return {"datasets": summaries, "overall_result": "pass" if overall_result else "fail"}
