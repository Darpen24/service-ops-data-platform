{% macro safe_divide(numerator, denominator) %}
    {{ numerator }}::numeric / nullif({{ denominator }}, 0)
{% endmacro %}
