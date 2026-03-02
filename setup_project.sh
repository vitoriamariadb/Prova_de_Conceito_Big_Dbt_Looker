#!/bin/bash
set -e

PROJECT_DIR="$HOME/Desenvolvimento/Prova_de_Conceito_Big_Dbt_Looker"
LOG_FILE="$PROJECT_DIR/log_setup.txt"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

log() {
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"
}

log_section() {
    echo "" | tee -a "$LOG_FILE"
    echo "========================================" | tee -a "$LOG_FILE"
    log "$1"
    echo "========================================" | tee -a "$LOG_FILE"
}

rename_mec_files() {
    local dir="$1"
    cd "$dir" || return

    shopt -s nullglob
    for file in microdados_ed_basica_*.csv; do
        year=$(echo "$file" | grep -oP '\d{4}')
        mv "$file" "mec_censo_escolar_${year}.csv"
        log "Renomeado: $file -> mec_censo_escolar_${year}.csv"
    done

    for file in microdados_enem_*.csv; do
        year=$(echo "$file" | grep -oP '\d{4}')
        mv "$file" "mec_enem_${year}.csv"
        log "Renomeado: $file -> mec_enem_${year}.csv"
    done

    for file in microdados_ed_superior_*.csv; do
        year=$(echo "$file" | grep -oP '\d{4}')
        mv "$file" "mec_censo_superior_${year}.csv"
        log "Renomeado: $file -> mec_censo_superior_${year}.csv"
    done
    shopt -u nullglob

    cd - > /dev/null
}

rename_credentials() {
    local cred_dir="$PROJECT_DIR/credentials"

    if [ -f "$cred_dir/provas-de-conceitos-e3111209d733.json" ]; then
        cp "$cred_dir/provas-de-conceitos-e3111209d733.json" "$cred_dir/gcp_key.json"
        log "Copiado: provas-de-conceitos-e3111209d733.json -> gcp_key.json"
    fi
}

log_section "INICIO SETUP - Prova de Conceito Big/Dbt/Looker"

if [ ! -d "$PROJECT_DIR" ]; then
    mkdir -p "$PROJECT_DIR"
    log "Diretorio criado: $PROJECT_DIR"
else
    log "Diretorio ja existe: $PROJECT_DIR"
fi

cd "$PROJECT_DIR"
log "Trabalhando em: $(pwd)"

log_section "CRIANDO ESTRUTURA DE PASTAS"

for dir in bases_csv credentials dbt scripts docs; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        log "Pasta criada: $dir"
    else
        log "Pasta existente (skip): $dir"
    fi
done

mkdir -p dbt/models/staging dbt/models/marts dbt/macros dbt/tests dbt/seeds dbt/snapshots
log "Subpastas dbt criadas"

log_section "CRIANDO ARQUIVOS BASE"

cat > .gitignore << 'EOF'
# dbt
target/
dbt_packages/
logs/
dbt/profiles.yml

# Credentials (NUNCA commitar)
*.json
credentials/

