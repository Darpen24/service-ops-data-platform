select
    s.subcategory_id,
    s.subcategory_name,
    c.category_id,
    c.category_name
from {{ source('raw', 'subcategories') }} as s
inner join {{ source('raw', 'categories') }} as c on s.category_id = c.category_id
