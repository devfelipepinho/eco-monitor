import pandas as pd

from src.analytics.stats import calcular_estatisticas_basicas, identificar_outliers


def criar_dataframe_teste() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "temperatura_agua": [20, 21, 22, 23, 24],
            "ph": [7.0, 7.1, 6.9, 7.2, 7.0],
            "oxigenio_dissolvido": [5.0, 5.1, 4.9, 5.2, 5.0],
            "condutividade": [100, 102, 101, 103, 180],
            "temperatura_ar": [25, 26, 24, 27, 28],
            "umidade": [60, 62, 61, 63, 64],
            "precipitacao": [0, 1, 0, 2, 0],
        }
    )


def test_calcular_estatisticas_basicas_retorna_parametros() -> None:
    df = criar_dataframe_teste()
    resultado = calcular_estatisticas_basicas(df)
    assert not resultado.empty
    assert "parametro" in resultado.columns
    assert "media" in resultado.columns
    assert len(resultado) == 7


def test_identificar_outliers_encontra_registro_extremo() -> None:
    df = criar_dataframe_teste()
    resultado = identificar_outliers(df, "condutividade")
    assert len(resultado) == 1
    assert resultado.iloc[0]["condutividade"] == 180
