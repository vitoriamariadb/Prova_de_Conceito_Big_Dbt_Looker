#!/usr/bin/env python3

import os
import sys
from pathlib import Path

try:
    import pandas as pd
    from google.cloud import bigquery
    from google.oauth2 import service_account
except ImportError as e:
    print(f"ERRO: Dependencia nao instalada: {e}")
    print("Execute: pip install pandas google-cloud-bigquery")
    sys.exit(1)

PROJECT_ID = "provas-de-conceitos"
DATASET_ID = "mec_educacao_dev"
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "raw"
CREDENTIALS_PATH = Path(__file__).parent.parent.parent.parent / "credentials" / "gcp_key.json"

TABELAS_CENSO = {
    "ESCOLAS": "raw_censo_escolas",
    "MATRICULAS": "raw_censo_matriculas",
    "DOCENTES": "raw_censo_docentes",
    "TURMAS": "raw_censo_turmas",
}

TABELAS_ENEM = {
    "MICRODADOS": "raw_enem_microdados",
}


def get_bigquery_client():
    if CREDENTIALS_PATH.exists():
        credentials = service_account.Credentials.from_service_account_file(
            str(CREDENTIALS_PATH)
        )
        return bigquery.Client(project=PROJECT_ID, credentials=credentials)
    else:
        return bigquery.Client(project=PROJECT_ID)


def carregar_csv_bigquery(
    client: bigquery.Client,
    arquivo_csv: Path,
    tabela_destino: str,
    schema: list = None,
    modo: str = "WRITE_TRUNCATE"
) -> bool:
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{tabela_destino}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True if schema is None else False,
        write_disposition=modo,
        max_bad_records=100,
    )

    if schema:
        job_config.schema = schema

    try:
        print(f"Carregando: {arquivo_csv.name} -> {tabela_destino}")
        tamanho_mb = arquivo_csv.stat().st_size / (1024 * 1024)
        print(f"  Tamanho: {tamanho_mb:.1f} MB")

        with open(arquivo_csv, "rb") as f:
            load_job = client.load_table_from_file(f, table_id, job_config=job_config)

        load_job.result()

        tabela = client.get_table(table_id)
        print(f"  Linhas carregadas: {tabela.num_rows:,}")
        return True

    except Exception as e:
        print(f"  ERRO: {e}")
        return False


def encontrar_arquivo_censo(pasta: Path, tipo: str) -> Path:
    padroes = {
        "ESCOLAS": ["*ESCOLAS*.CSV", "*ESCOLA*.csv", "*escolas*.csv"],
        "MATRICULAS": ["*MATRICULA*.CSV", "*MATRICULA*.csv", "*matricula*.csv"],
        "DOCENTES": ["*DOCENTE*.CSV", "*DOCENTE*.csv", "*docente*.csv"],
        "TURMAS": ["*TURMA*.CSV", "*TURMA*.csv", "*turma*.csv"],
    }

    for padrao in padroes.get(tipo, []):
        arquivos = list(pasta.rglob(padrao))
        if arquivos:
            return max(arquivos, key=lambda x: x.stat().st_size)

    return None


def encontrar_arquivo_enem(pasta: Path) -> Path:
    padroes = ["*MICRODADOS*.CSV", "*MICRODADOS*.csv", "*microdados*.csv"]

    for padrao in padroes:
        arquivos = list(pasta.rglob(padrao))
        if arquivos:
            return max(arquivos, key=lambda x: x.stat().st_size)

    return None


def carregar_censo(client: bigquery.Client, ano: int):
    pasta = DATA_DIR / f"censo_escolar_{ano}"

    if not pasta.exists():
        print(f"Pasta nao encontrada: {pasta}")
        print("Execute primeiro: python download_censo.py")
        return

    print(f"\n{'=' * 70}")
    print(f"CARREGANDO CENSO ESCOLAR {ano}")
    print(f"{'=' * 70}")

    for tipo, tabela in TABELAS_CENSO.items():
        arquivo = encontrar_arquivo_censo(pasta, tipo)
        if arquivo:
            carregar_csv_bigquery(client, arquivo, tabela)
        else:
            print(f"  Arquivo {tipo} nao encontrado")


def carregar_enem(client: bigquery.Client, ano: int, amostra: bool = True):
    pasta = DATA_DIR / f"enem_{ano}"

    if not pasta.exists():
        print(f"Pasta nao encontrada: {pasta}")
        print("Execute primeiro: python download_enem.py")
        return

    print(f"\n{'=' * 70}")
    print(f"CARREGANDO ENEM {ano}")
    print(f"{'=' * 70}")

    arquivo = encontrar_arquivo_enem(pasta)
    if arquivo:
        if amostra:
            print("  Modo amostra ativado (primeiras 100k linhas)")
            df = pd.read_csv(arquivo, sep=';', encoding='latin-1', nrows=100000)

            temp_csv = DATA_DIR / f"enem_{ano}_amostra.csv"
            df.to_csv(temp_csv, index=False)
            carregar_csv_bigquery(client, temp_csv, TABELAS_ENEM["MICRODADOS"])
            temp_csv.unlink()
        else:
            carregar_csv_bigquery(client, arquivo, TABELAS_ENEM["MICRODADOS"])
    else:
        print("  Arquivo ENEM nao encontrado")


def main():
    print("=" * 70)
    print("CARREGAR DADOS INEP PARA BIGQUERY")
    print("=" * 70)
    print()

    print(f"Projeto: {PROJECT_ID}")
    print(f"Dataset: {DATASET_ID}")
    print(f"Diretorio dados: {DATA_DIR}")
    print()

    client = get_bigquery_client()

    ano = 2023
    if len(sys.argv) > 1:
        try:
            ano = int(sys.argv[1])
        except ValueError:
            pass

    amostra = "--full" not in sys.argv

    carregar_censo(client, ano)
    carregar_enem(client, ano, amostra=amostra)

    print("\n" + "=" * 70)
    print("Carga concluida!")
    print("=" * 70)


if __name__ == "__main__":
    main()
