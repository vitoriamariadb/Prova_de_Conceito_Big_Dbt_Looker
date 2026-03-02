#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import pandas as pd
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Ellipse
    import matplotlib.transforms as transforms
    from sklearn.decomposition import PCA
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LinearRegression
    import seaborn as sns
except ImportError as e:
    print(f"ERRO: Dependencia nao instalada: {e}")
    print("Execute: pip install pandas numpy scikit-learn matplotlib seaborn")
    sys.exit(1)

try:
    from utils.data_loader import BigQueryLoader
    BIGQUERY_DISPONIVEL = True
except ImportError:
    BIGQUERY_DISPONIVEL = False

CORES_CORPORATIVO = {
    'primaria': '#1B4F72',
    'secundaria': '#2874A6',
    'terciaria': '#5DADE2',
    'destaque': '#117A65',
    'alerta': '#B7950B',
    'critico': '#943126',
    'fundo': '#F8F9F9',
    'texto': '#2C3E50',
    'grid': '#D5D8DC',
    'gradiente': ['#1B4F72', '#2874A6', '#3498DB', '#5DADE2', '#85C1E9']
}

DIMENSOES_RETRATO = (10.5, 14.9)
DPI = 150


def configurar_estilo_corporativo():
    plt.rcParams.update({
        'figure.figsize': DIMENSOES_RETRATO,
        'figure.dpi': DPI,
        'figure.facecolor': CORES_CORPORATIVO['fundo'],
        'axes.facecolor': '#FFFFFF',
        'axes.edgecolor': CORES_CORPORATIVO['texto'],
        'axes.linewidth': 0.8,
        'axes.titlesize': 11,
        'axes.titleweight': 'bold',
        'axes.titlecolor': CORES_CORPORATIVO['primaria'],
        'axes.labelsize': 9,
        'axes.labelcolor': CORES_CORPORATIVO['texto'],
        'xtick.labelsize': 8,
        'ytick.labelsize': 8,
        'xtick.color': CORES_CORPORATIVO['texto'],
        'ytick.color': CORES_CORPORATIVO['texto'],
        'grid.color': CORES_CORPORATIVO['grid'],
        'grid.linewidth': 0.5,
        'legend.fontsize': 8,
        'legend.framealpha': 0.9,
        'legend.edgecolor': CORES_CORPORATIVO['grid'],
        'font.family': 'DejaVu Sans',
        'font.size': 9
    })


def carregar_dados():
    if not BIGQUERY_DISPONIVEL:
        print("ERRO: BigQuery nao disponivel. Instale: pip install google-cloud-bigquery")
        sys.exit(1)

    loader = BigQueryLoader()
    df_educacao = loader.load_mart_educacao_uf()
    df_clusters = loader.load_mart_clusters()
    df_alocacao = loader.load_mart_alocacao()
    df_correlacoes = loader.load_mart_correlacoes()
    return df_educacao, df_clusters, df_alocacao, df_correlacoes


