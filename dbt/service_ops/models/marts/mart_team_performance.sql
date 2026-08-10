select
    assigned_team_id,
    count(*) as ticket_count,
    avg(resolution_minutes) as average_resolution_minutes,
    {{ safe_divide("count(*) filter (where is_sla_breached)", "count(*)") }} as sla_breach_rate
from {{ ref('fct_tickets') }}
group by 1
