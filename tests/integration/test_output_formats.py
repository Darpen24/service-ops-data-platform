"""Integration tests for generated JSON, CSV, Parquet, and manifest outputs."""

import json
from pathlib import Path

import pytest

from service_ops.generation.config import GenerationConfig
from service_ops.generation.generator import generate_dataset
from service_ops.generation.io import (
    read_committed_sample,
    read_rows,
    record_checksum,
    write_dataset,
)


def test_complete_small_dataset_round_trip(tmp_path: Path) -> None:
    """All formats round-trip and share schema and record counts for every dataset."""
    config = GenerationConfig(ticket_count=12, output_directory=tmp_path)
    generated = generate_dataset(config)
    manifest = write_dataset(generated, config)
    assert manifest["record_counts"]["tickets"] == 12
    assert manifest["reproducibility_checksum"] == record_checksum(generated.records)
    assert (tmp_path / "manifest.json").exists()
    for name, original_rows in generated.records.items():
        json_rows = read_rows(tmp_path / f"{name}.json")
        csv_rows = read_rows(tmp_path / f"{name}.csv")
        parquet_rows = read_rows(tmp_path / f"{name}.parquet")
        assert len(json_rows) == len(csv_rows) == len(parquet_rows) == len(original_rows)
        assert (
            set(json_rows[0]) == set(csv_rows[0]) == set(parquet_rows[0]) == set(original_rows[0])
        )
        assert json_rows == original_rows
        assert parquet_rows == original_rows


def test_defect_records_are_written_separately(tmp_path: Path) -> None:
    """Defect mode never replaces clean tickets and writes invalid examples separately."""
    config = GenerationConfig(
        ticket_count=20, output_directory=tmp_path, inject_defects=True, defect_rate=0.1
    )
    generated = generate_dataset(config)
    write_dataset(generated, config)
    invalid = json.loads((tmp_path / "invalid_tickets.json").read_text(encoding="utf-8"))
    assert len(invalid) == 2
    assert len(read_rows(tmp_path / "tickets.json")) == 20


def test_committed_sample_reader_detects_manifest_corruption(tmp_path: Path) -> None:
    """Typed sample validation reads files rather than regenerating source data."""
    config = GenerationConfig(ticket_count=8, output_directory=tmp_path)
    generated = generate_dataset(config)
    write_dataset(generated, config)
    records, manifest = read_committed_sample(tmp_path)
    assert records == generated.records
    assert manifest["reproducibility_checksum"] == record_checksum(records)
    manifest["record_counts"]["tickets"] = 999
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="record counts"):
        read_committed_sample(tmp_path)
