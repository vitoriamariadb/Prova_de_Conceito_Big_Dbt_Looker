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
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import seaborn as sns

try:
    from utils.data_loader import BigQueryLoader
    BIGQUERY_DISPONIVEL = True
except ImportError:
    BIGQUERY_DISPONIVEL = False

CORES = {
    'primaria': '#1B4F72',
    'secundaria': '#2874A6',
    'terciaria': '#5DADE2',
    'destaque': '#117A65',
    'alerta': '#B7950B',
    'critico': '#943126',
    'fundo': '#F8F9F9',
    'texto': '#2C3E50',
    'grid': '#D5D8DC',
}

DPI = 150
DIMS = (10.5, 14.9)
RODAPE = 'Fonte: INEP/MEC | Elaboracao: Prova de Conceito BigQuery + dbt'

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
    'Norte': '#117A65',
    'Nordeste': '#943126',
    'Centro-Oeste': '#B7950B',
    'Sudeste': '#1B4F72',
    'Sul': '#2874A6'
}


def cfg():
    plt.rcParams.update({
        'figure.dpi': DPI,
        'figure.facecolor': CORES['fundo'],
        'axes.facecolor': '#FFFFFF',
        'axes.edgecolor': CORES['texto'],
        'axes.linewidth': 0.8,
        'axes.titlesize': 13,
        'axes.titleweight': 'bold',
        'axes.titlecolor': CORES['primaria'],
        'axes.labelsize': 10,
        'axes.labelcolor': CORES['texto'],
        'xtick.labelsize': 8,
        'ytick.labelsize': 8,
        'xtick.color': CORES['texto'],
        'ytick.color': CORES['texto'],
        'grid.color': CORES['grid'],
        'grid.linewidth': 0.5,
        'legend.fontsize': 9,
        'legend.framealpha': 0.9,
        'font.family': 'DejaVu Sans',
        'font.size': 9
    })


def salvar(fig, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.text(0.5, 0.01, RODAPE, ha='center', fontsize=8,
             color=CORES['texto'], style='italic')
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    plt.savefig(path, dpi=DPI, bbox_inches='tight', facecolor=CORES['fundo'])
    plt.close()
    print(f"  [OK] {path}")


def carregar_dados():
    loader = BigQueryLoader()
    df_edu = loader.load_mart_educacao_uf()
    df_clusters = loader.load_mart_clusters()
    df_alocacao = loader.load_mart_alocacao()
    df_cenarios = loader.load_mart_simulacao_cenarios()
    df_correlacoes = loader.load_mart_correlacoes()
    return df_edu, df_clusters, df_alocacao, df_cenarios, df_correlacoes


# =====================================================================
# PAGINA DESCRITIVA
# =====================================================================

def grafico_mapa_matriculas(df):
    cfg()
    try:
        import geopandas as gpd
        brasil = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres') if hasattr(gpd.datasets, 'get_path') else None)
    except Exception:
        brasil = None

    if brasil is not None:
        try:
            url = 'https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson'
            brasil = gpd.read_file(url)
            brasil['UF'] = brasil['sigla']
            df_map = brasil.merge(df[['UF', 'TOTAL_MATRICULAS']], on='UF', how='left')

            fig, ax = plt.subplots(1, 1, figsize=DIMS)
            df_map.plot(column='TOTAL_MATRICULAS', cmap='Blues', linewidth=0.8,
                        ax=ax, edgecolor='white', legend=True,
                        legend_kwds={'label': 'Total de Matriculas', 'shrink': 0.6})

            for idx, row in df_map.iterrows():
                centroid = row.geometry.centroid
                ax.annotate(row['UF'], xy=(centroid.x, centroid.y),
                           ha='center', va='center', fontsize=7, fontweight='bold',
                           color=CORES['texto'])

            ax.set_title('Distribuicao de Matriculas por UF', fontsize=13,
                         color=CORES['primaria'], fontweight='bold', pad=20)
            ax.axis('off')
            salvar(fig, 'docs/images/descritiva_mapa_matriculas.png')
            return True
        except Exception as e:
            print(f"  [FALLBACK MAPA] {e}")

    fig, ax = plt.subplots(figsize=DIMS)
    df['REGIAO'] = df['UF'].map(UF_REGIAO)
    df_sorted = df.sort_values('TOTAL_MATRICULAS', ascending=True)
    cores = [CORES_REGIAO.get(UF_REGIAO.get(uf, ''), CORES['primaria']) for uf in df_sorted['UF']]

    bars = ax.barh(df_sorted['UF'], df_sorted['TOTAL_MATRICULAS'] / 1e6, color=cores,
                   edgecolor='white', linewidth=0.5)
    for bar, val in zip(bars, df_sorted['TOTAL_MATRICULAS'] / 1e6):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
                f'{val:.1f}M', va='center', ha='left', fontsize=7, color=CORES['texto'])

    ax.set_xlabel('Matriculas (milhoes)', fontweight='bold')
    ax.set_title('Distribuicao de Matriculas por UF', fontsize=13,
                 color=CORES['primaria'], fontweight='bold', pad=20)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, axis='x', alpha=0.3, linestyle='--')

    handles = [mpatches.Patch(color=c, label=r) for r, c in CORES_REGIAO.items()]
    ax.legend(handles=handles, loc='lower right', title='Regiao')
    salvar(fig, 'docs/images/descritiva_mapa_matriculas.png')


