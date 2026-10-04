
select * from "marketing"."gold"."fct_campaign_performance"
where spend_usd is not null
  and (spend_usd < 0 or spend_usd > 10000000)
