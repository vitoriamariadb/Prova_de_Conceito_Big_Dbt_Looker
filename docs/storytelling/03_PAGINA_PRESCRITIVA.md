# Página 3: Análise Prescritiva

## Título
**"Onde Investir? Priorização Inteligente de Recursos Educacionais"**

## Objetivo
Fornecer recomendações acionáveis sobre onde e como investir recursos para maximizar o impacto na educação, utilizando clusterização e simulação de cenários.

> **Safra dos dados:** Censo Escolar e microdados ENEM — referência 2023 (publicação INEP 2024).

---

## Metodologia Aplicada

### Clusterização K-Means (analise_clusterizacao.py)
Agrupa UFs com características educacionais similares para direcionar políticas específicas.

**Variáveis utilizadas:**
- Nota Média ENEM
- % Escolas com Internet
- % Escolas com Laboratório
- Alunos por Docente

### Simulação de Investimentos (analise_impacto_financeiro.py)
Estima o impacto de diferentes níveis de aumento orçamentário nos indicadores.

---

## Gráficos

### 1. Scatter 2D: Clusters de UFs

Dispersão com PCA mostrando os agrupamentos naturais de estados por perfil educacional.

**Fonte:**
```
provas-de-conceitos.mec_educacao_dev.mart_clusters
```

**Título:**
```
Agrupamento de Estados por Perfil Educacional — 2023
```

```sql
SELECT UF, PC1, PC2, CLUSTER_ID, DESCRICAO_CLUSTER
FROM `provas-de-conceitos.mec_educacao_dev.mart_clusters`
```

**Rótulos sugeridos:**

| Elemento | Rótulo exibido |
|----------|----------------|
| Eixo X | Componente Principal 1 (Desempenho) |
| Eixo Y | Componente Principal 2 (Infraestrutura) |
| Dimensão de cor | Cluster |
| Rótulos de ponto | UF |

Cores por cluster:

| Cluster | Descrição | Cor (hex) |
|---------|-----------|-----------|
| 1 | Alto Desempenho | `#1B4F72` |
| 2 | Médio | `#2874A6` |
| 3 | Potencial | `#B7950B` |
| 4 | Prioritário | `#943126` |

**Narrativa:** O scatter revela quatro perfis distintos de estados. O cluster Prioritário (vermelho) concentra UFs com baixo desempenho e baixa infraestrutura — são o ponto de partida para qualquer política de equidade educacional. A distância entre clusters no espaço bidimensional indica o tamanho do esforço necessário para que estados do cluster Prioritário alcancem o perfil do cluster de Alto Desempenho.

![Clusters de UFs](../images/clusters_corporativo.png)

---

### 2. Mapa de Clusters por UF

Visualização geográfica dos clusters educacionais no território brasileiro.

**Fonte:**
```
provas-de-conceitos.mec_educacao_dev.mart_clusters
```

**Título:**
```
Mapa de Perfis Educacionais por Estado — 2023
```

**Rótulos sugeridos:**

| Elemento | Rótulo exibido |
|----------|----------------|
| Dimensão | Estado (UF) |
| Dimensão de cor | Cluster (Perfil Educacional) |

**Narrativa:** A dimensão geográfica dos clusters revela padrões regionais nítidos: estados do Norte e Nordeste tendem ao cluster Prioritário, enquanto Sul e Sudeste concentram os clusters de Alto Desempenho e Médio. Esse padrão não é coincidência — reflete décadas de desigualdade de investimento público em infraestrutura e formação de professores entre as regiões.

![Mapa de Clusters](../images/prescritiva_mapa_clusters.png)

---

### 3. Priorização de Investimentos por UF

Investimento total estimado por estado, colorido por status de desempenho.

**Fonte:**
```
provas-de-conceitos.mec_educacao_dev.mart_alocacao
```

**Título:**
```
Investimento Necessário por Estado — Estimativa 2023
```

```sql
SELECT UF, INVESTIMENTO_TOTAL_ESTIMADO_BRL, STATUS_DESEMPENHO
FROM `provas-de-conceitos.mec_educacao_dev.mart_alocacao`
ORDER BY INVESTIMENTO_TOTAL_ESTIMADO_BRL DESC
```

**Rótulos sugeridos:**

| Elemento | Rótulo exibido |
|----------|----------------|
| Dimensão | Estado (UF) |
| Métrica | Investimento Estimado (R$) |
| Dimensão de cor | Status de Desempenho |

Cores por status:

| Status | Cor (hex) | Significado |
|--------|-----------|-------------|
| CRITICO | `#943126` | Intervenção urgente |
| ATENCAO | `#B7950B` | Monitoramento intensivo |
| REGULAR | `#5DADE2` | Manutenção e aprimoramento |
| ADEQUADO | `#117A65` | Referência e replicação |

