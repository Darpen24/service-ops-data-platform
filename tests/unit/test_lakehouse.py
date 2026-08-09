from datetime import UTC, datetime, timedelta

from service_ops.lakehouse.contracts import deduplicate_ticket_records, silver_ticket


def test_silver_quarantines_invalid_and_deduplicates_latest() -> None:
    created = datetime(2024, 1, 1, tzinfo=UTC)
    invalid, reason = silver_ticket(
        {"ticket_id": "x", "created_at": created, "updated_at": created - timedelta(minutes=1)}
    )
    assert invalid is None
    assert reason == "ticket_timestamp_order"
    records = [
        {"ticket_id": "x", "updated_at": created},
        {"ticket_id": "x", "updated_at": created + timedelta(minutes=1)},
    ]
    assert deduplicate_ticket_records(records) == [records[1]]
