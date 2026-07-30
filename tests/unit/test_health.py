"""Tests for the Phase 0 package boundary."""

from service_ops import foundation_status


def test_foundation_status() -> None:
    """The package exposes a deterministic smoke-test marker."""
    assert foundation_status() == "service-ops foundation ready"
