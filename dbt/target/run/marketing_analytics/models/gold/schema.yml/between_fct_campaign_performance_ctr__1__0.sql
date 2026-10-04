
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
select * from "marketing"."gold"."fct_campaign_performance"
where ctr is not null
  and (ctr < 0 or ctr > 1)

  
  
      
    ) dbt_internal_test