# Visão Geral do Projeto

## Contexto

Este projeto analisa dados educacionais do MEC (Ministério da Educação) para identificar padrões, correlações e oportunidades de melhoria na educação brasileira.

## Fontes de Dados

| Fonte | Descrição | Período |
|-------|-----------|---------|
| **Censo Escolar** | Dados de escolas, matrículas, docentes e infraestrutura | 2019-2025 |
| **ENEM** | Notas, perfil socioeconômico dos participantes | 2019-2025 |
| **PDDE** | Dados orçamentários da educação | 2019-2025 |

## Estrutura das Análises

O dashboard está organizado em **4 páginas** que seguem uma progressão lógica:

```
┌─────────────────────────────────────────────────────────────────┐
│  PÁGINA 1: RESUMO EXECUTIVO                                     │
│  "Qual é o panorama geral da educação brasileira?"              │
│  → KPIs principais                                              │
│  → Destaques e alertas                                          │
│  → Visão consolidada                                            │
└──────────────────────────────────────┬──────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────┐
│  PÁGINA 2: ANÁLISE DESCRITIVA                                   │
│  "O que está acontecendo na educação brasileira?"               │
│  → Distribuição geográfica                                      │
│  → Tendências temporais                                         │
│  → Infraestrutura escolar                                       │
└──────────────────────────────────────┬──────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────┐
│  PÁGINA 3: ANÁLISE PREDITIVA                                    │
│  "Por que alguns estados têm melhor desempenho?"                │
│  → Correlações (internet x nota)                                │
│  → Regressão linear                                             │
│  → Fatores de influência                                        │
└──────────────────────────────────────┬──────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────┐
│  PÁGINA 4: ANÁLISE PRESCRITIVA                                  │
│  "Onde investir para melhorar resultados?"                      │
│  → Clusterização de UFs                                         │
│  → Simulação de investimentos                                   │
│  → Priorização de recursos                                      │
└─────────────────────────────────────────────────────────────────┘
```

## Público-Alvo

- **Gestores educacionais** do MEC e Secretarias Estaduais
- **Analistas de políticas públicas**
- **Pesquisadores** em educação

## Indicadores Principais

| Indicador | Descrição | Meta |
|-----------|-----------|------|
| Nota Média ENEM | Média das 5 provas por UF | > 550 pontos |
| % Escolas com Internet | Conectividade digital | > 95% |
| Alunos por Docente | Proporção de atenção | < 25:1 |
| Taxa de Abandono | Evasão escolar | < 5% |
| IDEB | Índice de Desenvolvimento da Educação Básica | > 6.0 |

---

Navegue para os documentos específicos de cada página:
- [Página 1: Resumo Executivo](00_VISAO_GERAL.md)
- [Página 2: Análise Descritiva](01_PAGINA_DESCRITIVA.md)
- [Página 3: Análise Preditiva](02_PAGINA_PREDITIVA.md)
- [Página 4: Análise Prescritiva](03_PAGINA_PRESCRITIVA.md)