def grafico_matriculas_regiao(df):
    cfg()
    fig, ax = plt.subplots(figsize=DIMS)

    df['REGIAO'] = df['UF'].map(UF_REGIAO)
    df_reg = df.groupby('REGIAO')['TOTAL_MATRICULAS'].sum().sort_values(ascending=True)
    cores = [CORES_REGIAO[r] for r in df_reg.index]

    bars = ax.barh(df_reg.index, df_reg.values / 1e6, color=cores, edgecolor='white', linewidth=0.5, height=0.6)

    for bar, val in zip(bars, df_reg.values / 1e6):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                f'{val:.1f}M', va='center', ha='left', fontsize=10, fontweight='bold',
                color=CORES['texto'])

    total = df_reg.sum() / 1e6
    for bar, val in zip(bars, df_reg.values / 1e6):
        pct = val / total * 100
        ax.text(bar.get_width() / 2, bar.get_y() + bar.get_height()/2,
                f'{pct:.0f}%', va='center', ha='center', fontsize=9, fontweight='bold',
                color='white')

    ax.set_xlabel('Total de Matriculas (milhoes)', fontweight='bold')
    ax.set_title('Total de Matriculas por Regiao', fontsize=13,
                 color=CORES['primaria'], fontweight='bold', pad=20)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, axis='x', alpha=0.3, linestyle='--')
    salvar(fig, 'docs/images/descritiva_matriculas_regiao.png')


def grafico_infraestrutura(df):
    cfg()
    fig, ax = plt.subplots(figsize=DIMS)

    df_sorted = df.sort_values('PCT_ESCOLAS_INTERNET', ascending=True)
    y = np.arange(len(df_sorted))
    h = 0.35

    bars1 = ax.barh(y + h/2, df_sorted['PCT_ESCOLAS_INTERNET'], h,
                    color=CORES['secundaria'], label='Internet (%)', edgecolor='white')
    bars2 = ax.barh(y - h/2, df_sorted['PCT_ESCOLAS_LABORATORIO'], h,
                    color=CORES['destaque'], label='Laboratorio (%)', edgecolor='white')

    ax.set_yticks(y)
    ax.set_yticklabels(df_sorted['UF'])
    ax.set_xlabel('Percentual de Escolas (%)', fontweight='bold')
    ax.set_title('Infraestrutura Escolar por UF: Internet e Laboratorio', fontsize=13,
                 color=CORES['primaria'], fontweight='bold', pad=20)
    ax.legend(loc='lower right')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, axis='x', alpha=0.3, linestyle='--')
    ax.set_xlim(0, 105)
    salvar(fig, 'docs/images/descritiva_infraestrutura.png')


