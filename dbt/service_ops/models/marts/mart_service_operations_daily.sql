select
    activity_date,
    sum(ticket_count) as ticket_count,
    avg(average_resolution_minutes) as average_resolution_minutes,
    sum(breached_ticket_count) as breached_ticket_count
from {{ ref('int_team_daily_performance') }}
group by 1
