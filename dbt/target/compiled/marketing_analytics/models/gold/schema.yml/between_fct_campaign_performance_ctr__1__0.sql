
select * from "marketing"."gold"."fct_campaign_performance"
where ctr is not null
  and (ctr < 0 or ctr > 1)
