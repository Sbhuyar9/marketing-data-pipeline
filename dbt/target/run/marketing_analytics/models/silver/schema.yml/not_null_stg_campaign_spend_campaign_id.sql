
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select campaign_id
from "marketing"."silver"."stg_campaign_spend"
where campaign_id is null



  
  
      
    ) dbt_internal_test