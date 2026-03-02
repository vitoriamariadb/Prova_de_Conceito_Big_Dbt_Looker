#!/usr/bin/env python3

import sys
import os
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import pandas as pd
    import numpy as np
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import silhouette_score
    from sklearn.decomposition import PCA
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Ellipse
    import matplotlib.transforms as transforms
except ImportError as e:
    print(f"ERRO: Dependencia nao instalada: {e}")
    print("Execute: pip install pandas numpy scikit-learn matplotlib")
    sys.exit(1)

try:
    from utils.data_loader import BigQueryLoader
    BIGQUERY_DISPONIVEL = True
except ImportError:
    BIGQUERY_DISPONIVEL = False

try:
    from utils.estilo_corporativo import (
        CORES_CORPORATIVO, CORES_CLUSTER, DIMENSOES_PAISAGEM, DPI,
        configurar_estilo, adicionar_rodape, estilizar_eixos
    )
except ImportError:
    CORES_CORPORATIVO = {
        'primaria': '#1B4F72', 'secundaria': '#2874A6', 'destaque': '#117A65',
        'alerta': '#B7950B', 'terciaria': '#5DADE2',
        'fundo': '#F8F9F9', 'texto': '#2C3E50', 'grid': '#D5D8DC'
    }
    CORES_CLUSTER = ['#1B4F72', '#2874A6', '#117A65', '#B7950B', '#5DADE2']
    DIMENSOES_PAISAGEM = (14.9, 10.5)
    DPI = 150
    def configurar_estilo(): pass
    def adicionar_rodape(fig, texto=''): pass
    def estilizar_eixos(ax, **kwargs): pass


def carregar_dados_bigquery():
    loader = BigQueryLoader()
    df = loader.load_mart_educacao_uf()
    return df


def carregar_dados(caminho_csv=None):
    if caminho_csv:
        try:
            df = pd.read_csv(caminho_csv)
            print(f"Dados carregados: {caminho_csv}")
            return df
        except FileNotFoundError:
            print("Arquivo nao encontrado.")

    if BIGQUERY_DISPONIVEL:
        try:
            print("Carregando dados do BigQuery...")
            df = carregar_dados_bigquery()
            print(f"Dados carregados: {len(df)} UFs")
            return df
        except Exception as e:
            print(f"Erro ao carregar BigQuery: {e}")

    print("ERRO: Nenhuma fonte de dados disponivel")
    sys.exit(1)


def preparar_features(df, colunas_features):
    X = df[colunas_features].copy()
    X = X.fillna(X.mean())

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled, scaler


def encontrar_k_otimo(X, k_range=range(2, 8)):
    scores = []

    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)
        score = silhouette_score(X, labels)
        scores.append((k, score))
        print(f"  k={k}: Silhouette Score = {score:.4f}")

    k_otimo = max(scores, key=lambda x: x[1])[0]
    return k_otimo, scores


def executar_clustering(X, n_clusters):
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X)
    return kmeans, labels


def analisar_clusters(df, labels, colunas_features):
    df_resultado = df.copy()
    df_resultado['CLUSTER'] = labels
    analise = df_resultado.groupby('CLUSTER')[colunas_features].agg(['mean', 'std'])
    return df_resultado, analise


def desenhar_elipse(x, y, ax, n_std=1.5, **kwargs):
    if len(x) < 3:
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


