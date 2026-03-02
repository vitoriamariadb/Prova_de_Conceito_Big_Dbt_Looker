# Pagina 2: Analise Preditiva

## Titulo
**"Fatores de Sucesso: O Que Influencia o Desempenho Educacional?"**

## Objetivo
Identificar correlacoes entre variaveis de infraestrutura e desempenho educacional, permitindo entender quais fatores mais impactam os resultados.

---

## Metodologia Aplicada

### Regressao Linear (regressao_educacao.py)
Modelo: `Nota ENEM = B0 + B1 x % Escolas com Internet + e`

### Correlacao de Pearson (analise_correlacao_causalidade.py)
Mede a forca da relacao linear entre variaveis (-1 a +1)

---

## Graficos

### 1. Scatter Plot: % Internet vs Nota ENEM

Dispersao com linha de tendencia mostrando a correlacao entre infraestrutura digital e desempenho.

**Fonte BigQuery:** `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`

```sql
SELECT PCT_ESCOLAS_INTERNET, NOTA_MEDIA_ENEM, UF
FROM `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`
WHERE ANO = 2023
```

![Regressao Internet vs Nota](../images/regressao_corporativo.png)

---

### 2. Heatmap: Matriz de Correlacao

Mapa de calor identificando quais variaveis tem maior correlacao com o desempenho.

**Fonte BigQuery:** `provas-de-conceitos.mec_educacao_dev.mart_correlacoes`, `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`

```sql
SELECT * FROM `provas-de-conceitos.mec_educacao_dev.mart_correlacoes`
```

![Matriz de Correlacao](../images/preditiva_heatmap_correlacao.png)

---

### 3. Grafico Combo: Infraestrutura Digital vs Desempenho por UF

Barras (% internet) + linha (nota ENEM) para comparar simultaneamente infraestrutura e desempenho.

**Fonte BigQuery:** `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`

```sql
SELECT UF, PCT_ESCOLAS_INTERNET, NOTA_MEDIA_ENEM
FROM `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`
WHERE ANO = 2023
ORDER BY NOTA_MEDIA_ENEM DESC
```

![Combo Internet e Nota](../images/preditiva_combo_internet_nota.png)

---

### 4. Bullet Chart: Desempenho vs Meta PNE

Cada UF comparada a meta de 550 pontos do PNE, com gap positivo ou negativo.

**Fonte BigQuery:** `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`

```sql
SELECT UF, NOTA_MEDIA_ENEM, 550 AS META_NOTA
FROM `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`
WHERE ANO = 2023
```

![Bullet Desempenho vs Meta](../images/preditiva_bullet_desempenho.png)

---

### 5. Diagrama de Mediacao

Visualizacao das relacoes entre infraestrutura digital, infraestrutura fisica e desempenho educacional com coeficientes de correlacao.

**Fonte BigQuery:** `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`, `provas-de-conceitos.mec_educacao_dev.mart_correlacoes`

![Diagrama de Mediacao](../images/preditiva_diagrama_mediacao.png)

---

### 6. Tabela: Descricao dos Clusters

Resumo dos clusters identificados com quantidade de UFs, media ENEM e percentual de internet.

**Fonte BigQuery:** `provas-de-conceitos.mec_educacao_dev.mart_clusters`, `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`

![Tabela de Clusters](../images/preditiva_tabela_clusters.png)

---

## Narrativa

> **"A analise de regressao revela que o percentual de escolas com internet e um fator fortemente associado ao desempenho no ENEM. Estados com maior conectividade, como DF, SP e SC, apresentam notas consistentemente acima da media nacional."**

> **"A infraestrutura digital atua como variavel-chave: investimentos em conectividade escolar estao diretamente associados a melhores resultados educacionais. Isso sugere que politicas de universalizacao do acesso a internet nas escolas podem ajudar a reduzir desigualdades."**

---

## Cuidados na Interpretacao

**IMPORTANTE:** Correlacao NAO implica causalidade!

- A relacao internet x nota pode ter confundidores
- Dados transversais limitam inferencias causais
- Sempre considere explicacoes alternativas

---

## Perguntas que Esta Pagina Responde

1. Qual a relacao entre infraestrutura digital e desempenho no ENEM?
2. Quais variaveis mais influenciam as notas?
3. O acesso a internet impacta o desempenho?
4. Quais estados estao abaixo da meta de desempenho?
5. Quais grupos de UFs compartilham perfis educacionais semelhantes?

---

## Tabela de Dados (BigQuery)

**Fonte:** `mart_correlacoes`

| Coluna | Descricao |
|--------|-----------|
| VARIAVEL_1 | Primeira variavel |
| VARIAVEL_2 | Segunda variavel |
| CORRELACAO_PEARSON | Coeficiente de correlacao |
| P_VALUE | Significancia estatistica |
| N_OBSERVACOES | Tamanho da amostra |
