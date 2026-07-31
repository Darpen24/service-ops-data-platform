# Phase 1 source-data dictionary

All timestamps are ISO 8601 UTC strings. IDs are stable strings. The committed sample is deterministic (`seed=42`, 25 tickets); larger output belongs under ignored `data/raw/`.

| Dataset | Primary key | Relationships | Purpose |
| --- | --- | --- | --- |
| teams | `team_id` | Referenced by agents and tickets | Support ownership and region |
| agents | `agent_id` | `team_id` → teams | Assigned support agent |
| customers | `customer_id` | Referenced by tickets | Business-unit requester |
| categories | `category_id` | Parent of subcategories | High-level issue classification |
| subcategories | `subcategory_id` | `category_id` → categories | Detailed issue classification |
| sla_rules | `sla_rule_id` | One target per priority | SLA target in hours |
| tickets | `ticket_id` | Team, agent, customer, category, subcategory | Incident or service-request source event |
| ticket_status_history | `status_event_id` | `ticket_id` → tickets | Ordered lifecycle event history |

## Tickets

`ticket_id`, `ticket_type`, `created_at`, `updated_at`, `first_response_at`, `resolved_at`, `closed_at`, `priority`, `impact`, `urgency`, `category_id`, `subcategory_id`, `assigned_team_id`, `assigned_agent_id`, `customer_id`, `business_unit`, `region`, `channel`, `status`, `sla_target_hours`, `first_response_minutes`, `resolution_minutes`, `reopened_count`, `escalation_count`, `satisfaction_score`, `short_description`, `source_system`, and `generated_batch_id`.

`resolved_at`, `closed_at`, `resolution_minutes`, and `satisfaction_score` are null for unresolved tickets. Priorities are `P1`–`P4`; statuses are `new`, `assigned`, `in_progress`, `resolved`, and `closed`.

## Intentional defects

Defect mode writes `invalid_tickets.json` separately and never changes clean files. Supported `defect_type` values are `missing_team`, `invalid_priority`, `reversed_timestamp`, `duplicate_ticket_id`, `unknown_category`, and `negative_duration`.
