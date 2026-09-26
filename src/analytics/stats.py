import pandas as pd


PARAMETROS = [
    "temperatura_agua",
    "ph",
    "oxigenio_dissolvido",
    "condutividade",
    "temperatura_ar",
    "umidade",
    "precipitacao",
]


def calcular_estatisticas_basicas(df_leituras: pd.DataFrame) -> pd.DataFrame:
    resultados = []

    for parametro in PARAMETROS:
        serie = df_leituras[parametro].dropna()
        q1 = serie.quantile(0.25)
        q3 = serie.quantile(0.75)
        iqr = q3 - q1
        resultados.append(
            {
                "parametro": parametro,
                "media": round(serie.mean(), 2),
                "mediana": round(serie.median(), 2),
                "desvio_padrao": round(serie.std(ddof=1), 2),
                "q1": round(q1, 2),
                "q3": round(q3, 2),
                "iqr": round(iqr, 2),
            }
        )

    return pd.DataFrame(resultados)


def identificar_outliers(df_leituras: pd.DataFrame, coluna: str) -> pd.DataFrame:
    serie = df_leituras[coluna].dropna()
    q1 = serie.quantile(0.25)
    q3 = serie.quantile(0.75)
    iqr = q3 - q1
    limite_inferior = q1 - 1.5 * iqr
    limite_superior = q3 + 1.5 * iqr

    return df_leituras[
        (df_leituras[coluna] < limite_inferior) | (df_leituras[coluna] > limite_superior)
    ].copy()