def grafico_notas_enem(df):
    cfg()
    fig, ax = plt.subplots(figsize=DIMS)

    df_sorted = df.sort_values('NOTA_MEDIA_ENEM', ascending=False)
    media_nacional = df['NOTA_MEDIA_ENEM'].mean()
    cores = [CORES['destaque'] if n >= media_nacional else CORES['critico'] for n in df_sorted['NOTA_MEDIA_ENEM']]

    bars = ax.bar(df_sorted['UF'], df_sorted['NOTA_MEDIA_ENEM'], color=cores,
                  edgecolor='white', linewidth=0.5)
    ax.axhline(y=media_nacional, color=CORES['alerta'], linewidth=2, linestyle='--',
               label=f'Media Nacional: {media_nacional:.0f}')
    ax.axhline(y=550, color=CORES['critico'], linewidth=1.5, linestyle=':',
               label='Meta PNE: 550')

    ax.set_ylabel('Nota Media ENEM', fontweight='bold')
    ax.set_title('Nota Media ENEM por UF', fontsize=13,
                 color=CORES['primaria'], fontweight='bold', pad=20)
    ax.legend(loc='upper right')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, axis='y', alpha=0.3, linestyle='--')
    plt.xticks(rotation=45, ha='right')

    ymin = df_sorted['NOTA_MEDIA_ENEM'].min() - 20
    ax.set_ylim(ymin, df_sorted['NOTA_MEDIA_ENEM'].max() + 15)
    salvar(fig, 'docs/images/descritiva_notas_enem.png')


def grafico_scorecard(df):
    cfg()
    fig, axes = plt.subplots(2, 2, figsize=DIMS)

    metricas = [
        ('Total de Matriculas', f"{df['TOTAL_MATRICULAS'].sum():,.0f}".replace(',', '.'),
         CORES['primaria'], 'Educacao basica 2023'),
        ('Total de Escolas', f"{df['TOTAL_ESCOLAS'].sum():,.0f}".replace(',', '.'),
         CORES['secundaria'], 'Em funcionamento'),
        ('Media Nota ENEM', f"{df['NOTA_MEDIA_ENEM'].mean():.0f} pts",
         CORES['destaque'], 'Media das 27 UFs'),
        ('Escolas com Internet', f"{df['PCT_ESCOLAS_INTERNET'].mean():.1f}%",
         CORES['alerta'] if df['PCT_ESCOLAS_INTERNET'].mean() < 80 else CORES['destaque'],
         'Media nacional'),
    ]

    for ax, (titulo, valor, cor, subtitulo) in zip(axes.flatten(), metricas):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

        rect = FancyBboxPatch((0.05, 0.05), 0.9, 0.9, boxstyle="round,pad=0.05",
                               facecolor='white', edgecolor=cor, linewidth=3)
        ax.add_patch(rect)

        ax.text(0.5, 0.7, titulo, ha='center', va='center', fontsize=11,
                fontweight='bold', color=CORES['texto'], transform=ax.transAxes)
        ax.text(0.5, 0.45, valor, ha='center', va='center', fontsize=24,
                fontweight='bold', color=cor, transform=ax.transAxes)
        ax.text(0.5, 0.22, subtitulo, ha='center', va='center', fontsize=9,
                color=CORES['texto'], style='italic', transform=ax.transAxes)

    fig.suptitle('Indicadores Educacionais - Resumo Executivo', fontsize=15,
                 color=CORES['primaria'], fontweight='bold', y=0.98)
    salvar(fig, 'docs/images/descritiva_scorecard.png')


# =====================================================================
# PAGINA PREDITIVA
# =====================================================================

def grafico_combo_internet_nota(df):
    cfg()
    fig, ax1 = plt.subplots(figsize=DIMS)

    df_sorted = df.sort_values('NOTA_MEDIA_ENEM', ascending=False)

    bars = ax1.bar(df_sorted['UF'], df_sorted['PCT_ESCOLAS_INTERNET'],
                   color=CORES['terciaria'], alpha=0.7, label='% Internet', edgecolor='white')
    ax1.set_ylabel('% Escolas com Internet', color=CORES['secundaria'], fontweight='bold')
    ax1.set_ylim(0, 110)

    ax2 = ax1.twinx()
    ax2.plot(df_sorted['UF'], df_sorted['NOTA_MEDIA_ENEM'], color=CORES['critico'],
             marker='o', linewidth=2.5, markersize=6, label='Nota ENEM', zorder=5)
    ax2.set_ylabel('Nota Media ENEM', color=CORES['critico'], fontweight='bold')

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

    ax1.set_title('Comparativo: Infraestrutura Digital vs Desempenho por UF', fontsize=13,
                  color=CORES['primaria'], fontweight='bold', pad=20)
    ax1.spines['top'].set_visible(False)
    ax1.grid(True, axis='y', alpha=0.3, linestyle='--')
    plt.xticks(rotation=45, ha='right')
    salvar(fig, 'docs/images/preditiva_combo_internet_nota.png')


