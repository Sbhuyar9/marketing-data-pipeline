with ranked as (
    select
        *,
        row_number() over (
            partition by order_id
            order by _loaded_at desc, _source_file desc
        ) as rn
    from {{ ref('brz_orders') }}
    where order_id is not null
)

select
    order_id,
    customer_id,
    nullif(trim(campaign_id), '') as campaign_id,   -- null = organic / unattributed
    order_date,
    order_amount,
    upper(trim(status))           as status,
    _loaded_at
from ranked
where rn = 1
  and customer_id is not null
  and order_amount >= 0
