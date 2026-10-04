
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        channel as value_field,
        count(*) as n_records

    from "marketing"."silver"."stg_events"
    group by channel

)

select *
from all_values
where value_field not in (
    'paid_search','email','social','display','affiliate'
)



  
  
      
    ) dbt_internal_test