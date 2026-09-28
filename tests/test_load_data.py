import json
import pytest
import pandas as pd

from src.ingestion.load_data import anonimizar_estacoes, tratar_leituras, carregar_dados_json


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def df_estacoes_com_operador():
    return pd.DataFrame({
        "id_estacao": [1, 2],
        "nome_estacao": ["Rio Verde", "Rio Azul"],
        "operador": ["João", "Maria"],
    })


@pytest.fixture
def df_estacoes_sem_operador():
    return pd.DataFrame({
        "id_estacao": [1, 2],
        "nome_estacao": ["Rio Verde", "Rio Azul"],
    })


@pytest.fixture
def df_leituras_validas():
    return pd.DataFrame({
        "id_estacao":          [1, 1, 2],
        "data_hora":           ["2024-01-01 08:00", "2024-01-01 09:00", "2024-01-01 08:00"],
        "temperatura_agua":    [20.0, 21.0, 22.0],
        "ph":                  [7.0,  7.1,  6.9],
        "oxigenio_dissolvido": [5.0,  5.1,  4.9],
        "condutividade":       [100,  102,  101],
        "temperatura_ar":      [25.0, 26.0, 24.0],
        "umidade":             [60.0, 62.0, 61.0],
        "precipitacao":        [0.0,  1.0,  0.0],
    })


@pytest.fixture
def df_leituras_com_nan(df_leituras_validas):
    df = df_leituras_validas.copy()
    df.loc[0, "ph"] = None
    return df


@pytest.fixture
def arquivo_json_valido(tmp_path, df_leituras_validas):
    """Cria um arquivo JSON temporário com estrutura válida."""
    dados = {
        "estacoes": [
            {"id_estacao": 1, "nome_estacao": "Rio Verde", "municipio": "SP", "estado": "SP", "operador": "João"},
        ],
        "leituras": df_leituras_validas[df_leituras_validas["id_estacao"] == 1].to_dict(orient="records"),
    }
    caminho = tmp_path / "dados.json"
    caminho.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    return str(caminho)


# ---------------------------------------------------------------------------
# anonimizar_estacoes
# ---------------------------------------------------------------------------

def test_anonimizar_remove_coluna_operador(df_estacoes_com_operador):
    resultado = anonimizar_estacoes(df_estacoes_com_operador)
    assert "operador" not in resultado.columns


def test_anonimizar_preserva_outras_colunas(df_estacoes_com_operador):
    resultado = anonimizar_estacoes(df_estacoes_com_operador)
    assert "id_estacao" in resultado.columns
    assert "nome_estacao" in resultado.columns


def test_anonimizar_nao_modifica_original(df_estacoes_com_operador):
    """Função deve ser pura — não alterar o DataFrame de entrada."""
    anonimizar_estacoes(df_estacoes_com_operador)
    assert "operador" in df_estacoes_com_operador.columns


def test_anonimizar_sem_coluna_operador_nao_quebra(df_estacoes_sem_operador):
    """Quando 'operador' já não existe, deve retornar o DataFrame sem erro."""
    resultado = anonimizar_estacoes(df_estacoes_sem_operador)
    assert list(resultado.columns) == list(df_estacoes_sem_operador.columns)


def test_anonimizar_retorna_dataframe(df_estacoes_com_operador):
    resultado = anonimizar_estacoes(df_estacoes_com_operador)
    assert isinstance(resultado, pd.DataFrame)


# ---------------------------------------------------------------------------
# tratar_leituras
# ---------------------------------------------------------------------------

def test_tratar_converte_data_hora_para_datetime(df_leituras_validas):
    resultado = tratar_leituras(df_leituras_validas)
    assert pd.api.types.is_datetime64_any_dtype(resultado["data_hora"])


def test_tratar_nao_tem_nan_em_numericas(df_leituras_com_nan):
    """NaN em 'ph' deve ser preenchido pela mediana do grupo."""
    resultado = tratar_leituras(df_leituras_com_nan)
    assert resultado["ph"].isna().sum() == 0


def test_tratar_preenche_nan_pela_mediana_do_grupo(df_leituras_com_nan):
    """Estacao 1 tem ph=[None, 7.1] → mediana=7.1 preenche o NaN."""
    resultado = tratar_leituras(df_leituras_com_nan)
    valor_preenchido = resultado.loc[0, "ph"]
    assert valor_preenchido == pytest.approx(7.1)


def test_tratar_nao_modifica_original(df_leituras_validas):
    tratar_leituras(df_leituras_validas)
    assert df_leituras_validas["data_hora"].dtype == object


def test_tratar_retorna_dataframe(df_leituras_validas):
    resultado = tratar_leituras(df_leituras_validas)
    assert isinstance(resultado, pd.DataFrame)


def test_tratar_mantém_numero_de_linhas(df_leituras_validas):
    resultado = tratar_leituras(df_leituras_validas)
    assert len(resultado) == len(df_leituras_validas)


# ---------------------------------------------------------------------------
# carregar_dados_json
# ---------------------------------------------------------------------------

def test_carregar_retorna_dois_dataframes(arquivo_json_valido):
    df_est, df_lei = carregar_dados_json(arquivo_json_valido)
    assert isinstance(df_est, pd.DataFrame)
    assert isinstance(df_lei, pd.DataFrame)


def test_carregar_estacoes_tem_dados(arquivo_json_valido):
    df_est, _ = carregar_dados_json(arquivo_json_valido)
    assert len(df_est) == 1


def test_carregar_leituras_tem_dados(arquivo_json_valido):
    _, df_lei = carregar_dados_json(arquivo_json_valido)
    assert len(df_lei) == 2  # 2 leituras da estacao 1


def test_carregar_arquivo_inexistente_levanta_erro(tmp_path):
    with pytest.raises(FileNotFoundError):
        carregar_dados_json(str(tmp_path / "nao_existe.json"))
