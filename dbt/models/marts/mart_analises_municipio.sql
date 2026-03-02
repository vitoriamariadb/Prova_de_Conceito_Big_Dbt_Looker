{{
    config(
        materialized='table',
        description='Analises agregadas por municipio com texto narrativo para Looker Studio'
    )
}}

WITH educacao AS (
    SELECT * FROM {{ ref('mart_educacao_municipio') }}
    WHERE ANO = (SELECT MAX(ANO) FROM {{ ref('mart_educacao_municipio') }})
),

clusters_uf AS (
    SELECT
        UF,
        ANO,
        CLUSTER_ID,
        DESCRICAO_CLUSTER,
        PRIORIDADE_INVESTIMENTO
    FROM {{ ref('mart_clusters') }}
),

municipios AS (
    SELECT
        CAST(COD_MUNICIPIO_IBGE AS STRING) AS COD_MUNICIPIO_IBGE,
        NOME_MUNICIPIO_IBGE,
        UF,
        REGIAO
    FROM {{ ref('dim_municipios') }}
),

analises AS (
    SELECT
        m.COD_MUNICIPIO_IBGE,
        m.NOME_MUNICIPIO_IBGE AS CIDADE,
        m.UF,
        m.REGIAO,
        e.ANO,

        COALESCE(e.NOTA_MEDIA_ENEM, 0) AS NOTA_MEDIA_ENEM,
        COALESCE(e.PCT_ESCOLAS_INTERNET, 0) AS PCT_ESCOLAS_INTERNET,
        COALESCE(e.ALUNOS_POR_DOCENTE, 0) AS ALUNOS_POR_DOCENTE,
        COALESCE(e.TOTAL_MATRICULAS, 0) AS TOTAL_MATRICULAS,
        COALESCE(e.TOTAL_ESCOLAS, 0) AS TOTAL_ESCOLAS,
        COALESCE(e.RENDA_MEDIA_FAMILIAR, 0) AS RENDA_MEDIA_FAMILIAR,

        ROUND(COALESCE(e.NOTA_MEDIA_ENEM, 0) - AVG(e.NOTA_MEDIA_ENEM) OVER(), 2) AS DIFERENCA_MEDIA_NACIONAL,
        ROUND(PERCENT_RANK() OVER(ORDER BY e.NOTA_MEDIA_ENEM) * 100, 2) AS PERCENTIL_NOTA,

        COALESCE(c.CLUSTER_ID, 3) AS CLUSTER_ID,
        COALESCE(c.DESCRICAO_CLUSTER, 'Sem Classificacao') AS DESCRICAO_CLUSTER,
        COALESCE(c.PRIORIDADE_INVESTIMENTO, 'MEDIA') AS PRIORIDADE_INVESTIMENTO

    FROM municipios m
    LEFT JOIN educacao e
        ON m.COD_MUNICIPIO_IBGE = e.COD_MUNICIPIO
    LEFT JOIN clusters_uf c
        ON m.UF = c.UF AND e.ANO = c.ANO
)

SELECT
    a.*,

    CONCAT(
        a.CIDADE, ' (', a.UF, ') apresenta nota ENEM de ',
        CAST(ROUND(a.NOTA_MEDIA_ENEM, 1) AS STRING), ' pontos, ',
        CASE
            WHEN a.NOTA_MEDIA_ENEM > 620 THEN 'acima da media nacional. '
            WHEN a.NOTA_MEDIA_ENEM > 580 THEN 'proximo a media nacional. '
            WHEN a.NOTA_MEDIA_ENEM > 0 THEN 'abaixo da media nacional. '
            ELSE 'sem dados de ENEM. '
        END,
        CASE
            WHEN a.PCT_ESCOLAS_INTERNET > 90 THEN 'Infraestrutura digital adequada. '
            WHEN a.PCT_ESCOLAS_INTERNET > 70 THEN 'Infraestrutura digital em desenvolvimento. '
            WHEN a.PCT_ESCOLAS_INTERNET > 0 THEN 'Carencia em infraestrutura digital. '
            ELSE ''
        END,
        'Prioridade de investimento: ', a.PRIORIDADE_INVESTIMENTO, '.'
    ) AS TEXTO_ANALISE,

    CASE
        WHEN a.NOTA_MEDIA_ENEM > 650 THEN 'EXCELENTE'
        WHEN a.NOTA_MEDIA_ENEM > 600 THEN 'BOM'
        WHEN a.NOTA_MEDIA_ENEM > 550 THEN 'REGULAR'
        WHEN a.NOTA_MEDIA_ENEM > 0 THEN 'ATENCAO'
        ELSE 'SEM_DADOS'
    END AS CLASSIFICACAO_DESEMPENHO,

    CASE
        WHEN a.PCT_ESCOLAS_INTERNET > 90 AND a.NOTA_MEDIA_ENEM > 600 THEN 'CONSOLIDADO'
        WHEN a.PCT_ESCOLAS_INTERNET > 70 AND a.NOTA_MEDIA_ENEM > 550 THEN 'EM_DESENVOLVIMENTO'
        WHEN a.PCT_ESCOLAS_INTERNET < 50 OR a.NOTA_MEDIA_ENEM < 500 THEN 'PRIORITARIO'
        ELSE 'INTERMEDIARIO'
    END AS STATUS_GERAL,

    a.NOTA_MEDIA_ENEM AS SPARKLINE_NOTA,
    a.PCT_ESCOLAS_INTERNET AS SPARKLINE_INFRA,

    CURRENT_TIMESTAMP() AS DATA_PROCESSAMENTO

FROM analises a
WHERE a.COD_MUNICIPIO_IBGE IS NOT NULL
ORDER BY a.UF, a.CIDADE
