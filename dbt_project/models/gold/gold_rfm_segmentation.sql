-- Gold mart: RFM segmentation of customers with at least one COMPLETED order.
--   Recency   = days between the customer's last order and the latest order in the data
--   Frequency = number of completed orders
--   Monetary  = total completed order value
-- Each dimension is scored 1-5 with NTILE (5 = best); customer_id is the deterministic tie-breaker.
with reference as (
    select max(order_date) as reference_date
    from {{ ref('slv_orders') }}
    where status = 'COMPLETED'
),

customer_orders as (
    select
        customer_id,
        max(order_date)            as last_order_date,
        count(distinct order_id)   as frequency,
        sum(order_amount)          as monetary
    from {{ ref('slv_orders') }}
    where status = 'COMPLETED'
    group by customer_id
),

rfm as (
    select
        co.customer_id,
        co.last_order_date,
        {{ dbt.datediff('co.last_order_date', 'ref.reference_date', 'day') }} as recency_days,
        co.frequency,
        co.monetary
    from customer_orders co
    cross join reference ref
),

scored as (
    select
        *,
        ntile(5) over (order by recency_days desc, customer_id) as r_score,
        ntile(5) over (order by frequency asc,   customer_id)   as f_score,
        ntile(5) over (order by monetary asc,    customer_id)   as m_score
    from rfm
)

select
    s.customer_id,
    cu.email,
    cu.first_name,
    cu.last_name,
    cu.country,
    cu.marketing_opt_in,
    s.last_order_date,
    s.recency_days,
    s.frequency,
    s.monetary,
    s.r_score,
    s.f_score,
    s.m_score,
    concat(cast(s.r_score as varchar), cast(s.f_score as varchar), cast(s.m_score as varchar)) as rfm_code,
    case
        when s.r_score >= 4 and s.f_score >= 4 then 'CHAMPIONS'
        when s.r_score >= 3 and s.f_score >= 3 then 'LOYAL'
        when s.r_score >= 4 and s.f_score <= 2 then 'POTENTIAL_LOYALIST'
        when s.r_score <= 2 and s.f_score >= 3 then 'AT_RISK'
        when s.r_score <= 2 and s.f_score <= 2 then 'HIBERNATING'
        else 'NEEDS_ATTENTION'
    end as segment
from scored s
inner join {{ ref('slv_customers') }} cu
    on cu.customer_id = s.customer_id
