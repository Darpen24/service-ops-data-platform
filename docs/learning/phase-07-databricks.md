# Phase 7: Databricks, PySpark, and Delta Lake

`service_ops.lakehouse.contracts` holds pure, testable Bronze/Silver/Gold contracts that preserve
the PostgreSQL lifecycle and SLA rules. Bronze adds batch/source metadata, Silver standardises and
quarantines invalid tickets before deterministic latest-record deduplication, and Gold emits
priority SLA metrics. The Databricks notebook and job resource illustrate how those contracts map
to Spark DataFrames and Delta tables without making notebooks the only implementation.

Spark transformations are lazy; actions trigger execution. Partitioning and broadcast joins can
reduce shuffles when measured, while Delta `MERGE` supports idempotent incremental writes. Delta
schema enforcement protects Silver, `mergeSchema` is an explicit evolution decision, and history
supports time-travel inspection. A production streaming design would use a checkpointed source and
reuse the same Silver validation/quarantine contract.

No Java/Spark/Delta runtime or Databricks credentials are available in this environment. The pure
Python contract test runs locally; Spark execution and deployment are deliberately not claimed.
