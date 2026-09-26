import unicodedata
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd


PARAMETROS_GRAFICOS = [
    ("temperatura_agua", "Temperatura da Água (°C)"),
    ("ph", "pH"),
    ("oxigenio_dissolvido", "Oxigênio Dissolvido (mg/L)"),
    ("condutividade", "Condutividade (μS/cm)"),
]


def gerar_graficos_por_estacao(df_leituras: pd.DataFrame, pasta_saida: str = "reports") -> None:
    Path(pasta_saida).mkdir(parents=True, exist_ok=True)
    estacoes = df_leituras["nome_estacao"].unique()

    for estacao in estacoes:
        df_estacao = df_leituras[df_leituras["nome_estacao"] == estacao].copy()
        df_estacao["data_hora"] = pd.to_datetime(df_estacao["data_hora"])
        df_estacao = df_estacao.sort_values("data_hora")

        fig, eixos = plt.subplots(len(PARAMETROS_GRAFICOS), 1, figsize=(12, 10), sharex=True)
        fig.suptitle(f"Monitoramento — {estacao}", fontsize=13, fontweight="bold", y=1.01)

        for i, (coluna, rotulo) in enumerate(PARAMETROS_GRAFICOS):
            serie = df_estacao[coluna].dropna()
            datas = df_estacao.loc[serie.index, "data_hora"]

            media_movel = serie.rolling(window=3, min_periods=1).mean()
            desvio = serie.rolling(window=3, min_periods=1).std(ddof=1).fillna(0)

            eixos[i].plot(datas, serie, marker="o", markersize=3, linewidth=1.2,
                         color="steelblue", label="Leitura")
            eixos[i].plot(datas, media_movel, linewidth=1.5, color="darkorange",
                         linestyle="--", label="Média móvel (3 pts)")
            eixos[i].fill_between(
                datas,
                media_movel - desvio,
                media_movel + desvio,
                alpha=0.2,
                color="darkorange",
                label="± 1σ"
            )
            eixos[i].set_ylabel(rotulo, fontsize=9)
            eixos[i].legend(fontsize=7, loc="upper right")
            eixos[i].grid(True, linestyle="--", alpha=0.4)
            eixos[i].tick_params(axis="y", labelsize=8)

        eixos[-1].xaxis.set_major_formatter(mdates.DateFormatter("%d/%m %Hh"))
        eixos[-1].tick_params(axis="x", labelsize=7, rotation=30)

        plt.tight_layout()

        nome_arquivo = unicodedata.normalize("NFD", estacao.lower())
        nome_arquivo = "".join(c for c in nome_arquivo if unicodedata.category(c) != "Mn")
        nome_arquivo = nome_arquivo.replace(" ", "_")
        caminho = Path(pasta_saida) / f"grafico_{nome_arquivo}.png"
        fig.savefig(caminho, dpi=120, bbox_inches="tight")
        plt.close(fig)
        print(f"  Gráfico salvo: {caminho}")
