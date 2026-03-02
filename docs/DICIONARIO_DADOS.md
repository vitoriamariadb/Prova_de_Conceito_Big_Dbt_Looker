# Dicionário de Dados - MEC Educação

## Visão Geral

Este documento descreve todas as tabelas e campos do projeto de dados educacionais.

**Projeto BigQuery:** `provas-de-conceitos`
**Dataset:** `mec_educacao_dev`

---

## Camada Raw (Dados Brutos)

### raw_censo_escolas
Dados brutos do Censo Escolar carregados diretamente do INEP.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| CO_ENTIDADE | STRING | Código único da escola (INEP) |
| NO_ENTIDADE | STRING | Nome da escola |
| CO_MUNICIPIO | STRING | Código IBGE do município |
| NO_MUNICIPIO | STRING | Nome do município |
| SG_UF | STRING | Sigla da UF |
| NU_ANO_CENSO | INT64 | Ano do censo |
| TP_DEPENDENCIA | INT64 | Tipo de dependência (1=Fed, 2=Est, 3=Mun, 4=Priv) |
| TP_LOCALIZACAO | INT64 | Localização (1=Urbana, 2=Rural) |
| QT_MAT_BAS | INT64 | Matrículas educação básica |
| QT_MAT_FUND | INT64 | Matrículas ensino fundamental |
| QT_MAT_MED | INT64 | Matrículas ensino médio |
| QT_DOC_BAS | INT64 | Quantidade de docentes |
| IN_INTERNET | INT64 | Possui internet (0/1) |
| IN_LABORATORIO_INFORMATICA | INT64 | Possui laboratório (0/1) |
| IN_BIBLIOTECA | INT64 | Possui biblioteca (0/1) |
| IN_QUADRA_ESPORTES | INT64 | Possui quadra (0/1) |

### raw_enem_microdados
Microdados do ENEM carregados do INEP.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| NU_INSCRICAO | STRING | Número de inscrição |
| NU_ANO | INT64 | Ano da prova |
| CO_MUNICIPIO_ESC | STRING | Código do município da escola |
| SG_UF_ESC | STRING | UF da escola |
| TP_SEXO | STRING | Sexo (M/F) |
| NU_IDADE | INT64 | Idade do participante |
| TP_COR_RACA | INT64 | Cor/raça declarada |
| Q006 | STRING | Faixa de renda familiar |
| NU_NOTA_CN | FLOAT64 | Nota Ciências da Natureza |
| NU_NOTA_CH | FLOAT64 | Nota Ciências Humanas |
| NU_NOTA_LC | FLOAT64 | Nota Linguagens |
| NU_NOTA_MT | FLOAT64 | Nota Matemática |
| NU_NOTA_REDACAO | FLOAT64 | Nota Redação |
| TP_PRESENCA_CN | INT64 | Presença em CN |
| TP_PRESENCA_CH | INT64 | Presença em CH |
| TP_PRESENCA_LC | INT64 | Presença em LC |
| TP_PRESENCA_MT | INT64 | Presença em MT |

---

## Camada Staging (Dados Limpos)

### stg_censo_escolar
Dados do Censo Escolar limpos e padronizados.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| ANO | INT64 | Ano de referência |
| DATA_REFERENCIA | DATE | Data de referência (01/01/ANO) |
| UF | STRING | Sigla da UF |
| REGIAO | STRING | Norte, Nordeste, Centro-Oeste, Sudeste, Sul |
| COD_MUNICIPIO | STRING | Código IBGE do município |
| NOME_MUNICIPIO | STRING | Nome do município |
| COD_ESCOLA | STRING | Código INEP da escola |
| NOME_ESCOLA | STRING | Nome da escola |
| REDE | STRING | Federal, Estadual, Municipal, Privada |
| LOCALIZACAO | STRING | Urbana, Rural |
| MATRICULAS_TOTAL | INT64 | Total de matrículas |
| MATRICULAS_FUNDAMENTAL | INT64 | Matrículas no fundamental |
| MATRICULAS_MEDIO | INT64 | Matrículas no médio |
| DOCENTES_TOTAL | INT64 | Quantidade de docentes |
| TEM_INTERNET | BOOL | Escola possui internet |
| TEM_LABORATORIO | BOOL | Escola possui laboratório |
| TEM_BIBLIOTECA | BOOL | Escola possui biblioteca |
| TEM_QUADRA | BOOL | Escola possui quadra |
| DATA_CARGA | TIMESTAMP | Data de carga dos dados |

