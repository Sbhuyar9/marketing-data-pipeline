
select activity_date, campaign_id, count(*) as n
from "marketing"."gold"."fct_campaign_performance"
group by activity_date, campaign_id
having count(*) > 1