def grafico_bullet_desempenho(df):
    cfg()
    fig, ax = plt.subplots(figsize=DIMS)

    df_sorted = df.sort_values('NOTA_MEDIA_ENEM', ascending=True)
    META = 550

    y = np.arange(len(df_sorted))
    cores = [CORES['destaque'] if n >= META else CORES['critico'] if n < META - 50
             else CORES['alerta'] for n in df_sorted['NOTA_MEDIA_ENEM']]

    ax.barh(y, [META + 80] * len(y), color='#EAECEE', height=0.6, zorder=1)
    ax.barh(y, [META] * len(y), color='#D5D8DC', height=0.6, zorder=2)
    bars = ax.barh(y, df_sorted['NOTA_MEDIA_ENEM'], color=cores, height=0.35, zorder=3,
                   edgecolor='white', linewidth=0.5)

    ax.axvline(x=META, color=CORES['primaria'], linewidth=2.5, linestyle='-', zorder=4,
               label=f'Meta: {META} pts')

    for i, (nota, uf) in enumerate(zip(df_sorted['NOTA_MEDIA_ENEM'], df_sorted['UF'])):
        gap = nota - META
        sinal = '+' if gap >= 0 else ''
        ax.text(nota + 3, i, f'{nota:.0f} ({sinal}{gap:.0f})', va='center', fontsize=7,
                fontweight='bold', color=CORES['texto'], zorder=5)

    ax.set_yticks(y)
    ax.set_yticklabels(df_sorted['UF'])
    ax.set_xlabel('Nota Media ENEM', fontweight='bold')
    ax.set_title('Desempenho vs Meta PNE (550 pontos) por UF', fontsize=13,
                 color=CORES['primaria'], fontweight='bold', pad=20)
    ax.legend(loc='lower right')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    xmin = df_sorted['NOTA_MEDIA_ENEM'].min() - 30
    ax.set_xlim(xmin, META + 100)
    salvar(fig, 'docs/images/preditiva_bullet_desempenho.png')


def grafico_diagrama_mediacao(df):
    cfg()
    fig, ax = plt.subplots(figsize=(DIMS[0], 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')

    corr_internet_nota = df[['PCT_ESCOLAS_INTERNET', 'NOTA_MEDIA_ENEM']].corr().iloc[0, 1]
    corr_lab_nota = df[['PCT_ESCOLAS_LABORATORIO', 'NOTA_MEDIA_ENEM']].corr().iloc[0, 1]
    corr_internet_lab = df[['PCT_ESCOLAS_INTERNET', 'PCT_ESCOLAS_LABORATORIO']].corr().iloc[0, 1]

    boxes = [
        (1.5, 4.5, 'Infraestrutura\nDigital\n(Internet)', CORES['secundaria']),
        (7, 4.5, 'Desempenho\nEducacional\n(Nota ENEM)', CORES['destaque']),
        (4.25, 1.5, 'Infraestrutura\nFisica\n(Laboratorio)', CORES['alerta']),
    ]

    for x, y, txt, cor in boxes:
        rect = FancyBboxPatch((x - 1.2, y - 0.8), 2.4, 1.6,
                               boxstyle="round,pad=0.15", facecolor='white',
                               edgecolor=cor, linewidth=3)
        ax.add_patch(rect)
        ax.text(x, y, txt, ha='center', va='center', fontsize=11,
                fontweight='bold', color=cor)

    ax.annotate('', xy=(5.8, 4.5), xytext=(2.7, 4.5),
                arrowprops=dict(arrowstyle='->', color=CORES['primaria'], lw=3))
    ax.text(4.25, 4.85, f'r = {corr_internet_nota:.2f}', ha='center', fontsize=11,
            fontweight='bold', color=CORES['primaria'],
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=CORES['primaria']))

    ax.annotate('', xy=(3.05, 2.1), xytext=(2.0, 3.7),
                arrowprops=dict(arrowstyle='->', color=CORES['alerta'], lw=2.5))
    ax.text(1.8, 2.9, f'r = {corr_internet_lab:.2f}', ha='center', fontsize=10,
            fontweight='bold', color=CORES['alerta'],
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=CORES['alerta']))

    ax.annotate('', xy=(6.5, 3.7), xytext=(5.45, 2.1),
                arrowprops=dict(arrowstyle='->', color=CORES['destaque'], lw=2.5))
    ax.text(6.7, 2.9, f'r = {corr_lab_nota:.2f}', ha='center', fontsize=10,
            fontweight='bold', color=CORES['destaque'],
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=CORES['destaque']))

    ax.set_title('Diagrama de Mediacao: Infraestrutura e Desempenho', fontsize=13,
                 color=CORES['primaria'], fontweight='bold', pad=20)

    ax.text(5, 0.3, 'Correlacao NAO implica causalidade. Diagrama ilustrativo.',
            ha='center', fontsize=9, style='italic', color=CORES['texto'])

    salvar(fig, 'docs/images/preditiva_diagrama_mediacao.png')


