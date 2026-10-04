-- Bronze: raw data, typed but otherwise untouched. No filtering, no dedup.
select
    campaign_id,
    campaign_name,
    channel,
    cast(start_date as date)          as start_date,
    cast(end_date as date)            as end_date,
    cast(budget as decimal(18, 2))    as budget,
    status,
    _source_file,
    _loaded_at
from {{ source('raw', 'campaigns') }}
