#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
        CORES_CORPORATIVO, DIMENSOES_PAISAGEM, DPI,
        configurar_estilo, adicionar_rodape, criar_caixa_texto, estilizar_eixos
    )
except ImportError:
    CORES_CORPORATIVO = {
        'primaria': '#1B4F72', 'secundaria': '#2874A6', 'critico': '#943126',
        'fundo': '#F8F9F9', 'texto': '#2C3E50', 'grid': '#D5D8DC'
    }
    DIMENSOES_PAISAGEM = (14.9, 10.5)
    DPI = 150
    def configurar_estilo(): pass
    def adicionar_rodape(fig, texto=''): pass
    def criar_caixa_texto(ax, texto, posicao=(0.05, 0.95)): pass
    def estilizar_eixos(ax, **kwargs): pass


def carregar_dados_bigquery():
    loader = BigQueryLoader()
    df = loader.load_mart_educacao_uf()
    return df


def carregar_dados(caminho_csv=None):
    if caminho_csv:
        try:
            df = pd.read_csv(caminho_csv)
            print(f"Dados carregados: {caminho_csv} ({len(df)} linhas)")
            return df
        except FileNotFoundError:
            print(f"Arquivo nao encontrado: {caminho_csv}")

    if BIGQUERY_DISPONIVEL:
        try:
            print("Carregando dados do BigQuery...")
            df = carregar_dados_bigquery()
            print(f"Dados carregados do BigQuery: {len(df)} linhas")
            return df
        except Exception as e:
            print(f"Erro ao carregar BigQuery: {e}")

    print("ERRO: Nenhuma fonte de dados disponivel")
    sys.exit(1)


def executar_regressao(df, col_x='PCT_ESCOLAS_INTERNET', col_y='NOTA_MEDIA_ENEM'):
    df_clean = df[[col_x, col_y]].dropna()

    if len(df_clean) < 10:
        raise ValueError("Dados insuficientes para regressao")

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


def plotar_regressao(modelo, X, y, resultados, df=None, output_path='outputs/regressao_infra_nota.png'):
    configurar_estilo()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=DIMENSOES_PAISAGEM)

    ax.scatter(X, y, alpha=0.8, color=CORES_CORPORATIVO['primaria'], s=120,
              edgecolors='white', linewidth=1.5, zorder=5)

    if df is not None and 'UF' in df.columns:
        for i, uf in enumerate(df['UF'][:len(X)]):
            ax.annotate(uf, (X[i, 0], y[i]), fontsize=7, ha='center', va='bottom',
                       color=CORES_CORPORATIVO['texto'], fontweight='bold')

    X_line = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
    y_line = modelo.predict(X_line)
    ax.plot(X_line, y_line, color=CORES_CORPORATIVO['critico'], linewidth=2.5, zorder=4)

    y_pred_all = modelo.predict(X)
    conf_interval = 1.96 * np.std(y - y_pred_all)
    ax.fill_between(X_line.flatten(), y_line - conf_interval, y_line + conf_interval,
                   color=CORES_CORPORATIVO['critico'], alpha=0.1, zorder=3)

    ax.set_xlabel('% Escolas com Internet', fontsize=11,
                 color=CORES_CORPORATIVO['texto'], fontweight='bold')
    ax.set_ylabel('Nota Media ENEM', fontsize=11,
                 color=CORES_CORPORATIVO['texto'], fontweight='bold')
    ax.set_title('Regressao Linear: Infraestrutura Digital vs Desempenho Educacional',
                fontsize=13, color=CORES_CORPORATIVO['primaria'], fontweight='bold', pad=20)

    texto = f"R² = {resultados['r2_score']:.4f}\n"
    texto += f"Coef = {resultados['coeficiente']:.4f}\n"
    texto += f"n = {resultados['n_amostras']}"

    props = dict(boxstyle='round,pad=0.5', facecolor=CORES_CORPORATIVO['fundo'],
                edgecolor=CORES_CORPORATIVO['primaria'], alpha=0.95)
    ax.text(0.05, 0.95, texto, transform=ax.transAxes, fontsize=10,
           verticalalignment='top', bbox=props, fontweight='bold',
           color=CORES_CORPORATIVO['primaria'])

    estilizar_eixos(ax)
    adicionar_rodape(fig)

    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight', facecolor=CORES_CORPORATIVO['fundo'])
    plt.close()

    return output_path


def main():
    print("=" * 60)
    print("ANALISE DE REGRESSAO: INFRAESTRUTURA vs NOTA ENEM")
    print("=" * 60)
    print()

    csv_path = sys.argv[1] if len(sys.argv) > 1 else None

    df = carregar_dados(csv_path)

    print(f"\nDataset: {len(df)} registros")
    print(f"Colunas: {list(df.columns)}")

    try:
        modelo, resultados, (X, y) = executar_regressao(df)

        print("\n" + "=" * 60)
        print("RESULTADOS DA REGRESSAO")
        print("=" * 60)
        print(f"Coeficiente:       {resultados['coeficiente']:.4f}")
        print(f"Intercepto:        {resultados['intercepto']:.2f}")
        print(f"R² Score:          {resultados['r2_score']:.4f}")
        print(f"RMSE:              {resultados['rmse']:.2f}")
        print(f"Amostras:          {resultados['n_amostras']}")

        print("\nInterpretacao:")
        print(f"  Para cada 1% de aumento em escolas com internet,")
        print(f"  a nota ENEM aumenta em media {resultados['coeficiente']:.2f} pontos.")

        output_file = plotar_regressao(modelo, X, y, resultados, df)
        print(f"\nGrafico salvo: {output_file}")

    except Exception as e:
        print(f"\nERRO na regressao: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("Analise concluida!")
    print("=" * 60)


if __name__ == "__main__":
    main()
