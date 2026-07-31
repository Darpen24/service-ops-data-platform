"""Generate deterministic, related service-management source datasets."""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from service_ops.generation.config import GenerationConfig

Record = dict[str, Any]
Dataset = dict[str, list[Record]]

PRIORITIES = ("P1", "P2", "P3", "P4")
STATUSES = ("new", "assigned", "in_progress", "resolved", "closed")
CHANNELS = ("portal", "email", "phone", "chat")


@dataclass(frozen=True, slots=True)
class GeneratedDataset:
    """Generated clean records plus separately stored intentional defects."""

    records: Dataset
    invalid_records: list[Record]
    generated_batch_id: str


def _reference_data() -> Dataset:
    """Return stable reference entities and their relationships."""
    teams = [
        {"team_id": "team-app", "team_name": "Application Support", "region": "DE"},
        {"team_id": "team-network", "team_name": "Network Operations", "region": "DE"},
        {"team_id": "team-workplace", "team_name": "Workplace Services", "region": "EU"},
        {"team_id": "team-identity", "team_name": "Identity Services", "region": "EU"},
    ]
    agents = [
        {
            "agent_id": f"agent-{index:03d}",
            "agent_name": f"Agent {index:03d}",
            "team_id": team["team_id"],
        }
        for index, team in enumerate(teams, start=1)
        for _ in range(3)
    ]
    # Re-number duplicate comprehension positions while retaining stable team membership.
    for index, agent in enumerate(agents, start=1):
        agent["agent_id"] = f"agent-{index:03d}"
        agent["agent_name"] = f"Agent {index:03d}"
    customers = [
        {
            "customer_id": "customer-fin",
            "customer_name": "Finance",
            "business_unit": "Finance",
            "region": "DE",
        },
        {
            "customer_id": "customer-ops",
            "customer_name": "Operations",
            "business_unit": "Operations",
            "region": "DE",
        },
        {
            "customer_id": "customer-sales",
            "customer_name": "Sales",
            "business_unit": "Sales",
            "region": "EU",
        },
        {
            "customer_id": "customer-rnd",
            "customer_name": "Research and Development",
            "business_unit": "R&D",
            "region": "EU",
        },
    ]
    categories = [
        {"category_id": "cat-access", "category_name": "Access"},
        {"category_id": "cat-hardware", "category_name": "Hardware"},
        {"category_id": "cat-network", "category_name": "Network"},
        {"category_id": "cat-application", "category_name": "Application"},
    ]
    subcategories = [
        {
            "subcategory_id": "sub-password",
            "subcategory_name": "Password reset",
            "category_id": "cat-access",
        },
        {
            "subcategory_id": "sub-vpn",
            "subcategory_name": "VPN access",
            "category_id": "cat-access",
        },
        {
            "subcategory_id": "sub-laptop",
            "subcategory_name": "Laptop issue",
            "category_id": "cat-hardware",
        },
        {
            "subcategory_id": "sub-printer",
            "subcategory_name": "Printer issue",
            "category_id": "cat-hardware",
        },
        {
            "subcategory_id": "sub-wifi",
            "subcategory_name": "Wi-Fi connectivity",
            "category_id": "cat-network",
        },
        {
            "subcategory_id": "sub-lan",
            "subcategory_name": "LAN connectivity",
            "category_id": "cat-network",
        },
        {
            "subcategory_id": "sub-erp",
            "subcategory_name": "ERP support",
            "category_id": "cat-application",
        },
        {
            "subcategory_id": "sub-collaboration",
            "subcategory_name": "Collaboration tools",
            "category_id": "cat-application",
        },
    ]
    sla_rules = [
        {"sla_rule_id": "sla-p1", "priority": "P1", "target_hours": 4},
        {"sla_rule_id": "sla-p2", "priority": "P2", "target_hours": 8},
        {"sla_rule_id": "sla-p3", "priority": "P3", "target_hours": 24},
        {"sla_rule_id": "sla-p4", "priority": "P4", "target_hours": 72},
    ]
    return {
        "teams": teams,
        "agents": agents,
        "customers": customers,
        "categories": categories,
        "subcategories": subcategories,
        "sla_rules": sla_rules,
    }


