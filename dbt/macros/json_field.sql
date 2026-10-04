{# json_field('payload_json', 'device.category', 'varchar') works on DuckDB and Snowflake #}
{% macro json_field(col, path, dtype='varchar') -%}
  {%- if target.type == 'snowflake' -%}
    {{ col }}:{{ path }}::{{ dtype }}
  {%- else -%}
    cast(json_extract_string({{ col }}, '$.{{ path }}') as {{ dtype }})
  {%- endif -%}
{%- endmacro %}
