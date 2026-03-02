#!/usr/bin/env python3

import requests
import csv
import sys

IBGE_API = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios?orderBy=nome"

UF_REGIAO = {
    'AC': 'Norte', 'AL': 'Nordeste', 'AP': 'Norte', 'AM': 'Norte',
    'BA': 'Nordeste', 'CE': 'Nordeste', 'DF': 'Centro-Oeste', 'ES': 'Sudeste',
    'GO': 'Centro-Oeste', 'MA': 'Nordeste', 'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste',
    'MG': 'Sudeste', 'PA': 'Norte', 'PB': 'Nordeste', 'PR': 'Sul',
    'PE': 'Nordeste', 'PI': 'Nordeste', 'RJ': 'Sudeste', 'RN': 'Nordeste',
    'RS': 'Sul', 'RO': 'Norte', 'RR': 'Norte', 'SC': 'Sul',
    'SP': 'Sudeste', 'SE': 'Nordeste', 'TO': 'Norte'
}


def buscar_municipios_ibge():
    print("Buscando municipios da API IBGE...")
    response = requests.get(IBGE_API)
    response.raise_for_status()
    return response.json()


def processar_municipios(dados_ibge):
    municipios = []

    for m in dados_ibge:
        cod_ibge = m.get('id')
        nome = m.get('nome', '')

        try:
            if 'microrregiao' in m and m['microrregiao']:
                uf = m['microrregiao']['mesorregiao']['UF']['sigla']
            elif 'regiao-imediata' in m and m['regiao-imediata']:
                uf = m['regiao-imediata']['regiao-intermediaria']['UF']['sigla']
            else:
                uf = 'N/A'
        except (KeyError, TypeError):
            uf = 'N/A'

        regiao = UF_REGIAO.get(uf, 'N/A')

        municipios.append({
            'COD_MUNICIPIO_TOM': cod_ibge,
            'COD_MUNICIPIO_IBGE': cod_ibge,
            'NOME_MUNICIPIO_TOM': nome,
            'NOME_MUNICIPIO_IBGE': nome,
            'UF': uf,
            'REGIAO': regiao,
            'LATITUDE': '',
            'LONGITUDE': '',
            'POPULACAO_ESTIMADA': ''
        })

    return municipios


def salvar_csv(municipios, caminho):
    colunas = [
        'COD_MUNICIPIO_TOM', 'COD_MUNICIPIO_IBGE',
        'NOME_MUNICIPIO_TOM', 'NOME_MUNICIPIO_IBGE',
        'UF', 'REGIAO', 'LATITUDE', 'LONGITUDE', 'POPULACAO_ESTIMADA'
    ]

    with open(caminho, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=colunas)
        writer.writeheader()
        writer.writerows(municipios)

    print(f"Arquivo salvo: {caminho}")


def main():
    caminho_saida = sys.argv[1] if len(sys.argv) > 1 else 'dbt/seeds/dim_municipios.csv'

    try:
        dados = buscar_municipios_ibge()
        print(f"Total de municipios obtidos: {len(dados)}")

        municipios = processar_municipios(dados)
        municipios.sort(key=lambda x: (x['UF'], x['NOME_MUNICIPIO_IBGE']))

        salvar_csv(municipios, caminho_saida)

        print(f"\nResumo por UF:")
        contagem_uf = {}
        for m in municipios:
            uf = m['UF']
            contagem_uf[uf] = contagem_uf.get(uf, 0) + 1

        for uf in sorted(contagem_uf.keys()):
            print(f"  {uf}: {contagem_uf[uf]} municipios")

        print(f"\nTotal: {len(municipios)} municipios")

    except Exception as e:
        print(f"ERRO: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
