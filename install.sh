#!/bin/bash
set -e

echo "=== Instalacao do Projeto MEC/dbt/BigQuery ==="
echo ""

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "-> Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python3 nao encontrado. Instale com: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
echo "   Python encontrado: $PYTHON_VERSION"

echo ""
echo "-> Criando ambiente virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   venv criado"
else
    echo "   venv ja existe"
fi

echo ""
echo "-> Ativando venv e instalando dependencias..."
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "-> Verificando dbt..."
if command -v dbt &> /dev/null; then
    echo "   dbt instalado: $(dbt --version | head -1)"
else
    echo "   AVISO: dbt nao encontrado no PATH apos instalacao"
fi

echo ""
echo "-> Verificando gcloud..."
if command -v gcloud &> /dev/null; then
    echo "   gcloud instalado: $(gcloud --version | head -1)"
else
    echo "   AVISO: gcloud CLI nao encontrado"
    echo "   Instale via: https://cloud.google.com/sdk/docs/install"
fi

echo ""
echo "-> Estrutura do projeto:"
echo "  scripts/python/ - Scripts de analise"
echo "  scripts/bash/   - Scripts de automacao"
echo "  data/raw/       - Dados brutos"
echo "  data/processed/ - Dados processados"
echo "  outputs/        - Saidas de analises"
echo "  dbt/            - Projeto dbt"

echo ""
echo "=== Instalacao concluida! ==="
echo ""
echo "Proximos passos:"
echo "  1. Ative o venv: source venv/bin/activate"
echo "  2. Configure credenciais GCP em credentials/"
echo "  3. Configure dbt: cp dbt/profiles.yml ~/.dbt/profiles.yml"
echo "  4. Teste dbt: cd dbt && dbt debug"
echo ""