def gerar_grafico_regressao(df, output_path='outputs/regressao_corporativo.png'):
    configurar_estilo_corporativo()

    fig, ax = plt.subplots(figsize=DIMENSOES_RETRATO)

    X = df['PCT_ESCOLAS_INTERNET'].values.reshape(-1, 1)
    y = df['NOTA_MEDIA_ENEM'].values

    modelo = LinearRegression()
    modelo.fit(X, y)
    y_pred = modelo.predict(X)
    r2 = modelo.score(X, y)

    ax.scatter(X, y, c=CORES_CORPORATIVO['primaria'], s=120, alpha=0.8,
               edgecolors='white', linewidth=1.5, label='UFs', zorder=5)

    for i, uf in enumerate(df['UF']):
        ax.annotate(uf, (X[i, 0], y[i]), fontsize=7, ha='center', va='bottom',
                   color=CORES_CORPORATIVO['texto'], fontweight='bold')

    X_line = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
    y_line = modelo.predict(X_line)
    ax.plot(X_line, y_line, color=CORES_CORPORATIVO['critico'], linewidth=2.5,
            label='Regressao Linear', zorder=4)

    conf_interval = 1.96 * np.std(y - y_pred)
    ax.fill_between(X_line.flatten(), y_line - conf_interval, y_line + conf_interval,
                   color=CORES_CORPORATIVO['critico'], alpha=0.1, zorder=3)

    texto = f"R² = {r2:.4f}\n"
    texto += f"Coef = {modelo.coef_[0]:.4f}\n"
    texto += f"n = {len(df)}"

    props = dict(boxstyle='round,pad=0.5', facecolor=CORES_CORPORATIVO['fundo'],
                edgecolor=CORES_CORPORATIVO['primaria'], alpha=0.95)
    ax.text(0.05, 0.95, texto, transform=ax.transAxes, fontsize=10,
           verticalalignment='top', bbox=props, fontweight='bold',
           color=CORES_CORPORATIVO['primaria'])

    ax.set_xlabel('Percentual de Escolas com Internet (%)', fontsize=11,
                 color=CORES_CORPORATIVO['texto'], fontweight='bold')
    ax.set_ylabel('Nota Media ENEM (pontos)', fontsize=11,
                 color=CORES_CORPORATIVO['texto'], fontweight='bold')
    ax.set_title('Analise de Regressao: Infraestrutura Digital vs Desempenho Educacional',
                fontsize=13, color=CORES_CORPORATIVO['primaria'], fontweight='bold', pad=20)

    ax.grid(True, alpha=0.3, linestyle='--', color=CORES_CORPORATIVO['grid'])
    ax.legend(loc='lower right', framealpha=0.95)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.text(0.5, 0.02, 'Fonte: INEP/MEC | Elaboracao: Prova de Conceito BigQuery + dbt',
            ha='center', fontsize=8, color=CORES_CORPORATIVO['texto'], style='italic')

    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight', facecolor=CORES_CORPORATIVO['fundo'])
    plt.close()

    return output_path


def desenhar_elipse_confianca(x, y, ax, n_std=2.0, **kwargs):
    if len(x) < 2:
        return

    cov = np.cov(x, y)
    pearson = cov[0, 1] / np.sqrt(cov[0, 0] * cov[1, 1])

    ell_radius_x = np.sqrt(1 + pearson)
    ell_radius_y = np.sqrt(1 - pearson)
    ellipse = Ellipse((0, 0), width=ell_radius_x * 2, height=ell_radius_y * 2, **kwargs)

    scale_x = np.sqrt(cov[0, 0]) * n_std
    scale_y = np.sqrt(cov[1, 1]) * n_std

    transf = transforms.Affine2D() \
        .rotate_deg(45) \
        .scale(scale_x, scale_y) \
        .translate(np.mean(x), np.mean(y))

    ellipse.set_transform(transf + ax.transData)
    ax.add_patch(ellipse)


def gerar_grafico_clusters(df_educacao, df_clusters, output_path='outputs/clusters_corporativo.png'):
    configurar_estilo_corporativo()

    fig, ax = plt.subplots(figsize=DIMENSOES_RETRATO)

    features = ['NOTA_MEDIA_ENEM', 'PCT_ESCOLAS_INTERNET', 'ALUNOS_POR_DOCENTE']
    features_disponiveis = [f for f in features if f in df_educacao.columns]

    X = df_educacao[features_disponiveis].fillna(df_educacao[features_disponiveis].mean())
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    pca = PCA(n_components=2)
    X_2d = pca.fit_transform(X_scaled)

    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    cores_cluster = [CORES_CORPORATIVO['primaria'], CORES_CORPORATIVO['secundaria'],
                    CORES_CORPORATIVO['destaque'], CORES_CORPORATIVO['alerta']]

    descricoes = ['Alto Desempenho', 'Desempenho Medio', 'Em Desenvolvimento', 'Prioritario']

    for cluster in range(4):
        mask = labels == cluster
        x_cluster = X_2d[mask, 0]
        y_cluster = X_2d[mask, 1]

        ax.scatter(x_cluster, y_cluster,
                  c=cores_cluster[cluster], s=150, alpha=0.8,
                  edgecolors='white', linewidth=2,
                  label=f'Cluster {cluster+1}: {descricoes[cluster]}', zorder=5)

        if len(x_cluster) > 2:
            desenhar_elipse_confianca(x_cluster, y_cluster, ax, n_std=1.5,
                                     facecolor=cores_cluster[cluster], alpha=0.15,
                                     edgecolor=cores_cluster[cluster], linewidth=1.5,
                                     linestyle='--', zorder=3)

        for i, (xi, yi) in enumerate(zip(x_cluster, y_cluster)):
            uf = df_educacao.iloc[np.where(mask)[0][i]]['UF']
            ax.annotate(uf, (xi, yi), fontsize=7, ha='center', va='bottom',
                       color=CORES_CORPORATIVO['texto'], fontweight='bold')

    ax.set_xlabel(f'Componente Principal 1 ({pca.explained_variance_ratio_[0]*100:.1f}% variancia)',
                 fontsize=11, color=CORES_CORPORATIVO['texto'], fontweight='bold')
    ax.set_ylabel(f'Componente Principal 2 ({pca.explained_variance_ratio_[1]*100:.1f}% variancia)',
                 fontsize=11, color=CORES_CORPORATIVO['texto'], fontweight='bold')
    ax.set_title('Clusterizacao de UFs por Indicadores Educacionais (PCA 2D)',
                fontsize=13, color=CORES_CORPORATIVO['primaria'], fontweight='bold', pad=20)

    ax.axhline(y=0, color=CORES_CORPORATIVO['grid'], linestyle='-', linewidth=0.5, alpha=0.5)
    ax.axvline(x=0, color=CORES_CORPORATIVO['grid'], linestyle='-', linewidth=0.5, alpha=0.5)

    ax.grid(True, alpha=0.3, linestyle='--', color=CORES_CORPORATIVO['grid'])
    ax.legend(loc='upper right', framealpha=0.95, fontsize=9)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.text(0.5, 0.02, 'Fonte: INEP/MEC | Elaboracao: Prova de Conceito BigQuery + dbt',
            ha='center', fontsize=8, color=CORES_CORPORATIVO['texto'], style='italic')

    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight', facecolor=CORES_CORPORATIVO['fundo'])
    plt.close()

    return output_path


