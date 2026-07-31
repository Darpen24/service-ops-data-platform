"""Configuration for deterministic source-data generation."""

from dataclasses import dataclass
from datetime import date
from pathlib import Path

DEFAULT_FORMATS: tuple[str, ...] = ("json", "csv", "parquet")
SUPPORTED_FORMATS = frozenset(DEFAULT_FORMATS)


@dataclass(frozen=True, slots=True)
class GenerationConfig:
    """Validated inputs that fully describe a generation run."""

    seed: int = 42
    ticket_count: int = 100
    start_date: date = date(2024, 1, 1)
    end_date: date = date(2024, 3, 31)
    output_directory: Path = Path("data/raw/generated")
    output_formats: tuple[str, ...] = DEFAULT_FORMATS
    defect_rate: float = 0.0
    inject_defects: bool = False

    def __post_init__(self) -> None:
        """Reject invalid run configuration before any output is written."""
        if self.ticket_count <= 0:
            raise ValueError("ticket_count must be positive")
        if self.end_date < self.start_date:
            raise ValueError("end_date must not precede start_date")
        if not self.output_formats or not set(self.output_formats) <= SUPPORTED_FORMATS:
            raise ValueError(f"output_formats must be drawn from {sorted(SUPPORTED_FORMATS)}")
        if not 0.0 <= self.defect_rate <= 1.0:
            raise ValueError("defect_rate must be between 0 and 1")
        if self.inject_defects and self.defect_rate == 0.0:
            raise ValueError("defect_rate must be greater than zero when inject_defects is enabled")