**Narrativa:** Estados classificados como CRITICO demandam os maiores volumes de investimento estimado — e são exatamente os que têm menor capacidade fiscal própria para financiar essas melhorias. Isso reforça a necessidade de transferências federais direcionadas, não apenas de fórmulas de partilha per capita que tendem a beneficiar estados mais populosos e com maior base tributária.

![Priorização de Investimentos](../images/investimentos_corporativo.png)

---

### 4. Tabela de Priorização

Ranking de estados por necessidade de investimento com status, gaps de infraestrutura e valores estimados.

**Fonte:**
```
provas-de-conceitos.mec_educacao_dev.mart_alocacao
provas-de-conceitos.mec_educacao_dev.mart_clusters
```

**Título:**
```
Ranking de Priorização de Investimentos por Estado — 2023
```

```sql
SELECT
    a.UF,
    a.STATUS_DESEMPENHO,
    a.GAP_INTERNET_PCT,
    a.GAP_LABORATORIO_PCT,
    a.INVESTIMENTO_TOTAL_ESTIMADO_BRL,
    c.DESCRICAO_CLUSTER
FROM `provas-de-conceitos.mec_educacao_dev.mart_alocacao` a
JOIN `provas-de-conceitos.mec_educacao_dev.mart_clusters` c ON a.UF = c.UF
ORDER BY a.ORDEM_PRIORIDADE
```

**Rótulos sugeridos das colunas:**

| Campo | Rótulo exibido |
|-------|----------------|
| `UF` | Estado |
| `STATUS_DESEMPENHO` | Status |
| `GAP_INTERNET_PCT` | Gap Internet (p.p.) |
| `GAP_LABORATORIO_PCT` | Gap Laboratório (p.p.) |
| `INVESTIMENTO_TOTAL_ESTIMADO_BRL` | Investimento Estimado (R$) |
| `DESCRICAO_CLUSTER` | Perfil do Cluster |

Formatação condicional em `STATUS_DESEMPENHO`:

| Valor | Cor (hex) |
|-------|-----------|
| CRITICO | `#943126` |
| ATENCAO | `#B7950B` |
| REGULAR | `#5DADE2` |
| ADEQUADO | `#117A65` |

**Narrativa:** Esta tabela é a entrega mais acionável do dashboard — um ranking objetivo de onde cada real de investimento terá maior retorno. Os gaps de internet e laboratório em pontos percentuais traduzem déficits abstratos em metas concretas: saber que o Maranhão precisa conectar 38 p.p. mais de suas escolas é mais útil para um gestor do que simplesmente saber que o estado está "abaixo da média".

![Tabela de Priorização](../images/prescritiva_tabela_priorizacao.png)

---

### 5. Simulação de Cenários de Investimento

Impacto estimado de diferentes níveis de aumento orçamentário na nota ENEM e na redução do abandono escolar.

**Fonte:**
```
provas-de-conceitos.mec_educacao_dev.mart_simulacao_cenarios
```

**Título:**
```
Impacto Projetado por Cenário de Investimento
```

```sql
SELECT CENARIO_NOME, AUMENTO_PERCENTUAL, IMPACTO_NOTA_ENEM_PONTOS,
       REDUCAO_ABANDONO_PCT, AVALIACAO_RISCO
FROM `provas-de-conceitos.mec_educacao_dev.mart_simulacao_cenarios`
```

**Rótulos sugeridos:**

| Elemento | Rótulo exibido |
|----------|----------------|
| Dimensão | Cenário de Investimento |
| Métrica 1 | Ganho Estimado no ENEM (pontos) |
| Métrica 2 | Redução Estimada de Abandono (%) |

| Série | Cor (hex) |
|-------|-----------|
| Ganho na Nota ENEM | `#1B4F72` |
| Redução de Abandono | `#117A65` |

**Narrativa:** Os cenários de simulação respondem à pergunta mais frequente de gestores públicos: "quanto preciso investir para ver resultados mensuráveis?" O modelo indica que aumentos acima de +10% no orçamento apresentam retornos decrescentes em nota, mas continuam impactando positivamente a redução de abandono. Isso sugere que, em estados com abandono escolar elevado, a prioridade deve ser permanência antes de desempenho.

![Simulação de Cenários](../images/prescritiva_cenarios.png)

---

### 6. Mapa de Investimento Necessário por UF

Visualização geográfica do investimento estimado por estado.

**Fonte:**
```
provas-de-conceitos.mec_educacao_dev.mart_alocacao
```

**Título:**
```
Mapa de Necessidade de Investimento por Estado — 2023
```

**Rótulos sugeridos:**

| Elemento | Rótulo exibido |
|----------|----------------|
| Dimensão | Estado (UF) |
| Métrica | Investimento Estimado (R$) |
| Escala de cor | Azul claro (baixo) → Vermelho escuro (alto) |

Escala de cor: `#5DADE2` (mínimo) → `#943126` (máximo — maior investimento necessário)

