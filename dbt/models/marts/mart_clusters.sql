{{
    config(
        materialized='table',
        description='Clusterizacao de UFs por indicadores educacionais usando Z-Score'
    )
}}

WITH features AS (
    SELECT
        UF,
        ANO,
        NOTA_MEDIA_ENEM,
        RENDA_MEDIA_FAMILIAR,
        PCT_ESCOLAS_INTERNET,
        PCT_ESCOLAS_LABORATORIO,
        ALUNOS_POR_DOCENTE,
        TOTAL_MATRICULAS,
        TOTAL_DOCENTES
    FROM {{ ref('mart_educacao_uf') }}
    WHERE ANO = (SELECT MAX(ANO) FROM {{ ref('mart_educacao_uf') }})
      AND NOTA_MEDIA_ENEM IS NOT NULL
),

normalized AS (
    SELECT
        UF,
        ANO,
        NOTA_MEDIA_ENEM,
        RENDA_MEDIA_FAMILIAR,
        PCT_ESCOLAS_INTERNET,
        (NOTA_MEDIA_ENEM - AVG(NOTA_MEDIA_ENEM) OVER()) / NULLIF(STDDEV(NOTA_MEDIA_ENEM) OVER(), 0) AS Z_NOTA,
        (RENDA_MEDIA_FAMILIAR - AVG(RENDA_MEDIA_FAMILIAR) OVER()) / NULLIF(STDDEV(RENDA_MEDIA_FAMILIAR) OVER(), 0) AS Z_RENDA,
        (PCT_ESCOLAS_INTERNET - AVG(PCT_ESCOLAS_INTERNET) OVER()) / NULLIF(STDDEV(PCT_ESCOLAS_INTERNET) OVER(), 0) AS Z_INFRA
    FROM features
),

clustered AS (
    SELECT
        UF,
        ANO,
        NOTA_MEDIA_ENEM,
        RENDA_MEDIA_FAMILIAR,
        PCT_ESCOLAS_INTERNET,
        Z_NOTA,
        Z_RENDA,
        CASE
            WHEN Z_NOTA > 0.5 AND Z_RENDA > 0.5 THEN 1
            WHEN Z_NOTA > 0 AND Z_RENDA > 0 THEN 2
            WHEN Z_NOTA < 0 AND Z_RENDA > 0 THEN 3
            WHEN Z_NOTA < -0.5 AND Z_RENDA < -0.5 THEN 4
            ELSE 3
        END AS CLUSTER_ID
    FROM normalized
)

SELECT
    c.UF,
    c.ANO,
    c.CLUSTER_ID,
    CASE c.CLUSTER_ID
        WHEN 1 THEN 'Alto Desempenho / Alta Renda'
        WHEN 2 THEN 'Desempenho Medio / Renda Media'
        WHEN 3 THEN 'Baixo Desempenho / Alta Renda (Potencial)'
        WHEN 4 THEN 'Baixo Desempenho / Baixa Renda (Prioritario)'
    END AS DESCRICAO_CLUSTER,
    ROUND(c.NOTA_MEDIA_ENEM, 2) AS NOTA_MEDIA_ENEM,
    ROUND(c.RENDA_MEDIA_FAMILIAR, 2) AS RENDA_MEDIA_FAMILIAR,
    ROUND(c.PCT_ESCOLAS_INTERNET, 2) AS PCT_ESCOLAS_INTERNET,
    ROUND(c.Z_NOTA, 4) AS Z_SCORE_NOTA,
    ROUND(c.Z_RENDA, 4) AS Z_SCORE_RENDA,
    CASE c.CLUSTER_ID
        WHEN 4 THEN 'ALTA'
        WHEN 3 THEN 'MEDIA'
        WHEN 2 THEN 'BAIXA'
        WHEN 1 THEN 'MONITORAMENTO'
    END AS PRIORIDADE_INVESTIMENTO,
    CURRENT_TIMESTAMP() AS DATA_PROCESSAMENTO
FROM clustered c
ORDER BY CLUSTER_ID DESC, UF
