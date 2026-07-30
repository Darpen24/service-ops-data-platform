You are acting as a senior data engineer, analytics engineer, Power BI developer, DevOps engineer and technical documentation writer.

Build a complete portfolio-grade project named:

SERVICE OPERATIONS DATA PLATFORM

The project must demonstrate practical skills relevant to Data Engineer and Data Analyst interviews in Germany.

EXECUTION MODE

Execute the project phase by phase from start to finish.

Do not stop between phases unless blocked by:

1. Missing cloud credentials
2. A paid resource that requires explicit approval
3. A local application that is not installed
4. An authentication or administrator setting
5. An irreversible external action

When blocked by an external dependency:

1. Complete every possible local artifact.
2. Create mock or offline validation.
3. Document the exact remaining manual step.
4. Continue with all other phases.
5. Never invent successful deployments or test results.

Do not use real employer or confidential data.

Use deterministic synthetic service-management data.

PRIMARY BUSINESS SCENARIO

Create a data platform for analysing IT incidents and service requests.

The platform must answer:

1. How many tickets were created, resolved and reopened?
2. What is the current backlog?
3. Which teams have the highest SLA breach rate?
4. What is the average and median resolution time?
5. Which categories create the most repeated incidents?
6. How does priority affect resolution time?
7. How is operational performance changing month over month?
8. Which teams have growing backlogs?
9. Which channels generate the highest-value or highest-risk requests?
10. Which tickets are likely to breach their SLA?

CORE TECHNOLOGIES

Use:

* Python 3.12
* PostgreSQL
* SQL
* Docker and Docker Compose
* dbt Core with dbt-postgres
* pytest
* Ruff
* mypy
* SQLFluff
* GitHub Actions
* Snowflake implementation
* dbt-snowflake
* PySpark
* Delta Lake
* Databricks-compatible notebooks
* Terraform
* Power BI Project format
* Power Query M
* DAX
* Power BI semantic modelling
* Power BI report pages and visuals

Optional orchestration:

* Apache Airflow

Use Airflow only after the underlying pipeline can run independently through normal commands.

NON-NEGOTIABLE ENGINEERING RULES

1. Never commit secrets, access tokens, passwords or connection strings.
2. Create `.env.example`.
3. Use environment variables for sensitive configuration.
4. Use deterministic random seeds for generated data.
5. Make pipelines idempotent.
6. Add clear error handling and structured logging.
7. Keep functions small and testable.
8. Use type hints.
9. Do not place all logic in notebooks.
10. Do not generate fake test results.
11. Do not claim cloud deployment unless it was actually executed.
12. Do not run `terraform apply` without explicit approval.
13. Do not publish anything to LinkedIn automatically.
14. Do not create empty or artificial Git commits.
15. Every commit must represent one coherent implementation change.
16. Preserve a fully runnable local version even when cloud implementations are added.
17. Use synthetic data only.
18. Prefer readable code over unnecessarily complex abstractions.
19. Explain important architectural decisions.
20. Add tests for business logic, not only code execution.

INITIAL PLANNING FILES

Before implementing application code, create:

* `AGENTS.md`
* `PLANS.md`
* `IMPLEMENTATION_LOG.md`
* `DECISIONS.md`
* `README.md`
* `CONTRIBUTING.md`
* `SECURITY.md`
* `.gitignore`
* `.env.example`
* `LICENSE`
* `pyproject.toml`
* `docker-compose.yml`

AGENTS.MD

Create repository instructions telling future agents to:

* Read `PLANS.md`, `DECISIONS.md` and `IMPLEMENTATION_LOG.md`
* Keep changes scoped to the current phase
* Run relevant validation after every logical change
* Never expose secrets
* Update documentation when behaviour changes
* Avoid rewriting working components without justification
* Record material design decisions
* Explain failed approaches
* Use conventional commit messages
* Never fabricate cloud execution
* Preserve backward compatibility unless the plan explicitly changes it

PLANS.MD

Create a milestone plan for all phases.

For every phase include:

* Goal
* Concepts demonstrated
* Files to create or modify
* Tests
* Acceptance criteria
* Interview value
* Status
* Known blockers

IMPLEMENTATION_LOG.MD

Continuously record:

