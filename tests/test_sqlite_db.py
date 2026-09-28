import sqlite3
import pytest
import pandas as pd

from src.database.sqlite_db import (
    conectar_banco,
    criar_tabelas,
    inserir_dados,
    consultar_medias_por_estacao,
    consultar_periodo,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def conexao():
    """Banco em memória: criado antes do teste e fechado depois."""
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    yield conn
    conn.close()


@pytest.fixture
def conexao_com_tabelas(conexao):
    criar_tabelas(conexao)
    return conexao


@pytest.fixture
def df_estacoes():
    return pd.DataFrame({
        "id_estacao":   [1, 2],
        "nome_estacao": ["Rio Verde", "Rio Azul"],
        "municipio":    ["São Paulo", "Campinas"],
        "estado":       ["SP", "SP"],
        "latitude":     [-23.5, -22.9],
        "longitude":    [-46.6, -47.0],
    })


@pytest.fixture
def df_leituras():
    return pd.DataFrame({
        "id_leitura":         [1, 2, 3, 4],
        "id_estacao":         [1, 1, 2, 2],
        "data_hora":          [
            "2024-01-10 08:00",
            "2024-01-11 08:00",
            "2024-01-10 08:00",
            "2024-01-12 08:00",
        ],
        "temperatura_agua":   [20.0, 22.0, 18.0, 19.0],
        "ph":                 [7.0,  7.2,  6.8,  7.0],
        "oxigenio_dissolvido":[5.0,  5.2,  4.8,  5.1],
        "condutividade":      [100,  102,  98,   101],
        "temperatura_ar":     [25.0, 27.0, 23.0, 24.0],
        "umidade":            [60.0, 62.0, 58.0, 61.0],
        "precipitacao":       [0.0,  0.0,  1.0,  0.0],
    })


@pytest.fixture
def conexao_populada(conexao_com_tabelas, df_estacoes, df_leituras):
    inserir_dados(conexao_com_tabelas, df_estacoes, df_leituras)
    return conexao_com_tabelas


# ---------------------------------------------------------------------------
# conectar_banco
# ---------------------------------------------------------------------------

def test_conectar_banco_retorna_connection(tmp_path):
    caminho = str(tmp_path / "teste.db")
    conn = conectar_banco(caminho)
    assert isinstance(conn, sqlite3.Connection)
    conn.close()


def test_conectar_banco_em_memoria():
    conn = conectar_banco(":memory:")
    assert conn is not None
    conn.close()


# ---------------------------------------------------------------------------
# criar_tabelas
# ---------------------------------------------------------------------------

def test_criar_tabelas_cria_estacoes(conexao):
    criar_tabelas(conexao)
    cursor = conexao.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='estacoes'")
    assert cursor.fetchone() is not None


def test_criar_tabelas_cria_leituras(conexao):
    criar_tabelas(conexao)
    cursor = conexao.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='leituras'")
    assert cursor.fetchone() is not None


def test_criar_tabelas_idempotente(conexao):
    """Chamar duas vezes não deve levantar erro (IF NOT EXISTS)."""
    criar_tabelas(conexao)
    criar_tabelas(conexao)  # segunda chamada não deve quebrar


# ---------------------------------------------------------------------------
# inserir_dados
# ---------------------------------------------------------------------------

def test_inserir_dados_estacoes(conexao_populada):
    cursor = conexao_populada.execute("SELECT COUNT(*) FROM estacoes")
    assert cursor.fetchone()[0] == 2


def test_inserir_dados_leituras(conexao_populada):
    cursor = conexao_populada.execute("SELECT COUNT(*) FROM leituras")
    assert cursor.fetchone()[0] == 4


def test_inserir_dados_substitui_registros_anteriores(conexao_com_tabelas, df_estacoes, df_leituras):
    """Segunda inserção deve limpar e reinserir (DELETE + INSERT)."""
    inserir_dados(conexao_com_tabelas, df_estacoes, df_leituras)
    inserir_dados(conexao_com_tabelas, df_estacoes, df_leituras)
    cursor = conexao_com_tabelas.execute("SELECT COUNT(*) FROM estacoes")
    assert cursor.fetchone()[0] == 2  # não duplica


# ---------------------------------------------------------------------------
# consultar_medias_por_estacao
# ---------------------------------------------------------------------------

def test_medias_retorna_dataframe(conexao_populada):
    resultado = consultar_medias_por_estacao(conexao_populada)
    assert isinstance(resultado, pd.DataFrame)


def test_medias_retorna_uma_linha_por_estacao(conexao_populada):
    resultado = consultar_medias_por_estacao(conexao_populada)
    assert len(resultado) == 2


def test_medias_tem_coluna_nome_estacao(conexao_populada):
    resultado = consultar_medias_por_estacao(conexao_populada)
    assert "nome_estacao" in resultado.columns


def test_medias_tem_colunas_de_media(conexao_populada):
    resultado = consultar_medias_por_estacao(conexao_populada)
    assert "media_temperatura_agua" in resultado.columns
    assert "media_ph" in resultado.columns
    assert "media_oxigenio_dissolvido" in resultado.columns


def test_medias_calculo_correto(conexao_populada):
    """Rio Verde (id=1) tem temperatura_agua [20, 22] → média = 21.0."""
    resultado = consultar_medias_por_estacao(conexao_populada)
    linha = resultado[resultado["nome_estacao"] == "Rio Verde"].iloc[0]
    assert linha["media_temperatura_agua"] == pytest.approx(21.0)


def test_medias_ordenado_por_nome(conexao_populada):
    resultado = consultar_medias_por_estacao(conexao_populada)
    nomes = list(resultado["nome_estacao"])
    assert nomes == sorted(nomes)


# ---------------------------------------------------------------------------
# consultar_periodo
# ---------------------------------------------------------------------------

def test_periodo_retorna_dataframe(conexao_populada):
    resultado = consultar_periodo(conexao_populada, "2024-01-10", "2024-01-11")
    assert isinstance(resultado, pd.DataFrame)


def test_periodo_filtra_intervalo(conexao_populada):
    """Entre 10/01 e 11/01 há 3 leituras (2 da estacao 1 + 1 da estacao 2)."""
    resultado = consultar_periodo(conexao_populada, "2024-01-10", "2024-01-11")
    assert len(resultado) == 3


def test_periodo_exclui_fora_do_intervalo(conexao_populada):
    """12/01 não deve aparecer na consulta até 11/01."""
    resultado = consultar_periodo(conexao_populada, "2024-01-10", "2024-01-11")
    for data in resultado["data_hora"]:
        assert "2024-01-12" not in data


def test_periodo_vazio_fora_do_range(conexao_populada):
    resultado = consultar_periodo(conexao_populada, "2025-01-01", "2025-12-31")
    assert resultado.empty


def test_periodo_tem_coluna_nome_estacao(conexao_populada):
    resultado = consultar_periodo(conexao_populada, "2024-01-10", "2024-01-12")
    assert "nome_estacao" in resultado.columns
