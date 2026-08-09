# Phase 3: ETL, ELT, and data quality

Phase 3 adds a deliberately small production-style ingestion layer. `pipeline run-pipeline` reads
the typed committed Parquet contract, checks per-ticket source validity, stages valid tickets, and
records its run in PostgreSQL. Invalid records are written to `audit.quarantine_records` with a
rule, reason, record identifier, batch, and JSON-safe payload.

## ETL compared with ELT

The small ETL teaching path is the Python validation and record preparation that happens before
staging. The primary project path is ELT: source-shaped data remains in `raw`, `staging` captures
the ingestion contract, and Phase 4 dbt owns reusable analytical transformations. This avoids
embedding warehouse business metrics in an ingestion script.

## Reliability mechanisms

- A `pipeline_runs` audit record captures the batch, checksum, counts, outcome, error, and
  before/after watermark.
- `pipeline_watermarks` advance only inside the successful staging transaction. A database error
  rolls back the business write and records a failed run instead.
- `(batch_id, ticket_id)` identifies a staged source record; checksums make reruns deterministic
  and safely handle a corrected late record whose `updated_at` is newer than the watermark.
- Bad records are quarantined while good records can proceed as a `partial` run. The original
  source payload is retained only because this project uses synthetic data.

## Interview questions

1. What makes a load idempotent? Stable keys and a repeat-safe conflict policy; this pipeline uses
   the source batch/ticket key and checksum.
2. Why store a watermark? It bounds incremental work and makes the next run explicit.
3. Why update the watermark in the same transaction? A failed write must not cause source records
   to be skipped on retry.
4. Quarantine versus reject-all? Quarantine protects valid records while retaining evidence for a
   safe correction workflow.
5. Why is dbt deferred? Ingestion owns transport and audit; dbt owns declared analytical logic.
6. How are late records handled? A later `updated_at` crosses the watermark and the changed
   checksum updates the staged copy.