### stg_enem
Dados do ENEM limpos e padronizados.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| ID_INSCRICAO | STRING | Identificador único |
| ANO | INT64 | Ano da prova |
| DATA_REFERENCIA | DATE | Data de referência |
| UF | STRING | UF da escola |
| COD_MUNICIPIO | STRING | Código do município |
| SEXO | STRING | Masculino, Feminino |
| IDADE | INT64 | Idade do participante |
| COR_RACA | STRING | Branca, Preta, Parda, Amarela, Indígena |
| RENDA_FAMILIAR_ESTIMADA | FLOAT64 | Renda em reais |
| NOTA_CIENCIAS_NATUREZA | FLOAT64 | Nota CN (0-1000) |
| NOTA_CIENCIAS_HUMANAS | FLOAT64 | Nota CH (0-1000) |
| NOTA_LINGUAGENS | FLOAT64 | Nota LC (0-1000) |
| NOTA_MATEMATICA | FLOAT64 | Nota MT (0-1000) |
| NOTA_REDACAO | FLOAT64 | Nota Redação (0-1000) |
| PRESENTE_TODAS_PROVAS | BOOL | Compareceu em todas |
| NOTA_MEDIA | FLOAT64 | Média das 5 notas |
| DATA_CARGA | TIMESTAMP | Data de carga |

---

## Camada Marts (Análises)

### mart_educacao_uf
Agregação de indicadores educacionais por UF.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| ANO | INT64 | Ano de referência |
| DATA_REFERENCIA | DATE | Data de referência |
| UF | STRING | Sigla da UF |
| TOTAL_MATRICULAS | INT64 | Soma de matrículas |
| MATRICULAS_FUNDAMENTAL | INT64 | Soma fundamental |
| MATRICULAS_MEDIO | INT64 | Soma médio |
| TOTAL_DOCENTES | INT64 | Soma de docentes |
| TOTAL_ESCOLAS | INT64 | Quantidade de escolas |
| ALUNOS_POR_DOCENTE | FLOAT64 | Razão matrículas/docentes |
| PCT_ESCOLAS_INTERNET | FLOAT64 | % escolas com internet |
| PCT_ESCOLAS_LABORATORIO | FLOAT64 | % escolas com laboratório |
| PCT_ESCOLAS_BIBLIOTECA | FLOAT64 | % escolas com biblioteca |
| TOTAL_INSCRITOS_ENEM | INT64 | Inscritos no ENEM |
| NOTA_MEDIA_ENEM | FLOAT64 | Média do ENEM na UF |
| NOTA_MEDIA_MATEMATICA | FLOAT64 | Média de matemática |
| NOTA_MEDIA_REDACAO | FLOAT64 | Média de redação |
| RENDA_MEDIA_FAMILIAR | FLOAT64 | Renda média declarada |
| DESVIO_PADRAO_NOTA | FLOAT64 | Variabilidade das notas |
| DATA_CARGA | TIMESTAMP | Data de processamento |

### mart_educacao_municipio
Agregação de indicadores por município.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| ANO | INT64 | Ano de referência |
| DATA_REFERENCIA | DATE | Data de referência |
| UF | STRING | Sigla da UF |
| COD_MUNICIPIO | STRING | Código IBGE |
| NOME_MUNICIPIO | STRING | Nome do município |
| TOTAL_MATRICULAS | INT64 | Soma de matrículas |
| TOTAL_ESCOLAS | INT64 | Quantidade de escolas |
| ALUNOS_POR_DOCENTE | FLOAT64 | Razão matrículas/docentes |
| PCT_ESCOLAS_INTERNET | FLOAT64 | % escolas com internet |
| PCT_ESCOLAS_LABORATORIO | FLOAT64 | % escolas com laboratório |
| NOTA_MEDIA_ENEM | FLOAT64 | Média do ENEM |
| RENDA_MEDIA_FAMILIAR | FLOAT64 | Renda média |

