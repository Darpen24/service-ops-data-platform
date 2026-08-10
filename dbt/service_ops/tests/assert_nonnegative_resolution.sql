select *
from {{ ref('fct_tickets') }}
where resolution_minutes < 0
