select
    status_event_id,
    ticket_id,
    status,
    changed_at,
    "sequence" as status_sequence
from {{ source('raw', 'ticket_status_history') }}
