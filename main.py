"""Pipeline principal del Proyecto Alpha – El Pulso del Mercado.

Orquesta el ciclo completo de datos cuantitativos de forma desacoplada:
1. Extracción (CoinGecko REST API -> data/raw/)
2. Transformación (Limpieza y métricas con pandas -> data/processed/)
3. Visualización (Gráficos analíticos con matplotlib -> reports/figures/)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pandas as pd

from src.data.coingecko_client import (
    CoinGeckoAPIError,
    CoinGeckoClient,
    CoinGeckoRateLimitError,
)
from src.processing.market_transformer import MarketDataTransformer
from src.visualization.market_plotter import MarketPlotter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("ProyectoAlpha")


def run_alpha_pipeline(coin_id: str = "bitcoin", days: int = 30) -> None:
    """Ejecuta el pipeline completo de ingeniería de datos financieros."""
    print("\n" + "=" * 65)
    print(f"   PROYECTO ALPHA: PIPELINE CUANTITATIVO [{coin_id.upper()}]")
    print("=" * 65)

    # -------------------------------------------------------------
    # FASE 2: Capa de Extracción
    # -------------------------------------------------------------
    logger.info(">>> PASO 1: Ingestión de datos desde CoinGecko...")
    client = CoinGeckoClient()

    if not client.ping():
        logger.error("No hay conectividad con la API de CoinGecko. Abortando pipeline.")
        return

    try:
        raw_data: dict[str, Any] = client.get_market_chart(coin_id=coin_id, vs_currency="usd", days=days)
        raw_path: Path = client.save_raw_data(raw_data, filename=f"{coin_id}_{days}d")
        print(f"[OK] Extracción finalizada. Datos crudos: {raw_path.name}")
    except CoinGeckoRateLimitError as err:
        logger.warning(f"Límite de API alcanzado: {err}")
        print("\n[AVISO] Se alcanzó el límite temporal de peticiones por minuto de CoinGecko.")
        print("Espera unos instantes o añade tu COINGECKO_API_KEY a .env para mayor cuota.\n")
        return
    except CoinGeckoAPIError as err:
        logger.error(f"Error de API CoinGecko: {err}")
        return

    # -------------------------------------------------------------
    # FASE 3: Capa de Transformación (pandas)
    # -------------------------------------------------------------
    logger.info(">>> PASO 2: Transformación y cálculo de indicadores...")
    processed_filename: str = f"{coin_id}_{days}d_processed.csv"
    csv_path: Path = MarketDataTransformer.process_raw_file(
        raw_filepath=raw_path,
        output_filename=processed_filename,
    )
    print(f"[OK] Transformación finalizada. Dataset procesado: {csv_path.name}")

    # -------------------------------------------------------------
    # FASE 4: Capa de Visualización (matplotlib)
    # -------------------------------------------------------------
    logger.info(">>> PASO 3: Generación de gráfico financiero institucional...")
    df_processed: pd.DataFrame = pd.read_csv(csv_path, index_col="timestamp", parse_dates=True)
    figure_filename: str = f"{coin_id}_{days}d_analysis.png"
    fig_path: Path = MarketPlotter.plot_price_and_volume(
        df=df_processed,
        asset_name=f"{coin_id.capitalize()} ({coin_id.upper()}/USD)",
        output_filename=figure_filename,
    )
    print(f"[OK] Visualización finalizada. Gráfico guardado en: {fig_path.name}")

    print("=" * 65)
    print("PIPELINE COMPLETADO EXITOSAMENTE.")
    print(f"Gráfico disponible en: reports/figures/{figure_filename}")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    run_alpha_pipeline(coin_id="bitcoin", days=30)
