#!/usr/bin/env python3

import sys
import os
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import pandas as pd
    import numpy as np
    from scipy import stats
    from sklearn.linear_model import LinearRegression
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import seaborn as sns
except ImportError as e:
    print(f"ERRO: Dependencia nao instalada: {e}")
    print("Execute: pip install pandas numpy scipy scikit-learn matplotlib seaborn")
    sys.exit(1)

try:
    from utils.data_loader import BigQueryLoader
    BIGQUERY_DISPONIVEL = True
except ImportError:
    BIGQUERY_DISPONIVEL = False

try:
    from utils.estilo_corporativo import (
        CORES_CORPORATIVO, DIMENSOES_PAISAGEM, DPI,
        configurar_estilo, adicionar_rodape, estilizar_eixos
    )
except ImportError:
    CORES_CORPORATIVO = {
        'primaria': '#1B4F72', 'fundo': '#F8F9F9', 'texto': '#2C3E50', 'grid': '#D5D8DC'
    }
    DIMENSOES_PAISAGEM = (14.9, 10.5)
    DPI = 150
    def configurar_estilo(): pass
    def adicionar_rodape(fig, texto=''): pass
    def estilizar_eixos(ax, **kwargs): pass


def carregar_dados_bigquery():
    loader = BigQueryLoader()
    df_educacao = loader.load_mart_educacao_uf()
    df_correlacoes = loader.load_mart_correlacoes()
    return df_educacao, df_correlacoes


def carregar_dados(caminho_csv=None):
    if caminho_csv:
        try:
            df = pd.read_csv(caminho_csv)
            print(f"Dados carregados: {caminho_csv}")
            return df, None
        except FileNotFoundError:
            print("Arquivo nao encontrado.")

    if BIGQUERY_DISPONIVEL:
        try:
            print("Carregando dados do BigQuery...")
            df_educacao, df_correlacoes = carregar_dados_bigquery()
            print(f"Educacao UF: {len(df_educacao)} registros")
            print(f"Correlacoes: {len(df_correlacoes)} pares")
            return df_educacao, df_correlacoes
        except Exception as e:
            print(f"Erro ao carregar BigQuery: {e}")

    print("ERRO: Nenhuma fonte de dados disponivel")
    sys.exit(1)


def calcular_matriz_correlacao(df, colunas):
    df_num = df[colunas].dropna()
    matriz_corr = df_num.corr()

    p_values = pd.DataFrame(np.zeros((len(colunas), len(colunas))),
                           index=colunas, columns=colunas)

    for i, col1 in enumerate(colunas):
        for j, col2 in enumerate(colunas):
            if i != j:
                _, p = stats.pearsonr(df_num[col1], df_num[col2])
                p_values.loc[col1, col2] = p

    return matriz_corr, p_values


def plotar_matriz_correlacao(matriz_corr, output_path='outputs/matriz_correlacao.png'):
    configurar_estilo()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=DIMENSOES_PAISAGEM)

    labels_curtos = {
        'NOTA_MEDIA_ENEM': 'Nota ENEM',
        'PCT_ESCOLAS_INTERNET': 'Internet (%)',
        'PCT_ESCOLAS_LABORATORIO': 'Laboratorio (%)',
        'ALUNOS_POR_DOCENTE': 'Alunos/Docente',
        'TOTAL_MATRICULAS': 'Matriculas',
        'RENDA_MEDIA_FAMILIAR': 'Renda Media'
    }

    matriz_display = matriz_corr.copy()
    matriz_display.index = [labels_curtos.get(v, v) for v in matriz_display.index]
    matriz_display.columns = [labels_curtos.get(v, v) for v in matriz_display.columns]

    mask = np.triu(np.ones_like(matriz_display, dtype=bool))

    cmap = sns.diverging_palette(220, 20, as_cmap=True)

    sns.heatmap(matriz_display, mask=mask, annot=True, fmt='.2f', cmap=cmap,
               vmin=-1, vmax=1, center=0, square=True, linewidths=0.8,
               linecolor='white', cbar_kws={'shrink': 0.8, 'label': 'Correlacao'},
               annot_kws={'size': 10, 'weight': 'bold'}, ax=ax)

    ax.set_title('Matriz de Correlacao - Indicadores Educacionais',
                fontsize=13, color=CORES_CORPORATIVO['primaria'], fontweight='bold', pad=20)

    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
    plt.setp(ax.get_yticklabels(), rotation=0)

    interpretacao = """
Interpretacao:
• Forte positiva (> 0.7): Variaveis crescem juntas
• Moderada (0.4 a 0.7): Relacao perceptivel
• Fraca (< 0.4): Relacao pouco significativa
    """

    props = dict(boxstyle='round,pad=0.5', facecolor=CORES_CORPORATIVO['fundo'],
                edgecolor=CORES_CORPORATIVO['primaria'], alpha=0.95)
    fig.text(0.5, 0.08, interpretacao, ha='center', fontsize=9,
            color=CORES_CORPORATIVO['texto'], bbox=props, family='monospace')

    adicionar_rodape(fig)

    plt.tight_layout(rect=[0, 0.15, 1, 0.97])
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight', facecolor=CORES_CORPORATIVO['fundo'])
    plt.close()

    return output_path


