# Prova de Conceito: MEC + BigQuery + dbt + Looker Studio

Pipeline de dados educacionais do MEC para análise e visualização em dashboard corporativo.

**Projeto BigQuery**: `provas-de-conceitos`
**Dataset**: `mec_educacao_dev`
**Objetivo**: Demonstrar competências em engenharia de dados com foco em educação brasileira.

---

## Estrutura do Projeto

```
Prova_de_Conceito_Big_Dbt_Looker/
├── dbt/
│   ├── models/
│   │   ├── raw/                  # Views sobre dados brutos INEP
│   │   ├── staging/              # Limpeza e padronização
│   │   └── marts/                # Agregações e análises
│   ├── seeds/                    # Dimensões estáticas (municípios, calendário)
│   ├── macros/
│   ├── tests/
│   └── dbt_project.yml
├── scripts/
│   ├── python/
│   │   ├── etl/                  # Download e carga INEP
│   │   │   ├── download_censo.py
│   │   │   ├── download_enem.py
│   │   │   └── carregar_bigquery.py
│   │   ├── utils/                # Módulos compartilhados
│   │   │   ├── data_loader.py
│   │   │   └── estilo_corporativo.py
│   │   ├── regressao_educacao.py
│   │   ├── analise_clusterizacao.py
│   │   ├── analise_impacto_financeiro.py
│   │   ├── analise_correlacao_causalidade.py
│   │   └── gerar_graficos_corporativos.py
│   └── bash/
├── data/
│   ├── raw/                      # Microdados INEP
│   └── processed/
├── docs/
│   ├── GUIA_LOOKER_STUDIO.md     # Passo a passo do dashboard
│   ├── DICIONARIO_DADOS.md       # Dicionário de dados
│   ├── PIPELINE_ETL.md           # Fluxo completo
│   ├── storytelling/             # Narrativas por página
│   └── REFERENCIAS_METODOLOGICAS.md
├── outputs/                      # Gráficos gerados (PNG)
├── credentials/                  # GCP keys (NAO COMMITAR)
├── notebooks/                    # Notebooks Colab
└── requirements.txt
```

---

## Fluxo de Dados

```
INEP/MEC ──▶ Download ──▶ BigQuery (raw) ──▶ dbt ──▶ Looker Studio
                              │
                              └──▶ Python (analises) ──▶ PNG (graficos)
```

---

## Setup Rápido

### 1. Instalação

```bash
chmod +x install.sh && ./install.sh
source venv/bin/activate
```

### 2. Configurar GCP

```bash
# Credenciais
export GOOGLE_APPLICATION_CREDENTIALS="credentials/gcp_key.json"

# Ou via gcloud
gcloud auth application-default login
gcloud config set project provas-de-conceitos
```

### 3. Executar Pipeline

```bash
# Download dos dados INEP (opcional - dados simulados funcionam sem isso)
cd scripts/python/etl
python download_censo.py 2023
python download_enem.py 2023
python carregar_bigquery.py 2023

# Transformações dbt
cd ../../../dbt
dbt deps && dbt run && dbt test

# Gerar gráficos corporativos
cd ../scripts/python
python gerar_graficos_corporativos.py
```

---

## Modelos dbt

### Raw (Views sobre dados brutos)

| Modelo | Descrição |
|--------|-----------|
| `raw_censo_escolar` | Dados padronizados do Censo Escolar INEP |
| `raw_enem` | Dados padronizados do ENEM INEP |

### Staging (Limpeza)

| Modelo | Descrição |
|--------|-----------|
| `stg_censo_escolar` | Escolas, matrículas, docentes, infraestrutura |
| `stg_enem` | Notas, renda, dados socioeconômicos |

### Marts (Análises)

| Modelo | Descrição | Tipo |
|--------|-----------|------|
| `mart_educacao_uf` | Indicadores agregados por UF | Descritivo |
| `mart_educacao_municipio` | Indicadores por município | Descritivo |
| `mart_analises_municipio` | Análises com texto narrativo | Storytelling |
| `mart_clusters` | Clusterização de UFs | Preditivo |
| `mart_correlacoes` | Correlações entre variáveis | Preditivo |
| `mart_alocacao` | Priorização de investimentos | Prescritivo |
| `mart_simulacao_cenarios` | Simulação de impacto | Prescritivo |

---

## Dashboard Looker Studio

### Configuração
- **Dimensões**: 1588 x 2246 px (formato retrato/PDF)
- **Páginas**: 4 (Resumo Executivo, Descritiva, Preditiva, Prescritiva)
- **Estilo**: Corporativo/Governamental

### Páginas

1. **Resumo Executivo**: Apresentação do estudo e KPIs principais
2. **Análise Descritiva**: Matrículas, docentes, infraestrutura por UF/Região
3. **Análise Preditiva**: Clusters, correlações, regressão nota x infraestrutura
4. **Análise Prescritiva**: Priorização de investimentos, simulação de cenários

### Filtros
- Ano
- UF
- Município (5.571 municípios)
- Região

**Guia completo**: [docs/GUIA_LOOKER_STUDIO.md](docs/GUIA_LOOKER_STUDIO.md)

---

## Gráficos Python

### Estilo Corporativo

Os scripts geram gráficos em formato de alta qualidade:
- **Dimensões**: 1588 x 2246 px
- **DPI**: 150
- **Paleta**: Azul institucional (#1B4F72, #2874A6, #5DADE2)

### Execução

```bash
source venv/bin/activate
cd scripts/python

# Gerar todos os gráficos
python gerar_graficos_corporativos.py

# Ou individualmente
python regressao_educacao.py
python analise_clusterizacao.py
python analise_correlacao_causalidade.py
python analise_impacto_financeiro.py
```

### Outputs

```
outputs/
├── regressao_corporativo.png
├── clusters_corporativo.png
├── correlacao_corporativo.png
└── investimentos_corporativo.png
```

---

## Fontes de Dados

| Dataset | Fonte | URL |
|---------|-------|-----|
| Censo Escolar | INEP | gov.br/inep/microdados/censo-escolar |
| ENEM | INEP | gov.br/inep/microdados/enem |
| Municípios | IBGE | ibge.gov.br/cidades-e-estados |

**Compatibilidade**: O projeto funciona com dados simulados (fallback) ou dados reais do INEP.

---

## Documentação

| Documento | Descrição |
|-----------|-----------|
| [DICIONARIO_DADOS.md](docs/DICIONARIO_DADOS.md) | Dicionário de dados completo |
| [PIPELINE_ETL.md](docs/PIPELINE_ETL.md) | Fluxo de dados detalhado |
| [REFERENCIAS_METODOLOGICAS.md](docs/REFERENCIAS_METODOLOGICAS.md) | Fontes e metodologia |
| [storytelling/](docs/storytelling/) | Narrativas por página do dashboard |

---

## Custos BigQuery

| Operação | Custo Estimado |
|----------|----------------|
| Armazenamento | ~R$ 0,50/mês (5GB) |
| Queries | ~R$ 12,50/mês (100GB) |

**Otimizações aplicadas**:
- Particionamento por ANO
- Clusterização por UF
- Materialização de marts

---

## Contribuindo

Veja [CONTRIBUTING.md](CONTRIBUTING.md)

---

## Licença

GPL-3.0 - Veja [LICENSE](LICENSE)

---

## Autora

**Vitória Maria** - Engenheira de Dados

Competências demonstradas:
- Modelagem dimensional (dbt)
- Data Warehouse (BigQuery)
- Visualização (Looker Studio)
- Análise de dados (Python/scikit-learn)
- Automação (Bash/ETL)
- Versionamento (Git/GitHub)