* Completed phase
* Important files
* Commands executed
* Tests executed
* Test results
* Problems encountered
* How problems were solved
* Remaining issues
* Next phase

DECISIONS.MD

Use architecture decision records for important choices, including:

* Why synthetic service-management data was selected
* Why PostgreSQL is the local warehouse
* Why ELT is the primary production-style design
* Why a star schema is used
* Why dbt owns warehouse transformations
* Why the Snowflake and Databricks implementations are separate adapters
* Why Power BI connects to curated Gold or mart tables
* Why Terraform apply is approval-gated

REPOSITORY STRUCTURE

Use a structure similar to:

service-ops-data-platform/
.github/
workflows/
ISSUE_TEMPLATE/
pull_request_template.md
config/
data/
raw/
sample/
processed/
dbt/
service_ops_postgres/
service_ops_snowflake/
docker/
docs/
architecture/
data_dictionary/
interview/
learning/
linkedin/
powerbi/
runbooks/
infrastructure/
modules/
environments/
local/
dev/
notebooks/
databricks/
powerbi/
ServiceOperations.Report/
ServiceOperations.SemanticModel/
themes/
scripts/
src/
service_ops/
generation/
ingestion/
validation/
transformation/
loading/
quality/
common/
sql/
ddl/
analysis/
validation/
tests/
unit/
integration/
data/
.env.example
AGENTS.md
DECISIONS.md
IMPLEMENTATION_LOG.md
PLANS.md
README.md
docker-compose.yml
pyproject.toml

Adjust the structure only when there is a documented reason.

PHASE 0: PROJECT FOUNDATION

Create:

* Repository structure
* Python package configuration
* Development dependencies
* Docker Compose configuration
* PostgreSQL service
* Health checks
* Local setup scripts for Windows PowerShell and Bash
* Makefile or equivalent task commands
* GitHub templates
* Initial architecture diagram using Mermaid

Provide commands for:

* Environment setup
* Starting services
* Running tests
* Running linting
* Generating data
* Loading data
* Running dbt
* Running the complete local demo

Create a meaningful conventional commit for Phase 0.

PHASE 1: SYNTHETIC DATA GENERATION

Generate realistic synthetic data for:

* Tickets
* Teams
* Employees
* Categories
* Subcategories
* Customers or business units
* SLA rules
* Status history
* Ticket comments or events

Ticket fields should include:

* ticket_id
* ticket_type
* created_at
* updated_at
* resolved_at
* closed_at
* priority
* impact
* urgency
* category
* subcategory
* assigned_team_id
* assigned_agent_id
* customer_id
* business_unit
* region
* channel
* status
* sla_target_hours
* first_response_at
* first_response_minutes
* resolution_minutes
* reopened_count
* escalation_count
* satisfaction_score
* short_description

Generate realistic behaviour:

* P1 tickets are less common but more urgent.
* Resolution time varies by priority and team.
* Some tickets remain unresolved.
* Some tickets reopen.
* Some tickets breach SLA.
* Ticket volume changes over time.
* Some categories repeat more often.
* A small percentage of records intentionally contain data-quality problems.

Use deterministic configuration.

Output:

* JSON source files
* CSV sample files
* Optional API-style paginated responses
* Data-generation configuration
* Data dictionary

Add unit tests for:

* Deterministic generation
* Unique primary identifiers
* Valid timestamps
* Allowed priority values
* Realistic null behaviour
* Generated record counts
* Referential integrity

Create learning documentation:

`docs/learning/phase-01-python.md`

It must explain:

* Data structures used
* Functions
* Modules
* Type hints
* Dataclasses or models
* File handling
* Date handling
* Exception handling
* Logging
* Testing
* Design choices
* Five Python interview questions
* Five data-engineering interview questions
* Model answers tied to this implementation

Create a meaningful commit.

PHASE 2: POSTGRESQL AND SQL

Create PostgreSQL schemas:

* raw
* staging
* analytics
* audit

Create source and reference tables with:

* Primary keys
* Foreign keys
* Check constraints
* Appropriate data types
* Audit timestamps
* Source metadata
* Load batch IDs

Implement:

* Database initialisation
* Raw loading
* Full load
* Incremental load
* Upsert behaviour
* Deduplication
* Transaction handling
* Failed-record quarantine
* Load audit table

