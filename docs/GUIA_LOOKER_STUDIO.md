# Guia: Dashboard Educacao MEC no Looker Studio

## Conexao com BigQuery

### Acesso
1. Acesse [lookerstudio.google.com](https://lookerstudio.google.com)
2. Clique em **Criar** > **Relatorio**
3. Selecione **BigQuery** como fonte de dados
4. Autorize o acesso a sua conta Google
5. Navegue ate: Projeto `provas-de-conceitos` > Dataset `mec_educacao_dev`

### Tabelas Disponiveis

| Tabela | Uso |
|--------|-----|
| `mart_educacao_uf` | Analise descritiva por UF |
| `mart_educacao_municipio` | Filtros por municipio |
| `mart_analises_municipio` | Textos narrativos (storytelling) |
| `mart_clusters` | Clusterizacao de UFs |
| `mart_correlacoes` | Correlacoes entre variaveis |
| `mart_alocacao` | Priorizacao de investimentos |
| `mart_simulacao_cenarios` | Simulacao de cenarios |

---

## Configuracao Geral

### Dimensoes do Relatorio
- **Largura**: 1588 px | **Altura**: 2246 px
- **Orientacao**: Retrato (ideal para PDF)
- Configurar em: Menu **Arquivo** > **Configuracoes do relatorio** > **Tamanho personalizado**

### Paleta de Cores
```
Azul Primario:    #1B4F72
Azul Secundario:  #2874A6
Azul Claro:       #5DADE2
Verde Destaque:   #117A65
Amarelo Alerta:   #B7950B
Vermelho Critico: #943126
Fundo:            #F8F9F9
Texto:            #2C3E50
```
Aplicar em: Menu **Tema** > **Personalizar tema**

### Filtros (aplicar em todas as paginas)
- [ ] Filtro por **Ano** (lista suspensa, selecao unica)
- [ ] Filtro por **UF** (lista suspensa, selecao multipla, pesquisa habilitada)
- [ ] Filtro por **Municipio** (lista suspensa, fonte: `mart_analises_municipio`, campo: `CIDADE`)
- [ ] Filtro por **Regiao** (caixa de selecao: Norte, Nordeste, Centro-Oeste, Sudeste, Sul)

---

## Pagina 1: Resumo Executivo

**Fonte BigQuery**: `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`

### Checklist

- [ ] Titulo: "Painel de Indicadores Educacionais - MEC/INEP"
- [ ] Subtitulo com ano de referencia dos dados

- [ ] **4 Scorecards de KPIs**
  - Total de Matriculas: `SUM(TOTAL_MATRICULAS)`
  - Total de Escolas: `SUM(TOTAL_ESCOLAS)`
  - Media Nota ENEM: `AVG(NOTA_MEDIA_ENEM)`
  - % Escolas com Internet: `AVG(PCT_ESCOLAS_INTERNET)`

![Scorecards KPIs](images/descritiva_scorecard.png)

- [ ] **Mapa geografico do Brasil por UF**
  - Tipo: Mapa geografico
  - Dimensao: `UF`
  - Metrica: `SUM(TOTAL_MATRICULAS)`

![Mapa Matriculas por UF](images/descritiva_mapa_matriculas.png)

- [ ] Tabela resumo com Top 5 UFs por nota ENEM e Top 5 UFs em situacao critica
- [ ] Texto de contexto: objetivo do estudo e fontes de dados
- [ ] Rodape com fonte: "Dados: INEP/MEC - Censo Escolar e ENEM 2023"

---

## Pagina 2: Analise Descritiva

**Fonte BigQuery**: `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`

### Checklist

- [ ] Titulo: "Analise Descritiva por Unidade Federativa"

- [ ] **Grafico 1 - Matriculas por Regiao**
  - Tipo: Barras horizontal
  - Dimensao: `REGIAO` (campo calculado com CASE WHEN por UF)
  - Metrica: `SUM(TOTAL_MATRICULAS)`
  - Ordenacao: Decrescente
  - Cor: Degrade #1B4F72 a #5DADE2

![Matriculas por Regiao](images/descritiva_matriculas_regiao.png)

- [ ] **Grafico 2 - Infraestrutura por UF**
  - Tipo: Barras agrupadas
  - Dimensao: `UF`
  - Metricas: `AVG(PCT_ESCOLAS_INTERNET)` + `AVG(PCT_ESCOLAS_LABORATORIO)`
  - Cores: #2874A6 (Internet), #117A65 (Laboratorio)

![Infraestrutura por UF](images/descritiva_infraestrutura.png)

- [ ] **Grafico 3 - Distribuicao de Docentes**
  - Tipo: Barras horizontal por UF
  - Dimensao: `UF`
  - Metrica: `SUM(TOTAL_DOCENTES)`
  - Cores por regiao

![Distribuicao de Docentes](images/descritiva_docentes.png)

- [ ] **Grafico 4 - Notas ENEM por UF**
  - Tipo: Barras vertical
  - Dimensao: `UF`
  - Metrica: `AVG(NOTA_MEDIA_ENEM)`
  - Linha de referencia na media nacional

![Notas ENEM por UF](images/descritiva_notas_enem.png)

---

## Pagina 3: Analise Preditiva

**Fontes BigQuery**: `provas-de-conceitos.mec_educacao_dev.mart_clusters`, `provas-de-conceitos.mec_educacao_dev.mart_correlacoes`, `provas-de-conceitos.mec_educacao_dev.mart_educacao_uf`

### Checklist

- [ ] Titulo: "Analise Preditiva - Clusters e Correlacoes"

- [ ] **Grafico 1 - Clusters de UFs**
  - Tipo: Dispersao (Scatter)
  - Fonte: `mart_clusters`
  - Eixo X: `Z_SCORE_NOTA`
  - Eixo Y: `Z_SCORE_RENDA`
  - Cor por: `CLUSTER_ID`
  - Rotulos: `UF`
  - Cores: Cluster 1 #1B4F72, Cluster 2 #2874A6, Cluster 3 #B7950B, Cluster 4 #943126

![Clusters de UFs](images/clusters_corporativo.png)

- [ ] **Grafico 2 - Correlacao Nota x Infraestrutura**
  - Tipo: Dispersao com linha de tendencia
  - Eixo X: `PCT_ESCOLAS_INTERNET`
  - Eixo Y: `NOTA_MEDIA_ENEM`
  - Habilitar linha de tendencia

![Regressao Internet vs Nota](images/regressao_corporativo.png)

- [ ] **Grafico 3 - Matriz de Correlacao**
  - Tipo: Heatmap
  - Fonte: `mart_correlacoes` e `mart_educacao_uf`
  - Variaveis: Nota ENEM, Internet, Laboratorio, Alunos/Docente, Matriculas

![Matriz de Correlacao](images/preditiva_heatmap_correlacao.png)

- [ ] **Tabela - Descricao de Clusters**
  - Colunas: `CLUSTER_ID`, `DESCRICAO_CLUSTER`, `COUNT(UF)`, `AVG(NOTA_MEDIA_ENEM)`, `PRIORIDADE_INVESTIMENTO`

![Tabela de Clusters](images/preditiva_tabela_clusters.png)

- [ ] Texto narrativo explicando os clusters identificados

---

## Pagina 4: Analise Prescritiva

**Fontes BigQuery**: `provas-de-conceitos.mec_educacao_dev.mart_alocacao`, `provas-de-conceitos.mec_educacao_dev.mart_simulacao_cenarios`

### Checklist

- [ ] Titulo: "Analise Prescritiva - Priorizacao de Investimentos"

- [ ] **Grafico 1 - Priorizacao de Investimentos**
  - Tipo: Barras horizontal
  - Fonte: `mart_alocacao`
  - Dimensao: `UF`
  - Metrica: `INVESTIMENTO_TOTAL_ESTIMADO_BRL`
  - Cor condicional por `STATUS_DESEMPENHO`

![Priorizacao de Investimentos](images/investimentos_corporativo.png)

- [ ] **Grafico 2 - Simulacao de Cenarios**
  - Tipo: Barras vertical
  - Fonte: `mart_simulacao_cenarios`
  - Dimensao: `CENARIO_NOME`
  - Metricas: `IMPACTO_NOTA_ENEM_PONTOS` + `REDUCAO_ABANDONO_PCT`

![Simulacao de Cenarios](images/prescritiva_cenarios.png)

- [ ] **Mapa de Calor - Investimento por UF**
  - Tipo: Mapa geografico
  - Dimensao: `UF`
  - Metrica: `INVESTIMENTO_TOTAL_ESTIMADO_BRL`
  - Escala: Vermelho (#943126) para maior investimento necessario

![Mapa de Investimento](images/prescritiva_mapa_investimento.png)

- [ ] **Tabela de Priorizacao**
  - Fonte: `mart_alocacao` + `mart_clusters`
  - Colunas: UF, Status, Gap Internet, Gap Lab, Investimento, Cluster

![Tabela de Priorizacao](images/prescritiva_tabela_priorizacao.png)

- [ ] Texto com recomendacoes por status (Critico, Atencao, Regular, Adequado)

---

## Checklist Final

- [ ] Conexao BigQuery funcionando
- [ ] 4 paginas criadas (Resumo, Descritiva, Preditiva, Prescritiva)
- [ ] Filtros aplicados em todas as paginas
- [ ] Cores corporativas configuradas
- [ ] Titulos e rotulos em portugues
- [ ] Fonte de dados citada no rodape de cada pagina
- [ ] Teste de exportacao PDF realizado

---

## Queries Uteis

### Top 10 UFs por Nota ENEM
```sql
SELECT UF, ROUND(NOTA_MEDIA_ENEM, 2) AS NOTA
FROM mart_educacao_uf
WHERE ANO = 2023
ORDER BY NOTA_MEDIA_ENEM DESC
LIMIT 10
```

### Municipios Prioritarios
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
