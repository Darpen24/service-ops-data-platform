select
    category_id,
    subcategory_id,
    count(*) as ticket_count
from {{ ref('fct_tickets') }}
group by 1, 2
