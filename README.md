# Análise Educacional ENEM — BigQuery + dbt + Looker Studio

Pipeline de dados educacionais do MEC/INEP com clusterização de estados, simulação de cenários de investimento e dashboard analítico em quatro camadas: descritiva, preditiva, prescritiva e executiva.

**[Acessar o projeto completo.](https://lookerstudio.google.com/reporting/3825568c-1918-496f-8e10-4e8c051cfefd/page/p_222najef1d)**

---

## Contexto

A desigualdade educacional brasileira se manifesta com precisão nos microdados do ENEM: estados do Norte e Nordeste registram médias consistentemente abaixo dos 550 pontos do PNE enquanto o Sul e Sudeste superam essa marca. Este projeto transforma essa assimetria em análise quantificada — identificando quais estados precisam de intervenção, quanto isso custa e qual impacto pode ser esperado.

---

## Stack

| Camada | Tecnologia |
|--------|------------|
| Armazenamento | Google BigQuery |
| Transformação | dbt (arquitetura medallion: raw → staging → marts) |
| Visualização | Looker Studio |
| Análise estatística | Python — pandas, scikit-learn, matplotlib |
| Versionamento | Git + GitHub |
| Orquestração local | Bash |

---

## Arquitetura

```
INEP/MEC
  └── Censo Escolar 2023
  └── Microdados ENEM 2023
        │
        ▼
  BigQuery (raw)
        │
        ▼
  dbt — staging (limpeza e padronização)
        │
        ▼
  dbt — marts (7 modelos analíticos)
        │
        ▼
  Looker Studio (4 páginas)
```

---

## Modelos dbt

| Modelo | Camada | Descrição |
|--------|--------|-----------|
| `raw_censo_escolar` | Raw | View padronizada sobre microdados do Censo Escolar |
| `raw_enem` | Raw | View padronizada sobre microdados do ENEM |
| `stg_censo_escolar` | Staging | Limpeza de escolas, matrículas, docentes e infraestrutura |
| `stg_enem` | Staging | Limpeza de notas, renda e dados socioeconômicos |
| `mart_educacao_uf` | Mart | Indicadores agregados por Unidade Federativa |
| `mart_educacao_municipio` | Mart | Indicadores por município (5.571 cidades) |
| `mart_clusters` | Mart | Clusterização de UFs por Z-Score — perfis de desempenho |
| `mart_correlacoes` | Mart | Correlação de Pearson entre variáveis educacionais |
| `mart_alocacao` | Mart | Gaps de infraestrutura e estimativa de investimento por UF |
| `mart_simulacao_cenarios` | Mart | Projeção de impacto por cenário de aumento orçamentário |

---

## Dashboard

Quatro camadas analíticas progressivas:

**Resumo Executivo** — KPIs nacionais, mapa de matrículas por UF e ranking de desempenho ENEM.

**Análise Descritiva** — Infraestrutura digital e científica, distribuição do corpo docente e desempenho ENEM por estado e região, com filtros dinâmicos de ano, UF e município.

**Análise Preditiva** — Clusterização de estados em quatro perfis por Z-Score (nota × renda), mapa de bolhas georreferenciado e matriz de correlação de Pearson entre os principais indicadores.

**Análise Prescritiva** — Ranking de prioridade de investimento por estado, simulação de seis cenários orçamentários com projeção de ganho no ENEM e redução de evasão.

---

## Setup

```bash
# Instalação
chmod +x install.sh && ./install.sh
source venv/bin/activate

# Credenciais GCP
export GOOGLE_APPLICATION_CREDENTIALS="Credentials/gcp_key.json"

# Pipeline completo
cd scripts/python/etl
python download_censo.py 2023
python download_enem.py 2023
python carregar_bigquery.py 2023

# Transformações dbt
cd ../../../dbt
dbt deps && dbt run && dbt test
```

---

## Fontes de Dados

| Dataset | Fonte |
|---------|-------|
| Censo Escolar da Educação Básica | INEP/MEC — microdados.inep.gov.br |
| Microdados do ENEM | INEP/MEC — microdados.inep.gov.br |

---

## Autora

**Vitória Maria** — Engenheira e Analista de Dados

Competências aplicadas neste projeto:

- Engenharia de dados com dbt e BigQuery (modelagem medallion, testes, documentação)
- Análise estatística: Z-Score, correlação de Pearson, clusterização por perfil
- Visualização analítica e storytelling orientado a decisão de política pública
- ETL automatizado com Python e integração com APIs do governo federal
- Versionamento e entrega contínua com Git/GitHub

---

*Dados públicos. Código aberto. GPL-3.0.*
