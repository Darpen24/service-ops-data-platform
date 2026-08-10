# Phase 4: dbt transformations and marts

The dbt project is under `dbt/service_ops`. It reads Phase 2/3 `raw` relations and intentionally
builds into `dbt_analytics`, preserving the Phase 2 `analytics` views for backward-compatible SQL.
It makes dbt the canonical transformation path from this phase forward.

`source()` declares raw lineage and freshness; `ref()` makes the dependency graph explicit.
Staging and intermediate models are views, while dimensions, facts, and marts are tables. The fact
grains are one ticket (`fct_tickets`) and one lifecycle event (`fct_ticket_status_events`). The
daily and team marts have one row per activity date and one row per team respectively.

Use a local, uncommitted profile based on `profiles.yml.example` and environment variables:

```bash
dbt --project-dir dbt/service_ops --profiles-dir dbt/service_ops deps
dbt --project-dir dbt/service_ops --profiles-dir dbt/service_ops debug
dbt --project-dir dbt/service_ops --profiles-dir dbt/service_ops build
```

Snapshots demonstrate timestamp-based SCD history for mutable tickets. Generic and singular tests
protect identifiers, accepted priorities, relationships, and negative resolution durations.

Interview note: dbt is preferable to stored procedures here because transformations, tests,
lineage, and documentation are versioned beside the source. Python remains responsible for
transport, audit, and quarantine—not warehouse metric logic.
