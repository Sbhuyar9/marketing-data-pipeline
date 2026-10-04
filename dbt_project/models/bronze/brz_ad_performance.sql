select
    campaign_id,
    cast(ad_date as date)             as ad_date,
    cast(impressions as bigint)       as impressions,
    cast(clicks as bigint)            as clicks,
    cast(spend as decimal(18, 2))     as spend,
    cast(conversions as bigint)       as conversions,
    _source_file,
    _loaded_at
from {{ source('raw', 'ad_performance') }}
