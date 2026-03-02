#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as patheffects
from matplotlib.patches import FancyBboxPatch

from utils.data_loader import BigQueryLoader

CORES = {
    'primaria': '#1B4F72', 'secundaria': '#2874A6', 'terciaria': '#5DADE2',
    'destaque': '#117A65', 'alerta': '#B7950B', 'critico': '#943126',
    'fundo': '#F8F9F9', 'texto': '#2C3E50', 'grid': '#D5D8DC',
}
DPI = 150
DIMS = (10.5, 14.9)
RODAPE = 'Fonte: INEP/MEC | Elaboracao: Prova de Conceito BigQuery + dbt'


def salvar(fig, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.text(0.5, 0.01, RODAPE, ha='center', fontsize=8, color=CORES['texto'], style='italic')
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    plt.savefig(path, dpi=DPI, bbox_inches='tight', facecolor=CORES['fundo'])
    plt.close()
    print(f"  [OK] {path}")


def grafico_docentes_mapa(df):
    fig, ax = plt.subplots(figsize=DIMS)
    df_sorted = df.sort_values('TOTAL_DOCENTES', ascending=True)

    UF_REGIAO = {
        'AC': 'Norte', 'AP': 'Norte', 'AM': 'Norte', 'PA': 'Norte',
        'RO': 'Norte', 'RR': 'Norte', 'TO': 'Norte',
        'AL': 'Nordeste', 'BA': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Nordeste',
        'PB': 'Nordeste', 'PE': 'Nordeste', 'PI': 'Nordeste', 'RN': 'Nordeste', 'SE': 'Nordeste',
        'DF': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste',
        'ES': 'Sudeste', 'MG': 'Sudeste', 'RJ': 'Sudeste', 'SP': 'Sudeste',
        'PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul'
    }
    CORES_REGIAO = {
        'Norte': '#117A65', 'Nordeste': '#943126', 'Centro-Oeste': '#B7950B',
        'Sudeste': '#1B4F72', 'Sul': '#2874A6'
    }

    cores = [CORES_REGIAO.get(UF_REGIAO.get(uf, ''), CORES['primaria']) for uf in df_sorted['UF']]
    bars = ax.barh(df_sorted['UF'], df_sorted['TOTAL_DOCENTES'] / 1e3, color=cores,
                   edgecolor='white', linewidth=0.5)
    for bar, val in zip(bars, df_sorted['TOTAL_DOCENTES'] / 1e3):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                f'{val:.0f}k', va='center', ha='left', fontsize=7, color=CORES['texto'])

    ax.set_xlabel('Total de Docentes (milhares)', fontweight='bold')
    ax.set_title('Distribuicao de Docentes por UF', fontsize=13,
                 color=CORES['primaria'], fontweight='bold', pad=20)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, axis='x', alpha=0.3, linestyle='--')

    handles = [mpatches.Patch(color=c, label=r) for r, c in CORES_REGIAO.items()]
    ax.legend(handles=handles, loc='lower right', title='Regiao')
    salvar(fig, 'docs/images/descritiva_docentes.png')


def grafico_tabela_clusters(df_edu, df_clusters):
    fig, ax = plt.subplots(figsize=DIMS)
    ax.axis('off')

    df_merged = df_edu[['UF', 'NOTA_MEDIA_ENEM', 'PCT_ESCOLAS_INTERNET']].merge(
        df_clusters[['UF', 'CLUSTER_ID', 'DESCRICAO_CLUSTER', 'PRIORIDADE_INVESTIMENTO']], on='UF')

    resumo = df_merged.groupby(['CLUSTER_ID', 'DESCRICAO_CLUSTER', 'PRIORIDADE_INVESTIMENTO']).agg(
        QTD_UFS=('UF', 'count'),
        UFS=('UF', lambda x: ', '.join(sorted(x))),
        MEDIA_ENEM=('NOTA_MEDIA_ENEM', 'mean'),
        MEDIA_INTERNET=('PCT_ESCOLAS_INTERNET', 'mean')
    ).reset_index().sort_values('CLUSTER_ID')

    headers = ['Cluster', 'Descricao', 'UFs', 'Qtd', 'Media\nENEM', '% Internet', 'Prioridade']
    n_rows = len(resumo)

    table = ax.table(
        cellText=[['' for _ in range(len(headers))] for _ in range(n_rows)],
        colLabels=headers, loc='center', cellLoc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 2.0)

    cores_cluster = {1: '#D5F5E3', 2: '#D6EAF8', 3: '#FEF9E7', 4: '#FADBD8'}

    for j in range(len(headers)):
        cell = table[0, j]
        cell.set_facecolor(CORES['primaria'])
        cell.set_text_props(color='white', fontweight='bold', fontsize=9)

    for i, (_, row) in enumerate(resumo.iterrows()):
        bg = cores_cluster.get(int(row['CLUSTER_ID']), 'white')
        vals = [
            str(int(row['CLUSTER_ID'])),
            str(row['DESCRICAO_CLUSTER']),
            str(row['UFS']),
            str(int(row['QTD_UFS'])),
            f"{row['MEDIA_ENEM']:.0f}",
            f"{row['MEDIA_INTERNET']:.1f}%",
            str(row['PRIORIDADE_INVESTIMENTO'])
        ]
        for j, val in enumerate(vals):
            cell = table[i + 1, j]
            cell.set_facecolor(bg)
            cell.get_text().set_text(val)
            cell.get_text().set_fontsize(7 if j == 2 else 8)

    ax.set_title('Descricao dos Clusters Educacionais', fontsize=13,
                 color=CORES['primaria'], fontweight='bold', pad=20, y=0.98)
    salvar(fig, 'docs/images/preditiva_tabela_clusters.png')


