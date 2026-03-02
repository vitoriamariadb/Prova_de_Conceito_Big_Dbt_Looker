import os
import pandas as pd
from google.cloud import bigquery

PROJECT_ID = 'provas-de-conceitos'
DATASET = 'mec_educacao_dev'


class BigQueryLoader:

    def __init__(self, project_id=PROJECT_ID, dataset=DATASET):
        self.project_id = project_id
        self.dataset = dataset
        self.client = None

    def _get_client(self):
        if self.client is None:
            self.client = bigquery.Client(project=self.project_id)
        return self.client

    def query(self, sql):
        client = self._get_client()
        return client.query(sql).to_dataframe()

    def load_table(self, table_name):
        sql = f"SELECT * FROM `{self.project_id}.{self.dataset}.{table_name}`"
        return self.query(sql)

    def load_mart_educacao_uf(self):
        return self.load_table('mart_educacao_uf')

    def load_mart_clusters(self):
        return self.load_table('mart_clusters')

    def load_mart_correlacoes(self):
        return self.load_table('mart_correlacoes')

    def load_mart_alocacao(self):
        return self.load_table('mart_alocacao')

    def load_mart_simulacao_cenarios(self):
        return self.load_table('mart_simulacao_cenarios')

    def load_dim_municipios(self):
        return self.load_table('dim_municipios')


def carregar_dados_educacao(tabela='mart_educacao_uf'):
    loader = BigQueryLoader()
    return loader.load_table(tabela)
