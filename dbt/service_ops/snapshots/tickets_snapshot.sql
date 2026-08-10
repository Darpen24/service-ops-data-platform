{% snapshot tickets_snapshot %}
{{
  config(
    target_schema='dbt_snapshots',
    unique_key='ticket_id',
    strategy='timestamp',
    updated_at='updated_at'
  )
}}
select * from {{ source('raw', 'tickets') }}
{% endsnapshot %}
