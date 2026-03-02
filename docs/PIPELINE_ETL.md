# Pipeline ETL - MEC Educação

## Visão Geral do Pipeline

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │     │                 │
│   INEP/MEC      │────▶│   BigQuery      │────▶│      dbt        │────▶│  Looker Studio  │
│   (Fonte)       │     │   (Raw)         │     │   (Transform)   │     │  (Visualização) │
│                 │     │                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## 1. Extração (Extract)

### 1.1 Fontes de Dados

| Fonte | Dataset | URL | Periodicidade |
|-------|---------|-----|---------------|
| Censo Escolar | Microdados | gov.br/inep/microdados/censo-escolar | Anual |
| ENEM | Microdados | gov.br/inep/microdados/enem | Anual |
| Sinopses | Agregados | gov.br/inep/sinopses-estatisticas | Anual |

### 1.2 Scripts de Download

**Censo Escolar:**
```bash
cd scripts/python/etl
python download_censo.py 2023
```

**ENEM:**
```bash
python download_enem.py 2023
```

### 1.3 Estrutura de Arquivos Baixados

```
data/raw/
├── censo_escolar_2023/
│   ├── DADOS/
│   │   ├── microdados_ed_basica_2023.csv
│   │   └── ...
│   └── ANEXOS/
│       └── dicionario_dados.xlsx
├── enem_2023/
│   ├── DADOS/
│   │   └── MICRODADOS_ENEM_2023.csv
│   └── DICIONARIO/
│       └── Dicionario_Microdados_Enem_2023.xlsx
└── microdados_*.zip
```

---

## 2. Carga (Load)

### 2.1 Upload para BigQuery

```bash
python carregar_bigquery.py 2023
```

**Opções:**
- `--full`: Carrega dados completos (sem amostragem)
- Default: Carrega amostra de 100k linhas do ENEM

### 2.2 Tabelas Criadas

| Tabela BigQuery | Fonte | Tamanho Estimado |
|-----------------|-------|------------------|
| `raw_censo_escolas` | Censo Escolar | ~500 MB |
| `raw_enem_microdados` | ENEM | ~2 GB (amostra) |

### 2.3 Configuração de Carga

```python
job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.CSV,
    skip_leading_rows=1,
    autodetect=True,
    write_disposition="WRITE_TRUNCATE",
    max_bad_records=100
)
```

---

## 3. Transformação (Transform)

### 3.1 Camadas dbt

```
dbt/models/
├── raw/           # Views sobre dados brutos
│   ├── raw_censo_escolar.sql
│   └── raw_enem.sql
├── staging/       # Limpeza e padronização
│   ├── stg_censo_escolar.sql
│   └── stg_enem.sql
└── marts/         # Agregações e análises
    ├── mart_educacao_uf.sql
    ├── mart_educacao_municipio.sql
    ├── mart_analises_municipio.sql
    ├── mart_clusters.sql
    ├── mart_alocacao.sql
    ├── mart_simulacao_cenarios.sql
    └── mart_correlacoes.sql
```

### 3.2 Execução dbt

**Instalação de dependências:**
```bash
cd dbt
dbt deps
```

**Verificar conexão:**
```bash
dbt debug
```

**Executar modelos:**
```bash
dbt run                    # Todos os modelos
dbt run --select staging   # Apenas staging
dbt run --select marts     # Apenas marts
```

**Testes de qualidade:**
```bash
dbt test
```

**Full refresh:**
```bash
dbt run --full-refresh
```

### 3.3 DAG de Dependências

```
raw_censo_escolas ────▶ raw_censo_escolar ────▶ stg_censo_escolar ─┬──▶ mart_educacao_uf
                                                                    │
raw_enem_microdados ──▶ raw_enem ─────────────▶ stg_enem ──────────┼──▶ mart_educacao_municipio
                                                                    │
dim_municipios ────────────────────────────────────────────────────┴──▶ mart_analises_municipio
                                                                           │
                                                                           ▼
                                                                    mart_clusters
                                                                           │
                                                                           ▼
                                                                    mart_alocacao
```

---

## 4. Análises Python

### 4.1 Scripts Disponíveis

| Script | Descrição | Output |
|--------|-----------|--------|
| `regressao_educacao.py` | Regressão infraestrutura x nota | `outputs/regressao_*.png` |
| `analise_clusterizacao.py` | Clusterização de UFs | `outputs/clusters_*.png` |
| `analise_correlacao_causalidade.py` | Matriz de correlação | `outputs/correlacao_*.png` |
| `analise_impacto_financeiro.py` | Simulação de cenários | `outputs/impacto_*.png` |
| `gerar_graficos_corporativos.py` | Todos os gráficos (estilo formal) | `outputs/*.png` |

### 4.2 Execução

