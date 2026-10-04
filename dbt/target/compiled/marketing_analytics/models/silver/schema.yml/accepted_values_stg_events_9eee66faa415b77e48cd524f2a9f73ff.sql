
    
    

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


