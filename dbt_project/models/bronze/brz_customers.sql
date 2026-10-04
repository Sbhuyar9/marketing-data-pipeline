select
    customer_id,
    email,
    first_name,
    last_name,
    country,
    cast(signup_date as date)         as signup_date,
    cast(marketing_opt_in as boolean) as marketing_opt_in,
    _source_file,
    _loaded_at
from {{ source('raw', 'customers') }}