### mart_analises_municipio
Análises por município com texto narrativo para Looker Studio.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| COD_MUNICIPIO_IBGE | STRING | Código IBGE |
| CIDADE | STRING | Nome da cidade |
| UF | STRING | Sigla da UF |
| REGIAO | STRING | Região geográfica |
| ANO | INT64 | Ano de referência |
| NOTA_MEDIA_ENEM | FLOAT64 | Média ENEM |
| PCT_ESCOLAS_INTERNET | FLOAT64 | % internet |
| ALUNOS_POR_DOCENTE | FLOAT64 | Razão alunos/docente |
| TOTAL_MATRICULAS | INT64 | Total matrículas |
| DIFERENCA_MEDIA_NACIONAL | FLOAT64 | Diferença da média BR |
| PERCENTIL_NOTA | FLOAT64 | Percentil (0-100) |
| CLUSTER_ID | INT64 | ID do cluster |
| DESCRICAO_CLUSTER | STRING | Descrição do cluster |
| PRIORIDADE_INVESTIMENTO | STRING | ALTA, MEDIA, BAIXA, MONITORAMENTO |
| TEXTO_ANALISE | STRING | Narrativa automática |
| CLASSIFICACAO_DESEMPENHO | STRING | EXCELENTE, BOM, REGULAR, ATENCAO |
| STATUS_GERAL | STRING | CONSOLIDADO, EM_DESENVOLVIMENTO, PRIORITARIO |
| SPARKLINE_NOTA | FLOAT64 | Para mini-gráficos |
| SPARKLINE_INFRA | FLOAT64 | Para mini-gráficos |

### mart_clusters
Clusterização de UFs por indicadores.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| UF | STRING | Sigla da UF |
| ANO | INT64 | Ano de referência |
| CLUSTER_ID | INT64 | Identificador do cluster (1-4) |
| DESCRICAO_CLUSTER | STRING | Alto Desempenho / Alta Renda, Desempenho Médio / Renda Média, etc |
| NOTA_MEDIA_ENEM | FLOAT64 | Média ENEM |
| RENDA_MEDIA_FAMILIAR | FLOAT64 | Renda média |
| PCT_ESCOLAS_INTERNET | FLOAT64 | % internet |
| Z_SCORE_NOTA | FLOAT64 | Score normalizado nota |
| Z_SCORE_RENDA | FLOAT64 | Score normalizado renda |
| PRIORIDADE_INVESTIMENTO | STRING | ALTA, MEDIA, BAIXA, MONITORAMENTO |
| LATITUDE_UF | FLOAT64 | Latitude do centroide da UF |
| LONGITUDE_UF | FLOAT64 | Longitude do centroide da UF |
| LOCALIZACAO_GEO | STRING | Coordenadas concatenadas "lat,lng" para Google Maps |
| STATUS_DESEMPENHO | STRING | CRITICO, ATENCAO, REGULAR, ADEQUADO |
| GAP_INTERNET_PCT | FLOAT64 | Gap percentual de internet em relação à meta PNE |
| GAP_LABORATORIO_PCT | FLOAT64 | Gap percentual de laboratório em relação à meta PNE |
| INVESTIMENTO_TOTAL_ESTIMADO_BRL | FLOAT64 | Estimativa de investimento para fechar gaps |
| DATA_PROCESSAMENTO | TIMESTAMP | Data de processamento |

### mart_alocacao
Priorização de alocação de recursos.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| UF | STRING | Sigla da UF |
| ANO | INT64 | Ano de referência |
| TOTAL_MATRICULAS | INT64 | Total de matrículas |
| ALUNOS_POR_DOCENTE | FLOAT64 | Razão alunos/docente |
| DOCENTES_NECESSARIOS | INT64 | Docentes adicionais necessários |
| GAP_INTERNET_PCT | FLOAT64 | Gap percentual de internet |
| GAP_LABORATORIO_PCT | FLOAT64 | Gap percentual de laboratório |
| STATUS_DESEMPENHO | STRING | CRITICO, ATENCAO, REGULAR, ADEQUADO |
| CUSTO_DOCENTES_MENSAL_BRL | FLOAT64 | Custo mensal com docentes |
| CUSTO_INTERNET_ESTIMADO_BRL | FLOAT64 | Custo estimado internet |
| CUSTO_LABORATORIO_ESTIMADO_BRL | FLOAT64 | Custo estimado laboratório |
| INVESTIMENTO_TOTAL_ESTIMADO_BRL | FLOAT64 | Investimento total |
| ORDEM_PRIORIDADE | INT64 | Ordem de prioridade (1=maior)

