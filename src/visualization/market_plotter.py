"""Módulo de visualización gráfica de series temporales financieras.

Genera gráficos de doble panel (Precio + SMA 24h arriba, Volumen abajo)
a partir de los DataFrames procesados y guarda la imagen en reports/figures/.
"""

from __future__ import annotations

import logging
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from src.config import FIGURES_DIR, PROCESSED_DATA_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class MarketPlotter:
    """Genera visualizaciones de calidad institucional para análisis de mercado."""

    @staticmethod
    def plot_price_and_volume(
        df: pd.DataFrame,
        asset_name: str = "Bitcoin (BTC/USD)",
        output_filename: str = "bitcoin_30d_analysis.png",
    ) -> Path:
        """Genera un gráfico de 2 paneles (Precio/SMA arriba y Volumen abajo).

        Args:
            df: DataFrame con DatetimeIndex y columnas: price_usd, sma_24h, volume_24h_usd.
            asset_name: Título del activo para el encabezado.
            output_filename: Nombre del archivo de imagen a guardar.

        Returns:
            Path a la imagen guardada.
        """
        logger.info(f"Generando gráfico financiero para: {asset_name}...")

        # 1. Configurar estilo visual limpio y profesional
        plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
        fig, (ax_price, ax_vol) = plt.subplots(
            nrows=2,
            ncols=1,
            figsize=(14, 8),
            sharex=True,
            gridspec_kw={"height_ratios": [3, 1]},
        )

        # -------------------------------------------------------------
        # PANEL 1 (Superior): Precio y Media Móvil de 24 Horas
        # -------------------------------------------------------------
        ax_price.plot(
            df.index,
            df["price_usd"],
            label="Precio Spot (USD)",
            color="#1f77b4",
            linewidth=1.5,
            alpha=0.9,
        )

        if "sma_24h" in df.columns:
            ax_price.plot(
                df.index,
                df["sma_24h"],
                label="Media Móvil 24h (SMA)",
                color="#ff7f0e",
                linewidth=1.8,
                linestyle="--",
            )

        ax_price.set_title(f"Proyecto Alpha – Análisis de Mercado: {asset_name} (Últimos 30 días)", fontsize=14, fontweight="bold")
        ax_price.set_ylabel("Precio en USD ($)", fontsize=11)
        ax_price.legend(loc="upper left", frameon=True)
        ax_price.grid(True, linestyle=":", alpha=0.6)

        # Formatear eje Y con separadores de miles
        ax_price.yaxis.set_major_formatter("${x:,.0f}")

        # -------------------------------------------------------------
        # PANEL 2 (Inferior): Volumen de Negociación en 24h
        # -------------------------------------------------------------
        # Usamos barras o área rellena para representar liquidez
        ax_vol.bar(
            df.index,
            df["volume_24h_usd"] / 1e9,  # Convertir a Miles de Millones (Billions)
            width=0.04,
            color="#2ca02c",
            alpha=0.6,
            label="Volumen 24h ($B USD)",
        )

        ax_vol.set_ylabel("Volumen ($B)", fontsize=11)
        ax_vol.set_xlabel("Fecha (UTC)", fontsize=11)
        ax_vol.legend(loc="upper left", frameon=True)
        ax_vol.grid(True, linestyle=":", alpha=0.6)

        # Formatear fechas en el eje X
        ax_vol.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
        ax_vol.xaxis.set_major_locator(mdates.DayLocator(interval=3))
        fig.autofmt_xdate()

        # Ajuste de márgenes
        plt.tight_layout()

        # 2. Persistencia en disco
        target_path: Path = FIGURES_DIR / output_filename
        fig.savefig(target_path, dpi=300, bbox_inches="tight")
        plt.close(fig)

        logger.info(f"Gráfico guardado exitosamente en: {target_path}")
        return target_path


if __name__ == "__main__":
    csv_file = PROCESSED_DATA_DIR / "bitcoin_30d_processed.csv"
    if not csv_file.exists():
        raise FileNotFoundError(f"No se encontró el archivo procesado {csv_file}. Ejecuta la Fase 3 primero.")

    logger.info(f"Cargando datos limpios desde: {csv_file}")
    df_data = pd.read_csv(csv_file, index_col="timestamp", parse_dates=True)

    saved_plot = MarketPlotter.plot_price_and_volume(
        df=df_data,
        asset_name="Bitcoin (BTC)",
        output_filename="bitcoin_30d_analysis.png",
    )
    print(f"\n[OK] Gráfico generado exitosamente -> {saved_plot.name}")
