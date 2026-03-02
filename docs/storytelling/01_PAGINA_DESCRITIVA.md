# Página 1: Panorama Descritivo

## Título
**"Educação Brasileira em Números: Panorama Nacional"**

## Objetivo
Apresentar uma visão geral da situação educacional no Brasil, permitindo comparações entre estados e análise de tendências.

> **Safra dos dados:** Censo Escolar e microdados ENEM — referência 2023 (publicação INEP 2024).

---

## Gráficos

### 1. Scorecard: Indicadores Nacionais

KPIs principais do painel: total de matrículas, total de escolas, média ENEM e percentual de escolas com internet.

**Fonte:**
```
provas-de-conceitos.mec_educacao_dev.mart_educacao_uf
```

**Título de cada scorecard** (um por KPI):
```
Total de Matrículas
```
```
Total de Escolas
```
```
Média ENEM (0–1000)
```
```
% Escolas Conectadas
```

```sql
SELECT
    SUM(TOTAL_MATRICULAS) AS MATRICULAS,
    SUM(TOTAL_ESCOLAS) AS ESCOLAS,
    AVG(NOTA_MEDIA_ENEM) AS MEDIA_ENEM,
    AVG(PCT_ESCOLAS_INTERNET) AS PCT_INTERNET
FROM `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`
WHERE ANO = 2023
```

| Campo | Rótulo exibido |
|-------|----------------|
| `SUM(TOTAL_MATRICULAS)` | Total de Matrículas |
| `SUM(TOTAL_ESCOLAS)` | Total de Escolas |
| `AVG(NOTA_MEDIA_ENEM)` | Média ENEM (0–1000) |
| `AVG(PCT_ESCOLAS_INTERNET)` | % Escolas Conectadas |

**Narrativa:** Os KPIs nacionais estabelecem a escala do desafio educacional. O percentual de escolas conectadas é o indicador mais crítico: abaixo de 70% sinaliza que uma parcela significativa dos alunos não tem acesso a recursos digitais durante as aulas. Use como ponto de partida para aprofundar por UF nos demais gráficos.

![Scorecard KPIs](../images/descritiva_scorecard.png)

---

### 2. Distribuição de Matrículas por UF

Visualização da concentração de alunos por estado, com intensidade de cor proporcional ao volume.

**Fonte:**
```
provas-de-conceitos.mec_educacao_dev.mart_educacao_uf
```

**Título:**
```
Distribuição de Matrículas por Estado — 2023
```

```sql
SELECT UF, SUM(TOTAL_MATRICULAS) AS MATRICULAS
FROM `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`
WHERE ANO = 2023
GROUP BY UF
```

| Elemento | Rótulo exibido |
|----------|----------------|
| Dimensão | Estado (UF) |
| Métrica | Total de Matrículas |
| Escala de cor | `#5DADE2` (mínimo) → `#1B4F72` (máximo) |

**Narrativa:** SP, MG e BA concentram juntos mais de 40% das matrículas do país. Essa concentração reflete tanto o peso demográfico do Sudeste quanto a extensão territorial do Nordeste. Estados menores do Norte, apesar de populações reduzidas, apresentam desafios logísticos únicos que o volume absoluto de matrículas tende a subestimar.

![Distribuição de Matrículas](../images/descritiva_mapa_matriculas.png)

---

### 3. Total de Matrículas por Região

Comparativo regional com percentuais de concentração de alunos.

**Fonte:**
```
provas-de-conceitos.mec_educacao_dev.mart_educacao_uf
```

**Título:**
```
Matrículas por Região — Brasil 2023
```

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

| Elemento | Rótulo exibido |
|----------|----------------|
| Dimensão | Região |
| Métrica | Total de Matrículas |

Cores por região:

| Região | Cor (hex) |
|--------|-----------|
| Norte | `#943126` |
| Nordeste | `#B7950B` |
| Centro-Oeste | `#117A65` |
| Sudeste | `#1B4F72` |
| Sul | `#5DADE2` |

**Narrativa:** O Sudeste responde por mais da metade das matrículas nacionais, enquanto Norte e Centro-Oeste somados representam menos de 15%. Essa assimetria exige políticas diferenciadas: programas de conectividade e infraestrutura no Norte têm impacto proporcional muito maior por escola atendida do que no Sudeste.

![Matrículas por Região](../images/descritiva_matriculas_regiao.png)

---

### 4. Infraestrutura Escolar por UF

Comparativo de internet e laboratório entre estados.

**Fonte:**
```
provas-de-conceitos.mec_educacao_dev.mart_educacao_uf
```

**Título:**
```
Infraestrutura Digital e Científica por Estado — 2023
```

```sql
SELECT UF, PCT_ESCOLAS_INTERNET, PCT_ESCOLAS_LABORATORIO
FROM `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`
WHERE ANO = 2023
ORDER BY PCT_ESCOLAS_INTERNET DESC
```