def plotar_clusters(X, labels, ufs, output_path='outputs/clusters_ufs.png'):
    configurar_estilo()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    pca = PCA(n_components=2)
    X_2d = pca.fit_transform(X)

    fig, ax = plt.subplots(figsize=DIMENSOES_PAISAGEM)

    descricoes = ['Alto Desempenho', 'Desempenho Medio', 'Em Desenvolvimento',
                 'Prioritario', 'Especial']

    for cluster in np.unique(labels):
        mask = labels == cluster
        x_cluster = X_2d[mask, 0]
        y_cluster = X_2d[mask, 1]

        ax.scatter(x_cluster, y_cluster,
                  c=CORES_CLUSTER[cluster % len(CORES_CLUSTER)],
                  label=f'Cluster {cluster}: {descricoes[cluster % len(descricoes)]}',
                  s=150, alpha=0.8, edgecolors='white', linewidth=2, zorder=5)

        if len(x_cluster) > 2:
            desenhar_elipse(x_cluster, y_cluster, ax,
                          facecolor=CORES_CLUSTER[cluster % len(CORES_CLUSTER)],
                          alpha=0.15, edgecolor=CORES_CLUSTER[cluster % len(CORES_CLUSTER)],
                          linewidth=1.5, linestyle='--', zorder=3)

        for i, uf in enumerate(np.array(ufs)[mask]):
            ax.annotate(uf, (x_cluster[i], y_cluster[i]),
                       fontsize=8, ha='center', va='bottom',
                       color=CORES_CORPORATIVO['texto'], fontweight='bold')

    ax.set_xlabel(f'Componente Principal 1 ({pca.explained_variance_ratio_[0]*100:.1f}%)',
                 fontsize=11, color=CORES_CORPORATIVO['texto'], fontweight='bold')
    ax.set_ylabel(f'Componente Principal 2 ({pca.explained_variance_ratio_[1]*100:.1f}%)',
                 fontsize=11, color=CORES_CORPORATIVO['texto'], fontweight='bold')
    ax.set_title('Clusterizacao de UFs por Indicadores Educacionais',
                fontsize=13, color=CORES_CORPORATIVO['primaria'], fontweight='bold', pad=20)

    ax.axhline(y=0, color=CORES_CORPORATIVO['grid'], linestyle='-', linewidth=0.5, alpha=0.5)
    ax.axvline(x=0, color=CORES_CORPORATIVO['grid'], linestyle='-', linewidth=0.5, alpha=0.5)

    ax.legend(loc='upper right', framealpha=0.95)
    estilizar_eixos(ax)
    adicionar_rodape(fig)

    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight', facecolor=CORES_CORPORATIVO['fundo'])
    plt.close()

    return output_path


def main():
    print("=" * 70)
    print("ANALISE DE CLUSTERIZACAO: UFs por Indicadores Educacionais")
    print("=" * 70)
    print()

    csv_path = sys.argv[1] if len(sys.argv) > 1 else None

    df = carregar_dados(csv_path)

    colunas_features = ['NOTA_MEDIA_ENEM', 'PCT_ESCOLAS_INTERNET',
                       'PCT_ESCOLAS_LABORATORIO', 'ALUNOS_POR_DOCENTE']

    colunas_disponiveis = [c for c in colunas_features if c in df.columns]

    print(f"\nFeatures utilizadas: {colunas_disponiveis}")
    print(f"Total de UFs: {len(df)}")

    X_scaled, scaler = preparar_features(df, colunas_disponiveis)

    print("\nBuscando numero otimo de clusters...")
    k_otimo, scores = encontrar_k_otimo(X_scaled)
    print(f"\nNumero otimo de clusters: {k_otimo}")

    kmeans, labels = executar_clustering(X_scaled, k_otimo)

    df_resultado, analise = analisar_clusters(df, labels, colunas_disponiveis)

    print("\n" + "=" * 70)
    print("RESULTADOS DA CLUSTERIZACAO")
    print("=" * 70)

    for cluster in range(k_otimo):
        ufs_cluster = df_resultado[df_resultado['CLUSTER'] == cluster]['UF'].tolist()
        print(f"\nCluster {cluster}: {', '.join(ufs_cluster)}")
        print(f"  Quantidade: {len(ufs_cluster)} UFs")

        for col in colunas_disponiveis:
            media = df_resultado[df_resultado['CLUSTER'] == cluster][col].mean()
            print(f"  {col}: {media:.2f}")

    output_file = plotar_clusters(X_scaled, labels, df['UF'].tolist())
    print(f"\nGrafico salvo: {output_file}")

    df_resultado.to_csv('outputs/resultado_clusters.csv', index=False)
    print("Resultados salvos: outputs/resultado_clusters.csv")

    print("\n" + "=" * 70)
    print("Analise de clusterizacao concluida!")
    print("=" * 70)


if __name__ == "__main__":
    main()