# =====================================================================
# PAGINA PRESCRITIVA
# =====================================================================

def grafico_mapa_clusters(df_edu, df_clusters):
    cfg()

    try:
        import geopandas as gpd
        url = 'https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson'
        brasil = gpd.read_file(url)
        brasil['UF'] = brasil['sigla']

        df_merged = brasil.merge(df_clusters[['UF', 'CLUSTER_ID', 'DESCRICAO_CLUSTER']],
                                  on='UF', how='left')

        cores_cluster = {1: CORES['destaque'], 2: CORES['secundaria'],
                         3: CORES['alerta'], 4: CORES['critico']}

        fig, ax = plt.subplots(1, 1, figsize=DIMS)

        for cluster_id, grupo in df_merged.groupby('CLUSTER_ID'):
            cor = cores_cluster.get(int(cluster_id), CORES['primaria'])
            grupo.plot(ax=ax, color=cor, edgecolor='white', linewidth=0.8)

        for idx, row in df_merged.iterrows():
            centroid = row.geometry.centroid
            ax.annotate(row['UF'], xy=(centroid.x, centroid.y),
                       ha='center', va='center', fontsize=7, fontweight='bold',
                       color='white',
                       path_effects=[patheffects.withStroke(linewidth=2, foreground=CORES['texto'])])

        handles = []
        for cid in sorted(df_merged['CLUSTER_ID'].dropna().unique()):
            desc = df_merged[df_merged['CLUSTER_ID'] == cid]['DESCRICAO_CLUSTER'].iloc[0]
            handles.append(mpatches.Patch(color=cores_cluster.get(int(cid), CORES['primaria']),
                                          label=f'Cluster {int(cid)}: {desc}'))
        ax.legend(handles=handles, loc='lower left', fontsize=9, title='Clusters')

        ax.set_title('Mapa de Clusters: UFs por Perfil Educacional', fontsize=13,
                     color=CORES['primaria'], fontweight='bold', pad=20)
        ax.axis('off')
        salvar(fig, 'docs/images/prescritiva_mapa_clusters.png')
        return True
    except Exception as e:
        print(f"  [FALLBACK MAPA CLUSTERS] {e}")

    fig, ax = plt.subplots(figsize=DIMS)
    cores_cluster = {1: CORES['destaque'], 2: CORES['secundaria'],
                     3: CORES['alerta'], 4: CORES['critico']}

    df_plot = df_clusters.sort_values('CLUSTER_ID')
    cores = [cores_cluster.get(int(c), CORES['primaria']) for c in df_plot['CLUSTER_ID']]

    ax.barh(df_plot['UF'], df_plot['CLUSTER_ID'], color=cores, edgecolor='white')
    ax.set_xlabel('Cluster ID')
    ax.set_title('Mapa de Clusters: UFs por Perfil Educacional', fontsize=13,
                 color=CORES['primaria'], fontweight='bold', pad=20)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    handles = []
    for cid in sorted(df_plot['CLUSTER_ID'].unique()):
        desc = df_plot[df_plot['CLUSTER_ID'] == cid]['DESCRICAO_CLUSTER'].iloc[0]
        handles.append(mpatches.Patch(color=cores_cluster.get(int(cid), CORES['primaria']),
                                      label=f'Cluster {int(cid)}: {desc}'))
    ax.legend(handles=handles, loc='lower right')
    salvar(fig, 'docs/images/prescritiva_mapa_clusters.png')


