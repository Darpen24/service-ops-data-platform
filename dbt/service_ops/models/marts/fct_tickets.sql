select
    t.*,
    s.is_sla_breached
from {{ ref('stg_tickets') }} as t
inner join {{ ref('int_ticket_sla') }} as s using (ticket_id)
