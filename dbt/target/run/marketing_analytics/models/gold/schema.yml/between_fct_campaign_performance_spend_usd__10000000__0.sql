
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
select * from "marketing"."gold"."fct_campaign_performance"
where spend_usd is not null
  and (spend_usd < 0 or spend_usd > 10000000)

  
  
      
    ) dbt_internal_test