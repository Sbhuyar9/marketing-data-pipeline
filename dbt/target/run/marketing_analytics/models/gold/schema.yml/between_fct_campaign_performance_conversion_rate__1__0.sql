
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
select * from "marketing"."gold"."fct_campaign_performance"
where conversion_rate is not null
  and (conversion_rate < 0 or conversion_rate > 1)

  
  
      
    ) dbt_internal_test