-- Parse semi-structured JSON, cast types, standardize IDs, de-duplicate on event_id.
with parsed as (
    select
        cast(json_extract_string(payload_json, '$.event_id') as varchar)                              as event_id,
        cast(json_extract_string(payload_json, '$.event_timestamp') as timestamp)          as event_ts,
        lower(cast(json_extract_string(payload_json, '$.event_type') as varchar))                     as event_type,
        upper(trim(cast(json_extract_string(payload_json, '$.customer_id') as varchar)))              as customer_id,
        cast(json_extract_string(payload_json, '$.campaign_id') as varchar)                           as campaign_id,
        lower(cast(json_extract_string(payload_json, '$.channel') as varchar))                        as channel,
        cast(json_extract_string(payload_json, '$.device.category') as varchar)                       as device_category,
        cast(json_extract_string(payload_json, '$.page.path') as varchar)                             as page_path,
        coalesce(cast(json_extract_string(payload_json, '$.revenue') as double), 0)        as revenue_usd,
        _loaded_at
    from "marketing"."bronze"."ga_events"
)
select * from parsed
where event_id is not null
qualify row_number() over (partition by event_id order by _loaded_at) = 1