def grafico_tabela_priorizacao(df_alocacao, df_clusters):
    cfg()
    fig, ax = plt.subplots(figsize=DIMS)
    ax.axis('off')

    df_merged = df_alocacao.merge(df_clusters[['UF', 'CLUSTER_ID', 'DESCRICAO_CLUSTER']],
                                   on='UF', how='left')
    df_sorted = df_merged.sort_values('ORDEM_PRIORIDADE')

    cols = ['UF', 'STATUS_DESEMPENHO', 'GAP_INTERNET_PCT', 'GAP_LABORATORIO_PCT',
            'INVESTIMENTO_TOTAL_ESTIMADO_BRL', 'DESCRICAO_CLUSTER']
    headers = ['UF', 'Status', 'Gap Internet\n(p.p.)', 'Gap Lab\n(p.p.)',
               'Investimento\n(R$)', 'Cluster']

    n_rows = len(df_sorted)
    n_cols = len(cols)

    cores_status = {
        'CRITICO': '#FADBD8', 'ATENCAO': '#FEF9E7',
        'REGULAR': '#D6EAF8', 'ADEQUADO': '#D5F5E3'
    }

    table = ax.table(
        cellText=[['' for _ in range(n_cols)] for _ in range(n_rows)],
        colLabels=headers,
        loc='center',
        cellLoc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.4)

    for j, h in enumerate(headers):
        cell = table[0, j]
        cell.set_facecolor(CORES['primaria'])
        cell.set_text_props(color='white', fontweight='bold', fontsize=9)

    for i, (_, row) in enumerate(df_sorted.iterrows()):
        bg = cores_status.get(row['STATUS_DESEMPENHO'], 'white')
        for j, col in enumerate(cols):
            cell = table[i + 1, j]
            cell.set_facecolor(bg)
            val = row[col]
            if col == 'INVESTIMENTO_TOTAL_ESTIMADO_BRL':
                txt = f"R$ {val/1e6:.1f}M"
            elif col in ('GAP_INTERNET_PCT', 'GAP_LABORATORIO_PCT'):
                txt = f"{val:.1f}"
            else:
                txt = str(val)
            cell.get_text().set_text(txt)
            cell.get_text().set_fontsize(7)

    ax.set_title('Tabela de Priorizacao de Investimentos por UF', fontsize=13,
                 color=CORES['primaria'], fontweight='bold', pad=20, y=0.98)
    salvar(fig, 'docs/images/prescritiva_tabela_priorizacao.png')


def grafico_bullet_gap(df_alocacao):
    cfg()
    fig, axes = plt.subplots(1, 2, figsize=DIMS)

    df_sorted = df_alocacao.sort_values('GAP_INTERNET_PCT', ascending=True)

    cores_status = {
        'CRITICO': CORES['critico'], 'ATENCAO': CORES['alerta'],
        'REGULAR': CORES['secundaria'], 'ADEQUADO': CORES['destaque']
    }

    ax1 = axes[0]
    cores = [cores_status.get(s, CORES['primaria']) for s in df_sorted['STATUS_DESEMPENHO']]
    ax1.barh(df_sorted['UF'], df_sorted['GAP_INTERNET_PCT'], color=cores,
             edgecolor='white', linewidth=0.5)
    ax1.set_xlabel('Gap Internet (p.p.)', fontweight='bold')
    ax1.set_title('Gap de Internet', fontsize=11, color=CORES['primaria'], fontweight='bold')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.grid(True, axis='x', alpha=0.3, linestyle='--')
    ax1.axvline(x=0, color=CORES['texto'], linewidth=1)

    df_sorted2 = df_alocacao.sort_values('GAP_LABORATORIO_PCT', ascending=True)
    cores2 = [cores_status.get(s, CORES['primaria']) for s in df_sorted2['STATUS_DESEMPENHO']]
    ax2 = axes[1]
    ax2.barh(df_sorted2['UF'], df_sorted2['GAP_LABORATORIO_PCT'], color=cores2,
             edgecolor='white', linewidth=0.5)
    ax2.set_xlabel('Gap Laboratorio (p.p.)', fontweight='bold')
    ax2.set_title('Gap de Laboratorio', fontsize=11, color=CORES['primaria'], fontweight='bold')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.grid(True, axis='x', alpha=0.3, linestyle='--')
    ax2.axvline(x=0, color=CORES['texto'], linewidth=1)

    handles = [mpatches.Patch(color=c, label=s) for s, c in cores_status.items()]
    fig.legend(handles=handles, loc='lower center', ncol=4, fontsize=9, title='Status')

    fig.suptitle('Gap de Infraestrutura por UF', fontsize=13,
                 color=CORES['primaria'], fontweight='bold', y=0.98)
    salvar(fig, 'docs/images/prescritiva_bullet_gap.png')


