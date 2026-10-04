select
    order_id,
    customer_id,
    campaign_id,
    cast(order_date as date)          as order_date,
    cast(order_amount as decimal(18, 2)) as order_amount,
    status,
    _source_file,
    _loaded_at
from {{ source('raw', 'orders') }}
