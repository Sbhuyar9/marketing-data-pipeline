-- Gold total spend must equal Silver spend for known campaigns (no rows lost or double counted).
with gold as (
    select coalesce(sum(total_spend), 0) as gold_total from {{ ref('gold_campaign_performance') }}
),
silver as (
    select coalesce(sum(spend), 0) as silver_total
    from {{ ref('slv_ad_performance') }}
    where campaign_id in (select campaign_id from {{ ref('slv_campaigns') }})
)
select *
from gold cross join silver
where abs(gold_total - silver_total) > 0.01
