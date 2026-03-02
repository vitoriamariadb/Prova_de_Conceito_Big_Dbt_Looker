{% macro gerar_surrogate_key(columns) %}
    {{ return(dbt_utils.generate_surrogate_key(columns)) }}
{% endmacro %}

{% macro current_timestamp_br() %}
    DATETIME(CURRENT_TIMESTAMP(), 'America/Sao_Paulo')
{% endmacro %}

{% macro limpar_texto(column) %}
    TRIM(UPPER({{ column }}))
{% endmacro %}

{% macro pct_calc(numerador, denominador) %}
    ROUND({{ numerador }} / NULLIF({{ denominador }}, 0) * 100, 2)
{% endmacro %}

{% macro safe_divide(numerador, denominador, default_value=0) %}
    COALESCE(SAFE_DIVIDE({{ numerador }}, {{ denominador }}), {{ default_value }})
{% endmacro %}

{% macro classificar_nota_enem(coluna_nota) %}
    CASE
        WHEN {{ coluna_nota }} >= 800 THEN 'Excelente'
        WHEN {{ coluna_nota }} >= 700 THEN 'Muito Bom'
        WHEN {{ coluna_nota }} >= 600 THEN 'Bom'
        WHEN {{ coluna_nota }} >= 500 THEN 'Regular'
        WHEN {{ coluna_nota }} >= 400 THEN 'Abaixo da Media'
        ELSE 'Insuficiente'
    END
{% endmacro %}

{% macro classificar_infraestrutura(pct_internet, pct_lab, pct_biblioteca) %}
    CASE
        WHEN {{ pct_internet }} >= 90 AND {{ pct_lab }} >= 70 AND {{ pct_biblioteca }} >= 80 THEN 'Adequada'
        WHEN {{ pct_internet }} >= 70 AND {{ pct_lab }} >= 50 AND {{ pct_biblioteca }} >= 60 THEN 'Parcial'
        ELSE 'Precaria'
    END
{% endmacro %}

{% macro gerar_faixa_renda(renda) %}
    CASE
        WHEN {{ renda }} IS NULL THEN 'Nao Informado'
        WHEN {{ renda }} <= 1500 THEN 'Ate 1.5 SM'
        WHEN {{ renda }} <= 3000 THEN '1.5 a 3 SM'
        WHEN {{ renda }} <= 6000 THEN '3 a 6 SM'
        WHEN {{ renda }} <= 12000 THEN '6 a 12 SM'
        ELSE 'Acima de 12 SM'
    END
{% endmacro %}

{% macro normalizar_uf(coluna_uf) %}
    UPPER(TRIM({{ coluna_uf }}))
{% endmacro %}