Write SQL examples demonstrating:

* Filtering
* CASE expressions
* Aggregations
* Inner and outer joins
* CTEs
* Subqueries
* Date functions
* Window functions
* Running totals
* Rankings
* Lag and lead
* Percentiles
* Median calculations
* Cohort-style analysis
* Query-plan analysis
* Index examples

Create business queries for:

* Ticket backlog
* SLA breach rate
* Mean time to resolution
* Median resolution time
* Reopen rate
* Team ranking
* Monthly trends
* Backlog ageing
* Category recurrence
* Priority performance

Add SQL validation queries and integration tests.

Create:

`docs/learning/phase-02-sql.md`

Include project-specific SQL interview questions and answers.

Create a meaningful commit.

PHASE 3: ETL, ELT AND DATA QUALITY

Implement two small comparable paths:

ETL demonstration:

Source file
to Python transformation
to curated PostgreSQL table

Primary ELT implementation:

Source file
to raw PostgreSQL tables
to dbt transformations
to analytics marts

Demonstrate:

* Full loading
* Incremental loading
* Watermarks
* Idempotency
* Deduplication
* Retry handling
* Late-arriving data
* Schema validation
* Quarantine handling
* Audit logging
* Batch identifiers
* Recovery after partial failure

Create a CLI such as:

* generate
* ingest
* validate
* load
* run-pipeline
* show-status

Add tests proving that:

* Re-running the same batch does not duplicate data.
* An invalid record is quarantined.
* A failed transaction does not leave partial data.
* A corrected late record can be processed.
* Watermark behaviour is correct.

Create:

`docs/learning/phase-03-etl-elt.md`

Explain ETL versus ELT using actual files from the repository.

Create a meaningful commit.

PHASE 4: DBT

Create a complete dbt-postgres project.

Use:

* Sources
* Staging models
* Intermediate models
* Dimensions
* Facts
* Marts
* Seeds
* Snapshots
* Macros
* Documentation
* Exposures
* Singular tests
* Generic tests
* Unit tests where supported
* Source freshness

Suggested models:

* stg_tickets
* stg_teams
* stg_customers
* stg_status_history
* int_ticket_lifecycle
* int_ticket_sla
* int_team_daily_performance
* dim_date
* dim_team
* dim_customer
* dim_category
* dim_priority
* fct_tickets
* fct_ticket_status_events
* mart_service_operations_daily
* mart_team_performance
* mart_sla_analysis
* mart_category_recurrence

Define and document the grain of every fact table.

Add tests for:

* Unique identifiers
* Not-null identifiers
* Relationships
* Accepted values
* Non-negative durations
* Valid status transitions
* Resolved timestamp requirements
* SLA calculation consistency

Create generated dbt documentation where possible.

Create:

`docs/learning/phase-04-dbt.md`

Explain:

* `source`
* `ref`
* DAG lineage
* Materialisations
* Tests
* Snapshots
* Slowly changing dimensions
* Incremental models
* Macros
* dbt versus stored procedures
* dbt versus Python transformation

Create a meaningful commit.

PHASE 5: CI/CD

Create GitHub Actions workflows for:

Pull requests:

* Ruff
* mypy
* pytest
* SQLFluff
* dbt parse
* dbt build against an isolated PostgreSQL service
* Docker configuration validation
* Terraform formatting
* Terraform validation
* Secret scanning where suitable

Main branch:

* Full validation
* Build documentation artifacts
* Build or validate Docker image
* Produce test reports
* Produce dbt documentation artifact

Use caching appropriately.

Do not require Snowflake or Databricks credentials for normal pull-request validation.

Create status badges in README only when the corresponding workflow exists.

Create:

`docs/learning/phase-05-cicd.md`

Explain:

* Continuous integration
* Continuous delivery
* Workflow triggers
* Jobs
* Steps
* Runners
* Secrets
* Quality gates
* Artifacts
* Environment separation
* Rollback considerations
* CI/CD interview questions

Create a meaningful commit.

PHASE 6: SNOWFLAKE

Create a Snowflake implementation that mirrors the same business logic without breaking the local PostgreSQL version.

Create:

* Snowflake database and schema scripts
* Roles and grants
* Warehouse configuration
* Resource monitor example
* File formats
* Stages
* COPY INTO loading
* JSON variant handling
* Streams and task examples
* Time Travel demonstration documentation
* dbt-snowflake project or compatible target
* Snowflake-specific incremental models

Use environment variables for:

* Account
* User
* Role
* Warehouse
* Database
* Schema
* Authentication

Cloud integration tests must skip cleanly when credentials are absent.

Do not claim Snowflake execution unless it actually succeeds.

Create:

`docs/learning/phase-06-snowflake.md`

Include:

* Storage and compute separation
* Warehouses
* Micro-partitioning
* Clustering
* Stages
* COPY INTO
* Streams
* Tasks
* Time Travel
* Zero-copy cloning
* Cost controls
* Snowflake interview questions

Create a meaningful commit.

PHASE 7: DATABRICKS, PYSPARK AND DELTA LAKE

Create Databricks-compatible notebooks and Python modules for:

Bronze:

* Ingest raw JSON
* Add ingestion metadata
* Preserve raw source values
* Handle schema evolution

Silver:

* Cast data types
* Remove duplicates
* Quarantine invalid records
* Standardise categories
* Calculate lifecycle fields
* Apply quality rules

Gold:

* Daily operations metrics
* SLA metrics
* Team performance
* Backlog ageing
* Category recurrence

Demonstrate:

* Spark DataFrames
* Transformations and actions
* Lazy evaluation
* Partitions
* Broadcast joins
* Shuffle awareness
* Parquet
* Delta tables
* MERGE
* Schema enforcement
* Schema evolution
* Time Travel
* Optimisation concepts
* Batch processing
* A small streaming design example

Make the transformation business rules consistent with the PostgreSQL and dbt implementation.

Provide local PySpark or Delta validation where feasible.

Add Databricks deployment configuration without requiring automatic deployment.

Create:

`docs/learning/phase-07-databricks.md`

Include project-specific Spark and Databricks interview questions.

Create a meaningful commit.

PHASE 8: TERRAFORM

Create reusable Terraform modules for relevant infrastructure.

At minimum provide:

* Provider configuration
* Variables
* Outputs
* Environment separation
* Module structure
* Remote-state design documentation
* Snowflake resource examples
* Databricks resource examples
* Least-privilege guidance
* Cost and destruction warnings

Create safe commands for:

* terraform fmt
* terraform init
* terraform validate
* terraform plan

Never automatically execute:

* terraform apply
* terraform destroy

Add CI checks that do not require production credentials.

Create:

`docs/learning/phase-08-terraform.md`

Explain:

* Providers
* Resources
* Variables
* Outputs
* State
* Remote state
* Locking
* Modules
* Drift
* Plan versus apply
* Import
* Lifecycle
* Terraform interview questions

Create a meaningful commit.

PHASE 9: POWER BI SEMANTIC MODEL

First detect whether the following are available:

* Power BI Desktop on Windows
* Power BI Project support
* Power BI Modeling MCP server
* Power BI authoring skills
* Power BI Desktop Bridge
* PBIP project access

Use the Microsoft Power BI semantic-model-authoring workflow when available.

Create a PBIP project.

Build a star schema using:

* Fact Tickets
* Fact Ticket Status Events
* Dim Date
* Dim Team
* Dim Customer
* Dim Category
* Dim Priority

Create relationships with correct cardinality and filter direction.

Hide technical keys and unnecessary columns.

Create display folders.

Create friendly descriptions for tables, columns and measures.

Create Power Query M parameters for data-source configuration.

Use Power Query for connection and light source preparation only.

Keep core business transformations in dbt or the curated data layer.

Create DAX measures including:

* Total Tickets
* Open Tickets
* Resolved Tickets
* Closed Tickets
* Reopened Tickets
* Backlog
* SLA Breached Tickets
* SLA Breach Rate
* Average Resolution Hours
* Median Resolution Hours
* Average First Response Minutes
* Reopen Rate
* Escalation Rate
* Average Satisfaction Score
* Tickets Previous Month
* Ticket Volume Change
* Resolved Previous Month
* Resolution Change
* Backlog Previous Month
* Backlog Change
* Team Rank by SLA Performance
* Tickets Within SLA
* Percentage Within SLA
* P1 Open Tickets
* Aged Backlog Over 7 Days
* Aged Backlog Over 30 Days

