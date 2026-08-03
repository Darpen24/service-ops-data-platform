"""Unit tests for deterministic Phase 1 data generation."""

from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest

from service_ops.generation.config import GenerationConfig
from service_ops.generation.generator import generate_dataset
from service_ops.generation.io import record_checksum
from service_ops.generation.validation import validate_dataset


@pytest.fixture()
def config(tmp_path: Path) -> GenerationConfig:
    """Return a compact deterministic generation configuration."""
    return GenerationConfig(ticket_count=40, output_directory=tmp_path)


def test_generation_is_deterministic(config: GenerationConfig) -> None:
    """Equal configuration produces equal clean records and checksums."""
    first = generate_dataset(config).records
    second = generate_dataset(config).records
    assert first == second
    assert record_checksum(first) == record_checksum(second)


def test_different_seed_changes_checksum(config: GenerationConfig) -> None:
    """Changing the deterministic seed normally changes generated source records."""
    assert record_checksum(generate_dataset(config).records) != record_checksum(
        generate_dataset(replace(config, seed=99)).records
    )


def test_requested_record_count_and_clean_validation(config: GenerationConfig) -> None:
    """Clean output has requested ticket count and passes independent validation."""
    generated = generate_dataset(config)
    assert len(generated.records["tickets"]) == 40
    assert generated.invalid_records == []
    assert validate_dataset(generated.records)["overall_result"] == "pass"


def test_primary_and_foreign_key_relationships(config: GenerationConfig) -> None:
    """Tickets refer to valid teams, agents, customers, and category relationships."""
    records = generate_dataset(config).records
    tickets = records["tickets"]
    assert len({row["ticket_id"] for row in tickets}) == len(tickets)
    teams = {row["team_id"] for row in records["teams"]}
    agents = {row["agent_id"]: row["team_id"] for row in records["agents"]}
    categories = {row["subcategory_id"]: row["category_id"] for row in records["subcategories"]}
    assert all(ticket["assigned_team_id"] in teams for ticket in tickets)
    assert all(
        agents[ticket["assigned_agent_id"]] == ticket["assigned_team_id"] for ticket in tickets
    )
    assert all(categories[ticket["subcategory_id"]] == ticket["category_id"] for ticket in tickets)


def test_ticket_business_rules(config: GenerationConfig) -> None:
    """Clean tickets use accepted values, valid lifecycles, and expected null semantics."""
    tickets = generate_dataset(config).records["tickets"]
    assert {ticket["priority"] for ticket in tickets} <= {"P1", "P2", "P3", "P4"}
    assert {ticket["status"] for ticket in tickets} <= {
        "new",
        "assigned",
        "in_progress",
        "resolved",
        "closed",
    }
    assert all(ticket["sla_target_hours"] in {4, 8, 24, 72} for ticket in tickets)
    assert all(
        ticket["satisfaction_score"] is None or 1 <= ticket["satisfaction_score"] <= 5
        for ticket in tickets
    )
    assert all(
        ticket["resolved_at"] is not None or ticket["resolution_minutes"] is None
        for ticket in tickets
    )
    assert validate_dataset(generate_dataset(config).records)["overall_result"] == "pass"


def test_status_history_is_chronological_and_matches_ticket_status(
    config: GenerationConfig,
) -> None:
    """Every generated ticket has continuous lifecycle sequences and matching final status."""
    generated = generate_dataset(config).records
    tickets = {row["ticket_id"]: row for row in generated["tickets"]}
    history: dict[str, list[dict[str, object]]] = {}
    for event in generated["ticket_status_history"]:
        history.setdefault(str(event["ticket_id"]), []).append(event)
    for ticket_id, events in history.items():
        ordered = sorted(events, key=lambda event: int(event["sequence"]))
        assert [event["sequence"] for event in ordered] == list(range(1, len(ordered) + 1))
        assert [event["status"] for event in ordered][:3] == ["new", "assigned", "in_progress"]
        assert ordered[-1]["status"] == tickets[ticket_id]["status"]
        assert [event["changed_at"] for event in ordered] == sorted(
            event["changed_at"] for event in ordered
        )


def test_reordered_or_invalid_status_history_fails_validation(config: GenerationConfig) -> None:
    """Independent history validation rejects reordered timestamps and invalid transitions."""
    records = generate_dataset(config).records
    reordered = {name: [dict(row) for row in rows] for name, rows in records.items()}
    first_ticket_events = [
        event
        for event in reordered["ticket_status_history"]
        if event["ticket_id"] == "ticket-000001"
    ]
    first_ticket_events[1]["changed_at"], first_ticket_events[2]["changed_at"] = (
        first_ticket_events[2]["changed_at"],
        first_ticket_events[1]["changed_at"],
    )
    assert validate_dataset(reordered)["overall_result"] == "fail"
    invalid_transition = {name: [dict(row) for row in rows] for name, rows in records.items()}
    invalid_transition["ticket_status_history"][1]["status"] = "closed"
    assert validate_dataset(invalid_transition)["overall_result"] == "fail"


def test_explicit_defect_injection_is_separate(config: GenerationConfig) -> None:
    """Defects are absent by default and emitted separately only when enabled."""
    defective = generate_dataset(
        replace(config, ticket_count=120, inject_defects=True, defect_rate=0.05)
    )
    assert len(defective.invalid_records) == 6
    assert {row["defect_type"] for row in defective.invalid_records} == {
        "missing_team",
        "invalid_priority",
        "reversed_timestamp",
        "duplicate_ticket_id",
        "unknown_category",
        "negative_duration",
    }


def test_invalid_configuration(tmp_path: Path) -> None:
    """Invalid ranges, dates, formats, and defect settings are rejected."""
    with pytest.raises(ValueError):
        GenerationConfig(ticket_count=0, output_directory=tmp_path)
    with pytest.raises(ValueError):
        GenerationConfig(
            start_date=date(2024, 2, 1), end_date=date(2024, 1, 1), output_directory=tmp_path
        )
    with pytest.raises(ValueError):
        GenerationConfig(output_formats=("xml",), output_directory=tmp_path)
    with pytest.raises(ValueError):
        GenerationConfig(inject_defects=True, defect_rate=0, output_directory=tmp_path)
