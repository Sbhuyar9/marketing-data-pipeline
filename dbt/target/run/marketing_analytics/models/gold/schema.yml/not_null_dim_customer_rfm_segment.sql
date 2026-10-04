
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select segment
from "marketing"."gold"."dim_customer_rfm"
where segment is null



  
  
      
    ) dbt_internal_test