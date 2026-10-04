
    

    create  table
      "marketing"."gold"."dim_customer_rfm__dbt_tmp"
  
    
    as (
      -- RFM segmentation from purchase events. Reference date = latest event in data
-- (keeps results deterministic and backfill-safe).
with ref_date as (select max(event_ts) as as_of from "marketing"."silver"."stg_events"),
purchases as (
    select
        customer_id,
        max(event_ts)       as last_purchase_ts,
        count(*)            as frequency,
        sum(revenue_usd)    as monetary_usd
    from "marketing"."silver"."stg_events"
    where event_type = 'purchase' and customer_id is not null
    group by 1
),
scored as (
    select
        p.*,
        date_diff('day', p.last_purchase_ts, r.as_of)                as recency_days,
        ntile(5) over (order by p.last_purchase_ts asc)              as r_score,
        ntile(5) over (order by p.frequency asc, p.monetary_usd asc) as f_score,
        ntile(5) over (order by p.monetary_usd asc)                  as m_score
    from purchases p cross join ref_date r
)
select
    s.customer_id,
    c.email,
    c.region,
    s.last_purchase_ts,
    s.recency_days,
    s.frequency,
    s.monetary_usd,
    s.r_score, s.f_score, s.m_score,
    cast(s.r_score as varchar) || cast(s.f_score as varchar) || cast(s.m_score as varchar) as rfm_code,
    case
        when s.r_score >= 4 and s.f_score >= 4 and s.m_score >= 4 then 'Champions'
        when s.r_score >= 4 and s.f_score >= 3                    then 'Loyal'
        when s.r_score >= 4                                       then 'Recent'
        when s.r_score <= 2 and s.f_score >= 4                    then 'At Risk'
        when s.r_score <= 2 and s.m_score >= 4                    then 'Cant Lose Them'
        when s.r_score <= 2                                       then 'Hibernating'
        else 'Needs Attention'
    end as segment
from scored s
left join "marketing"."silver"."stg_customers" c using (customer_id)
    );
    
  