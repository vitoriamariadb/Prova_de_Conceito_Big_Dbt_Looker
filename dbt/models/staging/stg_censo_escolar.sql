-- depends_on: {{ ref('raw_censo_escolar') }}
{{
    config(
        materialized='table'
    )
}}

{% set raw_table_exists = adapter.get_relation(
    database='provas-de-conceitos',
    schema='mec_educacao_dev',
    identifier='raw_censo_escolas'
) %}

{% if raw_table_exists %}

SELECT
    ANO,
    DATA_REFERENCIA,
    UF,
    REGIAO,
    COD_MUNICIPIO,
    NOME_MUNICIPIO,
    COD_ESCOLA,
    NOME_ESCOLA,
    REDE,
    LOCALIZACAO,
    MATRICULAS_TOTAL,
    MATRICULAS_FUNDAMENTAL,
    MATRICULAS_MEDIO,
    DOCENTES_TOTAL,
    TEM_INTERNET,
    TEM_LABORATORIO,
    TEM_BIBLIOTECA,
    TEM_QUADRA,
    DATA_CARGA
FROM {{ ref('raw_censo_escolar') }}

{% else %}

WITH ufs AS (
    SELECT uf, regiao FROM UNNEST([
        STRUCT('AC' AS uf, 'Norte' AS regiao),
        STRUCT('AL', 'Nordeste'),
        STRUCT('AP', 'Norte'),
        STRUCT('AM', 'Norte'),
        STRUCT('BA', 'Nordeste'),
        STRUCT('CE', 'Nordeste'),
        STRUCT('DF', 'Centro-Oeste'),
        STRUCT('ES', 'Sudeste'),
        STRUCT('GO', 'Centro-Oeste'),
        STRUCT('MA', 'Nordeste'),
        STRUCT('MT', 'Centro-Oeste'),
        STRUCT('MS', 'Centro-Oeste'),
        STRUCT('MG', 'Sudeste'),
        STRUCT('PA', 'Norte'),
        STRUCT('PB', 'Nordeste'),
        STRUCT('PR', 'Sul'),
        STRUCT('PE', 'Nordeste'),
        STRUCT('PI', 'Nordeste'),
        STRUCT('RJ', 'Sudeste'),
        STRUCT('RN', 'Nordeste'),
        STRUCT('RS', 'Sul'),
        STRUCT('RO', 'Norte'),
        STRUCT('RR', 'Norte'),
        STRUCT('SC', 'Sul'),
        STRUCT('SP', 'Sudeste'),
        STRUCT('SE', 'Nordeste'),
        STRUCT('TO', 'Norte')
    ])
),

escolas_base AS (
    SELECT
        u.uf AS UF,
        u.regiao AS REGIAO,
        escola_num,
        CONCAT(u.uf, LPAD(CAST(escola_num AS STRING), 6, '0')) AS COD_ESCOLA,
        CONCAT('Escola ', u.uf, ' ', escola_num) AS NOME_ESCOLA,
        CONCAT(u.uf, '00000') AS COD_MUNICIPIO,
        CONCAT('Municipio ', u.uf) AS NOME_MUNICIPIO,
        CASE MOD(escola_num, 4)
            WHEN 0 THEN 'Federal'
            WHEN 1 THEN 'Estadual'
            WHEN 2 THEN 'Municipal'
            ELSE 'Privada'
        END AS REDE,
        CASE WHEN MOD(escola_num, 5) = 0 THEN 'Rural' ELSE 'Urbana' END AS LOCALIZACAO
    FROM ufs u
    CROSS JOIN UNNEST(GENERATE_ARRAY(1, 100)) AS escola_num
),

escolas_com_dados AS (
    SELECT
        2023 AS ANO,
        DATE('2023-01-01') AS DATA_REFERENCIA,
        UF,
        COD_MUNICIPIO,
        NOME_MUNICIPIO,
        COD_ESCOLA,
        NOME_ESCOLA,
        REDE,
        LOCALIZACAO,

        CAST(200 + RAND() * 800 AS INT64) AS MATRICULAS_TOTAL,
        CAST(100 + RAND() * 400 AS INT64) AS MATRICULAS_FUNDAMENTAL,
        CAST(50 + RAND() * 300 AS INT64) AS MATRICULAS_MEDIO,
        CAST(10 + RAND() * 40 AS INT64) AS DOCENTES_TOTAL,

        CASE
            WHEN REGIAO IN ('Sudeste', 'Sul') THEN RAND() > 0.15
            WHEN REGIAO = 'Centro-Oeste' THEN RAND() > 0.25
            ELSE RAND() > 0.40
        END AS TEM_INTERNET,

        CASE
            WHEN REGIAO IN ('Sudeste', 'Sul') THEN RAND() > 0.30
            WHEN REGIAO = 'Centro-Oeste' THEN RAND() > 0.40
            ELSE RAND() > 0.55
        END AS TEM_LABORATORIO,

        RAND() > 0.20 AS TEM_BIBLIOTECA,
        RAND() > 0.35 AS TEM_QUADRA,

        CURRENT_TIMESTAMP() AS DATA_CARGA

    FROM escolas_base
)

SELECT * FROM escolas_com_dados

{% endif %}
