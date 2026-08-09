select
    created_at::date as activity_date,
    assigned_team_id,
    count(*) as ticket_count,
    avg(resolution_minutes) as average_resolution_minutes,
    count(*) filter (where resolution_minutes > sla_target_hours * 60) as breached_ticket_count
from {{ ref('stg_tickets') }}
group by 1, 2
