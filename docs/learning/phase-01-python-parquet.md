# Phase 01: Python synthetic data and Parquet

Synthetic data lets this portfolio demonstrate operational behaviour without using employer data. `GenerationConfig` makes a seed, date range, count, formats, output path, and explicit defect rate the complete input to a run. A local `random.Random(seed)` avoids global mutable state, so the same configuration recreates the same clean records and checksum.

The generator is divided by responsibility: `config` validates inputs; `generator` creates related entities and lifecycles; `io` serialises JSON, CSV, and Snappy-compressed Parquet plus the manifest; `validation` independently checks duplicates, nulls, values, timestamp ordering, and foreign keys. Public functions have type hints and the CLI uses `argparse`. UTC-aware ISO timestamps prevent ambiguity around local time and daylight-saving transitions.

The ticket lifecycle records an explicit `in_progress_at` timestamp. History is therefore chronological (`new → assigned → in_progress → resolved → closed` where applicable) rather than using `updated_at`, which may represent final resolution or closure. The validator groups history by ticket and checks unique event IDs, continuous sequences, transition order, non-decreasing timestamps, final status alignment, and the absence of events after closure. `validate-sample` reads the committed Parquet files and manifest, verifies their counts and checksum, then validates the actual stored records.

JSON preserves nested-friendly typed records and is readable; CSV is universally portable but strings values on read; Parquet is column-oriented, typed, compressed, and suited to analytical scans. Row-oriented JSON/CSV are convenient source interchange, whereas Parquet avoids reading unused columns and is the planned local columnar interchange. The manifest records schema version, counts, names, range, seed, and a reproducibility checksum. Large generated files are ignored because they are reproducible outputs; the 25-ticket sample is intentionally small enough to review.

This is a portfolio simplification: names, categories, and probabilities are compact; a production generator would add schemas, domain calibration, privacy review, richer event semantics, and distributed scale controls.

## Interview prompts

### Python

1. **Why use a frozen dataclass for configuration?** It makes each run’s inputs explicit and prevents accidental mutation.
2. **Why pass `Random` instead of using global randomness?** It isolates deterministic state for repeatable tests.
3. **Why use `Path`?** It keeps output paths platform-independent and testable with temporary directories.
4. **Why type public functions?** Types document record boundaries and let mypy catch incompatible changes.
5. **Why return a dataset bundle?** It separates valid source records from explicit invalid examples.
6. **Why use `argparse`?** It provides a standard-library CLI without adding a framework for two commands.
7. **How are errors exposed?** Invalid configuration raises `ValueError`; the CLI converts expected operational errors to non-zero exits.
8. **Why no global configuration?** Tests can construct isolated configurations without state leaking between runs.
9. **Why use UTC?** Lifecycle comparisons remain unambiguous across regions and DST changes.
10. **Why test file outputs with temporary directories?** Tests do not depend on committed or previously generated files.

### Data engineering

1. **Why synthetic sources?** They are shareable, deterministic, and safe for interview review.
2. **What establishes referential integrity?** Tickets choose an agent from the selected team and a subcategory from the selected category.
3. **Why retain status history?** It supports later lifecycle, backlog, and SLA analysis without overwriting ticket state.
4. **Why have a batch ID?** Later ingestion can trace every source row to its generation run.
5. **Why separate validation from generation?** A generator cannot prove its own assumptions without independent rules.
6. **Why inject defects separately?** Clean-source workflows remain reliable while quality handling can be demonstrated deliberately.
7. **How are SLA targets derived?** One reference rule per priority keeps the relationship inspectable.
8. **Why include a manifest?** It captures reproducibility metadata and expected counts for downstream checks.
9. **How will this support ELT?** These files become source-shaped landing data in a later phase.
10. **Why commit only a sample?** The larger datasets are reproducible and would create noisy, oversized history.

### Parquet

1. **Why Parquet?** It is columnar, compressed, and efficient for analytical workloads.
2. **What does Snappy provide?** Fast compression/decompression with a practical size-performance trade-off.
3. **Why schema consistency tests?** Downstream tools depend on the same dataset shape across formats.
4. **When is CSV preferable?** For simple exchange with tools that cannot read Parquet.
5. **Why does columnar storage help?** Queries can read selected columns instead of every value in each row.

## 60-second project explanation

“Phase 1 builds the source layer for a Service Operations Data Platform. It deterministically generates related teams, agents, customers, classifications, SLA rules, tickets, and ticket-status history from a typed configuration. The generator models realistic operational patterns—rare P1 incidents, priority SLA targets, unresolved work, breaches, reopenings, and satisfaction effects—while preserving valid foreign keys and UTC lifecycles. It writes reviewable JSON and CSV plus Snappy Parquet, with a manifest and checksum for reproducibility. Independent validation and tests prove clean data quality; optional defect mode writes intentionally invalid examples separately for later quality workflows. This creates a safe, repeatable source foundation without using real employer data.”
