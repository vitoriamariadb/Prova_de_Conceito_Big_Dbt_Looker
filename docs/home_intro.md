# Home — Textos de Apresentação

---

## Parágrafo 1 — Contexto e Problema

A desigualdade educacional no Brasil se manifesta com precisão cirúrgica nos microdados do ENEM: estados do Norte e Nordeste registram médias consistentemente abaixo dos 550 pontos estabelecidos pelo Plano Nacional de Educação como referência de qualidade, enquanto estados do Sul e Sudeste superam essa marca com folga. Essa assimetria não é aleatória — ela é estruturada por décadas de diferenças em infraestrutura escolar, composição do corpo docente e contexto socioeconômico das famílias. Este estudo parte desse diagnóstico para construir uma análise quantitativa multicamada, capaz de ir além da descrição do problema e propor estratégias de melhoria com estimativas de custo e impacto projetado.

---

## Parágrafo 2 — Metodologia e Pipeline de Dados

O pipeline integra duas bases públicas do INEP/MEC — o Censo Escolar da Educação Básica e os Microdados do ENEM 2023 — processadas no BigQuery com transformações orquestradas pelo dbt seguindo arquitetura medallion (raw → staging → marts). Na camada analítica, variáveis de desempenho, renda e infraestrutura foram normalizadas por Z-Score e aplicadas em um modelo de clusterização que segmenta os 27 estados em perfis homogêneos. Sobre esses clusters, um modelo de alocação orçamentária simula o investimento necessário para eliminar gaps identificados em conectividade, laboratórios e razão aluno/docente, com estimativas de custo baseadas em parâmetros reais de mercado e metas do PNE.

---

## Parágrafo 3 — Estrutura do Dashboard

O dashboard está organizado em quatro camadas analíticas progressivas. A **camada descritiva** apresenta os indicadores por UF e região — matrículas, docentes, conectividade e desempenho no ENEM — com filtros dinâmicos de ano, estado e município. A **camada preditiva** aplica correlação de Pearson entre variáveis-chave e exibe os clusters estaduais em scatter plot e mapa de bolhas georreferenciado, permitindo leitura imediata dos perfis regionais. A **camada prescritiva** traduz os achados em prioridades de investimento: quais estados demandam intervenção urgente, qual o custo estimado para fechar cada gap e qual o impacto projetado em diferentes cenários de aumento orçamentário. Cada página é autocontida e navegável de forma independente.

---

## Parágrafo 4 — Sobre Este Projeto

Este projeto integra competências em engenharia de dados (dbt + BigQuery), análise estatística (Z-Score, correlação de Pearson, clusterização por perfil), visualização analítica (Looker Studio) e storytelling orientado a decisão de política pública. O código-fonte completo está disponível no GitHub e a arquitetura foi projetada para ser replicável em outros contextos — qualquer base de indicadores por unidade geográfica pode ser adaptada ao mesmo pipeline. O objetivo central é demonstrar que dados abertos, quando tratados com rigor metodológico, são suficientes para sustentar recomendações de investimento fundamentadas, auditáveis e acionáveis.
