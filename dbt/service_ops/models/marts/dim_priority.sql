select priority, target_hours as sla_target_hours from {{ source('raw', 'sla_rules') }}
