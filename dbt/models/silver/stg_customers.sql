-- Keep the most recent CRM record per customer; normalize email/region.
with cleaned as (
    select
        upper(trim(customer_id))              as customer_id,
        lower(trim(email))                    as email,
        first_name,
        last_name,
        lower(trim(region))                   as region,
        cast(signup_date as date)             as signup_date,
        cast(updated_at as timestamp)         as updated_at
    from {{ source('bronze', 'crm_customers') }}
)
select * from cleaned
qualify row_number() over (partition by customer_id order by updated_at desc) = 1
