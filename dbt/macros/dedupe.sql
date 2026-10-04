{% macro latest_row(relation, key, order_by) -%}
  select * from {{ relation }}
  qualify row_number() over (partition by {{ key }} order by {{ order_by }}) = 1
{%- endmacro %}
