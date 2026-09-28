import pytest
import pandas as pd

from src.analytics.stats import calcular_estatisticas_basicas, identificar_outliers

PARAMETROS_ESPERADOS = [
    "temperatura_agua",
    "ph",
    "oxigenio_dissolvido",
    "condutividade",
    "temperatura_ar",
    "umidade",
    "precipitacao",
]

COLUNAS_ESTATISTICAS = ["parametro", "media", "mediana", "desvio_padrao", "q1", "q3", "iqr"]


@pytest.fixture
def df_base():
    """DataFrame padrão com 5 leituras e um outlier em 'condutividade'."""
    return pd.DataFrame({
        "temperatura_agua":    [20.0, 21.0, 22.0, 23.0, 24.0],
        "ph":                  [7.0,  7.1,  6.9,  7.2,  7.0],
        "oxigenio_dissolvido": [5.0,  5.1,  4.9,  5.2,  5.0],
        "condutividade":       [100,  102,  101,  103,  180],
        "temperatura_ar":      [25.0, 26.0, 24.0, 27.0, 28.0],
        "umidade":             [60.0, 62.0, 61.0, 63.0, 64.0],
        "precipitacao":        [0.0,  1.0,  0.0,  2.0,  0.0],
    })


@pytest.fixture
def df_vazio():
    """DataFrame vazio com as colunas corretas."""
    return pd.DataFrame(columns=PARAMETROS_ESPERADOS)


@pytest.fixture
def df_uniforme(df_base):
    """DataFrame onde 'ph' não tem variação (IQR = 0)."""
    df = df_base.copy()
    df["ph"] = 7.0
    return df


@pytest.fixture
def df_com_nan(df_base):
    """DataFrame com alguns NaN em temperatura_agua."""
    df = df_base.copy()
    df.loc[1, "temperatura_agua"] = None
    df.loc[3, "temperatura_agua"] = None
    return df


# ---------------------------------------------------------------------------
# calcular_estatisticas_basicas — estrutura do retorno
# ---------------------------------------------------------------------------

def test_estatisticas_retorna_todas_colunas(df_base):
    resultado = calcular_estatisticas_basicas(df_base)
    for coluna in COLUNAS_ESTATISTICAS:
        assert coluna in resultado.columns, f"Coluna ausente: {coluna}"


def test_estatisticas_retorna_todos_parametros(df_base):
    resultado = calcular_estatisticas_basicas(df_base)
    assert list(resultado["parametro"]) == PARAMETROS_ESPERADOS


def test_estatisticas_retorna_dataframe(df_base):
    resultado = calcular_estatisticas_basicas(df_base)
    assert isinstance(resultado, pd.DataFrame)


def test_estatisticas_numero_de_linhas(df_base):
    resultado = calcular_estatisticas_basicas(df_base)
    assert len(resultado) == len(PARAMETROS_ESPERADOS)


# ---------------------------------------------------------------------------
# calcular_estatisticas_basicas — valores corretos
# ---------------------------------------------------------------------------

def test_estatisticas_media_temperatura(df_base):
    resultado = calcular_estatisticas_basicas(df_base)
    linha = resultado[resultado["parametro"] == "temperatura_agua"].iloc[0]
    assert linha["media"] == 22.0


def test_estatisticas_mediana_temperatura(df_base):
    resultado = calcular_estatisticas_basicas(df_base)
    linha = resultado[resultado["parametro"] == "temperatura_agua"].iloc[0]
    assert linha["mediana"] == 22.0


def test_estatisticas_quartis_temperatura(df_base):
    resultado = calcular_estatisticas_basicas(df_base)
    linha = resultado[resultado["parametro"] == "temperatura_agua"].iloc[0]
    assert linha["q1"] == 21.0
    assert linha["q3"] == 23.0
    assert linha["iqr"] == 2.0


@pytest.mark.parametrize("parametro", PARAMETROS_ESPERADOS)
def test_estatisticas_sem_valores_negativos_de_iqr(df_base, parametro):
    """IQR nunca pode ser negativo."""
    resultado = calcular_estatisticas_basicas(df_base)
    linha = resultado[resultado["parametro"] == parametro].iloc[0]
    assert linha["iqr"] >= 0


