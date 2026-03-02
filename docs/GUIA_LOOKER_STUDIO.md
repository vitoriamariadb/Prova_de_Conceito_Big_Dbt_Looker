# Guia: Dashboard Educação MEC no Looker Studio

## Conexão com BigQuery

### Acesso
1. Acesse [lookerstudio.google.com](https://lookerstudio.google.com)
2. Clique em **Criar** > **Relatório**
3. Selecione **BigQuery** como fonte de dados
4. Autorize o acesso à sua conta Google
5. Navegue até: Projeto `provas-de-conceitos` > Dataset `mec_educacao_dev`

### Tabelas Disponíveis

| Tabela | Uso |
|--------|-----|
| `mart_educacao_uf` | Análise descritiva por UF |
| `mart_educacao_municipio` | Filtros por município |
| `mart_analises_municipio` | Textos narrativos (storytelling) |
| `mart_clusters` | Clusterização de UFs |
| `mart_correlacoes` | Correlações entre variáveis |
| `mart_alocacao` | Priorização de investimentos |
| `mart_simulacao_cenarios` | Simulação de cenários |

---

## Campo Calculado: REGIAO

Crie este campo calculado em todas as fontes que usem a coluna `UF`. No Looker Studio, clique em **Adicionar campo** > **Campo calculado** e cole:

```sql
CASE
    WHEN UF IN ('AC','AP','AM','PA','RO','RR','TO') THEN 'Norte'
    WHEN UF IN ('AL','BA','CE','MA','PB','PE','PI','RN','SE') THEN 'Nordeste'
    WHEN UF IN ('DF','GO','MT','MS') THEN 'Centro-Oeste'
    WHEN UF IN ('ES','MG','RJ','SP') THEN 'Sudeste'
    WHEN UF IN ('PR','RS','SC') THEN 'Sul'
END
```

Nomeie o campo como `REGIAO`. Use este campo sempre que precisar da dimensão região em qualquer gráfico.

---

## Configuração Geral

### Dimensões do Relatório
- **Largura**: 1588 px | **Altura**: 2246 px
- **Orientação**: Retrato (ideal para PDF)
- Configurar em: Menu **Arquivo** > **Configurações do relatório** > **Tamanho personalizado**

### Paleta de Cores
```
Azul Escuro:      #1B4F72
Azul Médio:       #2874A6
Azul Claro:       #5DADE2
Verde:            #117A65
Amarelo/Dourado:  #B7950B
Vermelho:         #943126
Fundo:            #F8F9F9
Texto:            #2C3E50
```
Aplicar em: Menu **Tema** > **Personalizar tema**

### Filtros (aplicar em todas as páginas)
- [ ] Filtro por **Ano** (lista suspensa, seleção única)
- [ ] Filtro por **UF** (lista suspensa, seleção múltipla, pesquisa habilitada)
- [ ] Filtro por **Município** (lista suspensa, fonte: `mart_analises_municipio`, campo: `CIDADE`)
- [ ] Filtro por **Região** (caixa de seleção: Norte, Nordeste, Centro-Oeste, Sudeste, Sul)

---

## Página 1: Resumo Executivo

### Checklist

- [ ] Título da página:
  ```
  Painel de Indicadores Educacionais - MEC/INEP
  ```
- [ ] Subtítulo com ano de referência dos dados

---

#### Scorecards — 4 KPIs

**Tabela BigQuery**: `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`

| KPI | Campo | Rótulo exibido |
|-----|-------|----------------|
| Matrículas | `SUM(TOTAL_MATRICULAS)` | Total de Matrículas |
| Escolas | `SUM(TOTAL_ESCOLAS)` | Total de Escolas |
| ENEM | `AVG(NOTA_MEDIA_ENEM)` | Média ENEM (0–1000) |
| Internet | `AVG(PCT_ESCOLAS_INTERNET)` | % Escolas Conectadas |

![Scorecards KPIs](images/descritiva_scorecard.png)

---

#### Mapa geográfico — Matrículas por UF

**Tabela BigQuery**: `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`

**Título do gráfico:**
```
Distribuição de Matrículas por Estado — 2023
```

| Configuração | Valor |
|-------------|-------|
| Tipo | Mapa geográfico |
| Dimensão | `UF` |
| Métrica | `SUM(TOTAL_MATRICULAS)` — rótulo: *Total de Matrículas* |
| Escala de cor | `#5DADE2` (mínimo) → `#1B4F72` (máximo) |

![Mapa Matrículas por UF](images/descritiva_mapa_matriculas.png)

---

#### Tabela resumo — Top UFs

**Tabela BigQuery**: `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`

**Título do gráfico:**
```
Ranking de Estados por Desempenho no ENEM — 2023
```

| Configuração | Valor |
|-------------|-------|
| Top 5 melhores | Ordenar por `NOTA_MEDIA_ENEM` decrescente |
| Top 5 críticos | Ordenar por `NOTA_MEDIA_ENEM` crescente |
| Rodapé | Dados: INEP/MEC - Censo Escolar e ENEM 2023 |

---

## Página 2: Análise Descritiva

### Checklist

- [ ] Título da página:
  ```
  Análise Descritiva por Unidade Federativa
  ```

---

#### Gráfico 1 — Matrículas por Região

**Tabela BigQuery**: `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`

**Título do gráfico:**
```
Matrículas por Região — Brasil 2023
```

| Configuração | Valor |
|-------------|-------|
| Tipo | Barras horizontal |
| Dimensão | `REGIAO` (campo calculado — veja seção Campo Calculado acima) |
| Métrica | `SUM(TOTAL_MATRICULAS)` — rótulo: *Total de Matrículas* |
| Ordenação | Decrescente |

Cores por região (uma cor por barra):

| Região | Cor (hex) |
|--------|-----------|
| Norte | `#943126` |
| Nordeste | `#B7950B` |
| Centro-Oeste | `#117A65` |
| Sudeste | `#1B4F72` |
| Sul | `#5DADE2` |

![Matrículas por Região](images/descritiva_matriculas_regiao.png)

---

#### Gráfico 2 — Infraestrutura por UF

**Tabela BigQuery**: `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`

**Título do gráfico:**
```
Infraestrutura Digital e Científica por Estado — 2023
```

| Configuração | Valor |
|-------------|-------|
| Tipo | Barras agrupadas |
| Dimensão | `UF` — rótulo: *Estado (UF)* |

| Métrica | Rótulo exibido | Cor (hex) |
|---------|----------------|-----------|
| `AVG(PCT_ESCOLAS_INTERNET)` | % Escolas com Internet | `#2874A6` |
| `AVG(PCT_ESCOLAS_LABORATORIO)` | % Escolas com Laboratório | `#117A65` |

![Infraestrutura por UF](images/descritiva_infraestrutura.png)

---

#### Gráfico 3 — Distribuição de Docentes

**Tabela BigQuery**: `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`

**Título do gráfico:**
```
Distribuição do Corpo Docente por Estado — 2023
```

| Configuração | Valor |
|-------------|-------|
| Tipo | Barras horizontal |
| Dimensão | `UF` — rótulo: *Estado (UF)* |
| Métrica | `SUM(TOTAL_DOCENTES)` — rótulo: *Total de Docentes* |
| Dimensão de cor | `REGIAO` (campo calculado) |

Cores por região (use o campo calculado `REGIAO` como dimensão de cor):

| Região | Cor (hex) |
|--------|-----------|
| Norte | `#943126` |
| Nordeste | `#B7950B` |
| Centro-Oeste | `#117A65` |
| Sudeste | `#1B4F72` |
| Sul | `#5DADE2` |

![Distribuição de Docentes](images/descritiva_docentes.png)

---

#### Gráfico 4 — Notas ENEM por UF

**Tabela BigQuery**: `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`

**Título do gráfico:**
```
Desempenho no ENEM por Estado — 2023
```

| Configuração | Valor |
|-------------|-------|
| Tipo | Barras vertical |
| Dimensão | `UF` — rótulo: *Estado (UF)* |
| Métrica | `AVG(NOTA_MEDIA_ENEM)` — rótulo: *Desempenho Médio ENEM (0–1000)* |
| Linha de referência 1 | Média nacional — `AVG(NOTA_MEDIA_ENEM)` de todo o Brasil |
| Linha de referência 2 | Meta PNE: 550 pontos |
| Cor das barras | `#2874A6` |

![Notas ENEM por UF](images/descritiva_notas_enem.png)

---

## Página 3: Análise Preditiva

### Checklist

- [ ] Título da página:
  ```
  Análise Preditiva — Clusters e Correlações
  ```

---

#### Gráfico 1 — Clusters de UFs (Scatter)

**Tabela BigQuery**: `provas-de-conceitos.mec_educacao_dev.mart_clusters`

**Título do gráfico:**
```
Agrupamento de Estados por Perfil Educacional — 2023
```

| Configuração | Valor |
|-------------|-------|
| Tipo | Dispersão (Scatter) |
| Eixo X | `Z_SCORE_NOTA` — rótulo: *Componente Principal 1 (Desempenho)* |
| Eixo Y | `Z_SCORE_RENDA` — rótulo: *Componente Principal 2 (Infraestrutura)* |
| Dimensão de cor | `CLUSTER_ID` — rótulo: *Cluster* |
| Rótulos de ponto | `UF` |

Cores por cluster:

| Cluster | Descrição | Cor (hex) |
|---------|-----------|-----------|
| 1 | Alto Desempenho | `#1B4F72` |
| 2 | Médio | `#2874A6` |
| 3 | Potencial | `#B7950B` |
| 4 | Prioritário | `#943126` |

![Clusters de UFs](images/clusters_corporativo.png)

---

#### Gráfico 2 — Correlação Nota x Infraestrutura (Scatter com tendência)

**Tabela BigQuery**: `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`

**Título do gráfico:**
```
Conectividade Escolar vs. Desempenho no ENEM — 2023
```

| Configuração | Valor |
|-------------|-------|
| Tipo | Dispersão com linha de tendência |
| Eixo X | `PCT_ESCOLAS_INTERNET` — rótulo: *% Escolas Conectadas à Internet* |
| Eixo Y | `NOTA_MEDIA_ENEM` — rótulo: *Desempenho Médio ENEM (0–1000)* |
| Rótulos de ponto | `UF` |
| Cor dos pontos | `#2874A6` |
| Linha de tendência | Regressão linear — habilitar em Estilo > Série |

![Regressão Internet vs Nota](images/regressao_corporativo.png)

---

#### Gráfico 3 — Matriz de Correlação (Heatmap)

**Tabela BigQuery**: `provas-de-conceitos.mec_educacao_dev.mart_correlacoes`

**Título do gráfico:**
```
Matriz de Correlação entre Indicadores Educacionais
```

| Configuração | Valor |
|-------------|-------|
| Tipo | Tabela com formatação condicional (heatmap) |
| Dimensão | `PAR_VARIAVEIS` — rótulo: *Par de Variáveis* |
| Métrica | `CORRELACAO` — rótulo: *Correlação de Pearson* |

Escala de cor condicional:

| Valor | Cor (hex) | Significado |
|-------|-----------|-------------|
| -1.0 | `#943126` | Correlação negativa forte |
| 0.0 | `#F8F9F9` | Sem correlação |
| +1.0 | `#1B4F72` | Correlação positiva forte |

![Matriz de Correlação](images/preditiva_heatmap_correlacao.png)

---

#### Tabela — Descrição dos Clusters

**Tabela BigQuery**: `provas-de-conceitos.mec_educacao_dev.mart_clusters`

**Título do gráfico:**
```
Perfis de Clusters Educacionais — Resumo por Grupo
```

| Campo | Rótulo exibido |
|-------|----------------|
| `CLUSTER_ID` | Cluster |
| `DESCRICAO_CLUSTER` | Perfil do Grupo |
| `COUNT(UF)` | Nº de Estados |
| `AVG(NOTA_MEDIA_ENEM)` | Média ENEM (0–1000) |
| `PRIORIDADE_INVESTIMENTO` | Prioridade |

Formatação condicional em `PRIORIDADE_INVESTIMENTO`:

| Valor | Cor (hex) |
|-------|-----------|
| ALTA | `#943126` |
| MEDIA | `#B7950B` |
| BAIXA | `#117A65` |
| MONITORAMENTO | `#2874A6` |

![Tabela de Clusters](images/preditiva_tabela_clusters.png)

---

## Página 4: Análise Prescritiva

### Checklist

- [ ] Título da página:
  ```
  Análise Prescritiva — Priorização de Investimentos
  ```

---

#### Gráfico 1 — Priorização de Investimentos por UF

**Tabela BigQuery**: `provas-de-conceitos.mec_educacao_dev.mart_alocacao`

**Título do gráfico:**
```
Investimento Necessário por Estado — Estimativa 2023
```

| Configuração | Valor |
|-------------|-------|
| Tipo | Barras horizontal |
| Dimensão | `UF` — rótulo: *Estado (UF)* |
| Métrica | `INVESTIMENTO_TOTAL_ESTIMADO_BRL` — rótulo: *Investimento Estimado (R$)* |
| Dimensão de cor | `STATUS_DESEMPENHO` — rótulo: *Status de Desempenho* |

Cores por status:

| Status | Cor (hex) |
|--------|-----------|
| CRITICO | `#943126` |
| ATENCAO | `#B7950B` |
| REGULAR | `#5DADE2` |
| ADEQUADO | `#117A65` |

![Priorização de Investimentos](images/investimentos_corporativo.png)

---

#### Gráfico 2 — Simulação de Cenários

**Tabela BigQuery**: `provas-de-conceitos.mec_educacao_dev.mart_simulacao_cenarios`

**Título do gráfico:**
```
Impacto Projetado por Cenário de Investimento
```

| Configuração | Valor |
|-------------|-------|
| Tipo | Barras vertical agrupadas |
| Dimensão | `CENARIO_NOME` — rótulo: *Cenário de Investimento* |

| Métrica | Rótulo exibido | Cor (hex) |
|---------|----------------|-----------|
| `IMPACTO_NOTA_ENEM_PONTOS` | Ganho Estimado no ENEM (pontos) | `#1B4F72` |
| `REDUCAO_ABANDONO_PCT` | Redução Estimada de Abandono (%) | `#117A65` |

![Simulação de Cenários](images/prescritiva_cenarios.png)

---

#### Mapa de Calor — Investimento por UF

**Tabela BigQuery**: `provas-de-conceitos.mec_educacao_dev.mart_alocacao`

**Título do gráfico:**
```
Mapa de Necessidade de Investimento por Estado — 2023
```

| Configuração | Valor |
|-------------|-------|
| Tipo | Mapa geográfico |
| Dimensão | `UF` — rótulo: *Estado (UF)* |
| Métrica | `INVESTIMENTO_TOTAL_ESTIMADO_BRL` — rótulo: *Investimento Estimado (R$)* |
| Escala de cor | `#5DADE2` (mínimo) → `#943126` (máximo — maior necessidade) |

![Mapa de Investimento](images/prescritiva_mapa_investimento.png)

---

#### Tabela de Priorização

**Tabelas BigQuery**: `provas-de-conceitos.mec_educacao_dev.mart_alocacao` + `provas-de-conceitos.mec_educacao_dev.mart_clusters`

**Título do gráfico:**
```
Ranking de Prioridade de Investimento por Estado — 2023
```

| Campo | Rótulo exibido |
|-------|----------------|
| `UF` | Estado |
| `STATUS_DESEMPENHO` | Status |
| `GAP_INTERNET_PCT` | Gap Internet (p.p.) |
| `GAP_LABORATORIO_PCT` | Gap Laboratório (p.p.) |
| `INVESTIMENTO_TOTAL_ESTIMADO_BRL` | Investimento Estimado (R$) |
| `DESCRICAO_CLUSTER` | Perfil do Cluster |

- Ordenação: `ORDEM_PRIORIDADE` (crescente)
- Formatação condicional em `STATUS_DESEMPENHO` (mesmas cores do Gráfico 1 desta página)

![Tabela de Priorização](images/prescritiva_tabela_priorizacao.png)

---

#### Gráfico — Gap de Infraestrutura por UF

**Tabela BigQuery**: `provas-de-conceitos.mec_educacao_dev.mart_alocacao`

**Título do gráfico:**
```
Déficit de Infraestrutura por Estado — 2023
```

| Configuração | Valor |
|-------------|-------|
| Tipo | Barras agrupadas horizontal |
| Dimensão | `UF` — rótulo: *Estado (UF)* |
| Ordenação | `ORDEM_PRIORIDADE` (crescente) |

| Métrica | Rótulo exibido | Cor (hex) |
|---------|----------------|-----------|
| `GAP_INTERNET_PCT` | Gap Internet (pontos percentuais) | `#943126` |
| `GAP_LABORATORIO_PCT` | Gap Laboratório (pontos percentuais) | `#B7950B` |

![Gap de Infraestrutura](images/prescritiva_bullet_gap.png)

---

## Checklist Final

- [ ] Conexão BigQuery funcionando
- [ ] Campo calculado `REGIAO` criado em todas as fontes necessárias
- [ ] 4 páginas criadas (Resumo, Descritiva, Preditiva, Prescritiva)
- [ ] Filtros aplicados em todas as páginas
- [ ] Cores corporativas configuradas
- [ ] Títulos dos gráficos copiados e colados exatamente como indicado neste guia
- [ ] Rótulos de eixos e métricas em português legível
- [ ] Fonte de dados citada no rodapé de cada página
- [ ] Teste de exportação PDF realizado

---

## Queries Úteis

### Top 10 UFs por Nota ENEM
```sql
SELECT UF, ROUND(NOTA_MEDIA_ENEM, 2) AS NOTA
FROM mart_educacao_uf
WHERE ANO = 2023
ORDER BY NOTA_MEDIA_ENEM DESC
LIMIT 10
```

### Municípios Prioritários
```sql
SELECT CIDADE, UF, PRIORIDADE_INVESTIMENTO, TEXTO_ANALISE
FROM mart_analises_municipio
WHERE PRIORIDADE_INVESTIMENTO = 'ALTA'
ORDER BY NOTA_MEDIA_ENEM
LIMIT 50
```

### Comparativo Regional
```sql
SELECT
    CASE
        WHEN UF IN ('AC','AP','AM','PA','RO','RR','TO') THEN 'Norte'
        WHEN UF IN ('AL','BA','CE','MA','PB','PE','PI','RN','SE') THEN 'Nordeste'
        WHEN UF IN ('DF','GO','MT','MS') THEN 'Centro-Oeste'
        WHEN UF IN ('ES','MG','RJ','SP') THEN 'Sudeste'
        WHEN UF IN ('PR','RS','SC') THEN 'Sul'
    END AS REGIAO,
    COUNT(DISTINCT UF) AS UFS,
    SUM(TOTAL_MATRICULAS) AS MATRICULAS,
    AVG(NOTA_MEDIA_ENEM) AS MEDIA_ENEM,
    AVG(PCT_ESCOLAS_INTERNET) AS PCT_INTERNET
FROM mart_educacao_uf
GROUP BY 1
ORDER BY 4 DESC
```
