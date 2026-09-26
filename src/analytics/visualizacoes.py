import unicodedata
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import pandas as pd

from src.analytics.stats import identificar_outliers


PARAMETROS_GRAFICOS = [
    ("temperatura_agua", "Temperatura da Água (°C)"),
    ("ph", "pH"),
    ("oxigenio_dissolvido", "Oxigênio Dissolvido (mg/L)"),
    ("condutividade", "Condutividade (μS/cm)"),
]

# Paleta neutra e legível
COR_LEITURA = "#2c7bb6"
COR_MEDIA = "#d7191c"
COR_BANDA = "#fdae61"
COR_OUTLIER = "#d7191c"
COR_FUNDO_SUBPLOT = "#f9f9f9"


def _slugify(texto: str) -> str:
    """Remove acentos e restringe a letras, dígitos, _ e - para uso seguro em nomes de arquivo."""
    normalizado = unicodedata.normalize("NFD", texto.lower())
    sem_acento = "".join(c for c in normalizado if unicodedata.category(c) != "Mn")
    sem_acento = sem_acento.replace(" ", "_")
    return "".join(c for c in sem_acento if c.isalnum() or c in ("_", "-"))


def gerar_graficos_por_estacao(df_leituras: pd.DataFrame, pasta_saida: str = "reports") -> None:
    Path(pasta_saida).mkdir(parents=True, exist_ok=True)
    estacoes = df_leituras["nome_estacao"].unique()

    for estacao in estacoes:
        df_est = df_leituras[df_leituras["nome_estacao"] == estacao].copy()
        df_est["data_hora"] = pd.to_datetime(df_est["data_hora"])
        df_est = df_est.sort_values("data_hora").reset_index(drop=True)

        n = len(PARAMETROS_GRAFICOS)
        fig, eixos = plt.subplots(
            n, 1,
            figsize=(13, 3.5 * n),
            sharex=True,
            facecolor="white"
        )

        fig.suptitle(
            f"Monitoramento Ambiental — {estacao}",
            fontsize=14,
            fontweight="bold",
            color="#222222",
            y=1.01
        )

        for i, (coluna, rotulo) in enumerate(PARAMETROS_GRAFICOS):
            ax = eixos[i]
            ax.set_facecolor(COR_FUNDO_SUBPLOT)

            serie = df_est[coluna].dropna()
            datas = df_est.loc[serie.index, "data_hora"]

            media_movel = serie.rolling(window=3, min_periods=1).mean()
            desvio = serie.rolling(window=3, min_periods=1).std(ddof=1).fillna(0)

            # Banda de desvio
            ax.fill_between(
                datas,
                media_movel - desvio,
                media_movel + desvio,
                alpha=0.25,
                color=COR_BANDA,
                label="± 1σ (desvio padrão)",
                zorder=1
            )

            # Linha de leituras
            ax.plot(
                datas, serie,
                marker="o", markersize=4, linewidth=1.4,
                color=COR_LEITURA,
                label="Leitura",
                zorder=2
            )

            # Média móvel
            ax.plot(
                datas, media_movel,
                linewidth=1.8,
                color=COR_MEDIA,
                linestyle="--",
                label="Média móvel (3 pts)",
                zorder=3
            )

            # Marcação de outliers
            df_outliers = identificar_outliers(df_est, coluna)
            if not df_outliers.empty:
                datas_out = pd.to_datetime(df_outliers["data_hora"])
                valores_out = df_outliers[coluna]
                ax.scatter(
                    datas_out, valores_out,
                    color=COR_OUTLIER,
                    s=80, zorder=5,
                    marker="^",
                    label="Outlier"
                )
                for dt, vl in zip(datas_out, valores_out):
                    ax.annotate(
                        f" {vl:.1f}",
                        xy=(dt, vl),
                        fontsize=7.5,
                        color=COR_OUTLIER,
                        va="bottom"
                    )

            ax.set_ylabel(rotulo, fontsize=9, color="#333333")
            ax.tick_params(axis="y", labelsize=8, colors="#555555")
            ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins=5, prune="both"))
            ax.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.5, color="#cccccc")
            ax.grid(axis="x", linestyle=":", linewidth=0.4, alpha=0.4, color="#cccccc")
            ax.spines[["top", "right"]].set_visible(False)
            ax.spines[["left", "bottom"]].set_color("#dddddd")

            leg = ax.legend(
                fontsize=7.5,
                loc="upper right",
                framealpha=0.85,
                edgecolor="#dddddd"
            )
            leg.get_frame().set_linewidth(0.5)

        eixos[-1].xaxis.set_major_formatter(mdates.DateFormatter("%d/%m\n%Hh"))
        eixos[-1].tick_params(axis="x", labelsize=8, colors="#555555")

        fig.text(
            0.5, -0.01,
            "Período de monitoramento",
            ha="center",
            fontsize=9,
            color="#666666"
        )

        plt.tight_layout()

        nome_arquivo = _slugify(estacao)
        caminho = Path(pasta_saida) / f"grafico_{nome_arquivo}.png"
        fig.savefig(caminho, dpi=130, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        print(f"  Gráfico salvo: {caminho}")
