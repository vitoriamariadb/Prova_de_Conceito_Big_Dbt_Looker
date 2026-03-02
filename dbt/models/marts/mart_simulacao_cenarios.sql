{{
    config(
        materialized='table',
        description='Simulacao de cenarios de investimento em educacao com elasticidades baseadas em literatura'
    )
}}

WITH metricas_base AS (
    SELECT
        COUNT(DISTINCT UF) AS TOTAL_UFS,
        SUM(TOTAL_MATRICULAS) AS TOTAL_MATRICULAS_BRASIL,
        AVG(NOTA_MEDIA_ENEM) AS NOTA_MEDIA_NACIONAL,
        AVG(PCT_ESCOLAS_INTERNET) AS PCT_INTERNET_NACIONAL
    FROM {{ ref('mart_educacao_uf') }}
    WHERE ANO = (SELECT MAX(ANO) FROM {{ ref('mart_educacao_uf') }})
),

cenarios AS (
    SELECT 5 AS AUMENTO_PERCENTUAL, 'Conservador' AS TIPO_CENARIO UNION ALL
    SELECT 10, 'Conservador' UNION ALL
    SELECT 15, 'Moderado' UNION ALL
    SELECT 20, 'Moderado' UNION ALL
    SELECT 25, 'Agressivo' UNION ALL
    SELECT 30, 'Agressivo'
)

SELECT
    c.AUMENTO_PERCENTUAL,
    CONCAT(CAST(c.AUMENTO_PERCENTUAL AS STRING), '%') AS CENARIO_NOME,
    c.TIPO_CENARIO,
    m.TOTAL_MATRICULAS_BRASIL,
    m.NOTA_MEDIA_NACIONAL AS NOTA_BASE,
    ROUND(c.AUMENTO_PERCENTUAL * 0.4, 2) AS IMPACTO_NOTA_ENEM_PONTOS,
    ROUND(c.AUMENTO_PERCENTUAL * 0.08, 2) AS REDUCAO_ABANDONO_PCT,
    ROUND(c.AUMENTO_PERCENTUAL * 0.03, 2) AS IMPACTO_IDEB_PONTOS,
    CASE
        WHEN c.AUMENTO_PERCENTUAL <= 10 THEN 'Recomendado - Baixo risco'
        WHEN c.AUMENTO_PERCENTUAL <= 20 THEN 'Moderado - Risco medio'
        ELSE 'Ambicioso - Alto risco fiscal'
    END AS AVALIACAO_RISCO,
    CURRENT_TIMESTAMP() AS DATA_PROCESSAMENTO
FROM cenarios c
CROSS JOIN metricas_base m
ORDER BY c.AUMENTO_PERCENTUAL