def _iso(value: datetime | None) -> str | None:
    return value.isoformat().replace("+00:00", "Z") if value else None


def _weighted_priority(rng: random.Random) -> str:
    return rng.choices(PRIORITIES, weights=(3, 12, 45, 40), k=1)[0]


def _ticket_created_at(config: GenerationConfig, rng: random.Random, ticket_index: int) -> datetime:
    span_days = (config.end_date - config.start_date).days + 1
    day_offset = (ticket_index * 7 + rng.randrange(span_days)) % span_days
    hour = rng.choices(range(24), weights=[1] * 7 + [3] * 10 + [1] * 7, k=1)[0]
    return datetime.combine(
        config.start_date + timedelta(days=day_offset), datetime.min.time(), UTC
    ) + timedelta(hours=hour, minutes=rng.randrange(60))


def _build_ticket(
    config: GenerationConfig,
    reference: Dataset,
    rng: random.Random,
    ticket_index: int,
    batch_id: str,
) -> Record:
    priority = _weighted_priority(rng)
    category = rng.choice(reference["categories"])
    subcategory = rng.choice(
        [row for row in reference["subcategories"] if row["category_id"] == category["category_id"]]
    )
    team = rng.choice(reference["teams"])
    agent = rng.choice([row for row in reference["agents"] if row["team_id"] == team["team_id"]])
    customer = rng.choice(reference["customers"])
    target_hours = next(
        row["target_hours"] for row in reference["sla_rules"] if row["priority"] == priority
    )
    created_at = _ticket_created_at(config, rng, ticket_index)
    first_response_minutes = rng.randint(5, max(10, target_hours * 35))
    first_response_at = created_at + timedelta(minutes=first_response_minutes)
    unresolved = rng.random() < 0.14
    resolution_minutes: int | None = None
    resolved_at: datetime | None = None
    closed_at: datetime | None = None
    status = rng.choices(("new", "assigned", "in_progress"), weights=(1, 2, 5), k=1)[0]
    if not unresolved:
        category_factor = {
            "cat-access": 0.65,
            "cat-hardware": 1.15,
            "cat-network": 1.4,
            "cat-application": 1.65,
        }[category["category_id"]]
        team_factor = {
            "team-app": 1.25,
            "team-network": 1.35,
            "team-workplace": 1.0,
            "team-identity": 0.85,
        }[team["team_id"]]
        priority_factor = {"P1": 0.35, "P2": 0.55, "P3": 1.0, "P4": 1.45}[priority]
        resolution_minutes = max(
            15,
            int(
                target_hours
                * 60
                * category_factor
                * team_factor
                * priority_factor
                * rng.uniform(0.6, 1.8)
            ),
        )
        resolved_at = created_at + timedelta(minutes=resolution_minutes)
        status = "closed" if rng.random() < 0.55 else "resolved"
        if status == "closed":
            closed_at = resolved_at + timedelta(hours=rng.randint(1, 48))
    reopened_count = 1 if resolved_at and rng.random() < 0.11 else 0
    escalation_count = 1 if priority in {"P1", "P2"} and rng.random() < 0.26 else 0
    breached = resolution_minutes is not None and resolution_minutes > target_hours * 60
    satisfaction = (
        None
        if unresolved
        else max(
            1,
            min(
                5,
                5
                - int(breached)
                - int(resolution_minutes > target_hours * 90)
                - reopened_count
                + rng.choice((0, 0, 1)),
            ),
        )
    )
    updated_at = (
        closed_at or resolved_at or (first_response_at + timedelta(hours=rng.randint(1, 48)))
    )
    return {
        "ticket_id": f"ticket-{ticket_index:06d}",
        "ticket_type": "incident" if rng.random() < 0.62 else "service_request",
        "created_at": _iso(created_at),
        "updated_at": _iso(updated_at),
        "first_response_at": _iso(first_response_at),
        "resolved_at": _iso(resolved_at),
        "closed_at": _iso(closed_at),
        "priority": priority,
        "impact": rng.choice(("low", "medium", "high")),
        "urgency": {"P1": "high", "P2": "high", "P3": "medium", "P4": "low"}[priority],
        "category_id": category["category_id"],
        "subcategory_id": subcategory["subcategory_id"],
        "assigned_team_id": team["team_id"],
        "assigned_agent_id": agent["agent_id"],
        "customer_id": customer["customer_id"],
        "business_unit": customer["business_unit"],
        "region": customer["region"],
        "channel": rng.choice(CHANNELS),
        "status": status,
        "sla_target_hours": target_hours,
        "first_response_minutes": first_response_minutes,
        "resolution_minutes": resolution_minutes,
        "reopened_count": reopened_count,
        "escalation_count": escalation_count,
        "satisfaction_score": satisfaction,
        "short_description": (
            f"{subcategory['subcategory_name']} reported by {customer['customer_name']}"
        ),
        "source_system": "service-ops-synthetic",
        "generated_batch_id": batch_id,
    }


