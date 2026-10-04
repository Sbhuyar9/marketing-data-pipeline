-- Gold mart: one row per campaign with delivery, cost and attributed-revenue KPIs.
with campaigns as (
    select * from {{ ref('slv_campaigns') }}
),

delivery as (
    select
        campaign_id,
        sum(impressions)  as impressions,
        sum(clicks)       as clicks,
        sum(conversions)  as conversions,
        sum(spend)        as total_spend,
        min(ad_date)      as first_ad_date,
        max(ad_date)      as last_ad_date,
        count(*)          as active_days
    from {{ ref('slv_ad_performance') }}
    group by campaign_id
),

revenue as (
    select
        campaign_id,
        count(*)                    as attributed_orders,
        count(distinct customer_id) as attributed_customers,
        sum(order_amount)           as total_revenue
    from {{ ref('slv_orders') }}
    where status = 'COMPLETED'
      and campaign_id is not null
    group by campaign_id
),

joined as (
    select
        c.campaign_id,
        c.campaign_name,
        c.channel,
        c.status,
        c.budget,
        coalesce(d.impressions, 0)          as impressions,
        coalesce(d.clicks, 0)               as clicks,
        coalesce(d.conversions, 0)          as conversions,
        coalesce(d.total_spend, 0)          as total_spend,
        d.first_ad_date,
        d.last_ad_date,
        coalesce(d.active_days, 0)          as active_days,
        coalesce(r.attributed_orders, 0)    as attributed_orders,
        coalesce(r.attributed_customers, 0) as attributed_customers,
        coalesce(r.total_revenue, 0)        as total_revenue
    from campaigns c
    left join delivery d on d.campaign_id = c.campaign_id
    left join revenue  r on r.campaign_id = c.campaign_id
)

select
    *,
    round(cast(clicks as {{ dbt.type_float() }}) / nullif(impressions, 0), 4)   as ctr,
    round(total_spend / nullif(clicks, 0), 4)                                   as cpc,
    round(total_spend / nullif(attributed_orders, 0), 2)                        as cost_per_order,
    round(total_revenue / nullif(total_spend, 0), 4)                            as roas
from joined