Use:

* Measures instead of unnecessary calculated columns
* `DIVIDE`
* `CALCULATE`
* Variables
* `FILTER`
* `DISTINCTCOUNT`
* Iterators only when justified
* Time-intelligence patterns
* Explicit formatting

Validate every measure using sample queries where the available tools support it.

Create:

`docs/learning/phase-09-powerbi-model.md`

Explain:

* Star schema
* Grain
* Relationships
* Filter context
* Row context
* Context transition
* CALCULATE
* Measures versus columns
* Power Query versus dbt
* DAX interview questions
* Power BI modelling interview questions

If the Power BI authoring tools are unavailable:

1. Create all required DAX in documented files.
2. Create Power Query M scripts.
3. Create the model specification.
4. Create the table and relationship specification.
5. Create a Power BI setup checklist.
6. Do not pretend that a PBIP model was validated.

Create a meaningful commit.

PHASE 10: POWER BI REPORT

Use the Power BI report planning skill first.

Then use the Power BI report design skill.

Then use the Power BI report authoring skill.

Use the Power BI Desktop Bridge for reloads, screenshots and visual validation where available.

Create these pages:

PAGE 1: EXECUTIVE OVERVIEW

Include:

* Total Tickets
* Open Tickets
* Backlog
* SLA Breach Rate
* Average Resolution Hours
* Monthly ticket trend
* Resolution versus creation trend
* Backlog by priority
* Team SLA ranking
* Date, team, priority and region slicers

PAGE 2: SLA AND RESOLUTION ANALYSIS

Include:

* SLA breach trend
* SLA rate by team
* SLA rate by priority
* Resolution-time distribution
* Average and median resolution time
* First-response performance
* Drill-through to ticket details

PAGE 3: TEAM PERFORMANCE

Include:

* Team scorecards
* Ticket volume by team
* Resolution performance
* Backlog growth
* Reopen rate
* Escalation rate
* Team ranking
* Dynamic selected-team title

PAGE 4: CATEGORY AND ROOT-CAUSE ANALYSIS

Include:

* Tickets by category
* Repeat categories
* Category trend
* Reopen rate by category
* SLA breaches by category
* Description or keyword analysis where practical

PAGE 5: TICKET DETAILS

Include:

* Searchable ticket table
* Conditional formatting
* Drill-through support
* Ticket identifiers
* Dates
* Priority
* Status
* Team
* Category
* SLA status
* Resolution duration

DESIGN REQUIREMENTS

* Professional and restrained appearance
* Consistent spacing
* Accessible contrast
* Limited colour palette
* Clear page titles
* Consistent visual hierarchy
* No unnecessary pie charts
* No decorative gauges
* Avoid overloaded pages
* Use tooltips where useful
* Use bookmarks only when they add value
* Use modern supported visuals
* Create a report theme JSON
* Add page navigation
* Include a last-refresh indicator
* Use 16:9 page dimensions

VALIDATION

After every logical report change:

* Validate PBIR structure
* Reload Power BI Desktop
* Capture a screenshot
* Check for broken visuals
* Check measure bindings
* Check visual titles
* Check filter behaviour
* Check empty-state behaviour
* Check alignment and spacing

Perform an independent report-design review and correct material issues.

Store dashboard screenshots under:

`docs/powerbi/screenshots/`

Create:

`docs/learning/phase-10-powerbi-report.md`

Explain:

* Why every visual was selected
* Why alternative visuals were rejected
* Page-level filter design
* Slicer strategy
* Drill-through
* Tooltips
* Conditional formatting
* Dashboard performance
* Common Power BI interview questions

If direct PBIR authoring is not available, create:

* Detailed report specification
* Theme JSON
* DAX files
* Power Query files
* Page wireframes
* Exact field-to-visual mappings
* Manual Power BI implementation checklist

Do not claim the dashboard was created when it was only specified.

Create a meaningful commit.

PHASE 11: ORCHESTRATION, OBSERVABILITY AND PRODUCTION READINESS

Add an optional Airflow implementation for the local pipeline.

Include tasks for:

* Source generation or arrival check
* Raw ingestion
* Validation
* PostgreSQL loading
* dbt build
* Data-quality validation
* Pipeline completion logging

