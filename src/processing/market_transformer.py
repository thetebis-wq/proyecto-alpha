"""Módulo de procesamiento y transformación de datos de mercado.

Convierte datos crudos de CoinGecko (JSON) en DataFrames de pandas limpios,
calcula métricas cuantitativas básicas (retornos, medias móviles) y
persiste los resultados en formato tabular (CSV).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import PROCESSED_DATA_DIR, RAW_DATA_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class MarketDataTransformer:
    """Transforma datos crudos de series temporales en estructuras analíticas."""

    @staticmethod
    def json_to_dataframe(raw_data: dict[str, Any]) -> pd.DataFrame:
        """Convierte la estructura de CoinGecko market_chart en un DataFrame indexado por fecha.

        Args:
            raw_data: Diccionario crudo con listas 'prices', 'market_caps' y 'total_volumes'.

        Returns:
            pd.DataFrame limpio con DatetimeIndex en UTC y columnas numéricas.
        """
        logger.info("Transformando listas crudas en DataFrame...")

        # 1. Validar que las claves requeridas existan
        for key in ("prices", "market_caps", "total_volumes"):
            if key not in raw_data:
                raise ValueError(f"El diccionario crudo no contiene la clave obligatoria '{key}'.")

        # 2. Convertir listas [timestamp, valor] a DataFrames individuales
        df_prices = pd.DataFrame(raw_data["prices"], columns=["timestamp", "price_usd"])
        df_market_caps = pd.DataFrame(raw_data["market_caps"], columns=["timestamp", "market_cap_usd"])
        df_volumes = pd.DataFrame(raw_data["total_volumes"], columns=["timestamp", "volume_24h_usd"])

        # 3. Fusionar sobre la columna timestamp
        df_merged = df_prices.merge(df_market_caps, on="timestamp").merge(df_volumes, on="timestamp")

        # 4. Normalizar timestamps UNIX (milisegundos) a DatetimeIndex en UTC
        df_merged["timestamp"] = pd.to_datetime(df_merged["timestamp"], unit="ms", utc=True)
        df_merged.set_index("timestamp", inplace=True)
        df_merged.sort_index(inplace=True)

        # 5. Cálculos cuantitativos básicos
        # Retorno simple del período: (Precio_t / Precio_t-1) - 1
        df_merged["return_pct"] = df_merged["price_usd"].pct_change()

        # Media Móvil Simple de 24 horas (SMA - Simple Moving Average)
        df_merged["sma_24h"] = df_merged["price_usd"].rolling(window=24).mean()

        logger.info(f"DataFrame generado con éxito. Dimensiones: {df_merged.shape}")
        return df_merged

    @classmethod
    def process_raw_file(cls, raw_filepath: Path, output_filename: str) -> Path:
        """Lee un archivo JSON crudo, lo procesa y guarda el resultado en data/processed/.

        Args:
            raw_filepath: Ruta del archivo JSON crudo.
            output_filename: Nombre base del archivo CSV procesado.

        Returns:
            Path del archivo CSV generado.
        """
        logger.info(f"Leyendo archivo crudo: {raw_filepath}")
        with open(raw_filepath, mode="r", encoding="utf-8") as f:
            raw_data: dict[str, Any] = json.load(f)

        df_processed: pd.DataFrame = cls.json_to_dataframe(raw_data)

        # Guardar en CSV
        if not output_filename.endswith(".csv"):
            output_filename = f"{output_filename}.csv"

        target_path: Path = PROCESSED_DATA_DIR / output_filename
        df_processed.to_csv(target_path, index=True)

        logger.info(f"Datos limpios guardados en: {target_path}")
        return target_path


def get_latest_raw_file(prefix: str = "bitcoin_30d") -> Path:
    """Busca el archivo JSON crudo más reciente con el prefijo especificado."""
    matching_files = list(RAW_DATA_DIR.glob(f"{prefix}_*.json"))
    if not matching_files:
        raise FileNotFoundError(f"No se encontraron archivos crudos con prefijo '{prefix}' en {RAW_DATA_DIR}")
    # Ordenar por fecha de modificación (el más reciente al final)
    matching_files.sort(key=lambda p: p.stat().st_mtime)
    return matching_files[-1]


if __name__ == "__main__":
    latest_file = get_latest_raw_file("bitcoin_30d")
    out_file = MarketDataTransformer.process_raw_file(
        raw_filepath=latest_file,
        output_filename="bitcoin_30d_processed.csv",
    )
    print(f"\n[OK] Transformación completada exitosamente -> {out_file.name}")
