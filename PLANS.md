# Delivery plan

The phase order below follows `PROJECT_SPEC.md`. Each phase is independently reviewable; no phase is started merely to create a placeholder.

| Phase | Goal and concepts | Major outputs / validation | Interview value | Status / blockers |
| --- | --- | --- | --- | --- |
| 0 | Foundation: repository design, src layout, dependency isolation, Docker Compose | Tooling, documentation, PostgreSQL health check, templates; smoke, test, lint, types, Compose | Explains reproducible local delivery | Complete; native Python 3.12 installation remains a workstation prerequisite |
| 1 | Deterministic synthetic service-management data | JSON/CSV outputs, config, data dictionary, generation tests | Python, modelling realistic source behaviour | Not started |
| 2 | PostgreSQL and SQL | Schemas, idempotent loading, audit/quarantine, analytical SQL and integration tests | SQL, transactions, warehouse design | Not started |
| 3 | ETL, ELT, and data quality | Comparable ETL/ELT paths, CLI, watermarks, retry/recovery tests | Pipeline design and quality engineering | Not started |
| 4 | dbt | Postgres models, tests, docs, snapshots, marts | ELT, lineage, dimensional modelling | Not started |
| 5 | CI/CD | GitHub Actions quality gates and isolated PostgreSQL validation | Automation and release discipline | Not started |
| 6 | Snowflake | Optional adapter, scripts, roles/grants, dbt target, credential-skipping tests | Cloud warehouse architecture and cost control | Not started; credentials/approval may block execution |
| 7 | Databricks, PySpark, and Delta Lake | Bronze/Silver/Gold-compatible modules and notebooks | Spark, lakehouse, Delta semantics | Not started; local tooling or credentials may block execution |
| 8 | Terraform | Reusable modules, safe plan-only workflow, validation | Infrastructure as code and least privilege | Not started; apply remains manual-approval-only |
| 9 | Power BI semantic model | PBIP model, Power Query parameters, DAX, model validation | Star schemas, DAX, semantic modelling | Not started; Desktop/tool availability may block validation |
| 10 | Power BI report | Five report pages, theme, screenshots, design review | Dashboard design and stakeholder communication | Not started; Desktop Bridge availability may block validation |
| 11 | Orchestration and observability | Optional Airflow plus readiness/runbook documentation | Orchestration, recovery, observability | Not started |
| 12 | Portfolio and interview package | Expanded README, question banks, explanations, LinkedIn drafts | Clear technical storytelling | Not started |

## Phase 0 acceptance criteria

- Required foundation files, structure, package, scripts, and templates exist.
- Python target is 3.12 and tools are configured in `pyproject.toml`.
- PostgreSQL Compose service uses environment variables, named storage, and a health check.
- No real secrets, business tables, synthetic data, dbt models, cloud resources, Airflow, or Power BI artifacts are added.
- Every executable local check is run and its exact result is recorded.

## Phase detail

### Phase 0 — Foundation

**Goal and concepts:** establish reproducibility, isolation, configuration, and safe local services. **Files:** root governance/docs, `src/service_ops`, `tests`, `scripts`, Compose, and GitHub templates. **Tests:** import smoke, pytest, Ruff, mypy, Compose config, PostgreSQL health and connection. **Acceptance:** all foundation artifacts exist and checks are recorded. **Interview value:** explains a maintainable starting point. **Blockers:** native Python 3.12 must be installed for host-only execution.

### Phase 1 — Synthetic data generation

**Goal and concepts:** deterministic, realistic source data and data-quality edge cases. **Files:** generation modules, source outputs, configuration, data dictionary, and learning documentation. **Tests:** determinism, identifiers, timestamps, accepted values, nulls, counts, and references. **Acceptance:** reproducible, documented synthetic sources. **Interview value:** Python data modelling. **Blockers:** none expected.

### Phase 2 — PostgreSQL and SQL

**Goal and concepts:** relational modelling, transactions, loading, and analytical SQL. **Files:** DDL, loading code, SQL examples/validation, integration tests, and learning documentation. **Tests:** constraints, full/incremental loads, upserts, deduplication, rollback, and queries. **Acceptance:** local schemas and business answers are reproducible. **Interview value:** SQL and warehouse design. **Blockers:** Docker/PostgreSQL availability.