Demonstrate:

* Dependencies
* Retries
* Idempotency
* Backfills
* Scheduling
* Failure callbacks
* Logging
* Separation between orchestration and business logic

Add production-readiness documentation for:

* Monitoring
* Alerting
* Data freshness
* Data lineage
* Schema changes
* Incident recovery
* Access control
* Cost control
* Backup and recovery
* Deployment environments
* Data retention

Create a meaningful commit.

PHASE 12: PORTFOLIO AND INTERVIEW PACKAGE

Improve the root README with:

* Clear business problem
* Architecture diagram
* Technology stack
* Screenshots
* Local quick start
* Data model
* Pipeline explanation
* Testing approach
* CI/CD explanation
* Cloud implementations
* Power BI dashboard
* Known limitations
* Future improvements
* Interview talking points

Create:

`docs/interview/data-engineer-question-bank.md`

Include at least:

* 15 Python questions
* 20 SQL questions
* 15 data-modelling questions
* 20 ETL and ELT questions
* 15 dbt questions
* 15 CI/CD questions
* 15 Snowflake questions
* 20 Spark and Databricks questions
* 15 Terraform questions
* 10 architecture questions
* 10 behavioural questions

Create:

`docs/interview/data-analyst-question-bank.md`

Include at least:

* 20 SQL questions
* 15 Power Query questions
* 25 DAX questions
* 15 Power BI modelling questions
* 15 dashboard-design questions
* 10 stakeholder questions
* 10 data-quality questions
* 10 behavioural questions

Every answer must reference this project where appropriate.

Create:

`docs/interview/project-explanations.md`

Include:

* 30-second project explanation
* 60-second project explanation
* Three-minute project explanation
* Data Engineer version
* Data Analyst version
* Technical deep-dive version
* Non-technical stakeholder version
* Challenges and lessons
* Tradeoffs
* Production improvements
* STAR examples

Create one LinkedIn draft for every major phase under:

`docs/linkedin/`

Each post must:

* Describe a genuine implemented feature
* Explain one technical lesson
* Mention one challenge
* Avoid exaggerated claims
* Suggest an architecture diagram, code snippet or dashboard screenshot
* End with one relevant technical question
* Include a repository link placeholder
* Never state that a cloud deployment succeeded unless validated

FINAL VALIDATION

Run all possible local checks.

At minimum verify:

* Python package installation
* Data generation
* Unit tests
* Integration tests
* PostgreSQL startup
* Raw loading
* Incremental loading
* Deduplication
* dbt build
* dbt tests
* SQL linting
* Python linting
* Type checking
* Docker Compose validation
* Terraform formatting
* Terraform validation
* Power BI PBIP validation when tools are present
* Dashboard screenshots when Desktop Bridge is present

Create:

`docs/FINAL_VALIDATION_REPORT.md`

The report must separate:

* Passed and executed
* Failed and executed
* Skipped because credentials were missing
* Not executable in the current environment
* Manual verification required

GIT WORKFLOW

Use conventional commits.

Suggested commit structure:

* chore: initialise project foundation
* feat: add deterministic service-ticket generator
* feat: implement PostgreSQL ingestion and SQL analytics
* feat: add idempotent ETL and ELT pipelines
* feat: build dbt transformation and testing layer
* ci: add repository quality gates
* feat: add Snowflake implementation
* feat: add Databricks medallion pipeline
* feat: add Terraform infrastructure modules
* feat: create Power BI semantic model
* feat: build Power BI operational dashboard
* feat: add Airflow orchestration
* docs: add interview and portfolio package

Do not combine every phase into one commit.

Do not create meaningless commits.

When GitHub integration is available:

1. Work on a feature branch.
2. Push the branch.
3. Open a pull request.
4. Include the validation summary.
5. Do not merge without user review.

FINAL RESPONSE

At completion, provide:

1. What was built
2. Repository structure
3. Commands to run it
4. Test results
5. Cloud features requiring credentials
6. Power BI status
7. Manual steps remaining
8. Commit list
9. Interview documentation location
10. LinkedIn draft locations
11. Known limitations
12. Recommended first file for the user to study

Do not hide incomplete work.

Do not call a feature complete unless its acceptance criteria passed.
