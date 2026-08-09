select customer_id, customer_name, business_unit, region from {{ ref('stg_customers') }}