| Métrica | Rótulo exibido | Cor (hex) |
|---------|----------------|-----------|
| `PCT_ESCOLAS_INTERNET` | % Escolas com Internet | `#2874A6` |
| `PCT_ESCOLAS_LABORATORIO` | % Escolas com Laboratório | `#117A65` |

**Narrativa:** UFs com menos de 60% de conectividade — especialmente no Norte — concentram os maiores gaps de infraestrutura digital. O gap de laboratório é igualmente crítico: sem equipamentos físicos, o acesso à internet isolado não é suficiente para garantir educação de qualidade em ciências. Estados como MA, PA e AM requerem intervenção simultânea nas duas dimensões.

![Infraestrutura Escolar](../images/descritiva_infraestrutura.png)

---

### 5. Distribuição de Docentes por UF

Total de docentes por estado com cores por região.

**Fonte:**
```
provas-de-conceitos.mec_educacao_dev.mart_educacao_uf
```

**Título:**
```
Distribuição do Corpo Docente por Estado — 2023
```

```sql
SELECT UF, SUM(TOTAL_DOCENTES) AS DOCENTES
FROM `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`
WHERE ANO = 2023
GROUP BY UF
ORDER BY DOCENTES DESC
```

| Elemento | Rótulo exibido |
|----------|----------------|
| Dimensão | Estado (UF) |
| Métrica | Total de Docentes |
| Dimensão de cor | Região (campo calculado `REGIAO`) |

Cores por região:

| Região | Cor (hex) |
|--------|-----------|
| Norte | `#943126` |
| Nordeste | `#B7950B` |
| Centro-Oeste | `#117A65` |
| Sudeste | `#1B4F72` |
| Sul | `#5DADE2` |

**Narrativa:** A distribuição de docentes replica o padrão de matrículas: Sudeste e Nordeste lideram em volume absoluto. Contudo, a relação alunos/docente é o indicador mais relevante para qualidade — estados com grandes contingentes podem ainda ter salas superlotadas. Combine este gráfico com o scorecard de matrículas para calcular a proporção real por UF.

![Distribuição de Docentes](../images/descritiva_docentes.png)

---

### 6. Nota Média ENEM por UF

Ranking de desempenho com linhas de referência para média nacional e meta PNE (550 pontos).

**Fonte:**
```
provas-de-conceitos.mec_educacao_dev.mart_educacao_uf
```

**Título:**
```
Desempenho no ENEM por Estado — 2023
```

```sql
SELECT UF, NOTA_MEDIA_ENEM
FROM `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`
WHERE ANO = 2023
ORDER BY NOTA_MEDIA_ENEM DESC
```

| Elemento | Rótulo exibido |
|----------|----------------|
| Dimensão | Estado (UF) |
| Métrica | Desempenho Médio ENEM (0–1000) |
| Cor das barras | `#2874A6` |
| Linha de referência 1 | Média Nacional |
| Linha de referência 2 | Meta PNE (550 pts) |

**Narrativa:** Apenas um punhado de estados atingem ou superam a meta do PNE de 550 pontos — DF, SC e SP lideram consistentemente. O padrão geográfico é claro: estados do Norte e Nordeste concentram os menores desempenhos, com diferença de até 80 pontos em relação aos líderes nacionais. Esse gap representa anos de defasagem curricular que exigem intervenção estrutural, não apenas programas de reforço.

![Notas ENEM por UF](../images/descritiva_notas_enem.png)

---

## Narrativa Geral da Página

> **"O Brasil possui milhões de alunos matriculados na educação básica. A análise regional revela disparidades significativas: enquanto o Sudeste concentra a maior parte das matrículas, regiões como Norte e Nordeste enfrentam desafios de infraestrutura, com percentuais mais baixos de escolas conectadas à internet. O gap de desempenho no ENEM entre estados líderes e os mais vulneráveis aponta para a necessidade urgente de políticas diferenciadas por território."**

---

## Perguntas que Esta Página Responde

1. Quantos alunos estão matriculados em cada estado?
2. Qual a proporção entre regiões?
3. Quais estados têm melhor infraestrutura escolar?
4. Como se distribui o corpo docente pelo país?
5. Quais UFs estão acima ou abaixo da média no ENEM?

---

## Tabela de Dados (BigQuery)

**Fonte:** `mart_educacao_uf`

| Coluna | Descrição |
|--------|-----------|
| ANO | Ano de referência |
| UF | Sigla do estado |
| TOTAL_MATRICULAS | Soma de matrículas |
| TOTAL_DOCENTES | Soma de docentes |
| TOTAL_ESCOLAS | Total de escolas |
| PCT_ESCOLAS_INTERNET | % de escolas com internet |
| PCT_ESCOLAS_LABORATORIO | % de escolas com laboratório |
| NOTA_MEDIA_ENEM | Média do ENEM por UF |
