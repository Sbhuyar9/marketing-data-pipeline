select
    cast(spend_date as date)      as spend_date,
    campaign_id,
    cast(spend_usd as double)     as spend_usd
from "marketing"."bronze"."campaign_spend"
qualify row_number() over (partition by spend_date, campaign_id order by _loaded_at desc) = 1