```bash
cd scripts/python

# Ativar ambiente virtual
source ../../venv/bin/activate

# Executar análises
python regressao_educacao.py
python analise_clusterizacao.py
python analise_correlacao_causalidade.py
python analise_impacto_financeiro.py

# Ou gerar todos de uma vez (estilo corporativo)
python gerar_graficos_corporativos.py
```

---

## 5. Automação

### 5.1 Script de Execução Completa

```bash
#!/bin/bash
# scripts/bash/run_pipeline.sh

set -e

echo "=== PIPELINE ETL MEC ==="

echo "1. Download de dados..."
cd scripts/python/etl
python download_censo.py 2023
python download_enem.py 2023

echo "2. Carga no BigQuery..."
python carregar_bigquery.py 2023

echo "3. Transformações dbt..."
cd ../../../dbt
dbt deps
dbt run
dbt test

echo "4. Geração de gráficos..."
cd ../scripts/python
python gerar_graficos_corporativos.py

echo "=== PIPELINE CONCLUÍDO ==="
```

### 5.2 Cron Job (Execução Agendada)

```cron
# Atualizar dados mensalmente (dia 1, 3h da manhã)
0 3 1 * * /path/to/project/scripts/bash/run_pipeline.sh >> /var/log/mec_pipeline.log 2>&1
```

---

## 6. Monitoramento

### 6.1 Verificações de Qualidade

**Contar registros:**
```sql
SELECT 'stg_censo_escolar' AS tabela, COUNT(*) AS registros
FROM mec_educacao_dev.stg_censo_escolar
UNION ALL
SELECT 'stg_enem', COUNT(*)
FROM mec_educacao_dev.stg_enem
UNION ALL
SELECT 'mart_educacao_uf', COUNT(*)
FROM mec_educacao_dev.mart_educacao_uf
```

**Verificar completude:**
```sql
SELECT
    UF,
    COUNT(*) AS escolas,
    SUM(CASE WHEN TEM_INTERNET THEN 1 ELSE 0 END) AS com_internet,
    AVG(MATRICULAS_TOTAL) AS media_matriculas
FROM mec_educacao_dev.stg_censo_escolar
GROUP BY UF
ORDER BY UF
```

### 6.2 Alertas

- Verificar se todas as 27 UFs estão presentes
- Validar se as métricas estão dentro de ranges esperados
- Conferir datas de última carga

---

## 7. Troubleshooting

### 7.1 Problemas Comuns

**Erro de conexão BigQuery:**
```bash
# Verificar credenciais
gcloud auth application-default login

# Ou usar service account
export GOOGLE_APPLICATION_CREDENTIALS="credentials/gcp_key.json"
```

**Erro de memória no download:**
```python
# Usar chunks para arquivos grandes
pd.read_csv(arquivo, chunksize=100000)
```

**dbt não encontra tabelas raw:**
```bash
# Verificar se as tabelas existem
bq ls mec_educacao_dev

# Se necessário, usar dados simulados (fallback automático)
dbt run
```

### 7.2 Logs

```bash
# dbt logs
cat dbt/logs/dbt.log

# BigQuery jobs
bq ls -j --max_results=10
```

---

## 8. Segurança

### 8.1 Credenciais

- **NÃO commitar** arquivos em `credentials/`
- Usar variáveis de ambiente para produção
- Rotacionar service account keys periodicamente

### 8.2 Permissões BigQuery

| Role | Permissão | Uso |
|------|-----------|-----|
| `bigquery.dataEditor` | Criar/modificar tabelas | ETL |
| `bigquery.dataViewer` | Apenas leitura | Looker Studio |
| `bigquery.jobUser` | Executar queries | Analistas |

---

## 9. Custos

### 9.1 Estimativa BigQuery

| Operação | Volume | Custo Estimado |
|----------|--------|----------------|
| Armazenamento | 5 GB | R$ 0,50/mês |
| Queries (on-demand) | 100 GB/mês | R$ 12,50/mês |
| Streaming inserts | N/A | - |

### 9.2 Otimizações

- Particionar tabelas por ANO
- Clusterizar por UF
- Usar tabelas materializadas para marts
- Limitar scans com WHERE clauses

---

## 10. Evolução do Pipeline

### 10.1 Próximos Passos

- [ ] Adicionar dados do SAEB
- [ ] Integrar PDDE (financeiro)
- [ ] Implementar CDC (Change Data Capture)
- [ ] Criar dashboard de monitoramento do pipeline
- [ ] Implementar testes de schema
- [ ] Adicionar data lineage

### 10.2 Backlog Técnico

- Migrar para Airflow/Cloud Composer
- Implementar data quality framework (Great Expectations)
- Adicionar metadata management
- Criar ambiente de staging separado
