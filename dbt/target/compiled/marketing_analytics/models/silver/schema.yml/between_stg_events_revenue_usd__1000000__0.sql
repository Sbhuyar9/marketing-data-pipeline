
select * from "marketing"."silver"."stg_events"
where revenue_usd is not null
  and (revenue_usd < 0 or revenue_usd > 1000000)