def grafico_cenarios(df_cenarios):
    cfg()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=DIMS)

    df_sorted = df_cenarios.sort_values('AUMENTO_PERCENTUAL')
    x = df_sorted['AUMENTO_PERCENTUAL']

    cores_tipo = {'Conservador': CORES['destaque'], 'Moderado': CORES['alerta'],
                  'Agressivo': CORES['critico']}
    cores_bar = [cores_tipo.get(t, CORES['primaria']) for t in df_sorted['TIPO_CENARIO']]

    bars1 = ax1.bar(df_sorted['CENARIO_NOME'], df_sorted['IMPACTO_NOTA_ENEM_PONTOS'],
                    color=cores_bar, edgecolor='white', linewidth=0.5)
    for bar, val in zip(bars1, df_sorted['IMPACTO_NOTA_ENEM_PONTOS']):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                 f'+{val:.1f} pts', ha='center', fontsize=9, fontweight='bold',
                 color=CORES['texto'])
    ax1.set_ylabel('Impacto na Nota ENEM (pontos)', fontweight='bold')
    ax1.set_title('Impacto Estimado no ENEM por Cenario de Investimento', fontsize=11,
                  color=CORES['primaria'], fontweight='bold')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.grid(True, axis='y', alpha=0.3, linestyle='--')

    bars2 = ax2.bar(df_sorted['CENARIO_NOME'], df_sorted['REDUCAO_ABANDONO_PCT'],
                    color=cores_bar, edgecolor='white', linewidth=0.5)
    for bar, val in zip(bars2, df_sorted['REDUCAO_ABANDONO_PCT']):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                 f'-{abs(val):.2f}%', ha='center', fontsize=9, fontweight='bold',
                 color=CORES['texto'])
    ax2.set_ylabel('Reducao no Abandono (%)', fontweight='bold')
    ax2.set_title('Reducao Estimada no Abandono por Cenario', fontsize=11,
                  color=CORES['primaria'], fontweight='bold')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.grid(True, axis='y', alpha=0.3, linestyle='--')

    handles = [mpatches.Patch(color=c, label=t) for t, c in cores_tipo.items()]
    fig.legend(handles=handles, loc='lower center', ncol=3, fontsize=9, title='Tipo de Cenario')
    plt.xticks(rotation=30, ha='right')
    salvar(fig, 'docs/images/prescritiva_cenarios.png')


def main():
    print("=" * 70)
    print("GERACAO DE GRAFICOS STORYTELLING - TODAS AS PAGINAS")
    print("=" * 70)
    print()

    os.makedirs('docs/images', exist_ok=True)

    print("Carregando dados do BigQuery...")
    df_edu, df_clusters, df_alocacao, df_cenarios, df_correlacoes = carregar_dados()
    print(f"  Educacao UF: {len(df_edu)} registros")
    print(f"  Clusters: {len(df_clusters)} registros")
    print(f"  Alocacao: {len(df_alocacao)} registros")
    print(f"  Cenarios: {len(df_cenarios)} registros")
    print()

    print("--- PAGINA 1: DESCRITIVA ---")
    grafico_scorecard(df_edu)
    grafico_mapa_matriculas(df_edu)
    grafico_matriculas_regiao(df_edu)
    grafico_infraestrutura(df_edu)
    grafico_notas_enem(df_edu)
    print()

    print("--- PAGINA 2: PREDITIVA ---")
    grafico_combo_internet_nota(df_edu)
    grafico_bullet_desempenho(df_edu)
    grafico_diagrama_mediacao(df_edu)
    print()

    print("--- PAGINA 3: PRESCRITIVA ---")
    grafico_mapa_clusters(df_edu, df_clusters)
    grafico_tabela_priorizacao(df_alocacao, df_clusters)
    grafico_bullet_gap(df_alocacao)
    grafico_cenarios(df_cenarios)
    print()

    print("=" * 70)
    print("Todos os graficos storytelling gerados!")
    print("=" * 70)


if __name__ == "__main__":
    main()
