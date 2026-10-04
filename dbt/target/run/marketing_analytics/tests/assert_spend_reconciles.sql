
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  -- Fails if total spend in the gold mart drifts from silver by more than a cent.
select s.total as silver_total, g.total as gold_total
from (select sum(spend_usd) as total from "marketing"."silver"."stg_campaign_spend") s
cross join (select sum(spend_usd) as total from "marketing"."gold"."fct_campaign_performance") g
where abs(s.total - g.total) > 0.01
  
  
      
    ) dbt_internal_test