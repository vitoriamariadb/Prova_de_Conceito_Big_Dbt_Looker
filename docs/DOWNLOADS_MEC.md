# Guia de Downloads - Dados Abertos MEC

Este documento contém comandos para download manual dos microdados do MEC/INEP.

---

## 1. Comandos de Download

### Censo Escolar (Essencial)

```bash
cd ~/Desenvolvimento/Prova_de_Conceito_Big_Dbt_Looker/bases_csv

wget -c https://download.inep.gov.br/microdados/microdados_censo_escolar_2022.zip
wget -c https://download.inep.gov.br/microdados/microdados_censo_escolar_2023.zip
```

### ENEM (Essencial)

```bash
wget -c https://download.inep.gov.br/microdados/microdados_enem_2022.zip
wget -c https://download.inep.gov.br/microdados/microdados_enem_2023.zip
```

### PDDE - Programa Dinheiro Direto na Escola

```bash
curl -L "https://dados.gov.br/dados/conjuntos-dados/programa-dinheiro-direto-na-escola-pdde" -o pdde_info.html
```

### SIOPE - Sistema de Informações sobre Orçamentos Públicos em Educação

```bash
curl -L "https://www.fnde.gov.br/siope/dadosAbertos" -o siope_dados.html
```

---

## 2. Datasets Opcionais

### SisIndígena - Sistema de Escolas Indígenas

```bash
curl -L "https://dadosabertos.mec.gov.br/sisindigena" -o sisindigena_info.html
```

### PNEERQ - Programa Nacional de Educação Escolar Quilombola

```bash
curl -L "https://dados.gov.br/dados/conjuntos-dados/pnnerq-escola-quilombo" -o pneerq_info.html
```

### SISU - Sistema de Seleção Unificada

```bash
curl -L "https://dadosabertos.mec.gov.br/sisu" -o sisu_info.html
```

### PROUNI - Programa Universidade para Todos

```bash
curl -L "https://dadosabertos.mec.gov.br/prouni" -o prouni_info.html
```

### FIES - Financiamento Estudantil

```bash
curl -L "https://dadosabertos.mec.gov.br/fies" -o fies_info.html
```

---

## 3. Descompactação

Após baixar os ZIPs, descompacte manualmente:

```bash
cd ~/Desenvolvimento/Prova_de_Conceito_Big_Dbt_Looker/bases_csv

unzip microdados_censo_escolar_2022.zip -d censo_2022/
unzip microdados_censo_escolar_2023.zip -d censo_2023/
unzip microdados_enem_2022.zip -d enem_2022/
unzip microdados_enem_2023.zip -d enem_2023/
```

---

## 4. Renomeações Padronizadas

Após extrair, renomeie para o padrão `mec_*`:

```bash
cd ~/Desenvolvimento/Prova_de_Conceito_Big_Dbt_Looker/bases_csv

mv censo_2022/DADOS/microdados_ed_basica_2022.csv mec_censo_escolar_2022.csv
mv censo_2023/DADOS/microdados_ed_basica_2023.csv mec_censo_escolar_2023.csv

mv enem_2022/DADOS/MICRODADOS_ENEM_2022.csv mec_enem_2022.csv
mv enem_2023/DADOS/MICRODADOS_ENEM_2023.csv mec_enem_2023.csv

rm -rf censo_2022/ censo_2023/ enem_2022/ enem_2023/
rm -f *.zip
```

---

## 5. Validação GCP

Verifique suas credenciais antes de subir para BigQuery:

```bash
gcloud auth list

gcloud auth activate-service-account --key-file=../credentials/provas-de-conceitos-e3111209d733.json

gcloud config set project provas-de-conceitos

bq ls
```

---

## 6. Upload para BigQuery

```bash
bq load --source_format=CSV --autodetect \
    provas-de-conceitos:mec_educacao.censo_escolar_2022 \
    mec_censo_escolar_2022.csv

bq load --source_format=CSV --autodetect \
    provas-de-conceitos:mec_educacao.censo_escolar_2023 \
    mec_censo_escolar_2023.csv

bq load --source_format=CSV --autodetect \
    provas-de-conceitos:mec_educacao.enem_2022 \
    mec_enem_2022.csv

bq load --source_format=CSV --autodetect \
    provas-de-conceitos:mec_educacao.enem_2023 \
    mec_enem_2023.csv
```

---

## Nuances e Edge Cases

| Situação | Solução |
|----------|---------|
| Link quebrado | Verifique em dados.gov.br ou inep.gov.br |
| Arquivo muito grande (>2GB) | Use `wget -c` para continuar download |
| Timeout | Adicione `--timeout=300` ao wget |
| Encoding errado | Use `iconv -f ISO-8859-1 -t UTF-8` |
| Colunas faltantes | Verifique dicionário de dados no ZIP |

## Custos Estimados no BigQuery

| Dataset | Tamanho Aproximado | Custo Query (USD) |
|---------|-------------------|-------------------|
| Censo Escolar 2023 | ~2GB | ~0.01/query |
| ENEM 2023 | ~4GB | ~0.02/query |
| PDDE | ~500MB | ~0.003/query |

---

Estrutura de downloads pronta para cópia manual!
