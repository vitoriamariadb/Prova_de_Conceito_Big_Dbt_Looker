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
    CASE
        WHEN UF IN ('AC','AP','AM','PA','RO','RR','TO') THEN 'Norte'
        WHEN UF IN ('AL','BA','CE','MA','PB','PE','PI','RN','SE') THEN 'Nordeste'
        WHEN UF IN ('DF','GO','MT','MS') THEN 'Centro-Oeste'
        WHEN UF IN ('ES','MG','RJ','SP') THEN 'Sudeste'
        WHEN UF IN ('PR','RS','SC') THEN 'Sul'
        ELSE 'Desconhecida'
    END AS REGIAO,
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
    SELECT uf, nota_base, renda_base FROM UNNEST([
        -- Norte: baixo desempenho, baixa renda → Cluster 4 (Prioritário)
        STRUCT('AC' AS uf, 508.0 AS nota_base, 1200.0 AS renda_base),
        STRUCT('AP', 502.0, 1150.0),
        STRUCT('AM', 510.0, 1250.0),
        STRUCT('PA', 505.0, 1180.0),
        STRUCT('RO', 520.0, 1350.0),
        STRUCT('RR', 500.0, 1100.0),
        STRUCT('TO', 518.0, 1300.0),
        -- Nordeste baixo → Cluster 4
        STRUCT('AL', 500.0, 1100.0),
        STRUCT('MA', 492.0, 1050.0),
        STRUCT('PI', 496.0, 1080.0),
        -- Nordeste médio → Cluster 3 (Potencial)
        STRUCT('BA', 516.0, 1280.0),
        STRUCT('CE', 526.0, 1380.0),
        STRUCT('PB', 520.0, 1220.0),
        STRUCT('PE', 524.0, 1320.0),
        STRUCT('RN', 522.0, 1240.0),
        STRUCT('SE', 518.0, 1200.0),
        -- Centro-Oeste médio → Cluster 2 (Médio)
        STRUCT('GO', 540.0, 2050.0),
        STRUCT('MT', 540.0, 1980.0),
        STRUCT('MS', 542.0, 2020.0),
        STRUCT('ES', 544.0, 2200.0),
        -- Sudeste/Sul alto → Cluster 1 (Alto Desempenho)
        STRUCT('MG', 558.0, 2450.0),
        STRUCT('RJ', 560.0, 2700.0),
        STRUCT('PR', 565.0, 2550.0),
        STRUCT('RS', 570.0, 2650.0),
        STRUCT('SC', 575.0, 2750.0),
        STRUCT('SP', 585.0, 3200.0),
        STRUCT('DF', 600.0, 3500.0)
    ])
),

inscricoes_base AS (
    SELECT
        u.uf AS UF,
        u.nota_base,
        u.renda_base,
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
        CASE
            WHEN UF IN ('AC','AP','AM','PA','RO','RR','TO') THEN 'Norte'
            WHEN UF IN ('AL','BA','CE','MA','PB','PE','PI','RN','SE') THEN 'Nordeste'
            WHEN UF IN ('DF','GO','MT','MS') THEN 'Centro-Oeste'
            WHEN UF IN ('ES','MG','RJ','SP') THEN 'Sudeste'
            WHEN UF IN ('PR','RS','SC') THEN 'Sul'
            ELSE 'Desconhecida'
        END AS REGIAO,
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

        GREATEST(500, ROUND(renda_base + (RAND() - 0.5) * renda_base * 0.4, 0)) AS RENDA_FAMILIAR_ESTIMADA,

        ROUND(nota_base + (RAND() - 0.5) * 80, 2) AS NOTA_CIENCIAS_NATUREZA,
        ROUND(nota_base + (RAND() - 0.5) * 80, 2) AS NOTA_CIENCIAS_HUMANAS,
        ROUND(nota_base + (RAND() - 0.5) * 80, 2) AS NOTA_LINGUAGENS,
        ROUND(nota_base + (RAND() - 0.5) * 80, 2) AS NOTA_MATEMATICA,
        ROUND(nota_base + (RAND() - 0.5) * 100, 2) AS NOTA_REDACAO,

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