# Dados grandes
bases_csv/*.csv
!bases_csv/empty_*.csv

# Python
__pycache__/
*.pyc
.venv/
venv/

# IDE
.vscode/
.idea/

# OS
.DS_Store
*.swp

# Logs
*.log
log_setup.txt
EOF
log "Criado: .gitignore"

cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2024 Vitoria Maria

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
log "Criado: LICENSE (MIT)"

cat > CONTRIBUTING.md << 'EOF'
# Contribuindo

## Como Contribuir

1. Faça um **Fork** do repositório
2. Crie uma branch para sua feature: `git checkout -b feature/minha-feature`
3. Commit suas mudanças: `git commit -m 'Adiciona minha feature'`
4. Push para a branch: `git push origin feature/minha-feature`
5. Abra um **Pull Request**

## Padrões

- Código Python: PEP8
- SQL (dbt): snake_case, prefixos stg_/mart_
- Commits: mensagens em português, descritivas

## Dúvidas

Abra uma Issue descrevendo sua dúvida ou sugestão.
EOF
log "Criado: CONTRIBUTING.md"

log_section "CONFIGURANDO DBT"

cat > dbt/dbt_project.yml << 'EOF'
name: 'mec_education_demo'
version: '1.0.0'
config-version: 2

profile: 'mec_education_demo'

model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]
docs-paths: ["docs"]

target-path: "target"
clean-targets:
  - "target"
  - "dbt_packages"

models:
  mec_education_demo:
    staging:
      +materialized: view
      +schema: staging
    marts:
      +materialized: table
      +schema: marts
EOF
log "Criado: dbt/dbt_project.yml"

cat > dbt/models/staging/stg_censo_escolar.sql << 'EOF'
{{ config(materialized='view') }}

SELECT
    1 as id,
    2024 as ano,
    'DF' as uf,
    'Placeholder - substituir por dados reais' as descricao
EOF
log "Criado: dbt/models/staging/stg_censo_escolar.sql"

cat > dbt/models/staging/stg_enem.sql << 'EOF'
{{ config(materialized='view') }}

SELECT
    1 as id,
    2024 as ano,
    500.0 as nota_media,
    'Placeholder ENEM' as descricao
EOF
log "Criado: dbt/models/staging/stg_enem.sql"

cat > dbt/models/marts/mart_educacao_uf.sql << 'EOF'
{{ config(materialized='table') }}

WITH censo AS (
    SELECT * FROM {{ ref('stg_censo_escolar') }}
),

enem AS (
    SELECT * FROM {{ ref('stg_enem') }}
)

SELECT
    censo.uf,
    censo.ano,
    enem.nota_media,
    'Agregacao por UF - placeholder' as descricao
FROM censo
LEFT JOIN enem ON censo.ano = enem.ano
EOF
log "Criado: dbt/models/marts/mart_educacao_uf.sql"

cat > dbt/models/staging/schema.yml << 'EOF'
version: 2

models:
  - name: stg_censo_escolar
    description: "Dados staging do Censo Escolar MEC"
    columns:
      - name: id
        description: "ID placeholder"
      - name: ano
        description: "Ano de referência"
      - name: uf
        description: "Unidade Federativa"

  - name: stg_enem
    description: "Dados staging do ENEM"
    columns:
      - name: id
        description: "ID placeholder"
      - name: ano
        description: "Ano de referência"
      - name: nota_media
        description: "Nota média"
EOF
log "Criado: dbt/models/staging/schema.yml"

cat > dbt/models/marts/schema.yml << 'EOF'
version: 2

models:
  - name: mart_educacao_uf
    description: "Mart agregado de educação por UF"
    columns:
      - name: uf
        description: "Unidade Federativa"
        tests:
          - not_null
      - name: ano
        description: "Ano de referência"
      - name: nota_media
        description: "Nota média ENEM"
EOF
log "Criado: dbt/models/marts/schema.yml"

cat > dbt/macros/utils.sql << 'EOF'
{% macro gerar_surrogate_key(columns) %}
    {{ return(dbt_utils.generate_surrogate_key(columns)) }}
{% endmacro %}

{% macro current_timestamp_br() %}
    DATETIME(CURRENT_TIMESTAMP(), 'America/Sao_Paulo')
{% endmacro %}

{% macro limpar_texto(column) %}
    TRIM(UPPER({{ column }}))
{% endmacro %}
EOF
log "Criado: dbt/macros/utils.sql"

cat > dbt/packages.yml << 'EOF'
packages:
  - package: dbt-labs/dbt_utils
    version: ">=1.0.0"
EOF
log "Criado: dbt/packages.yml"

log_section "CONFIGURANDO CSVs PLACEHOLDER"

echo "ANO,UF,QTD_ESCOLAS,QTD_ALUNOS" > bases_csv/empty_censo.csv
echo "ANO,UF,NOTA_CN,NOTA_CH,NOTA_LC,NOTA_MT,NOTA_REDACAO" > bases_csv/empty_enem.csv
echo "ANO,UF,IES,QTD_CURSOS,QTD_VAGAS" > bases_csv/empty_censo_superior.csv
log "Criados: CSVs placeholder em bases_csv/"

log_section "CRIANDO SCRIPTS QoL"

cat > scripts/init_dbt.sh << 'EOF'
#!/bin/bash
set -e

echo "=== Inicializando ambiente dbt ==="

cd "$(dirname "$0")/../dbt"

echo "-> Instalando dependências (dbt deps)..."
dbt deps

echo "-> Verificando conexão (dbt debug)..."
dbt debug

echo "-> Compilando modelos (dbt compile)..."
dbt compile

echo "=== dbt pronto! ==="
EOF
chmod +x scripts/init_dbt.sh
log "Criado: scripts/init_dbt.sh"

cat > scripts/validate_gcp.sh << 'EOF'
#!/bin/bash
set -e

echo "=== Validando configuração GCP ==="

CRED_FILE="../credentials/provas-de-conceitos-e3111209d733.json"
CRED_ALT="../credentials/gcp_key.json"

echo "-> Verificando gcloud CLI..."
if command -v gcloud &> /dev/null; then
    echo "   gcloud encontrado: $(gcloud --version | head -1)"
    echo ""
    echo "-> Contas autenticadas:"
    gcloud auth list 2>/dev/null || echo "   Nenhuma conta autenticada"
else
    echo "   AVISO: gcloud CLI não encontrado"
fi

echo ""
echo "-> Verificando credenciais..."

if [ -f "$CRED_FILE" ]; then
    echo "   OK: $CRED_FILE existe"
    PROJECT=$(grep -o '"project_id": "[^"]*"' "$CRED_FILE" | cut -d'"' -f4)
    echo "   Project ID: $PROJECT"
elif [ -f "$CRED_ALT" ]; then
    echo "   OK: $CRED_ALT existe"
    PROJECT=$(grep -o '"project_id": "[^"]*"' "$CRED_ALT" | cut -d'"' -f4)
    echo "   Project ID: $PROJECT"
else
    echo "   ERRO: Nenhum arquivo de credencial encontrado!"
    echo "   Esperado: $CRED_FILE ou $CRED_ALT"
    exit 1
fi

echo ""
echo "=== Validação concluída ==="
EOF
chmod +x scripts/validate_gcp.sh
log "Criado: scripts/validate_gcp.sh"

cat > scripts/download_rename.sh << 'EOF'
#!/bin/bash
set -e

echo "=== Download e Renomeação de Microdados MEC ==="
echo ""
echo "STUB: Este script será configurado para:"
echo "  1. wget dos microdados do INEP"
echo "  2. Descompactação automática"
echo "  3. Renomeação para padrão mec_*"
echo ""
echo "URLs dos dados:"
echo "  - Censo Escolar: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar"
echo "  - ENEM: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem"
echo "  - Censo Superior: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-da-educacao-superior"
echo ""
echo "Para uso futuro, adicione as funções de download aqui."

rename_mec_files() {
    local dir="${1:-../bases_csv}"
    cd "$dir" || return

    for file in microdados_ed_basica_*.csv 2>/dev/null; do
        [ -e "$file" ] || continue
        year=$(echo "$file" | grep -oP '\d{4}')
        mv "$file" "mec_censo_escolar_${year}.csv"
        echo "Renomeado: $file -> mec_censo_escolar_${year}.csv"
    done

    for file in microdados_enem_*.csv 2>/dev/null; do
        [ -e "$file" ] || continue
        year=$(echo "$file" | grep -oP '\d{4}')
        mv "$file" "mec_enem_${year}.csv"
        echo "Renomeado: $file -> mec_enem_${year}.csv"
    done

    cd - > /dev/null
}

if [ "$1" == "--rename" ]; then
    rename_mec_files "${2:-../bases_csv}"
fi
EOF
chmod +x scripts/download_rename.sh
log "Criado: scripts/download_rename.sh"

cat > scripts/run_dbt.sh << 'EOF'
#!/bin/bash
set -e

cd "$(dirname "$0")/../dbt"

case "${1:-run}" in
    run)
        echo "-> dbt run..."
        dbt run
        ;;
    test)
        echo "-> dbt test..."
        dbt test
        ;;
    build)
        echo "-> dbt build (run + test)..."
        dbt build
        ;;
    docs)
        echo "-> Gerando documentação..."
        dbt docs generate
        dbt docs serve --port 8080
        ;;
    fresh)
        echo "-> dbt run --full-refresh..."
        dbt run --full-refresh
        ;;
    *)
        echo "Uso: $0 {run|test|build|docs|fresh}"
        exit 1
        ;;
esac
EOF
chmod +x scripts/run_dbt.sh
log "Criado: scripts/run_dbt.sh"

log_section "CRIANDO SCRIPT PYTHON DE REGRESSÃO"

cat > scripts/regressao_educacao.py << 'EOF'
#!/usr/bin/env python3
"""
Análise de Regressão Linear: Renda vs Nota ENEM
Projeto: Prova de Conceito MEC/BigQuery/Looker
"""

import sys

try:
    import pandas as pd
    import numpy as np
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import r2_score, mean_squared_error
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except ImportError as e:
    print(f"ERRO: Dependência não instalada: {e}")
    print("Execute: pip install pandas numpy scikit-learn matplotlib")
    sys.exit(1)


def gerar_dados_exemplo():
    """Gera dados sintéticos para demonstração"""
    np.random.seed(42)
    n = 500

    renda = np.random.exponential(scale=3000, size=n) + 1000
    ruido = np.random.normal(0, 50, n)
    nota = 400 + (renda * 0.02) + ruido
    nota = np.clip(nota, 0, 1000)

    return pd.DataFrame({
        'RENDA_FAMILIAR': renda,
        'NOTA_ENEM': nota,
        'UF': np.random.choice(['SP', 'RJ', 'MG', 'BA', 'RS'], n),
        'ANO': 2023
    })


def carregar_dados(caminho_csv=None):
    """Carrega dados reais ou gera exemplo"""
    if caminho_csv:
        try:
            df = pd.read_csv(caminho_csv)
            print(f"Dados carregados: {caminho_csv} ({len(df)} linhas)")
            return df
        except FileNotFoundError:
            print(f"Arquivo não encontrado: {caminho_csv}")
            print("Usando dados de exemplo...")

    print("Gerando dados sintéticos para demonstração...")
    return gerar_dados_exemplo()


def executar_regressao(df, col_x='RENDA_FAMILIAR', col_y='NOTA_ENEM'):
    """Executa regressão linear e retorna métricas"""

    df_clean = df[[col_x, col_y]].dropna()

    if len(df_clean) < 10:
        raise ValueError("Dados insuficientes para regressão")

    X = df_clean[[col_x]].values
    y = df_clean[col_y].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    modelo = LinearRegression()
    modelo.fit(X_train, y_train)

    y_pred = modelo.predict(X_test)

    resultados = {
        'coeficiente': modelo.coef_[0],
        'intercepto': modelo.intercept_,
        'r2_score': r2_score(y_test, y_pred),
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
        'n_amostras': len(df_clean)
    }

    return modelo, resultados, (X, y)


def plotar_regressao(modelo, X, y, resultados, output_path='regressao_renda_nota.png'):
    """Gera scatter plot com linha de regressão"""

    plt.figure(figsize=(10, 6))

    plt.scatter(X, y, alpha=0.5, label='Dados', color='steelblue')

    X_line = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
    y_line = modelo.predict(X_line)
    plt.plot(X_line, y_line, color='red', linewidth=2, label='Regressão Linear')

    plt.xlabel('Renda Familiar (R$)', fontsize=12)
    plt.ylabel('Nota ENEM', fontsize=12)
    plt.title('Regressão Linear: Renda vs Nota ENEM', fontsize=14)

    texto = f"R² = {resultados['r2_score']:.4f}\n"
    texto += f"Coef = {resultados['coeficiente']:.6f}\n"
    texto += f"n = {resultados['n_amostras']}"
    plt.text(0.05, 0.95, texto, transform=plt.gca().transAxes,
             verticalalignment='top', fontsize=10,
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

    return output_path


def main():
    print("=" * 60)
    print("ANÁLISE DE REGRESSÃO: RENDA vs NOTA ENEM")
    print("=" * 60)
    print()

    csv_path = sys.argv[1] if len(sys.argv) > 1 else None

    df = carregar_dados(csv_path)

    print(f"\nDataset: {len(df)} registros")
    print(df.describe())

    try:
        modelo, resultados, (X, y) = executar_regressao(df)

        print("\n" + "=" * 60)
        print("RESULTADOS DA REGRESSÃO")
        print("=" * 60)
        print(f"Coeficiente (β₁):  {resultados['coeficiente']:.6f}")
        print(f"Intercepto (β₀):   {resultados['intercepto']:.2f}")
        print(f"R² Score:          {resultados['r2_score']:.4f}")
        print(f"RMSE:              {resultados['rmse']:.2f}")
        print(f"Amostras:          {resultados['n_amostras']}")

        print("\nInterpretação:")
        print(f"  Para cada R$ 1.000 de aumento na renda,")
        print(f"  a nota ENEM aumenta em média {resultados['coeficiente']*1000:.2f} pontos.")

        output_file = plotar_regressao(modelo, X, y, resultados)
        print(f"\nGráfico salvo: {output_file}")

    except Exception as e:
        print(f"\nERRO na regressão: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("Análise concluída!")
    print("=" * 60)


if __name__ == "__main__":
    main()
EOF
chmod +x scripts/regressao_educacao.py
log "Criado: scripts/regressao_educacao.py"

log_section "CRIANDO DOCUMENTAÇÃO"

cat > README.md << 'EOF'
# Prova de Conceito: MEC + BigQuery + dbt + Looker

Pipeline de dados educacionais do MEC para análise e visualização.

## Estrutura do Projeto

```
Prova_de_Conceito_Big_Dbt_Looker/
├── bases_csv/              # Dados brutos (CSVs do INEP)
│   ├── empty_censo.csv
│   ├── empty_enem.csv
│   └── empty_censo_superior.csv
├── credentials/            # Credenciais GCP (NÃO COMMITAR)
│   └── gcp_key.json
├── dbt/                    # Projeto dbt
│   ├── models/
│   │   ├── staging/        # Views de staging
│   │   └── marts/          # Tabelas agregadas
│   ├── macros/
│   ├── tests/
│   └── dbt_project.yml
├── scripts/                # Automação
│   ├── init_dbt.sh
│   ├── validate_gcp.sh
│   ├── run_dbt.sh
│   ├── download_rename.sh
│   └── regressao_educacao.py
├── docs/                   # Documentação dbt
├── .gitignore
├── LICENSE
├── CONTRIBUTING.md
└── README.md
```

## Setup Inicial

### 1. Pré-requisitos

```bash
# Python 3.9+
python3 --version

# dbt-bigquery
pip install dbt-bigquery

# gcloud CLI
gcloud --version
```

### 2. Configurar Credenciais GCP

```bash
# Coloque sua service account key em:
credentials/gcp_key.json

# Valide:
./scripts/validate_gcp.sh
```

### 3. Configurar profiles.yml

Crie `~/.dbt/profiles.yml`:

```yaml
mec_education_demo:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: service-account
      project: provas-de-conceitos
      dataset: educacao_dev
      keyfile: /caminho/para/credentials/gcp_key.json
      location: US
      threads: 4
```

### 4. Inicializar dbt

```bash
./scripts/init_dbt.sh
```

## Uso

### Rodar Modelos dbt

```bash
./scripts/run_dbt.sh run      # Executa modelos
./scripts/run_dbt.sh test     # Roda testes
./scripts/run_dbt.sh build    # Run + Test
./scripts/run_dbt.sh docs     # Gera e serve docs
```

### Análise de Regressão

```bash
cd scripts
python regressao_educacao.py                    # Dados sintéticos
python regressao_educacao.py ../bases_csv/dados.csv  # Dados reais
```

## Fontes de Dados

- **Censo Escolar**: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar
- **ENEM**: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem
- **Censo Superior**: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-da-educacao-superior

## Looker

Após rodar os modelos dbt, conecte o Looker Studio ao BigQuery:
1. Acesse [Looker Studio](https://lookerstudio.google.com)
2. Conecte ao projeto `provas-de-conceitos`
3. Selecione dataset `educacao_dev` ou `educacao_prod`

## Contribuindo

Veja [CONTRIBUTING.md](CONTRIBUTING.md)

## Licença

MIT - Veja [LICENSE](LICENSE)
EOF
log "Criado: README.md"

cat > docs/index.html << 'EOF'
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentação - MEC Education Demo</title>
    <style>
        body { font-family: system-ui, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        h1 { color: #1a73e8; }
        code { background: #f1f3f4; padding: 2px 6px; border-radius: 4px; }
        pre { background: #f1f3f4; padding: 16px; border-radius: 8px; overflow-x: auto; }
    </style>
</head>
<body>
    <h1>MEC Education Demo - Documentação dbt</h1>

    <p>Este é um placeholder para a documentação gerada pelo dbt.</p>

    <h2>Gerar Documentação</h2>
    <pre><code>cd dbt
dbt docs generate
dbt docs serve --port 8080</code></pre>

    <h2>Modelos Disponíveis</h2>
    <ul>
        <li><strong>stg_censo_escolar</strong>: Staging do Censo Escolar</li>
        <li><strong>stg_enem</strong>: Staging do ENEM</li>
        <li><strong>mart_educacao_uf</strong>: Agregação por UF</li>
    </ul>

    <h2>Links Úteis</h2>
    <ul>
        <li><a href="https://docs.getdbt.com/">Documentação dbt</a></li>
        <li><a href="https://cloud.google.com/bigquery/docs">BigQuery Docs</a></li>
        <li><a href="https://www.gov.br/inep">INEP - Dados Abertos</a></li>
    </ul>
</body>
</html>
EOF
log "Criado: docs/index.html"

log_section "RENOMEANDO ARQUIVOS EXISTENTES"

rename_credentials
rename_mec_files "$PROJECT_DIR/bases_csv"

log_section "CONFIGURANDO GIT"

if [ ! -d ".git" ]; then
    git init
    log "Git inicializado"
else
    log "Git já inicializado (skip)"
fi

REMOTE_URL="https://github.com/vitoriamariadb/Prova_de_Conceito_Big_Dbt_Looker.git"
CURRENT_REMOTE=$(git remote get-url origin 2>/dev/null || echo "")

if [ -z "$CURRENT_REMOTE" ]; then
    git remote add origin "$REMOTE_URL"
    log "Remote adicionado: $REMOTE_URL"
elif [ "$CURRENT_REMOTE" != "$REMOTE_URL" ]; then
    log "Remote existente: $CURRENT_REMOTE (mantido)"
else
    log "Remote já configurado: $REMOTE_URL"
fi

git add .
log "Arquivos staged para commit"

if git diff --cached --quiet; then
    log "Nenhuma mudança para commit"
else
    git commit -m "Setup inicial: estrutura completa MEC/dbt/BigQuery/Looker

- Estrutura de pastas (data, dbt, scripts, docs)
- Projeto dbt com models staging/marts
- Scripts de automação (init, validate, run)
- Script Python de regressão educacional
- Documentação README e placeholders"
    log "Commit criado"
fi

log_section "SETUP CONCLUÍDO"

echo ""
echo "=========================================="
echo "  ESTRUTURA PRONTA!"
echo "=========================================="
echo ""
echo "Próximos passos:"
echo "  1. Configure ~/.dbt/profiles.yml"
echo "  2. Coloque credenciais em credentials/"
echo "  3. Execute: ./scripts/validate_gcp.sh"
echo "  4. Execute: ./scripts/init_dbt.sh"
echo ""
echo "Para push manual:"
echo "  git push -u origin main"
echo ""
echo "Log completo em: $LOG_FILE"
echo ""
log "Script finalizado com sucesso"