@pytest.mark.parametrize("parametro", PARAMETROS_ESPERADOS)
def test_estatisticas_desvio_nao_negativo(df_base, parametro):
    resultado = calcular_estatisticas_basicas(df_base)
    linha = resultado[resultado["parametro"] == parametro].iloc[0]
    assert linha["desvio_padrao"] >= 0


# ---------------------------------------------------------------------------
# calcular_estatisticas_basicas — casos de borda
# ---------------------------------------------------------------------------

def test_estatisticas_com_df_vazio_retorna_nan(df_vazio):
    resultado = calcular_estatisticas_basicas(df_vazio)
    assert len(resultado) == len(PARAMETROS_ESPERADOS)
    assert resultado["media"].isna().all()
    assert resultado["mediana"].isna().all()


def test_estatisticas_ignora_nan_no_calculo(df_com_nan):
    """Com 2 NaN em temperatura_agua, calcula sobre os 3 restantes: 20, 22, 24 → média = 22."""
    resultado = calcular_estatisticas_basicas(df_com_nan)
    linha = resultado[resultado["parametro"] == "temperatura_agua"].iloc[0]
    assert linha["media"] == 22.0


def test_estatisticas_com_uma_linha_nao_quebra():
    """DataFrame com apenas 1 linha — desvio_padrao deve ser NaN (sem variação calculável)."""
    df = pd.DataFrame({p: [1.0] for p in PARAMETROS_ESPERADOS})
    resultado = calcular_estatisticas_basicas(df)
    assert len(resultado) == len(PARAMETROS_ESPERADOS)
    linha = resultado[resultado["parametro"] == "temperatura_agua"].iloc[0]
    assert linha["media"] == 1.0
    # std com ddof=1 em série de 1 elemento é NaN
    assert pd.isna(linha["desvio_padrao"])


# ---------------------------------------------------------------------------
# identificar_outliers — comportamento principal
# ---------------------------------------------------------------------------

def test_outlier_detecta_valor_extremo(df_base):
    resultado = identificar_outliers(df_base, "condutividade")
    assert len(resultado) == 1
    assert resultado.iloc[0]["condutividade"] == 180


def test_outlier_retorna_vazio_sem_anomalia(df_base):
    resultado = identificar_outliers(df_base, "temperatura_agua")
    assert resultado.empty


def test_outlier_retorna_todas_colunas_originais(df_base):
    resultado = identificar_outliers(df_base, "condutividade")
    for coluna in df_base.columns:
        assert coluna in resultado.columns


def test_outlier_retorna_dataframe(df_base):
    resultado = identificar_outliers(df_base, "condutividade")
    assert isinstance(resultado, pd.DataFrame)


def test_outlier_com_coluna_uniforme_retorna_vazio(df_uniforme):
    """IQR = 0, fences são iguais ao valor → nenhum outlier."""
    resultado = identificar_outliers(df_uniforme, "ph")
    assert resultado.empty


def test_outlier_com_dois_extremos():
    """Detecta outliers nos dois sentidos (inferior e superior)."""
    df = pd.DataFrame({p: [7.0] * 5 for p in PARAMETROS_ESPERADOS})
    df["ph"] = [7.0, 7.0, 7.0, 7.0, 20.0]   # superior
    df2 = df.copy()
    df2["ph"] = [-10.0, 7.0, 7.0, 7.0, 7.0]  # inferior
    assert len(identificar_outliers(df, "ph")) == 1
    assert len(identificar_outliers(df2, "ph")) == 1


@pytest.mark.parametrize("coluna", ["temperatura_agua", "ph", "umidade", "precipitacao"])
def test_outlier_retorna_subset_do_df_original(df_base, coluna):
    """Linhas retornadas devem estar no DataFrame original."""
    resultado = identificar_outliers(df_base, coluna)
    for idx in resultado.index:
        assert idx in df_base.index
