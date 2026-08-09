select distinct created_at::date as date_key from {{ ref('stg_tickets') }}
