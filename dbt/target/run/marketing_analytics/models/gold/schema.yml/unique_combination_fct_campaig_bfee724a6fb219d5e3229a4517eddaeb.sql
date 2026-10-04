
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
select activity_date, campaign_id, count(*) as n
from "marketing"."gold"."fct_campaign_performance"
group by activity_date, campaign_id
having count(*) > 1

  
  
      
    ) dbt_internal_test