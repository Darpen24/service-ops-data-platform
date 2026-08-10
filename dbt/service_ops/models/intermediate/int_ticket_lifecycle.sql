select
    ticket_id,
    created_at,
    first_response_at,
    in_progress_at,
    resolved_at,
    closed_at,
    status,
    resolution_minutes,
    first_response_minutes
from {{ ref('stg_tickets') }}
