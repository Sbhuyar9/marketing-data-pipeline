with ranked as (
    select
        *,
        row_number() over (
            partition by campaign_id, ad_date
            order by _loaded_at desc, _source_file desc
        ) as rn
    from {{ ref('brz_ad_performance') }}
    where campaign_id is not null
      and ad_date is not null
)

select
    campaign_id,
    ad_date,
    impressions,
    clicks,
    spend,
    conversions,
    _loaded_at
from ranked
where rn = 1
  and impressions >= 0
  and clicks >= 0
  and clicks <= impressions
  and spend >= 0
  and conversions >= 0