def gerar_heatmap_correlacao(df_educacao, output_path='outputs/correlacao_corporativo.png'):
    configurar_estilo_corporativo()

    fig, ax = plt.subplots(figsize=DIMENSOES_RETRATO)

    variaveis = ['NOTA_MEDIA_ENEM', 'PCT_ESCOLAS_INTERNET', 'PCT_ESCOLAS_LABORATORIO',
                'ALUNOS_POR_DOCENTE', 'RENDA_MEDIA_FAMILIAR']
    variaveis_disponiveis = [v for v in variaveis if v in df_educacao.columns]

    df_num = df_educacao[variaveis_disponiveis].dropna()
    matriz_corr = df_num.corr()

    labels_curtos = {
        'NOTA_MEDIA_ENEM': 'Nota ENEM',
        'PCT_ESCOLAS_INTERNET': 'Internet (%)',
        'PCT_ESCOLAS_LABORATORIO': 'Laboratorio (%)',
        'ALUNOS_POR_DOCENTE': 'Alunos/Docente',
        'RENDA_MEDIA_FAMILIAR': 'Renda Media'
    }

    matriz_corr.index = [labels_curtos.get(v, v) for v in matriz_corr.index]
    matriz_corr.columns = [labels_curtos.get(v, v) for v in matriz_corr.columns]

    mask = np.triu(np.ones_like(matriz_corr, dtype=bool))

    cmap = sns.diverging_palette(220, 20, as_cmap=True)

    sns.heatmap(matriz_corr, mask=mask, annot=True, fmt='.2f', cmap=cmap,
               vmin=-1, vmax=1, center=0, square=True, linewidths=0.8,
               linecolor='white', cbar_kws={'shrink': 0.8, 'label': 'Correlacao'},
               annot_kws={'size': 10, 'weight': 'bold'}, ax=ax)

    ax.set_title('Matriz de Correlacao - Indicadores Educacionais',
                fontsize=13, color=CORES_CORPORATIVO['primaria'], fontweight='bold', pad=20)

    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
    plt.setp(ax.get_yticklabels(), rotation=0)

    interpretacao = """
Interpretacao das Correlacoes:
• Forte positiva (> 0.7): Variaveis crescem juntas
• Moderada (0.4 a 0.7): Relacao perceptivel
• Fraca (< 0.4): Relacao pouco significativa
• Negativa: Relacao inversa
    """

    props = dict(boxstyle='round,pad=0.5', facecolor=CORES_CORPORATIVO['fundo'],
                edgecolor=CORES_CORPORATIVO['primaria'], alpha=0.95)
    fig.text(0.5, 0.12, interpretacao, ha='center', fontsize=9,
            color=CORES_CORPORATIVO['texto'], bbox=props, family='monospace')

    fig.text(0.5, 0.02, 'Fonte: INEP/MEC | Elaboracao: Prova de Conceito BigQuery + dbt',
            ha='center', fontsize=8, color=CORES_CORPORATIVO['texto'], style='italic')

    plt.tight_layout(rect=[0, 0.18, 1, 0.97])
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight', facecolor=CORES_CORPORATIVO['fundo'])
    plt.close()

    return output_path