def _status_history(tickets: list[Record]) -> list[Record]:
    """Create lifecycle events that mirror each ticket's valid timestamps."""
    events: list[Record] = []
    for ticket in tickets:
        event_time = ticket["created_at"]
        states = [
            ("new", event_time),
            ("assigned", ticket["first_response_at"]),
            ("in_progress", ticket["updated_at"]),
        ]
        if ticket["resolved_at"]:
            states.append(("resolved", ticket["resolved_at"]))
        if ticket["closed_at"]:
            states.append(("closed", ticket["closed_at"]))
        for sequence, (status, changed_at) in enumerate(states, start=1):
            events.append(
                {
                    "status_event_id": f"{ticket['ticket_id']}-event-{sequence}",
                    "ticket_id": ticket["ticket_id"],
                    "status": status,
                    "changed_at": changed_at,
                    "sequence": sequence,
                }
            )
    return events


def _inject_defects(records: Dataset, rng: random.Random, defect_rate: float) -> list[Record]:
    """Create explicit invalid ticket copies without corrupting clean output."""
    count = max(1, round(len(records["tickets"]) * defect_rate))
    invalid: list[Record] = []
    defect_kinds = (
        "missing_team",
        "invalid_priority",
        "reversed_timestamp",
        "duplicate_ticket_id",
        "unknown_category",
        "negative_duration",
    )
    for index, ticket in enumerate(records["tickets"][:count]):
        copy = dict(ticket)
        kind = defect_kinds[index % len(defect_kinds)]
        if kind == "missing_team":
            copy["assigned_team_id"] = None
        elif kind == "invalid_priority":
            copy["priority"] = "P0"
        elif kind == "reversed_timestamp":
            copy["resolved_at"] = "2023-12-31T00:00:00Z"
        elif kind == "duplicate_ticket_id":
            copy["ticket_id"] = records["tickets"][0]["ticket_id"]
        elif kind == "unknown_category":
            copy["category_id"] = "cat-unknown"
        else:
            copy["resolution_minutes"] = -1
        copy["defect_type"] = kind
        invalid.append(copy)
    rng.shuffle(invalid)
    return invalid


def generate_dataset(config: GenerationConfig) -> GeneratedDataset:
    """Generate clean related records and optional invalid examples deterministically."""
    rng = random.Random(config.seed)
    batch_id = (
        f"batch-{config.seed}-{config.start_date.isoformat()}-"
        f"{config.end_date.isoformat()}-{config.ticket_count}"
    )
    records = _reference_data()
    records["tickets"] = [
        _build_ticket(config, records, rng, index, batch_id)
        for index in range(1, config.ticket_count + 1)
    ]
    records["ticket_status_history"] = _status_history(records["tickets"])
    invalid_records = (
        _inject_defects(records, rng, config.defect_rate) if config.inject_defects else []
    )
    return GeneratedDataset(
        records=records, invalid_records=invalid_records, generated_batch_id=batch_id
    )
