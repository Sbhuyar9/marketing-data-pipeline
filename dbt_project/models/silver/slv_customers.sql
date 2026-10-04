with ranked as (
    select
        *,
        row_number() over (
            partition by customer_id
            order by _loaded_at desc, _source_file desc
        ) as rn
    from {{ ref('brz_customers') }}
    where customer_id is not null
)

select
    customer_id,
    lower(trim(email))      as email,
    upper(substr(trim(first_name), 1, 1)) || lower(substr(trim(first_name), 2)) as first_name,
    upper(substr(trim(last_name), 1, 1)) || lower(substr(trim(last_name), 2)) as last_name,
    upper(trim(country))    as country,
    signup_date,
    coalesce(marketing_opt_in, false) as marketing_opt_in,
    _loaded_at
from ranked
where rn = 1