**Narrativa:** O mapa geográfico complementa o ranking da tabela com a dimensão espacial: padrões regionais contínuos (Norte e Nordeste em vermelho) sugerem que soluções regionalizadas — como programas específicos para a Amazônia Legal ou o Semiárido — podem ser mais eficientes do que abordagens estado a estado.

![Mapa de Investimento](../images/prescritiva_mapa_investimento.png)

---

### 7. Gap de Infraestrutura por UF

Comparativo dos gaps de internet e laboratório por estado, com classificação por status.

**Fonte:**
```
provas-de-conceitos.mec_educacao_dev.mart_alocacao
```

**Título:**
```
Déficit de Infraestrutura por Estado — 2023
```

```sql
SELECT UF, GAP_INTERNET_PCT, GAP_LABORATORIO_PCT, STATUS_DESEMPENHO
FROM `provas-de-conceitos.mec_educacao_dev.mart_alocacao`
ORDER BY ORDEM_PRIORIDADE
```

**Rótulos sugeridos:**

| Elemento | Rótulo exibido |
|----------|----------------|
| Dimensão | Estado (UF) |
| Métrica 1 | Gap Internet (pontos percentuais) |
| Métrica 2 | Gap Laboratório (pontos percentuais) |

| Série | Cor (hex) |
|-------|-----------|
| Gap Internet | `#943126` |
| Gap Laboratório | `#B7950B` |

**Narrativa:** O gap de infraestrutura em pontos percentuais é a métrica mais direta para definir metas de programas. Estados onde o gap de internet supera 30 p.p. precisam de uma estratégia de conectividade de longo prazo — não é um problema resolvível com uma rodada de compras de equipamentos. O gap de laboratório tende a ser menor, mas sua associação com o desempenho em ciências é igualmente relevante para o currículo do ENEM.

![Gap de Infraestrutura](../images/prescritiva_bullet_gap.png)

---

## Narrativa Geral da Página

> **"A análise de clusterização identificou grupos distintos de estados. O cluster de intervenção prioritária concentra estados majoritariamente no Norte e Nordeste, que apresentam indicadores significativamente abaixo da média nacional."**

> **"Simulações indicam que aumentos no orçamento educacional podem elevar a nota média do ENEM e reduzir a taxa de abandono. O retorno sobre investimento é mais alto nos estados do cluster prioritário, onde cada real investido gera maior impacto relativo."**

> **"Recomenda-se priorizar investimentos nos estados que apresentam os maiores gaps de infraestrutura e pertencem ao cluster de intervenção prioritária — combinando programas de conectividade, ampliação de laboratórios e formação continuada de professores."**

---

## Perguntas que Esta Página Responde

1. Quais estados têm características educacionais similares?
2. Onde o investimento terá maior impacto?
3. Quanto precisamos investir para atingir a meta?
4. Quais estados estão com maiores gaps de infraestrutura?
5. Qual o impacto esperado para cada cenário de investimento?

---

## Ações Recomendadas

| Cluster | Ação Prioritária | Investimento Sugerido |
|---------|------------------|----------------------|
| Alto Desempenho | Programas de excelência e replicação de boas práticas | Manutenção |
| Médio | Reforço escolar e formação continuada | +5% |
| Potencial | Infraestrutura tecnológica e conectividade | +10% |
| Prioritário | **Intervenção integral: conectividade + laboratório + formação** | **+20%** |

---

## Tabelas de Dados (BigQuery)

**Fonte 1:** `mart_clusters`

| Coluna | Descrição |
|--------|-----------|
| UF | Sigla do estado |
| CLUSTER_ID | Identificador do cluster (1-4) |
| DESCRICAO_CLUSTER | Nome descritivo |
| PC1, PC2 | Componentes principais (PCA) |

**Fonte 2:** `mart_alocacao`

| Coluna | Descrição |
|--------|-----------|
| UF | Sigla do estado |
| ANO | Ano de referência |
| TOTAL_MATRICULAS | Total de matrículas |
| GAP_INTERNET_PCT | Gap de internet em pontos percentuais |
| GAP_LABORATORIO_PCT | Gap de laboratório em pontos percentuais |
| STATUS_DESEMPENHO | Classificação (Crítico, Atenção, Regular, Adequado) |
| INVESTIMENTO_TOTAL_ESTIMADO_BRL | Investimento total estimado em reais |
| ORDEM_PRIORIDADE | Ranking de prioridade |

**Fonte 3:** `mart_simulacao_cenarios`

| Coluna | Descrição |
|--------|-----------|
| CENARIO_NOME | Nome do cenário |
| AUMENTO_PERCENTUAL | Percentual de aumento |
| IMPACTO_NOTA_ENEM_PONTOS | Impacto estimado na nota |
| REDUCAO_ABANDONO_PCT | Redução estimada no abandono |
| AVALIACAO_RISCO | Nível de risco |
