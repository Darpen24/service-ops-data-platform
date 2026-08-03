# Phase 2 PostgreSQL data dictionary

| Object | Grain / key | Purpose | Integrity controls |
| --- | --- | --- | --- |
| `raw.teams` | team | `team_id`, name, region | primary key |
| `raw.agents` | agent | assigned support team | team foreign key |
| `raw.customers` | customer/business unit | requester organisation | primary key |
| `raw.categories` / `raw.subcategories` | category / subcategory | ticket taxonomy | hierarchy foreign key |
| `raw.sla_rules` | priority | SLA target hours | unique priority; positive target |
| `raw.tickets` | ticket | source-shaped operational ticket | keys, status/priority, measures, lifecycle checks |
| `raw.ticket_status_history` | lifecycle event | chronological ticket status event | event key, ticket FK, sequence uniqueness |
| `audit.sample_loads` | generated source batch | loaded manifest checksum and time | unique batch id |

Ticket timestamps use `TIMESTAMPTZ`. `created_at <= first_response_at <= in_progress_at <=
resolved_at <= closed_at` when those terminal timestamps exist; unresolved tickets retain null
resolution, closure, resolution-minutes, and satisfaction values. `updated_at` is never before the
latest lifecycle timestamp. `resolution_minutes`, `reopened_count`, and `escalation_count` cannot
be negative, and satisfaction is 1–5 when supplied.

The analytical views retain those grains: dimensions use their business key, `fct_tickets` is one
ticket, and `fct_ticket_status_events` is one event. See the Phase 1 dictionary for source-column
definitions and the DDL for exact PostgreSQL types.
