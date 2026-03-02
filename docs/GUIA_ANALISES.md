# Guia de Análises - Scripts Python

Este documento explica como utilizar os scripts de análise disponíveis no projeto.

---

## Visão Geral

O projeto contém 5 scripts principais de análise:

| Script | Tipo de Análise | Saída |
|--------|-----------------|-------|
| `regressao_educacao.py` | Regressão Linear | Coeficientes, R², gráfico scatter |
| `analise_clusterizacao.py` | K-Means Clustering | Clusters de UFs, gráfico PCA |
| `analise_impacto_financeiro.py` | Simulação de Cenários | ROI, gaps, gráficos |
| `analise_correlacao_causalidade.py` | Correlação/Mediação | Matriz, correlações parciais |
| `gerar_graficos_corporativos.py` | Todos (estilo formal) | Gráficos de alta qualidade |

---

## Fonte de Dados

Os scripts funcionam com duas fontes:

1. **BigQuery (preferencial)**: Dados das tabelas marts via `data_loader.py`
2. **CSV local**: Arquivo CSV passado como argumento

**Requisito**: Conexao com BigQuery configurada (variavel GOOGLE_APPLICATION_CREDENTIALS ou ADC).

---

## 1. Regressão Linear: Infraestrutura vs Nota ENEM

### Objetivo
Quantificar a relação entre infraestrutura escolar (internet) e desempenho no ENEM.

### Como Usar

```bash
cd ~/Desenvolvimento/Prova_de_Conceito_Big_Dbt_Looker
source venv/bin/activate
cd scripts/python

python regressao_educacao.py                              # BigQuery
python regressao_educacao.py ../../data/raw/dados_uf.csv  # CSV local
```

### Interpretação dos Resultados

- **Coeficiente**: Variação na nota para cada 1% de aumento em escolas com internet
- **Intercepto (B0)**: Nota esperada quando PCT_INTERNET = 0
- **R² Score**: Proporção da variância explicada (0 a 1)
- **RMSE**: Erro médio de predição em pontos

### Formato de Saida

```
Coeficiente:       [valor calculado]
Intercepto:        [valor calculado]
R² Score:          [valor calculado]
RMSE:              [valor calculado]

Interpretacao:
  Para cada 1% de aumento em escolas com internet,
  a nota ENEM aumenta em media [coeficiente] pontos.
```

### Output
- Gráfico: `outputs/regressao_infra_nota.png`

---

## 2. Clusterização: Agrupamento de UFs

### Objetivo
Identificar grupos de UFs com características educacionais similares para direcionar políticas.

### Como Usar

```bash
cd scripts/python

python analise_clusterizacao.py                           # BigQuery
python analise_clusterizacao.py ../../data/raw/dados.csv  # CSV local
```

### Interpretação dos Resultados

- **Silhouette Score**: Qualidade dos clusters (quanto maior, melhor)
- **Cluster 0-3**: Grupos identificados automaticamente
- **PCA**: Redução dimensional para visualização

### Aplicação Prática

| Cluster | Característica | Ação Recomendada |
|---------|----------------|------------------|
| Alto desempenho | Notas e renda altas | Monitoramento |
| Médio | Valores intermediários | Programas de melhoria |
| Potencial | Renda alta, nota baixa | Investir em infraestrutura |
| Prioritário | Notas e renda baixas | Intervenção urgente |

### Output
- Gráfico: `outputs/clusters_ufs.png`
- CSV: `outputs/resultado_clusters.csv`

---

## 3. Impacto Financeiro: Simulação de Investimentos

### Objetivo
Simular cenários de aumento de investimento e estimar impacto nos indicadores.

### Como Usar

```bash
cd scripts/python

python analise_impacto_financeiro.py                       # BigQuery
python analise_impacto_financeiro.py ../../data/raw/d.csv  # CSV local
```

### Interpretação dos Resultados

- **Elasticidade**: Sensibilidade do indicador ao investimento
- **Cenários**: Projeções para diferentes níveis de aumento (5%, 10%, 15%...)
- **Gap Orçamentário**: Diferença entre orçamento atual e ideal por UF

### Formato de Cenario

```
CENARIO: Aumento de [X]%
  Impacto Nota ENEM: +[calculado] pontos
  Reducao Abandono: -[calculado]%
```

### Output
- Gráfico: `outputs/impacto_financeiro.png`

---

## 4. Correlação e Causalidade

### Objetivo
Identificar relações estatísticas e explorar possíveis mecanismos causais.

### Como Usar

```bash
cd scripts/python

python analise_correlacao_causalidade.py                   # BigQuery
python analise_correlacao_causalidade.py ../../data/raw/d.csv  # CSV local
```

### Interpretação dos Resultados

#### Matriz de Correlação
- **r > 0.7**: Correlação forte positiva
- **r > 0.4**: Correlação moderada
- **r < 0.4**: Correlação fraca
- **r < 0**: Correlação negativa

### Cuidados

- **Correlação NÃO implica causalidade**
- Variáveis confundidoras podem distorcer resultados
- Dados transversais limitam inferências temporais
- Sempre considere explicações alternativas

### Output
- Gráfico: `outputs/matriz_correlacao.png`

---

## 5. Gráficos Corporativos

### Objetivo
Gerar todos os gráficos em estilo formal/governamental para uso em relatórios e dashboards.

### Como Usar

```bash
cd scripts/python
python gerar_graficos_corporativos.py
```

### Especificações

- **Dimensões**: 1588 x 2246 px (formato retrato)
- **DPI**: 150
- **Paleta**: Azul institucional (#1B4F72)
- **Fonte**: DejaVu Sans

### Outputs
```
outputs/
├── regressao_corporativo.png
├── clusters_corporativo.png
├── correlacao_corporativo.png
└── investimentos_corporativo.png
```

---

## Requisitos

### Dependências Python

```bash
pip install pandas numpy scikit-learn scipy matplotlib seaborn
```

### Formato dos Dados de Entrada

Os scripts aceitam CSVs com as seguintes colunas:

| Coluna | Descrição | Exemplo |
|--------|-----------|---------|
| UF | Sigla da UF | SP, RJ, MG |
| ANO | Ano de referência | 2023 |
| NOTA_MEDIA_ENEM | Nota média | 520.5 |
| PCT_ESCOLAS_INTERNET | Percentual 0-100 | 85.5 |
| TOTAL_MATRICULAS | Contagem | 1500000 |
| ALUNOS_POR_DOCENTE | Razão | 22.5 |

---

## Fluxo de Trabalho Recomendado

```
1. Executar dbt
   cd dbt && dbt run

2. Gerar gráficos corporativos
   cd scripts/python && python gerar_graficos_corporativos.py

3. Visualizar resultados
   ls outputs/*.png

4. Incorporar no Looker Studio
   - Ver docs/GUIA_LOOKER_STUDIO.md
```

---

## Resolução de Problemas

### BigQuery nao disponivel
Configure a variavel de ambiente GOOGLE_APPLICATION_CREDENTIALS apontando para o arquivo de credenciais do projeto.

### Erro de importação
```bash
pip install -r requirements.txt
```

### Gráficos não gerados
Verificar se a pasta `outputs/` existe:
```bash
mkdir -p outputs
```
