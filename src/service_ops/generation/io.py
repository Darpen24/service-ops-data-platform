"""Read and write JSON, CSV, and Snappy-compressed Parquet datasets."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import pyarrow as pa  # type: ignore[import-untyped]
import pyarrow.parquet as pq  # type: ignore[import-untyped]

from service_ops.generation.config import GenerationConfig
from service_ops.generation.generator import Dataset, GeneratedDataset

Record = dict[str, Any]
REQUIRED_DATASETS = (
    "teams",
    "agents",
    "customers",
    "categories",
    "subcategories",
    "sla_rules",
    "tickets",
    "ticket_status_history",
)


def _normalise(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _write_json(path: Path, rows: list[Record]) -> None:
    path.write_text(json.dumps(rows, indent=2, sort_keys=True), encoding="utf-8")


def _write_csv(path: Path, rows: list[Record]) -> None:
    fieldnames = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{key: _normalise(value) for key, value in row.items()} for row in rows])


def _write_parquet(path: Path, rows: list[Record]) -> None:
    pq.write_table(pa.Table.from_pylist(rows), path, compression="snappy")


def record_checksum(records: Dataset) -> str:
    """Return a stable SHA-256 indicator for generated clean records."""
    canonical = json.dumps(records, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def write_dataset(dataset: GeneratedDataset, config: GenerationConfig) -> dict[str, Any]:
    """Write generated data and manifest, returning the manifest payload."""
    output = config.output_directory
    output.mkdir(parents=True, exist_ok=True)
    filenames: dict[str, dict[str, str]] = {}
    for dataset_name, rows in dataset.records.items():
        filenames[dataset_name] = {}
        for output_format in config.output_formats:
            path = output / f"{dataset_name}.{output_format}"
            if output_format == "json":
                _write_json(path, rows)
            elif output_format == "csv":
                _write_csv(path, rows)
            else:
                _write_parquet(path, rows)
            filenames[dataset_name][output_format] = path.name
    if dataset.invalid_records:
        _write_json(output / "invalid_tickets.json", dataset.invalid_records)
    manifest = {
        "schema_version": "1.0",
        "random_seed": config.seed,
        "generation_timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "generated_batch_id": dataset.generated_batch_id,
        "record_counts": {name: len(rows) for name, rows in dataset.records.items()},
        "invalid_record_count": len(dataset.invalid_records),
        "date_range": {"start": config.start_date.isoformat(), "end": config.end_date.isoformat()},
        "output_filenames": filenames,
        "reproducibility_checksum": record_checksum(dataset.records),
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )
    return manifest


def read_rows(path: Path) -> list[Record]:
    """Read a supported generated file back to a list of records."""
    if path.suffix == ".json":
        return cast(list[Record], json.loads(path.read_text(encoding="utf-8")))
    if path.suffix == ".csv":
        with path.open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))
    if path.suffix == ".parquet":
        return cast(list[Record], pq.read_table(path).to_pylist())
    raise ValueError(f"Unsupported generated file: {path}")


def read_committed_sample(directory: Path) -> tuple[Dataset, dict[str, Any]]:
    """Read and verify the committed typed Parquet sample and its manifest."""
    manifest_path = directory / "manifest.json"
    if not manifest_path.is_file():
        raise ValueError(f"Missing sample manifest: {manifest_path}")
    manifest = cast(dict[str, Any], json.loads(manifest_path.read_text(encoding="utf-8")))
    records: Dataset = {}
    for name in REQUIRED_DATASETS:
        path = directory / f"{name}.parquet"
        if not path.is_file():
            raise ValueError(f"Missing sample dataset: {path}")
        records[name] = read_rows(path)
    record_counts = manifest.get("record_counts")
    if not isinstance(record_counts, dict) or any(
        record_counts.get(name) != len(records[name]) for name in REQUIRED_DATASETS
    ):
        raise ValueError("Sample manifest record counts do not match Parquet files")
    if manifest.get("reproducibility_checksum") != record_checksum(records):
        raise ValueError("Sample manifest reproducibility checksum does not match Parquet files")
    return records, manifest
