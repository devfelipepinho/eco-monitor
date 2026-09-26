import os
from pathlib import Path

from dotenv import load_dotenv

from src.analytics.stats import calcular_estatisticas_basicas, identificar_outliers
from src.database.sqlite_db import (
    conectar_banco,
    consultar_medias_por_estacao,
    consultar_periodo,
    criar_tabelas,
    inserir_dados,
)
from src.ingestion.load_data import anonimizar_estacoes, carregar_dados_json, tratar_leituras


def garantir_pastas() -> None:
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    Path("reports").mkdir(parents=True, exist_ok=True)


def salvar_relatorio_textual(medias_por_estacao, estatisticas, outliers) -> None:
    caminho_relatorio = Path("reports/relatorio_analitico.txt")
    with caminho_relatorio.open("w", encoding="utf-8") as arquivo:
        arquivo.write("RELATÓRIO ANALÍTICO - ECO MONITOR\n")
        arquivo.write("=" * 50 + "\n\n")
        arquivo.write("1. Médias por estação\n")
        arquivo.write(medias_por_estacao.to_string(index=False))
        arquivo.write("\n\n2. Estatísticas básicas\n")
        arquivo.write(estatisticas.to_string(index=False))
        arquivo.write("\n\n3. Outliers em condutividade\n")
        if outliers.empty:
            arquivo.write("Nenhum outlier encontrado.\n")
        else:
            arquivo.write(outliers.to_string(index=False))
            arquivo.write("\n")


def run_pipeline() -> None:
    load_dotenv()
    garantir_pastas()

    caminho_json = os.getenv("CAMINHO_JSON", "data/raw/dados_monitoramento.json")
    caminho_banco = os.getenv("CAMINHO_BANCO", "eco_monitor.db")

    df_estacoes, df_leituras = carregar_dados_json(caminho_json)
    df_estacoes = anonimizar_estacoes(df_estacoes)
    df_leituras = tratar_leituras(df_leituras)

    df_estacoes.to_csv("data/processed/estacoes_tratadas.csv", index=False)
    df_leituras.to_csv("data/processed/leituras_tratadas.csv", index=False)

    conexao = conectar_banco(caminho_banco)
    try:
        criar_tabelas(conexao)
        inserir_dados(conexao, df_estacoes, df_leituras)

        medias_por_estacao = consultar_medias_por_estacao(conexao)
        leituras_periodo = consultar_periodo(conexao, "2026-01-01", "2026-01-02")
        estatisticas = calcular_estatisticas_basicas(leituras_periodo)
        outliers = identificar_outliers(leituras_periodo, "condutividade")

        print("\nMÉDIAS POR ESTAÇÃO")
        print(medias_por_estacao.to_string(index=False))
        print("\nESTATÍSTICAS BÁSICAS")
        print(estatisticas.to_string(index=False))
        print("\nOUTLIERS DE CONDUTIVIDADE")
        print(outliers.to_string(index=False))

        salvar_relatorio_textual(medias_por_estacao, estatisticas, outliers)
    finally:
        conexao.close()


if __name__ == "__main__":
    run_pipeline()
