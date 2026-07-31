"""Deterministic synthetic source-data generation for Phase 1."""

from service_ops.generation.config import GenerationConfig
from service_ops.generation.generator import generate_dataset
from service_ops.generation.validation import validate_dataset

__all__ = ["GenerationConfig", "generate_dataset", "validate_dataset"]
