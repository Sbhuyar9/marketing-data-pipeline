
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
select * from "marketing"."silver"."stg_campaign_spend"
where spend_usd is not null
  and (spend_usd < 0 or spend_usd > 1000000)

  
  
      
    ) dbt_internal_test