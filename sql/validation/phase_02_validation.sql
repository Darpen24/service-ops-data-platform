SELECT
    'duplicate_ticket_ids',
    count(*)
FROM (
    SELECT ticket_id FROM raw.tickets
    GROUP BY 1
    HAVING count(*) > 1
) AS d;
SELECT
    'orphan_agents',
    count(*)
FROM raw.agents
LEFT JOIN raw.teams AS t ON agents.team_id = t.team_id
WHERE t.team_id IS NULL;
SELECT
'orphan_subcategories',
count(*)
FROM raw.subcategories
LEFT JOIN raw.categories AS c ON subcategories.category_id = c.category_id
WHERE c.category_id IS NULL;
SELECT
'orphan_tickets',
count(*)
FROM raw.tickets
LEFT JOIN raw.customers AS c ON tickets.customer_id = c.customer_id
WHERE c.customer_id IS NULL;
SELECT
'invalid_priority',
count(*)
FROM raw.tickets
WHERE priority NOT IN ('P1', 'P2', 'P3', 'P4');
SELECT
'invalid_status',
count(*)
FROM raw.tickets
WHERE status NOT IN ('new', 'assigned', 'in_progress', 'resolved', 'closed');
SELECT
'invalid_timestamps',
count(*)
FROM raw.tickets
WHERE
created_at > first_response_at
    OR first_response_at > in_progress_at
    OR resolved_at < in_progress_at
    OR closed_at < resolved_at
    OR updated_at < coalesce(closed_at, resolved_at, in_progress_at);
SELECT
'negative_durations',
count(*)
FROM raw.tickets
WHERE resolution_minutes < 0 OR reopened_count < 0 OR escalation_count < 0;
SELECT
'invalid_satisfaction',
count(*)
FROM raw.tickets
WHERE satisfaction_score NOT BETWEEN 1 AND 5;
SELECT
'agent_team_mismatch',
count(*)
FROM raw.tickets AS t
INNER JOIN raw.agents AS a ON t.assigned_agent_id = a.agent_id
WHERE a.team_id <> t.assigned_team_id;
SELECT
'missing_sla_mapping',
count(*)
FROM raw.tickets
LEFT JOIN raw.sla_rules AS s ON tickets.priority = s.priority
WHERE s.priority IS NULL;
SELECT
'invalid_unresolved',
count(*)
FROM raw.tickets
WHERE
resolved_at IS NULL AND (closed_at IS NOT NULL OR resolution_minutes IS NOT NULL OR satisfaction_score IS NOT NULL);
SELECT
'invalid_history',
count(*)
FROM (SELECT
ticket_id,
sequence,
changed_at,
lag(sequence) OVER w AS previous_sequence,
lag(changed_at) OVER w AS previous_time
FROM raw.ticket_status_history WINDOW w AS (PARTITION BY ticket_id ORDER BY sequence)) AS h
WHERE sequence <> coalesce(previous_sequence, 0) + 1 OR changed_at < previous_time;
SELECT
    'invalid_history_transitions',
    count(*)
FROM (
    SELECT
        status,
        lag(status) OVER (PARTITION BY ticket_id ORDER BY sequence) AS previous_status
    FROM raw.ticket_status_history
) AS h
WHERE (previous_status IS NULL AND status <> 'new')
    OR (previous_status = 'new' AND status <> 'assigned')
    OR (previous_status = 'assigned' AND status <> 'in_progress')
    OR (previous_status = 'in_progress' AND status <> 'resolved')
    OR (previous_status = 'resolved' AND status <> 'closed')
    OR previous_status = 'closed';
SELECT
    'history_final_status_mismatch',
    count(*)
FROM raw.tickets AS t
INNER JOIN (
    SELECT DISTINCT ON (ticket_id)
        ticket_id,
        status
    FROM raw.ticket_status_history
    ORDER BY ticket_id, sequence DESC
) AS h ON t.ticket_id = h.ticket_id
WHERE t.status <> h.status;
SELECT
    'missing_ticket_history',
    count(*)
FROM raw.tickets AS t
LEFT JOIN raw.ticket_status_history AS h ON t.ticket_id = h.ticket_id
WHERE h.ticket_id IS NULL;
