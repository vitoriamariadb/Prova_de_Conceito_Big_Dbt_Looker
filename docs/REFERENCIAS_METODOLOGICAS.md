# Referências Metodológicas

## Fontes de Dados

### Censo Escolar (INEP/MEC)
- **Fonte:** Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira
- **URL:** https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar
- **Periodicidade:** Anual
- **Variáveis utilizadas:**
  - Matrículas por nível de ensino
  - Quantidade de docentes
  - Infraestrutura escolar (internet, laboratório, biblioteca)
  - Localização (urbana/rural)
  - Rede de ensino (federal, estadual, municipal, privada)

### ENEM (INEP/MEC)
- **Fonte:** Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira
- **URL:** https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem
- **Periodicidade:** Anual
- **Variáveis utilizadas:**
  - Notas por área do conhecimento
  - Nota de redação
  - Dados socioeconômicos (renda familiar)
  - Presença nas provas

### IBGE - Municípios
- **Fonte:** Instituto Brasileiro de Geografia e Estatística
- **URL:** https://servicodados.ibge.gov.br/api/v1/localidades/municipios
- **Variáveis utilizadas:**
  - Código IBGE
  - Nome do município
  - UF
  - Região

---

## Pipeline de Dados

O projeto suporta duas modalidades:

### 1. Dados Reais INEP (Produção)
- Download via scripts em `scripts/python/etl/`
- Carga para BigQuery em tabelas `raw_*`
- Transformação via dbt

### 2. Dados Gerados (Demonstração)
- Fallback automático quando tabelas raw não existem
- Dados gerados mantendo padrões estatísticos realistas
- Permite demonstração do pipeline sem dependência de dados externos

---

## Metodologias Estatísticas

### Clusterização (K-Means)
Agrupamento de UFs por indicadores educacionais utilizando:
- Normalização Z-Score
- Número de clusters determinado por Silhouette Score
- Variáveis: nota ENEM, renda, infraestrutura

**Referências:**
- MacQueen, J. (1967). Some methods for classification and analysis of multivariate observations.
- Rousseeuw, P. J. (1987). Silhouettes: a graphical aid to the interpretation and validation of cluster analysis.

### Correlação de Pearson
Análise de correlações lineares entre indicadores:
- Correlação entre -1 e 1
- p-valor para significância estatística

**Referências:**
- Pearson, K. (1895). Notes on regression and inheritance in the case of two parents.

### Regressão Linear
Modelagem da relação entre variáveis:
- R² como medida de ajuste
- Coeficientes para interpretação de impacto

**Referências:**
- Galton, F. (1886). Regression towards mediocrity in hereditary stature.

---

## Parâmetros e Elasticidades

### Metas do PNE (Plano Nacional de Educação)
| Meta | Indicador | Valor 2024 | Valor 2030 |
|------|-----------|------------|------------|
| 1 | Taxa escolarização 4-5 anos | 100% | 100% |
| 2 | Taxa escolarização 6-14 anos | 100% | 100% |
| 3 | Taxa escolarização 15-17 anos | 85% | 100% |
| 5 | Taxa alfabetização 3º ano | 100% | 100% |
| 7 | IDEB anos iniciais | 6.0 | 7.0 |

**Fonte:** Lei 13.005/2014 - Plano Nacional de Educação

### Elasticidades Estimadas
| Relação | Elasticidade | R² | Fonte |
|---------|-------------|-----|-------|
| Investimento -> Nota ENEM | 0.40 | 0.65 | Literatura |
| Investimento -> Redução Abandono | 0.08 | 0.55 | INEP |
| Internet -> Nota ENEM | 0.25 | 0.48 | Censo Escolar |

---

## Custos de Referência

| Item | Valor (R$) | Unidade | Fonte |
|------|-----------|---------|-------|
| Salário docente médio | 8.000 | mensal | PNAD/IBGE |
| Instalação internet escola | 15.000 | por escola | MEC |
| Montagem laboratório | 50.000 | por escola | MEC |
| Material didático | 350 | aluno/ano | FNDE |

---

## Limitações

1. **Agregação por UF:** A análise agregada por UF pode mascarar desigualdades intramunicipais.

2. **Correlação vs Causalidade:** As correlações encontradas não implicam necessariamente em relações causais.

3. **Período temporal:** Análises focadas em dados recentes (2019-2023).

4. **Defasagens:** Impactos de investimentos podem levar anos para se materializarem.

---

## Atualizações

- **Versão 1.0** - Março 2024: Versão inicial
- **Versão 2.0** - Março 2026: Integração com dados reais INEP, gráficos corporativos

---

## Citação

Para citar este projeto:

```
Projeto MEC Educação - Pipeline de Dados Educacionais
Autora: Vitória Maria
Repositório: github.com/vitoriamariadb/Prova_de_Conceito_Big_Dbt_Looker
```
