-- Parse semi-structured JSON, cast types, standardize IDs, de-duplicate on event_id.
with parsed as (
    select
        {{ json_field('payload_json', 'event_id') }}                              as event_id,
        {{ json_field('payload_json', 'event_timestamp', 'timestamp') }}          as event_ts,
        lower({{ json_field('payload_json', 'event_type') }})                     as event_type,
        upper(trim({{ json_field('payload_json', 'customer_id') }}))              as customer_id,
        {{ json_field('payload_json', 'campaign_id') }}                           as campaign_id,
        lower({{ json_field('payload_json', 'channel') }})                        as channel,
        {{ json_field('payload_json', 'device.category') }}                       as device_category,
        {{ json_field('payload_json', 'page.path') }}                             as page_path,
        coalesce({{ json_field('payload_json', 'revenue', 'double') }}, 0)        as revenue_usd,
        _loaded_at
    from {{ source('bronze', 'ga_events') }}
)
select * from parsed
where event_id is not null
qualify row_number() over (partition by event_id order by _loaded_at) = 1
