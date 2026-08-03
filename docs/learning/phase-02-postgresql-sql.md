# Phase 2: PostgreSQL and SQL

## What this phase demonstrates

This phase turns deterministic Phase 1 Parquet into a repeatable local PostgreSQL analytical base.
The loader uses `psycopg`, a typed source reader, a manifest checksum, ordered parent-first inserts,
one transaction, and conflict-safe inserts. PostgreSQL constraints are the last line of defence;
the independent SQL validation file catches cross-row business rules such as an assigned agent from
another team.

The design separates a source-shaped `raw` layer from `analytics` views. This is intentionally a
small, transparent foundation rather than prematurely recreating the dbt layer planned for Phase 4.
`audit.sample_loads` makes the loaded source batch and its reproducibility checksum visible.

## SQL techniques in the repository

`sql/analysis/service_operations.sql` answers twenty operational questions. It uses filters,
`CASE`, aggregates, inner and outer joins, `HAVING`, CTEs, date truncation, subquery-style CTE
composition, rankings, running totals, `lag`, `lead`, and `percentile_cont` for the median.
`sql/validation/phase_02_validation.sql` reports duplicate keys, missing parents, accepted-value
violations, lifecycle errors, negative values, satisfaction range errors, agent-team mismatches,
missing SLA mappings, unresolved-ticket null violations, and non-continuous history.

Use the loader and validator:

```powershell
python -m service_ops database initialise
python -m service_ops database load-sample
python -m service_ops database validate
python -m service_ops database query-summary
```

## Query plans and indexes

The indexes in `003_indexes.sql` cover foreign keys plus typical ticket date/status/priority/team
filters and status-history lookups. Test a plan after loading:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT assigned_team_id, count(*)
FROM analytics.fct_tickets
WHERE status NOT IN ('resolved', 'closed')
GROUP BY assigned_team_id;
```

On the committed 25-ticket sample a sequential scan can be optimal; a larger realistic volume is
needed before index benefit is expected. Query plans are data and statistics dependent, so do not
assume an index will always be used.

## Interview questions

1. Why use `TIMESTAMPTZ`? It preserves an absolute instant and avoids server-local timezone
   ambiguity for operational events.
2. Primary key versus unique key? A primary key is the row identity and non-null; a unique
   constraint enforces another candidate key, such as ticket sequence per ticket.
3. Why enforce both Python and database validation? Python gives useful source feedback; database
   constraints protect every writer.
4. Why one transaction? It prevents a failed load leaving partial relational state.
5. What makes a load idempotent? Stable source keys plus `ON CONFLICT DO NOTHING` make the same
   batch safe to rerun.
6. Why are raw tables source-shaped? They preserve lineage and make later transformations explicit.
7. Why an analytics view now instead of tables? It gives a stable query contract without inventing
   Phase 4 transformation logic.
8. Why use a composite unique constraint on status history? It makes event sequence continuous
   validation meaningful and prevents duplicate positions.
9. Mean versus median resolution? Mean reflects total operational burden but is sensitive to long
   tails; median describes a typical ticket.
10. What does a left join find? Missing dimension or reference mappings.
11. Why use `ON CONFLICT DO NOTHING` here? The committed source has stable primary keys, so a rerun
    can safely retain the already-landed row.
12. When would an upsert be preferable? When a source can legitimately correct mutable attributes;
    that semantic is intentionally deferred until Phase 3's incremental design.
13. Why index foreign keys? PostgreSQL does not automatically create the child-side lookup index,
    and parent changes or joins can otherwise scan the child table.
14. Why can an index be absent from a plan? A small table, low selectivity, or stale statistics can
    make a sequential scan cheaper.
15. What does `EXPLAIN ANALYZE` add? It executes the query and reports actual timing and row counts.
16. Why include `BUFFERS`? It shows cache and disk-buffer work, which helps explain I/O cost.
17. What is a CTE? A named query result used to make a multi-step query readable.
18. What does `HAVING` do? It filters grouped results after aggregate values are calculated.
19. Why use `FILTER` on an aggregate? It expresses conditional counts without repeating a `CASE`.
20. What does `NULLIF` avoid in the breach-rate query? Division by zero.
21. Why use `percentile_cont(0.5)`? PostgreSQL's continuous percentile gives a precise median for
    numeric resolution values.
22. What is a window function? It calculates across related rows without collapsing them into one
    grouped row.
23. What does `lag` support here? Month-over-month volume and backlog change.
24. What does `lead` support here? Duration between one status event and the next.
25. Why partition `lead` by ticket? One ticket's final event must never use another ticket's event.
26. What is the grain of a fact table? The real-world meaning of one row; this project has one row
    per ticket and one row per status event.
27. Why define grain before metrics? It prevents duplicated counts after joins.
28. Why is a status-history sequence unique per ticket? It gives an unambiguous lifecycle order.
29. Why validate a final status separately? A valid transition sequence can still end at a status
    inconsistent with the ticket snapshot.
30. Why are unresolved resolution fields null? A fabricated duration or satisfaction score would be
    misleading rather than a zero value.
31. Why is `updated_at` checked against lifecycle timestamps? It must not claim an earlier snapshot
    than an event that has already occurred.
32. Why is the agent/team rule not a simple check constraint? It requires looking up a different
    row in `raw.agents`.
33. What does a quarantine table solve? It preserves invalid source rows and errors for later repair;
    it is planned for Phase 3, not invented in this phase.
34. Why use a manifest checksum? It proves the loaded committed source has not silently changed.
35. Why validate counts as well as checksum? Counts give an immediately understandable completeness
    signal and protect against a malformed manifest.
36. What makes the sample deterministic? Seeded Phase 1 generation and a checksum excluding the
    generation timestamp.
37. Why keep JSON and CSV if Parquet is the loader input? They aid inspection and interchange; typed
    Parquet is safer for database ingestion.
38. Why keep the reset command guarded? Schema drops are destructive even in local development.
39. Why use views in `analytics`? They separate stable consumer names from raw objects while later
    phases decide materialisation and transformation ownership.
40. How would this evolve for production? Add incremental watermarks, quarantine, retries,
    observability, dbt transformations, and credential-managed deployment in their planned phases.

For reviewers, the most important evidence is the DDL, loader transaction, validation SQL, the
integration test suite, and the recorded command results.
