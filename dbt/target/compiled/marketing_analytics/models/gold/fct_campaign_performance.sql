-- Daily campaign KPIs: impressions, clicks, conversions, spend, revenue + ratios.
with events as (
    select
        cast(event_ts as date)                                  as activity_date,
        campaign_id,
        channel,
        count(*) filter (where event_type = 'impression')       as impressions,
        count(*) filter (where event_type = 'click')            as clicks,
        count(*) filter (where event_type = 'purchase')         as conversions,
        sum(revenue_usd)                                        as revenue_usd
    from "marketing"."silver"."stg_events"
    group by 1, 2, 3
),
spend as (
    select spend_date as activity_date, campaign_id, sum(spend_usd) as spend_usd
    from "marketing"."silver"."stg_campaign_spend"
    group by 1, 2
)
select
    coalesce(e.activity_date, s.activity_date)                  as activity_date,
    coalesce(e.campaign_id, s.campaign_id)                      as campaign_id,
    e.channel,
    coalesce(e.impressions, 0)                                  as impressions,
    coalesce(e.clicks, 0)                                       as clicks,
    coalesce(e.conversions, 0)                                  as conversions,
    coalesce(s.spend_usd, 0)                                    as spend_usd,
    coalesce(e.revenue_usd, 0)                                  as revenue_usd,
    e.clicks      * 1.0 / nullif(e.impressions, 0)              as ctr,
    e.conversions * 1.0 / nullif(e.clicks, 0)                   as conversion_rate,
    s.spend_usd   / nullif(e.conversions, 0)                    as cost_per_acquisition,
    e.revenue_usd / nullif(s.spend_usd, 0)                      as roas
from events e
full outer join spend s
  on e.activity_date = s.activity_date and e.campaign_id = s.campaign_id