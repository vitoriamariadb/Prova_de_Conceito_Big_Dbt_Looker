#!/usr/bin/env python3

import matplotlib.pyplot as plt

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

CORES_STATUS = {
    'CRITICO': CORES_CORPORATIVO['critico'],
    'ATENCAO': CORES_CORPORATIVO['alerta'],
    'REGULAR': CORES_CORPORATIVO['secundaria'],
    'ADEQUADO': CORES_CORPORATIVO['destaque']
}

CORES_CLUSTER = [
    CORES_CORPORATIVO['primaria'],
    CORES_CORPORATIVO['secundaria'],
    CORES_CORPORATIVO['destaque'],
    CORES_CORPORATIVO['alerta'],
    CORES_CORPORATIVO['terciaria']
]

DIMENSOES_RETRATO = (10.5, 14.9)
DIMENSOES_PAISAGEM = (14.9, 10.5)
DIMENSOES_QUADRADO = (10, 10)
DPI = 150


def configurar_estilo():
    plt.rcParams.update({
        'figure.figsize': DIMENSOES_PAISAGEM,
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


def adicionar_rodape(fig, texto='Fonte: INEP/MEC | Elaboracao: Prova de Conceito BigQuery + dbt'):
    fig.text(0.5, 0.02, texto, ha='center', fontsize=8,
            color=CORES_CORPORATIVO['texto'], style='italic')


def criar_caixa_texto(ax, texto, posicao=(0.05, 0.95)):
    props = dict(boxstyle='round,pad=0.5', facecolor=CORES_CORPORATIVO['fundo'],
                edgecolor=CORES_CORPORATIVO['primaria'], alpha=0.95)
    ax.text(posicao[0], posicao[1], texto, transform=ax.transAxes, fontsize=10,
           verticalalignment='top', bbox=props, fontweight='bold',
           color=CORES_CORPORATIVO['primaria'])


def estilizar_eixos(ax, remover_superior=True, remover_direita=True, grid=True):
    if remover_superior:
        ax.spines['top'].set_visible(False)
    if remover_direita:
        ax.spines['right'].set_visible(False)
    if grid:
        ax.grid(True, alpha=0.3, linestyle='--', color=CORES_CORPORATIVO['grid'])
