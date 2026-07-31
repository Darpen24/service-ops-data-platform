# Architecture decision records

## ADR-001: Use synthetic service-management data

**Decision:** Use deterministic synthetic incident and service-request data.

**Rationale:** It permits safe sharing and repeatable tests while reflecting the target business scenario. No employer or confidential data will enter the repository.

## ADR-002: PostgreSQL is the primary local platform

**Decision:** PostgreSQL is the runnable local analytical platform.

**Rationale:** It is open source, SQL-capable, Docker-friendly, and provides a stable local baseline independent of cloud credentials.

## ADR-003: Prefer ELT for the production-style path

**Decision:** Land source-shaped data before transforming it with dbt in later phases.

**Rationale:** ELT makes raw lineage, reruns, and analytical transformations more transparent. A small ETL path will be retained later for comparison.

## ADR-004: Use Parquet as local columnar interchange

**Decision:** Use Parquet for future local columnar interchange.

**Rationale:** It supports efficient analytical storage and interoperability without committing to a cloud platform. No Parquet data is generated in Phase 0.

## ADR-005: dbt owns analytics transformations

**Decision:** dbt will own the analytical transformation layer.

**Rationale:** It provides versioned SQL transformations, lineage, testing, documentation, and a clear boundary from ingestion.

## ADR-006: Use a star schema for analytics and BI

**Decision:** Model future curated analytics with facts at declared grains and shared dimensions.

**Rationale:** A star schema makes ticket metrics, filtering, and relationships understandable in SQL, dbt, and Power BI. It is planned for later phases and is intentionally not implemented in Phase 0.

## ADR-007: Power BI before cloud migration

**Decision:** Build the Power BI semantic model and report against the local curated path before optional cloud migration.

**Rationale:** Power BI will connect to curated Gold or mart tables rather than raw sources, validating business value while keeping the core project runnable without paid accounts.

## ADR-008: Snowflake and Databricks are separate alternative adapters

**Decision:** Snowflake and Databricks will mirror business logic as optional adapters.

**Rationale:** The project demonstrates platform breadth without making credentials or paid infrastructure mandatory.

## ADR-009: Cloud deployment is optional

**Decision:** Cloud execution is optional and must never be represented as complete without evidence.

**Rationale:** The portfolio remains usable locally and avoids misleading deployment claims.

## ADR-010: Terraform apply requires manual approval

**Decision:** `terraform apply` and `terraform destroy` require explicit manual approval.

**Rationale:** Infrastructure mutation is irreversible or costly enough to require a human decision after reviewing a plan.

## ADR-011: Keep the Phase 0 package intentionally minimal

**Decision:** Expose one dependency-free status function and its test only.

**Rationale:** It proves packaging and validation without prematurely implementing future business logic.

## ADR-012: Use deterministic source generation with separate defect output

**Decision:** Generate clean, related source records from a seed and write optional invalid ticket copies separately.

**Rationale:** The default source set remains trustworthy and reproducible, while later data-quality phases have explicit, documented malformed examples to process.

## ADR-013: Publish JSON, CSV, and Snappy Parquet source formats

**Decision:** Write each generated dataset to readable JSON/CSV and Snappy-compressed Parquet, with a manifest checksum.

**Rationale:** JSON and CSV make source inspection and simple interchange easy; Parquet provides the columnar, compressed format needed by later analytical workflows. The manifest captures reproducibility and file inventory without committing larger generated output.