def exibir_correlacoes_bigquery(df_correlacoes):
    print("\n" + "=" * 70)
    print("CORRELACOES DO BIGQUERY")
    print("=" * 70)

    for _, row in df_correlacoes.iterrows():
        par = row.get('PAR_VARIAVEIS', 'N/A')
        corr = row.get('CORRELACAO', 0)
        n = row.get('N_OBSERVACOES', 0)

        forca = 'forte' if abs(corr) > 0.7 else 'moderada' if abs(corr) > 0.4 else 'fraca'
        direcao = 'positiva' if corr > 0 else 'negativa'

        print(f"\n{par}:")
        print(f"  Correlacao: {corr:.4f} ({forca} {direcao})")
        print(f"  N observacoes: {n}")


def main():
    print("=" * 70)
    print("ANALISE DE CORRELACAO E CAUSALIDADE")
    print("=" * 70)
    print()

    csv_path = sys.argv[1] if len(sys.argv) > 1 else None

    df_educacao, df_correlacoes = carregar_dados(csv_path)

    print(f"\nTotal de observacoes: {len(df_educacao)}")

    if df_correlacoes is not None:
        exibir_correlacoes_bigquery(df_correlacoes)

    variaveis = ['NOTA_MEDIA_ENEM', 'PCT_ESCOLAS_INTERNET',
                'PCT_ESCOLAS_LABORATORIO', 'ALUNOS_POR_DOCENTE',
                'TOTAL_MATRICULAS']

    variaveis_disponiveis = [v for v in variaveis if v in df_educacao.columns]

    if len(variaveis_disponiveis) >= 2:
        print("\n" + "=" * 70)
        print("MATRIZ DE CORRELACAO CALCULADA")
        print("=" * 70)

        matriz_corr, p_values = calcular_matriz_correlacao(df_educacao, variaveis_disponiveis)
        print("\nCorrelacoes de Pearson:")
        print(matriz_corr.round(3).to_string())

        output1 = plotar_matriz_correlacao(matriz_corr)
        print(f"\nGrafico salvo: {output1}")

    print("\n" + "=" * 70)
    print("CONSIDERACOES SOBRE CAUSALIDADE")
    print("=" * 70)
    print("""
IMPORTANTE: Correlacao NAO implica causalidade!

Para estabelecer causalidade, sao necessarios:
1. Associacao estatistica (correlacao) - verificado acima
2. Precedencia temporal - requer dados longitudinais
3. Ausencia de variaveis confundidoras - dificil garantir
4. Mecanismo teorico plausivel - conhecimento de dominio

Recomendacoes:
- Use correlacoes parciais para controlar confundidores
- Considere analise de mediacao para entender mecanismos
- Interprete resultados com cautela
""")

    print("=" * 70)
    print("Analise de correlacao e causalidade concluida!")
    print("=" * 70)


if __name__ == "__main__":
    main()
