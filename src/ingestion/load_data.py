import json
from pathlib import Path

import pandas as pd


def carregar_dados_json(caminho_json: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    caminho = Path(caminho_json)
    with caminho.open("r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    df_estacoes = pd.DataFrame(dados.get("estacoes", []))
    df_leituras = pd.DataFrame(dados.get("leituras", []))
    return df_estacoes, df_leituras


def anonimizar_estacoes(df_estacoes: pd.DataFrame) -> pd.DataFrame:
    df = df_estacoes.copy()
    if "operador" in df.columns:
        df = df.drop(columns=["operador"])
    return df


def tratar_leituras(df_leituras: pd.DataFrame) -> pd.DataFrame:
    df = df_leituras.copy()
    colunas_numericas = [
        "temperatura_agua",
        "ph",
        "oxigenio_dissolvido",
        "condutividade",
        "temperatura_ar",
        "umidade",
        "precipitacao",
    ]

    df["data_hora"] = pd.to_datetime(df["data_hora"])

    for coluna in colunas_numericas:
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce")
        df[coluna] = df.groupby("id_estacao")[coluna].transform(lambda serie: serie.fillna(serie.median()))

    return df
