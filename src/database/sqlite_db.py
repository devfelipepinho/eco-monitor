import sqlite3
from pathlib import Path

import pandas as pd


def conectar_banco(caminho_banco: str) -> sqlite3.Connection:
    caminho = Path(caminho_banco)
    conexao = sqlite3.connect(caminho)
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def criar_tabelas(conexao: sqlite3.Connection) -> None:
    cursor = conexao.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS estacoes (
            id_estacao INTEGER PRIMARY KEY,
            nome_estacao TEXT NOT NULL,
            municipio TEXT NOT NULL,
            estado TEXT NOT NULL,
            latitude REAL,
            longitude REAL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS leituras (
            id_leitura INTEGER PRIMARY KEY,
            id_estacao INTEGER NOT NULL,
            data_hora TEXT NOT NULL,
            temperatura_agua REAL,
            ph REAL,
            oxigenio_dissolvido REAL,
            condutividade REAL,
            temperatura_ar REAL,
            umidade REAL,
            precipitacao REAL,
            FOREIGN KEY (id_estacao) REFERENCES estacoes (id_estacao)
        )
        """
    )
    conexao.commit()


def inserir_dados(conexao: sqlite3.Connection, df_estacoes: pd.DataFrame, df_leituras: pd.DataFrame) -> None:
    df_estacoes.to_sql("estacoes", conexao, if_exists="replace", index=False)
    df_leituras_formatado = df_leituras.copy()
    df_leituras_formatado["data_hora"] = df_leituras_formatado["data_hora"].astype(str)
    df_leituras_formatado.to_sql("leituras", conexao, if_exists="replace", index=False)


def consultar_medias_por_estacao(conexao: sqlite3.Connection) -> pd.DataFrame:
    consulta = """
    SELECT
        e.nome_estacao,
        ROUND(AVG(l.temperatura_agua), 2) AS media_temperatura_agua,
        ROUND(AVG(l.ph), 2) AS media_ph,
        ROUND(AVG(l.oxigenio_dissolvido), 2) AS media_oxigenio_dissolvido
    FROM leituras l
    JOIN estacoes e ON e.id_estacao = l.id_estacao
    GROUP BY e.id_estacao, e.nome_estacao
    ORDER BY e.nome_estacao
    """
    return pd.read_sql_query(consulta, conexao)


def consultar_periodo(conexao: sqlite3.Connection, data_inicial: str, data_final: str) -> pd.DataFrame:
    consulta = """
    SELECT l.*, e.nome_estacao
    FROM leituras l
    JOIN estacoes e ON e.id_estacao = l.id_estacao
    WHERE date(l.data_hora) BETWEEN date(?) AND date(?)
    ORDER BY l.data_hora
    """
    return pd.read_sql_query(consulta, conexao, params=(data_inicial, data_final))
