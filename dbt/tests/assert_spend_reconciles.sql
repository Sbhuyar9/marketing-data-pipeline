-- Fails if total spend in the gold mart drifts from silver by more than a cent.
select s.total as silver_total, g.total as gold_total
from (select sum(spend_usd) as total from {{ ref('stg_campaign_spend') }}) s
cross join (select sum(spend_usd) as total from {{ ref('fct_campaign_performance') }}) g
where abs(s.total - g.total) > 0.01
