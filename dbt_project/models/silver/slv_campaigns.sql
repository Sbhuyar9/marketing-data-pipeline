-- Silver: cleaned, standardised, de-duplicated (latest load wins).
with ranked as (
    select
        *,
        row_number() over (
            partition by campaign_id
            order by _loaded_at desc, _source_file desc
        ) as rn
    from {{ ref('brz_campaigns') }}
    where campaign_id is not null
)

select
    campaign_id,
    trim(campaign_name)     as campaign_name,
    upper(trim(channel))    as channel,
    start_date,
    end_date,
    budget,
    upper(trim(status))     as status,
    _loaded_at
from ranked
where rn = 1
