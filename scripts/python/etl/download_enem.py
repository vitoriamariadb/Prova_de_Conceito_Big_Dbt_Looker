#!/usr/bin/env python3

import os
import sys
import zipfile
import requests
from pathlib import Path

BASE_URL_ENEM = "https://download.inep.gov.br/microdados/microdados_enem_{ano}.zip"
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "raw"


def download_arquivo(url: str, destino: Path, chunk_size: int = 8192) -> bool:
    try:
        print(f"Baixando: {url}")
        response = requests.get(url, stream=True, timeout=600)
        response.raise_for_status()

        tamanho_total = int(response.headers.get('content-length', 0))
        tamanho_baixado = 0

        with open(destino, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    tamanho_baixado += len(chunk)
                    if tamanho_total:
                        pct = (tamanho_baixado / tamanho_total) * 100
                        print(f"\r  Progresso: {pct:.1f}%", end="", flush=True)

        print(f"\n  Salvo: {destino}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"Erro no download: {e}")
        return False


def extrair_zip(arquivo_zip: Path, destino: Path) -> bool:
    try:
        print(f"Extraindo: {arquivo_zip}")
        with zipfile.ZipFile(arquivo_zip, 'r') as zf:
            zf.extractall(destino)
        print(f"  Extraido para: {destino}")
        return True
    except zipfile.BadZipFile as e:
        print(f"Erro ao extrair ZIP: {e}")
        return False


def download_enem(ano: int, extrair: bool = True) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    url = BASE_URL_ENEM.format(ano=ano)
    arquivo_zip = DATA_DIR / f"microdados_enem_{ano}.zip"
    pasta_destino = DATA_DIR / f"enem_{ano}"

    if pasta_destino.exists() and any(pasta_destino.iterdir()):
        print(f"ENEM {ano} ja existe em: {pasta_destino}")
        return pasta_destino

    if not arquivo_zip.exists():
        sucesso = download_arquivo(url, arquivo_zip)
        if not sucesso:
            url_alternativa = "https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem"
            print(f"\nDownload automatico falhou.")
            print(f"Baixe manualmente de: {url_alternativa}")
            print(f"Salve em: {arquivo_zip}")
            return None

    if extrair:
        pasta_destino.mkdir(parents=True, exist_ok=True)
        extrair_zip(arquivo_zip, pasta_destino)

    return pasta_destino


def listar_arquivos_enem(pasta: Path) -> list:
    if not pasta or not pasta.exists():
        return []

    arquivos = []
    for ext in ['*.csv', '*.CSV', '*.txt', '*.TXT']:
        arquivos.extend(pasta.rglob(ext))

    return sorted(arquivos)


def main():
    print("=" * 70)
    print("DOWNLOAD MICRODADOS ENEM - INEP")
    print("=" * 70)
    print()

    ano = 2023
    if len(sys.argv) > 1:
        try:
            ano = int(sys.argv[1])
        except ValueError:
            print(f"Ano invalido: {sys.argv[1]}")
            sys.exit(1)

    print(f"Ano selecionado: {ano}")
    print(f"Diretorio de dados: {DATA_DIR}")
    print(f"\nATENCAO: Microdados ENEM podem ter ~8GB. Certifique-se de ter espaco.")
    print()

    pasta = download_enem(ano)

    if pasta:
        print("\n" + "=" * 70)
        print("ARQUIVOS DISPONIVEIS")
        print("=" * 70)

        arquivos = listar_arquivos_enem(pasta)
        for arq in arquivos[:20]:
            tamanho_mb = arq.stat().st_size / (1024 * 1024)
            print(f"  {arq.name}: {tamanho_mb:.1f} MB")

        if len(arquivos) > 20:
            print(f"  ... e mais {len(arquivos) - 20} arquivos")

        print(f"\nTotal: {len(arquivos)} arquivos")

    print("\n" + "=" * 70)
    print("Download concluido!")
    print("=" * 70)


if __name__ == "__main__":
    main()