def grafico_heatmap_correlacao(df_edu):
    import seaborn as sns
    fig, ax = plt.subplots(figsize=DIMS)

    variaveis = ['NOTA_MEDIA_ENEM', 'PCT_ESCOLAS_INTERNET', 'PCT_ESCOLAS_LABORATORIO',
                 'ALUNOS_POR_DOCENTE', 'TOTAL_MATRICULAS']
    variaveis_disponiveis = [v for v in variaveis if v in df_edu.columns]
    df_num = df_edu[variaveis_disponiveis].dropna()
    matriz = df_num.corr()

    labels = {
        'NOTA_MEDIA_ENEM': 'Nota ENEM', 'PCT_ESCOLAS_INTERNET': 'Internet (%)',
        'PCT_ESCOLAS_LABORATORIO': 'Lab (%)', 'ALUNOS_POR_DOCENTE': 'Alunos/Docente',
        'TOTAL_MATRICULAS': 'Matriculas'
    }
    matriz.index = [labels.get(v, v) for v in matriz.index]
    matriz.columns = [labels.get(v, v) for v in matriz.columns]

    mask = np.triu(np.ones_like(matriz, dtype=bool))
    cmap = sns.diverging_palette(220, 20, as_cmap=True)
    sns.heatmap(matriz, mask=mask, annot=True, fmt='.2f', cmap=cmap,
                vmin=-1, vmax=1, center=0, square=True, linewidths=0.8,
                linecolor='white', cbar_kws={'shrink': 0.6}, annot_kws={'size': 11, 'weight': 'bold'}, ax=ax)

    ax.set_title('Matriz de Correlacao - Indicadores Educacionais', fontsize=13,
                 color=CORES['primaria'], fontweight='bold', pad=20)
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    salvar(fig, 'docs/images/preditiva_heatmap_correlacao.png')


def grafico_mapa_investimento(df_alocacao):
    try:
        import geopandas as gpd
        url = 'https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson'
        brasil = gpd.read_file(url)
        brasil['UF'] = brasil['sigla']
        df_map = brasil.merge(df_alocacao[['UF', 'INVESTIMENTO_TOTAL_ESTIMADO_BRL', 'STATUS_DESEMPENHO']],
                               on='UF', how='left')

        fig, ax = plt.subplots(1, 1, figsize=DIMS)
        df_map.plot(column='INVESTIMENTO_TOTAL_ESTIMADO_BRL', cmap='OrRd', linewidth=0.8,
                    ax=ax, edgecolor='white', legend=True,
                    legend_kwds={'label': 'Investimento Estimado (R$)', 'shrink': 0.6})

        for idx, row in df_map.iterrows():
            centroid = row.geometry.centroid
            val = row['INVESTIMENTO_TOTAL_ESTIMADO_BRL']
            label = f"{row['UF']}\n{val/1e6:.1f}M" if pd.notna(val) else row['UF']
            ax.annotate(label, xy=(centroid.x, centroid.y), ha='center', va='center',
                       fontsize=6, fontweight='bold', color=CORES['texto'],
                       path_effects=[patheffects.withStroke(linewidth=2, foreground='white')])

        ax.set_title('Mapa de Investimento Necessario por UF', fontsize=13,
                     color=CORES['primaria'], fontweight='bold', pad=20)
        ax.axis('off')
        salvar(fig, 'docs/images/prescritiva_mapa_investimento.png')
        return
    except Exception as e:
        print(f"  [FALLBACK] {e}")

    fig, ax = plt.subplots(figsize=DIMS)
    cores_status = {
        'CRITICO': CORES['critico'], 'ATENCAO': CORES['alerta'],
        'REGULAR': CORES['secundaria'], 'ADEQUADO': CORES['destaque']
    }
    df_sorted = df_alocacao.sort_values('INVESTIMENTO_TOTAL_ESTIMADO_BRL', ascending=True)
    cores = [cores_status.get(s, CORES['primaria']) for s in df_sorted['STATUS_DESEMPENHO']]
    ax.barh(df_sorted['UF'], df_sorted['INVESTIMENTO_TOTAL_ESTIMADO_BRL'] / 1e6,
            color=cores, edgecolor='white')
    ax.set_xlabel('Investimento (R$ milhoes)', fontweight='bold')
    ax.set_title('Mapa de Investimento Necessario por UF', fontsize=13,
                 color=CORES['primaria'], fontweight='bold', pad=20)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, axis='x', alpha=0.3, linestyle='--')
    handles = [mpatches.Patch(color=c, label=s) for s, c in cores_status.items()]
    ax.legend(handles=handles, loc='lower right', title='Status')
    salvar(fig, 'docs/images/prescritiva_mapa_investimento.png')


def main():
    print("Gerando graficos faltantes...")
    loader = BigQueryLoader()
    df_edu = loader.load_mart_educacao_uf()
    df_clusters = loader.load_mart_clusters()
    df_alocacao = loader.load_mart_alocacao()

    grafico_docentes_mapa(df_edu)
    grafico_tabela_clusters(df_edu, df_clusters)
    grafico_heatmap_correlacao(df_edu)
    grafico_mapa_investimento(df_alocacao)

    print("Concluido!")


if __name__ == "__main__":
    main()
