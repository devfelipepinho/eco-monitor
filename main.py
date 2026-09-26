import os
import shutil
from pathlib import Path

from dotenv import load_dotenv

from src.analytics.stats import calcular_estatisticas_basicas, identificar_outliers
from src.analytics.visualizacoes import gerar_graficos_por_estacao
from src.database.sqlite_db import (
    conectar_banco,
    consultar_medias_por_estacao,
    consultar_periodo,
    criar_tabelas,
    inserir_dados,
)
from src.ingestion.load_data import anonimizar_estacoes, carregar_dados_json, tratar_leituras


def limpar_execucao_anterior(caminho_banco: str) -> None:
    """Remove banco e relatórios da execução anterior antes de gerar novos."""
    banco = Path(caminho_banco)
    if banco.exists():
        banco.unlink()

    pasta_reports = Path("reports")
    if pasta_reports.exists():
        shutil.rmtree(pasta_reports)


def garantir_pastas() -> None:
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    Path("reports").mkdir(parents=True, exist_ok=True)


def salvar_relatorio_textual(medias_por_estacao, estatisticas, outliers_por_parametro) -> None:
    caminho_relatorio = Path("reports/relatorio_analitico.txt")
    with caminho_relatorio.open("w", encoding="utf-8") as arquivo:
        arquivo.write("RELATÓRIO ANALÍTICO - ECO MONITOR\n")
        arquivo.write("=" * 50 + "\n\n")

        arquivo.write("1. Médias por estação\n")
        arquivo.write("-" * 50 + "\n")
        arquivo.write(medias_por_estacao.to_string(index=False))
        arquivo.write("\n\n")

        arquivo.write("2. Estatísticas básicas (todos os parâmetros)\n")
        arquivo.write("-" * 50 + "\n")
        arquivo.write(estatisticas.to_string(index=False))
        arquivo.write("\n\n")

        arquivo.write("3. Outliers por parâmetro\n")
        arquivo.write("-" * 50 + "\n")
        for parametro, df_outliers in outliers_por_parametro.items():
            arquivo.write(f"\nParâmetro: {parametro}\n")
            if df_outliers.empty:
                arquivo.write("  Nenhum outlier encontrado.\n")
            else:
                colunas = ["id_leitura", "nome_estacao", "data_hora", parametro]
                arquivo.write(df_outliers[colunas].to_string(index=False))
                arquivo.write("\n")


def run_pipeline() -> None:
    load_dotenv()

    caminho_json = os.getenv("CAMINHO_JSON", "data/raw/dados_monitoramento.json")
    caminho_banco = os.getenv("CAMINHO_BANCO", "eco_monitor.db")
    data_inicial = os.getenv("DATA_INICIAL", "2026-01-01")
    data_final = os.getenv("DATA_FINAL", "2026-01-08")

    print("[1/6] Limpando execução anterior...")
    limpar_execucao_anterior(caminho_banco)
    garantir_pastas()

    print("[2/6] Carregando e tratando dados...")
    df_estacoes, df_leituras = carregar_dados_json(caminho_json)
    df_estacoes = anonimizar_estacoes(df_estacoes)
    df_leituras = tratar_leituras(df_leituras)

    df_estacoes.to_csv("data/processed/estacoes_tratadas.csv", index=False)
    df_leituras.to_csv("data/processed/leituras_tratadas.csv", index=False)

    print("[3/6] Persistindo no banco de dados...")
    conexao = conectar_banco(caminho_banco)
    try:
        criar_tabelas(conexao)
        inserir_dados(conexao, df_estacoes, df_leituras)

        print("[4/6] Consultando e calculando estatísticas...")
        medias_por_estacao = consultar_medias_por_estacao(conexao)
        leituras_periodo = consultar_periodo(conexao, data_inicial, data_final)

        estatisticas = calcular_estatisticas_basicas(leituras_periodo)

        parametros_outlier = [
            "temperatura_agua", "ph", "oxigenio_dissolvido", "condutividade"
        ]
        outliers_por_parametro = {
            p: identificar_outliers(leituras_periodo, p) for p in parametros_outlier
        }

        print("[5/6] Gerando relatório textual...")
        salvar_relatorio_textual(medias_por_estacao, estatisticas, outliers_por_parametro)

        print("[6/6] Gerando gráficos...")
        gerar_graficos_por_estacao(leituras_periodo, pasta_saida="reports")

        print("\n" + "=" * 50)
        print("MÉDIAS POR ESTAÇÃO")
        print(medias_por_estacao.to_string(index=False))
        print("\nESTATÍSTICAS BÁSICAS")
        print(estatisticas.to_string(index=False))
        print("\nOUTLIERS ENCONTRADOS")
        for parametro, df_outliers in outliers_por_parametro.items():
            total = len(df_outliers)
            if total > 0:
                print(f"  {parametro}: {total} outlier(s)")
        print("=" * 50)
        print("\nRelatório salvo em: reports/relatorio_analitico.txt")
        print("Gráficos salvos em: reports/grafico_*.png")
    finally:
        conexao.close()


if __name__ == "__main__":
    run_pipeline()
