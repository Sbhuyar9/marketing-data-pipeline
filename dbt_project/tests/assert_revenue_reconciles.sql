-- Gold attributed revenue must equal Silver completed, campaign-attributed order revenue.
with gold as (
    select coalesce(sum(total_revenue), 0) as gold_total from {{ ref('gold_campaign_performance') }}
),
silver as (
    select coalesce(sum(order_amount), 0) as silver_total
    from {{ ref('slv_orders') }}
    where status = 'COMPLETED'
      and campaign_id in (select campaign_id from {{ ref('slv_campaigns') }})
)
select *
from gold cross join silver
where abs(gold_total - silver_total) > 0.01
