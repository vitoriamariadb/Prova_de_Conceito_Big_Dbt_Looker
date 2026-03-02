# Pagina 1: Panorama Descritivo

## Titulo
**"Educacao Brasileira em Numeros: Panorama Nacional"**

## Objetivo
Apresentar uma visao geral da situacao educacional no Brasil, permitindo comparacoes entre estados e analise de tendencias.

---

## Graficos

### 1. Scorecard: Indicadores Nacionais

KPIs principais do painel: total de matriculas, total de escolas, media ENEM e percentual de escolas com internet.

**Fonte BigQuery:** `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`

```sql
SELECT
    SUM(TOTAL_MATRICULAS) AS MATRICULAS,
    SUM(TOTAL_ESCOLAS) AS ESCOLAS,
    AVG(NOTA_MEDIA_ENEM) AS MEDIA_ENEM,
    AVG(PCT_ESCOLAS_INTERNET) AS PCT_INTERNET
FROM `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`
WHERE ANO = 2023
```

![Scorecard KPIs](../images/descritiva_scorecard.png)

---

### 2. Distribuicao de Matriculas por UF

Visualizacao da concentracao de alunos por estado, com cores por regiao.

**Fonte BigQuery:** `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`

```sql
SELECT UF, SUM(TOTAL_MATRICULAS) AS MATRICULAS
FROM `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`
WHERE ANO = 2023
GROUP BY UF
```

![Distribuicao de Matriculas](../images/descritiva_mapa_matriculas.png)

---

### 3. Total de Matriculas por Regiao

Comparativo regional com percentuais de concentracao de alunos.

**Fonte BigQuery:** `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`

```sql
SELECT
    CASE
        WHEN UF IN ('AC','AP','AM','PA','RO','RR','TO') THEN 'Norte'
        WHEN UF IN ('AL','BA','CE','MA','PB','PE','PI','RN','SE') THEN 'Nordeste'
        WHEN UF IN ('DF','GO','MT','MS') THEN 'Centro-Oeste'
        WHEN UF IN ('ES','MG','RJ','SP') THEN 'Sudeste'
        WHEN UF IN ('PR','RS','SC') THEN 'Sul'
    END AS REGIAO,
    SUM(TOTAL_MATRICULAS) AS MATRICULAS
FROM `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`
WHERE ANO = 2023
GROUP BY 1
```

![Matriculas por Regiao](../images/descritiva_matriculas_regiao.png)

---

### 4. Infraestrutura Escolar por UF

Comparativo de internet e laboratorio entre estados.

**Fonte BigQuery:** `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`

```sql
SELECT UF, PCT_ESCOLAS_INTERNET, PCT_ESCOLAS_LABORATORIO
FROM `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`
WHERE ANO = 2023
ORDER BY PCT_ESCOLAS_INTERNET DESC
```

![Infraestrutura Escolar](../images/descritiva_infraestrutura.png)

---

### 5. Distribuicao de Docentes por UF

Total de docentes por estado com cores por regiao.

**Fonte BigQuery:** `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`

```sql
SELECT UF, SUM(TOTAL_DOCENTES) AS DOCENTES
FROM `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`
WHERE ANO = 2023
GROUP BY UF
ORDER BY DOCENTES DESC
```

![Distribuicao de Docentes](../images/descritiva_docentes.png)

---

### 6. Nota Media ENEM por UF

Ranking de desempenho com linhas de referencia para media nacional e meta PNE (550 pontos).

**Fonte BigQuery:** `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`

```sql
SELECT UF, NOTA_MEDIA_ENEM
FROM `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`
WHERE ANO = 2023
ORDER BY NOTA_MEDIA_ENEM DESC
```

![Notas ENEM por UF](../images/descritiva_notas_enem.png)

---

## Narrativa

> **"O Brasil possui milhoes de alunos matriculados na educacao basica. A analise regional revela disparidades significativas: enquanto o Sudeste concentra a maior parte das matriculas, regioes como Norte e Nordeste enfrentam desafios de infraestrutura, com percentuais mais baixos de escolas conectadas a internet."**

---

## Perguntas que Esta Pagina Responde

1. Quantos alunos estao matriculados em cada estado?
2. Qual a proporcao entre regioes?
3. Quais estados tem melhor infraestrutura escolar?
4. Como se distribui o corpo docente pelo pais?
5. Quais UFs estao acima ou abaixo da media no ENEM?

---

## Tabela de Dados (BigQuery)

**Fonte:** `mart_educacao_uf`

| Coluna | Descricao |
|--------|-----------|
| ANO | Ano de referencia |
| UF | Sigla do estado |
| TOTAL_MATRICULAS | Soma de matriculas |
| TOTAL_DOCENTES | Soma de docentes |
| TOTAL_ESCOLAS | Total de escolas |
| PCT_ESCOLAS_INTERNET | % de escolas com internet |
| PCT_ESCOLAS_LABORATORIO | % de escolas com laboratorio |
| NOTA_MEDIA_ENEM | Media do ENEM por UF |