### Phase 3 — ETL, ELT, and data quality

**Goal and concepts:** comparable ETL/ELT design, idempotency, watermarks, quarantine, and recovery. **Files:** CLI, pipeline modules, quality rules, audit artifacts, and learning documentation. **Tests:** reruns, invalid records, transactions, late data, and watermarks. **Acceptance:** the primary ELT path is recoverable and observable. **Interview value:** pipeline engineering. **Blockers:** Phase 1/2 inputs.

### Phase 4 — dbt

**Goal and concepts:** versioned SQL transformations, lineage, testing, and marts. **Files:** dbt project, models, macros, tests, documentation, snapshots, and learning guide. **Tests:** source, schema, relationship, freshness, and business-rule tests. **Acceptance:** documented models build against PostgreSQL. **Interview value:** analytics engineering. **Blockers:** Phase 2 schemas and Phase 3 raw data.

### Phase 5 — CI/CD

**Goal and concepts:** repeatable quality gates and isolated service testing. **Files:** GitHub Actions workflows, reports, badges when valid, and learning guide. **Tests:** Python, SQLFluff, dbt, Docker, and Terraform-safe validation. **Acceptance:** pull-request checks run without cloud credentials. **Interview value:** delivery automation. **Blockers:** GitHub Actions execution is external.

### Phase 6 — Snowflake

**Goal and concepts:** cloud-warehouse adapter, security, and cost controls. **Files:** Snowflake SQL, dbt target, configuration, and learning guide. **Tests:** local-compatible parsing and credential-aware skips. **Acceptance:** no local path is broken; cloud execution is evidenced or marked skipped. **Interview value:** cloud warehouse architecture. **Blockers:** credentials, paid resources, and approval.

### Phase 7 — Databricks, PySpark, and Delta Lake

**Goal and concepts:** medallion architecture and distributed transformation. **Files:** modules, notebooks, deployment configuration, and learning guide. **Tests:** feasible local Spark/Delta validation. **Acceptance:** business rules match the PostgreSQL/dbt path. **Interview value:** lakehouse engineering. **Blockers:** Spark tooling or platform credentials.

### Phase 8 — Terraform

**Goal and concepts:** reusable infrastructure-as-code with environment separation. **Files:** modules, variables, outputs, provider guidance, and learning guide. **Tests:** `fmt`, `init`, `validate`, and `plan` where authorized. **Acceptance:** no `apply` or `destroy` runs automatically. **Interview value:** infrastructure safety. **Blockers:** providers/credentials; apply is approval-gated.

### Phase 9 — Power BI semantic model

**Goal and concepts:** star schema, relationships, Power Query parameters, and DAX. **Files:** PBIP model or documented fallback, M/DAX files, specification, and learning guide. **Tests:** available model validation and sample-query checks. **Acceptance:** model is validated or clearly documented as manual. **Interview value:** BI semantic modelling. **Blockers:** Power BI Desktop/Bridge support.

### Phase 10 — Power BI report

**Goal and concepts:** accessible executive, SLA, team, category, and ticket-detail reporting. **Files:** report pages, theme, screenshots, wireframes/fallback, and learning guide. **Tests:** structural, visual, filter, and binding validation. **Acceptance:** every created visual is verified; manual work is explicit. **Interview value:** dashboard design. **Blockers:** Power BI authoring tools.

### Phase 11 — Orchestration and observability

**Goal and concepts:** optional orchestration, retries, scheduling, operational readiness. **Files:** Airflow assets where useful, runbooks, monitoring/recovery documentation. **Tests:** independent pipeline run and task behaviour. **Acceptance:** orchestration wraps—not contains—business logic. **Interview value:** production operations. **Blockers:** local Airflow capacity.

### Phase 12 — Portfolio and interview package

**Goal and concepts:** technical storytelling, question banks, and genuine public-facing drafts. **Files:** README expansion, interview guides, project explanations, and LinkedIn drafts. **Tests:** content review against implemented evidence. **Acceptance:** claims are traceable to completed work. **Interview value:** concise communication. **Blockers:** prior phase evidence.
