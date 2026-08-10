select
    priority,
    count(*) as ticket_count,
    count(*) filter (where is_sla_breached) as breached_ticket_count,
    {{ safe_divide("count(*) filter (where is_sla_breached)", "count(*)") }} as sla_breach_rate
from {{ ref('fct_tickets') }}
group by 1
