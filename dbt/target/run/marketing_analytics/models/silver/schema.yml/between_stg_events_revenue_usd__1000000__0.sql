
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
select * from "marketing"."silver"."stg_events"
where revenue_usd is not null
  and (revenue_usd < 0 or revenue_usd > 1000000)

  
  
      
    ) dbt_internal_test