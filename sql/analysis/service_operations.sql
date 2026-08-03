-- 01: Total tickets
SELECT count(*) AS total_tickets FROM analytics.fct_tickets;

-- 02: Tickets created by month
SELECT date_trunc('month', created_at) AS month_start, count(*) AS created_tickets
FROM analytics.fct_tickets
GROUP BY 1
ORDER BY 1;

-- 03: Tickets resolved by month
SELECT date_trunc('month', resolved_at) AS month_start, count(*) AS resolved_tickets
FROM analytics.fct_tickets
WHERE resolved_at IS NOT NULL
GROUP BY 1
ORDER BY 1;

-- 04: Current ticket backlog
SELECT count(*) AS current_backlog
FROM analytics.fct_tickets
WHERE status NOT IN ('resolved', 'closed');

-- 05: Current backlog by priority
SELECT priority, count(*) AS backlog
FROM analytics.fct_tickets
WHERE status NOT IN ('resolved', 'closed')
GROUP BY priority
ORDER BY priority;

-- 06: Backlog ageing by priority
SELECT priority, avg(now() - created_at) AS average_backlog_age
FROM analytics.fct_tickets
WHERE status NOT IN ('resolved', 'closed')
GROUP BY priority;

-- 07: SLA-breached ticket count
SELECT count(*) AS breached_tickets
FROM analytics.fct_tickets
WHERE resolution_minutes > sla_target_hours * 60;

-- 08: SLA breach rate for resolved tickets
SELECT count(*) FILTER (WHERE resolution_minutes > sla_target_hours * 60)::numeric
    / nullif(count(*), 0) AS sla_breach_rate
FROM analytics.fct_tickets
WHERE resolution_minutes IS NOT NULL;

-- 09: Average resolution minutes
SELECT avg(resolution_minutes) AS average_resolution_minutes
FROM analytics.fct_tickets
WHERE resolution_minutes IS NOT NULL;

-- 10: Median resolution minutes
SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY resolution_minutes) AS median_resolution_minutes
FROM analytics.fct_tickets
WHERE resolution_minutes IS NOT NULL;

-- 11: Average first-response minutes
SELECT avg(first_response_minutes) AS average_first_response_minutes
FROM analytics.fct_tickets;

-- 12: Reopen rate
SELECT avg(CASE WHEN reopened_count > 0 THEN 1 ELSE 0 END) AS reopen_rate
FROM analytics.fct_tickets;

-- 13: Escalation rate
SELECT avg(CASE WHEN escalation_count > 0 THEN 1 ELSE 0 END) AS escalation_rate
FROM analytics.fct_tickets;

-- 14: Team satisfaction
SELECT assigned_team_id, avg(satisfaction_score) AS average_satisfaction
FROM analytics.fct_tickets
GROUP BY assigned_team_id;

-- 15: Team ranking by satisfaction
SELECT assigned_team_id, rank() OVER (ORDER BY avg(satisfaction_score) DESC NULLS LAST) AS team_rank
FROM analytics.fct_tickets
GROUP BY assigned_team_id;

-- 16: Category recurrence
SELECT c.category_name, count(*) AS ticket_count
FROM analytics.fct_tickets AS t
INNER JOIN analytics.dim_category AS c ON t.subcategory_id = c.subcategory_id
GROUP BY c.category_name
HAVING count(*) > 0
ORDER BY ticket_count DESC;

-- 17: Month-over-month ticket volume
WITH monthly AS (
    SELECT date_trunc('month', created_at) AS month_start, count(*) AS ticket_volume
    FROM analytics.fct_tickets
    GROUP BY 1
)

SELECT month_start, ticket_volume, ticket_volume - lag(ticket_volume) OVER (ORDER BY month_start)
    AS volume_change
FROM monthly;

-- 18: Monthly backlog change
WITH monthly AS (
    SELECT date_trunc('month', created_at) AS month_start,
        count(*) FILTER (WHERE status NOT IN ('resolved', 'closed')) AS backlog
    FROM analytics.fct_tickets
    GROUP BY 1
)

SELECT month_start, backlog, backlog - lag(backlog) OVER (ORDER BY month_start) AS backlog_change
FROM monthly;

-- 19: Ticket running total and row order
SELECT ticket_id, created_at, row_number() OVER (ORDER BY created_at) AS ticket_order,
    count(*) OVER (ORDER BY created_at) AS running_tickets
FROM analytics.fct_tickets;

-- 20: Duration represented by each lifecycle status
SELECT ticket_id, status, changed_at,
    coalesce(lead(changed_at) OVER (PARTITION BY ticket_id ORDER BY sequence), now()) - changed_at
        AS time_in_status
FROM analytics.fct_ticket_status_events;