def gerar_grafico_investimentos(df_alocacao, output_path='outputs/investimentos_corporativo.png'):
    configurar_estilo_corporativo()

    fig, ax = plt.subplots(figsize=DIMENSOES_RETRATO)

    df_sorted = df_alocacao.sort_values('INVESTIMENTO_TOTAL_ESTIMADO_BRL', ascending=True)

    cores_status = {
        'CRITICO': CORES_CORPORATIVO['critico'],
        'ATENCAO': CORES_CORPORATIVO['alerta'],
        'REGULAR': CORES_CORPORATIVO['secundaria'],
        'ADEQUADO': CORES_CORPORATIVO['destaque']
    }

    cores = [cores_status.get(s, CORES_CORPORATIVO['primaria'])
             for s in df_sorted['STATUS_DESEMPENHO']]

    valores = df_sorted['INVESTIMENTO_TOTAL_ESTIMADO_BRL'] / 1e9

    bars = ax.barh(df_sorted['UF'], valores, color=cores, edgecolor='white', linewidth=0.5)

    for bar, valor in zip(bars, valores):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
               f'R$ {valor:.2f} bi', va='center', ha='left', fontsize=8,
               color=CORES_CORPORATIVO['texto'])

    ax.set_xlabel('Investimento Estimado (R$ bilhoes)', fontsize=11,
                 color=CORES_CORPORATIVO['texto'], fontweight='bold')
    ax.set_ylabel('Unidade Federativa', fontsize=11,
                 color=CORES_CORPORATIVO['texto'], fontweight='bold')
    ax.set_title('Priorizacao de Investimentos por UF',
                fontsize=13, color=CORES_CORPORATIVO['primaria'], fontweight='bold', pad=20)

    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=CORES_CORPORATIVO['critico'], label='Critico'),
        Patch(facecolor=CORES_CORPORATIVO['alerta'], label='Atencao'),
        Patch(facecolor=CORES_CORPORATIVO['secundaria'], label='Regular'),
        Patch(facecolor=CORES_CORPORATIVO['destaque'], label='Adequado')
    ]
    ax.legend(handles=legend_elements, loc='lower right', title='Status', framealpha=0.95)

    ax.grid(True, axis='x', alpha=0.3, linestyle='--', color=CORES_CORPORATIVO['grid'])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    total = df_sorted['INVESTIMENTO_TOTAL_ESTIMADO_BRL'].sum() / 1e9
    fig.text(0.95, 0.95, f'Total: R$ {total:.1f} bilhoes', ha='right',
            fontsize=11, color=CORES_CORPORATIVO['primaria'], fontweight='bold')

    fig.text(0.5, 0.02, 'Fonte: INEP/MEC | Elaboracao: Prova de Conceito BigQuery + dbt',
            ha='center', fontsize=8, color=CORES_CORPORATIVO['texto'], style='italic')

    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight', facecolor=CORES_CORPORATIVO['fundo'])
    plt.close()

    return output_path


def main():
    print("=" * 70)
    print("GERACAO DE GRAFICOS CORPORATIVOS - MEC/INEP")
    print("=" * 70)
    print()
    print(f"Formato: {DIMENSOES_RETRATO[0] * DPI:.0f} x {DIMENSOES_RETRATO[1] * DPI:.0f} px")
    print(f"DPI: {DPI}")
    print()

    df_educacao, df_clusters, df_alocacao, df_correlacoes = carregar_dados()

    print("Gerando graficos...")
    print()

    output1 = gerar_grafico_regressao(df_educacao)
    print(f"  [OK] {output1}")

    output2 = gerar_grafico_clusters(df_educacao, df_clusters)
    print(f"  [OK] {output2}")

    output3 = gerar_heatmap_correlacao(df_educacao)
    print(f"  [OK] {output3}")

    output4 = gerar_grafico_investimentos(df_alocacao)
    print(f"  [OK] {output4}")

    print()
    print("=" * 70)
    print("Graficos corporativos gerados com sucesso!")
    print("=" * 70)


if __name__ == "__main__":
    main()
