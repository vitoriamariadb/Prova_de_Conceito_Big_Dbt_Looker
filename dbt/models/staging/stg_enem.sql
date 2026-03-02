-- depends_on: {{ ref('raw_enem') }}
{{
    config(
        materialized='table'
    )
}}

{% set raw_table_exists = adapter.get_relation(
    database='provas-de-conceitos',
    schema='mec_educacao_dev',
    identifier='raw_enem_microdados'
) %}

{% if raw_table_exists %}

SELECT
    ID_INSCRICAO,
    ANO,
    DATA_REFERENCIA,
    UF,
    COD_MUNICIPIO,
    SEXO,
    IDADE,
    COR_RACA,
    RENDA_FAMILIAR_ESTIMADA,
    NOTA_CIENCIAS_NATUREZA,
    NOTA_CIENCIAS_HUMANAS,
    NOTA_LINGUAGENS,
    NOTA_MATEMATICA,
    NOTA_REDACAO,
    PRESENTE_TODAS_PROVAS,
    NOTA_MEDIA,
    DATA_CARGA
FROM {{ ref('raw_enem') }}

{% else %}

WITH ufs AS (
    SELECT uf, fator_nota FROM UNNEST([
        STRUCT('AC' AS uf, 0.88 AS fator_nota),
        STRUCT('AL', 0.85),
        STRUCT('AP', 0.87),
        STRUCT('AM', 0.89),
        STRUCT('BA', 0.90),
        STRUCT('CE', 0.92),
        STRUCT('DF', 1.08),
        STRUCT('ES', 1.00),
        STRUCT('GO', 0.98),
        STRUCT('MA', 0.86),
        STRUCT('MT', 0.96),
        STRUCT('MS', 0.97),
        STRUCT('MG', 1.02),
        STRUCT('PA', 0.88),
        STRUCT('PB', 0.91),
        STRUCT('PR', 1.04),
        STRUCT('PE', 0.93),
        STRUCT('PI', 0.89),
        STRUCT('RJ', 1.03),
        STRUCT('RN', 0.90),
        STRUCT('RS', 1.05),
        STRUCT('RO', 0.92),
        STRUCT('RR', 0.88),
        STRUCT('SC', 1.06),
        STRUCT('SP', 1.07),
        STRUCT('SE', 0.89),
        STRUCT('TO', 0.91)
    ])
),

inscricoes_base AS (
    SELECT
        u.uf AS UF,
        u.fator_nota,
        inscricao_num,
        CONCAT('2023', u.uf, LPAD(CAST(inscricao_num AS STRING), 8, '0')) AS ID_INSCRICAO,
        CONCAT(u.uf, '00000') AS COD_MUNICIPIO
    FROM ufs u
    CROSS JOIN UNNEST(GENERATE_ARRAY(1, 500)) AS inscricao_num
),

inscricoes_com_dados AS (
    SELECT
        ID_INSCRICAO,
        2023 AS ANO,
        DATE('2023-01-01') AS DATA_REFERENCIA,
        UF,
        COD_MUNICIPIO,

        CASE WHEN RAND() > 0.45 THEN 'Feminino' ELSE 'Masculino' END AS SEXO,
        CAST(16 + RAND() * 10 AS INT64) AS IDADE,

        CASE CAST(FLOOR(RAND() * 6) AS INT64)
            WHEN 0 THEN 'Branca'
            WHEN 1 THEN 'Preta'
            WHEN 2 THEN 'Parda'
            WHEN 3 THEN 'Parda'
            WHEN 4 THEN 'Amarela'
            ELSE 'Indigena'
        END AS COR_RACA,

        CASE CAST(FLOOR(RAND() * 10) AS INT64)
            WHEN 0 THEN 998
            WHEN 1 THEN 1497
            WHEN 2 THEN 1996
            WHEN 3 THEN 2495
            WHEN 4 THEN 2994
            WHEN 5 THEN 3992
            WHEN 6 THEN 4990
            WHEN 7 THEN 5988
            WHEN 8 THEN 6986
            ELSE 7984
        END AS RENDA_FAMILIAR_ESTIMADA,

        ROUND(400 + (RAND() * 200 + 100) * fator_nota, 2) AS NOTA_CIENCIAS_NATUREZA,
        ROUND(400 + (RAND() * 200 + 100) * fator_nota, 2) AS NOTA_CIENCIAS_HUMANAS,
        ROUND(400 + (RAND() * 200 + 100) * fator_nota, 2) AS NOTA_LINGUAGENS,
        ROUND(400 + (RAND() * 200 + 100) * fator_nota, 2) AS NOTA_MATEMATICA,
        ROUND(400 + (RAND() * 400 + 100) * fator_nota, 2) AS NOTA_REDACAO,

        RAND() > 0.05 AS PRESENTE_TODAS_PROVAS,

        CURRENT_TIMESTAMP() AS DATA_CARGA

    FROM inscricoes_base
),

final AS (
    SELECT
        *,
        ROUND((NOTA_CIENCIAS_NATUREZA + NOTA_CIENCIAS_HUMANAS + NOTA_LINGUAGENS + NOTA_MATEMATICA + NOTA_REDACAO) / 5, 2) AS NOTA_MEDIA
    FROM inscricoes_com_dados
)

SELECT * FROM final

{% endif %}
