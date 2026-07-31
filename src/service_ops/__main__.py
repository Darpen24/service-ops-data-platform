"""Command-line interface for the Service Operations Data Platform."""

from __future__ import annotations

import argparse
import json
import logging
from collections.abc import Sequence
from datetime import date
from pathlib import Path

from service_ops.generation.config import DEFAULT_FORMATS, GenerationConfig
from service_ops.generation.generator import generate_dataset
from service_ops.generation.io import write_dataset
from service_ops.generation.validation import validate_dataset


def _date_argument(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("dates must use YYYY-MM-DD") from error


def _config_from_args(args: argparse.Namespace) -> GenerationConfig:
    return GenerationConfig(
        seed=args.seed,
        ticket_count=args.count,
        start_date=args.start_date,
        end_date=args.end_date,
        output_directory=args.output_directory,
        output_formats=tuple(args.formats.split(",")),
        defect_rate=args.defect_rate,
        inject_defects=args.inject_defects,
    )


def _generate(args: argparse.Namespace) -> int:
    config = _config_from_args(args)
    dataset = generate_dataset(config)
    summary = validate_dataset(dataset.records)
    if summary["overall_result"] != "pass":
        logging.error("generation_validation_failed")
        return 1
    manifest = write_dataset(dataset, config)
    logging.info(
        "generation_complete tickets=%s output=%s", config.ticket_count, config.output_directory
    )
    print(json.dumps({"manifest": manifest, "validation": summary}, indent=2, sort_keys=True))
    return 0


def _validate_sample(_: argparse.Namespace) -> int:
    config = GenerationConfig(ticket_count=25, output_directory=Path("data/sample/phase-01"))
    dataset = generate_dataset(config)
    summary = validate_dataset(dataset.records)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["overall_result"] == "pass" else 1


def build_parser() -> argparse.ArgumentParser:
    """Build the Phase 1 CLI argument parser."""
    parser = argparse.ArgumentParser(prog="python -m service_ops")
    parser.add_argument(
        "--log-level", default="INFO", choices=("DEBUG", "INFO", "WARNING", "ERROR")
    )
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("generate", help="generate source datasets")
    generate.add_argument("--count", type=int, default=100)
    generate.add_argument("--seed", type=int, default=42)
    generate.add_argument("--start-date", type=_date_argument, default=date(2024, 1, 1))
    generate.add_argument("--end-date", type=_date_argument, default=date(2024, 3, 31))
    generate.add_argument("--output-directory", type=Path, default=Path("data/raw/generated"))
    generate.add_argument("--formats", default=",".join(DEFAULT_FORMATS))
    generate.add_argument("--inject-defects", action="store_true")
    generate.add_argument("--defect-rate", type=float, default=0.05)
    generate.set_defaults(handler=_generate)
    validate = commands.add_parser(
        "validate-sample", help="validate the deterministic sample configuration"
    )
    validate.set_defaults(handler=_validate_sample)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run a Phase 1 command and return a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(level=args.log_level, format="%(levelname)s %(message)s")
    try:
        return int(args.handler(args))
    except (OSError, ValueError) as error:
        logging.error("command_failed error=%s", error)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
