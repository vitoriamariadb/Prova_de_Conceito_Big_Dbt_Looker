{{
    config(
        materialized='table'
    )
}}

WITH dados_uf AS (
    SELECT
        ANO,
        UF,
        NOTA_MEDIA_ENEM,
        RENDA_MEDIA_FAMILIAR,
        ALUNOS_POR_DOCENTE,
        PCT_ESCOLAS_INTERNET,
        PCT_ESCOLAS_LABORATORIO,
        PCT_ESCOLAS_BIBLIOTECA,
        TOTAL_MATRICULAS,
        TOTAL_DOCENTES
    FROM {{ ref('mart_educacao_uf') }}
    WHERE NOTA_MEDIA_ENEM IS NOT NULL
      AND RENDA_MEDIA_FAMILIAR IS NOT NULL
)

SELECT
    'Renda x Nota ENEM' AS PAR_VARIAVEIS,
    ROUND(CORR(RENDA_MEDIA_FAMILIAR, NOTA_MEDIA_ENEM), 4) AS CORRELACAO,
    COUNT(*) AS N_OBSERVACOES,
    'Correlacao entre renda familiar media e nota media do ENEM por UF' AS INTERPRETACAO

FROM dados_uf

UNION ALL

SELECT
    'Docentes x Nota ENEM' AS PAR_VARIAVEIS,
    ROUND(CORR(ALUNOS_POR_DOCENTE, NOTA_MEDIA_ENEM), 4) AS CORRELACAO,
    COUNT(*) AS N_OBSERVACOES,
    'Correlacao entre razao aluno/docente e nota media do ENEM' AS INTERPRETACAO
FROM dados_uf

UNION ALL

SELECT
    'Internet x Nota ENEM' AS PAR_VARIAVEIS,
    ROUND(CORR(PCT_ESCOLAS_INTERNET, NOTA_MEDIA_ENEM), 4) AS CORRELACAO,
    COUNT(*) AS N_OBSERVACOES,
    'Correlacao entre percentual de escolas com internet e nota ENEM' AS INTERPRETACAO
FROM dados_uf

UNION ALL

SELECT
    'Laboratorio x Nota ENEM' AS PAR_VARIAVEIS,
    ROUND(CORR(PCT_ESCOLAS_LABORATORIO, NOTA_MEDIA_ENEM), 4) AS CORRELACAO,
    COUNT(*) AS N_OBSERVACOES,
    'Correlacao entre percentual de escolas com laboratorio e nota ENEM' AS INTERPRETACAO
FROM dados_uf

UNION ALL

SELECT
    'Biblioteca x Nota ENEM' AS PAR_VARIAVEIS,
    ROUND(CORR(PCT_ESCOLAS_BIBLIOTECA, NOTA_MEDIA_ENEM), 4) AS CORRELACAO,
    COUNT(*) AS N_OBSERVACOES,
    'Correlacao entre percentual de escolas com biblioteca e nota ENEM' AS INTERPRETACAO
FROM dados_uf
