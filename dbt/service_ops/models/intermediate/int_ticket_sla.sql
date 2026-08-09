select
    ticket_id,
    assigned_team_id,
    priority,
    resolution_minutes,
    sla_target_hours,
    resolution_minutes > sla_target_hours * 60 as is_sla_breached
from {{ ref('stg_tickets') }}
