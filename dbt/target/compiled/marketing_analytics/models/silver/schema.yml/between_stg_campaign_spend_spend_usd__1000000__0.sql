
select * from "marketing"."silver"."stg_campaign_spend"
where spend_usd is not null
  and (spend_usd < 0 or spend_usd > 1000000)
