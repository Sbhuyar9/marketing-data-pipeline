
select * from "marketing"."gold"."fct_campaign_performance"
where conversion_rate is not null
  and (conversion_rate < 0 or conversion_rate > 1)
