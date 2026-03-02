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
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
except ImportError as e:
    print(f"ERRO: Dependencia nao instalada: {e}")
    print("Execute: pip install pandas numpy scipy matplotlib")
    sys.exit(1)

try:
    from utils.data_loader import BigQueryLoader
    BIGQUERY_DISPONIVEL = True
except ImportError:
    BIGQUERY_DISPONIVEL = False

try:
    from utils.estilo_corporativo import (
        CORES_CORPORATIVO, CORES_STATUS, DIMENSOES_PAISAGEM, DPI,
        configurar_estilo, adicionar_rodape, estilizar_eixos
    )
except ImportError:
    CORES_CORPORATIVO = {
        'primaria': '#1B4F72', 'secundaria': '#2874A6', 'destaque': '#117A65',
        'critico': '#943126', 'alerta': '#B7950B',
        'fundo': '#F8F9F9', 'texto': '#2C3E50', 'grid': '#D5D8DC'
    }
    CORES_STATUS = {
        'CRITICO': '#943126', 'ATENCAO': '#B7950B',
        'REGULAR': '#2874A6', 'ADEQUADO': '#117A65'
    }
    DIMENSOES_PAISAGEM = (14.9, 10.5)
    DPI = 150
    def configurar_estilo(): pass
    def adicionar_rodape(fig, texto=''): pass
    def estilizar_eixos(ax, **kwargs): pass


def carregar_dados_bigquery():
    loader = BigQueryLoader()
    df_alocacao = loader.load_mart_alocacao()
    df_cenarios = loader.load_mart_simulacao_cenarios()
    return df_alocacao, df_cenarios


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
            df_alocacao, df_cenarios = carregar_dados_bigquery()
            print(f"Alocacao: {len(df_alocacao)} UFs")
            print(f"Cenarios: {len(df_cenarios)} simulacoes")
            return df_alocacao, df_cenarios
        except Exception as e:
            print(f"Erro ao carregar BigQuery: {e}")

    print("ERRO: Nenhuma fonte de dados disponivel")
    sys.exit(1)


def analisar_gap_recursos(df_alocacao):
    print("\n" + "=" * 70)
    print("ANALISE DE GAP DE RECURSOS")
    print("=" * 70)

    if 'STATUS_DESEMPENHO' in df_alocacao.columns:
        for status in ['CRITICO', 'ATENCAO', 'REGULAR', 'ADEQUADO']:
            ufs = df_alocacao[df_alocacao['STATUS_DESEMPENHO'] == status]
            if len(ufs) > 0:
                print(f"\n{status}: {len(ufs)} UFs")
                print(f"  UFs: {', '.join(ufs['UF'].tolist())}")

                if 'INVESTIMENTO_TOTAL_ESTIMADO_BRL' in ufs.columns:
                    total = ufs['INVESTIMENTO_TOTAL_ESTIMADO_BRL'].sum()
                    print(f"  Investimento total: R$ {total/1e6:.2f} milhoes")

    return df_alocacao


def analisar_cenarios(df_cenarios):
    print("\n" + "=" * 70)
    print("SIMULACAO DE CENARIOS")
    print("=" * 70)

    if df_cenarios is not None and len(df_cenarios) > 0:
        for _, row in df_cenarios.iterrows():
            pct = row.get('AUMENTO_PERCENTUAL', row.get('CENARIO_NOME', 'N/A'))
            tipo = row.get('TIPO_CENARIO', 'N/A')
            impacto_nota = row.get('IMPACTO_NOTA_ENEM_PONTOS', 0)
            reducao_abandono = row.get('REDUCAO_ABANDONO_PCT', 0)

            print(f"\nCenario {pct}% ({tipo}):")
            print(f"  Impacto ENEM: +{impacto_nota:.1f} pontos")
            print(f"  Reducao abandono: -{reducao_abandono:.2f}%")

    return df_cenarios