### mart_simulacao_cenarios
Simulação de cenários de investimento.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| AUMENTO_PERCENTUAL | INT64 | % de aumento no investimento |
| CENARIO_NOME | STRING | Nome do cenário (ex: "10%") |
| TIPO_CENARIO | STRING | Conservador, Moderado, Agressivo |
| TOTAL_MATRICULAS_BRASIL | INT64 | Total de matrículas no Brasil |
| NOTA_BASE | FLOAT64 | Nota média nacional atual |
| IMPACTO_NOTA_ENEM_PONTOS | FLOAT64 | Impacto esperado na nota ENEM (pontos) |
| NOTA_PROJETADA | FLOAT64 | Nota projetada após o investimento |
| REDUCAO_ABANDONO_PCT | FLOAT64 | Redução esperada no abandono (p.p.) |
| IMPACTO_IDEB_PONTOS | FLOAT64 | Impacto esperado no IDEB (pontos) |
| AVALIACAO_RISCO | STRING | Baixo risco, Risco moderado, Alto risco fiscal |
| ORDEM_RISCO | INT64 | Ordenação por risco (1=menor) |
| DATA_PROCESSAMENTO | TIMESTAMP | Data de processamento |

### mart_correlacoes
Correlações entre variáveis educacionais.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| PAR_VARIAVEIS | STRING | Par de variáveis (ex: Renda x Nota ENEM) |
| CORRELACAO | FLOAT64 | Coeficiente de Pearson (-1 a 1) |
| N_OBSERVACOES | INT64 | Quantidade de observações |
| INTERPRETACAO | STRING | Descrição da correlação |

---

## Seeds (Dados Estáticos)

### dim_municipios
Dimensão de municípios brasileiros.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| COD_MUNICIPIO_TOM | STRING | Código TOM |
| COD_MUNICIPIO_IBGE | STRING | Código IBGE |
| NOME_MUNICIPIO_TOM | STRING | Nome TOM |
| NOME_MUNICIPIO_IBGE | STRING | Nome IBGE |
| UF | STRING | Sigla da UF |
| REGIAO | STRING | Região geográfica |
| LATITUDE | FLOAT64 | Latitude |
| LONGITUDE | FLOAT64 | Longitude |
| POPULACAO_ESTIMADA | INT64 | População estimada |

### dim_calendario
Dimensão de datas.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| DATA | DATE | Data |
| ANO | INT64 | Ano |
| MES | INT64 | Mês |
| TRIMESTRE | INT64 | Trimestre |
| SEMESTRE | INT64 | Semestre |
| DIA_SEMANA | STRING | Nome do dia |
| ANO_LETIVO | BOOL | É ano letivo |

### params_metas_pne
Metas do Plano Nacional de Educação.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| META_ID | INT64 | Identificador da meta |
| DESCRICAO | STRING | Descrição da meta |
| INDICADOR | STRING | Indicador associado |
| VALOR_META_2024 | FLOAT64 | Valor alvo para 2024 |

### params_custos
Parâmetros de custos unitários.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| ITEM | STRING | Item de custo |
| CUSTO_UNITARIO_BRL | FLOAT64 | Custo em reais |
| ANO_REFERENCIA | INT64 | Ano base |

### params_elasticidades
Elasticidades para simulações.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| VARIAVEL | STRING | Variável de entrada |
| ELASTICIDADE | FLOAT64 | Coeficiente de elasticidade |
| FONTE | STRING | Fonte da estimativa |

---

## Glossário

| Termo | Definição |
|-------|-----------|
| ENEM | Exame Nacional do Ensino Médio |
| INEP | Instituto Nacional de Estudos e Pesquisas Educacionais |
| MEC | Ministério da Educação |
| PNE | Plano Nacional de Educação |
| IBGE | Instituto Brasileiro de Geografia e Estatística |
| Z-Score | Valor padronizado (desvios da média) |
| Cluster | Grupo de UFs com características similares |
| Gap | Diferença entre valor atual e meta |
