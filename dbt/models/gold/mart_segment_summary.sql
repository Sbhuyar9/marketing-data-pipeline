select
    segment,
    count(*)                       as customers,
    round(avg(monetary_usd), 2)    as avg_monetary_usd,
    round(avg(frequency), 2)       as avg_frequency,
    round(avg(recency_days), 1)    as avg_recency_days,
    round(sum(monetary_usd), 2)    as total_revenue_usd
from {{ ref('dim_customer_rfm') }}
group by 1