def plotar_analise(df_alocacao, df_cenarios, output_path='outputs/impacto_financeiro.png'):
    configurar_estilo()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=DIMENSOES_PAISAGEM)

    if 'STATUS_DESEMPENHO' in df_alocacao.columns and 'INVESTIMENTO_TOTAL_ESTIMADO_BRL' in df_alocacao.columns:
        ax1 = axes[0]

        df_sorted = df_alocacao.sort_values('INVESTIMENTO_TOTAL_ESTIMADO_BRL', ascending=True)
        cores = [CORES_STATUS.get(s, CORES_CORPORATIVO['primaria'])
                for s in df_sorted['STATUS_DESEMPENHO']]

        valores = df_sorted['INVESTIMENTO_TOTAL_ESTIMADO_BRL'] / 1e9
        bars = ax1.barh(df_sorted['UF'], valores, color=cores, edgecolor='white', linewidth=0.5)

        for bar, valor in zip(bars, valores):
            ax1.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
                    f'R$ {valor:.1f}bi', va='center', ha='left', fontsize=7,
                    color=CORES_CORPORATIVO['texto'])

        ax1.set_xlabel('Investimento (R$ bilhoes)', fontsize=11,
                      color=CORES_CORPORATIVO['texto'], fontweight='bold')
        ax1.set_ylabel('UF', fontsize=11,
                      color=CORES_CORPORATIVO['texto'], fontweight='bold')
        ax1.set_title('Investimento Necessario por UF',
                     fontsize=12, color=CORES_CORPORATIVO['primaria'], fontweight='bold')

        legend_elements = [
            Patch(facecolor=CORES_STATUS['CRITICO'], label='Critico'),
            Patch(facecolor=CORES_STATUS['ATENCAO'], label='Atencao'),
            Patch(facecolor=CORES_STATUS['REGULAR'], label='Regular'),
            Patch(facecolor=CORES_STATUS['ADEQUADO'], label='Adequado')
        ]
        ax1.legend(handles=legend_elements, loc='lower right', title='Status', fontsize=8)

        estilizar_eixos(ax1)

    if df_cenarios is not None and 'IMPACTO_NOTA_ENEM_PONTOS' in df_cenarios.columns:
        ax2 = axes[1]

        x_labels = df_cenarios['AUMENTO_PERCENTUAL'].astype(str) + '%'
        valores = df_cenarios['IMPACTO_NOTA_ENEM_PONTOS']

        bars = ax2.bar(x_labels, valores, color=CORES_CORPORATIVO['primaria'],
                      edgecolor='white', linewidth=0.5)

        for bar, v in zip(bars, valores):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                    f'+{v:.1f}', ha='center', fontsize=10, fontweight='bold',
                    color=CORES_CORPORATIVO['primaria'])

        ax2.set_xlabel('Aumento de Investimento', fontsize=11,
                      color=CORES_CORPORATIVO['texto'], fontweight='bold')
        ax2.set_ylabel('Impacto na Nota ENEM (pontos)', fontsize=11,
                      color=CORES_CORPORATIVO['texto'], fontweight='bold')
        ax2.set_title('Impacto por Cenario de Investimento',
                     fontsize=12, color=CORES_CORPORATIVO['primaria'], fontweight='bold')

        estilizar_eixos(ax2)

    fig.suptitle('Analise de Impacto Financeiro - Investimentos em Educacao',
                fontsize=14, color=CORES_CORPORATIVO['primaria'], fontweight='bold', y=1.02)

    adicionar_rodape(fig)

    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight', facecolor=CORES_CORPORATIVO['fundo'])
    plt.close()

    return output_path


def main():
    print("=" * 70)
    print("ANALISE DE IMPACTO FINANCEIRO: Simulacao de Investimentos")
    print("=" * 70)
    print()

    csv_path = sys.argv[1] if len(sys.argv) > 1 else None

    df_alocacao, df_cenarios = carregar_dados(csv_path)

    analisar_gap_recursos(df_alocacao)

    if df_cenarios is not None:
        analisar_cenarios(df_cenarios)

    output_file = plotar_analise(df_alocacao, df_cenarios)
    print(f"\nGrafico salvo: {output_file}")

    if 'INVESTIMENTO_TOTAL_ESTIMADO_BRL' in df_alocacao.columns:
        total = df_alocacao['INVESTIMENTO_TOTAL_ESTIMADO_BRL'].sum()
        print(f"\nInvestimento total necessario: R$ {total/1e9:.2f} bilhoes")

    print("\n" + "=" * 70)
    print("Analise de impacto financeiro concluida!")
    print("=" * 70)


if __name__ == "__main__":
    main()
