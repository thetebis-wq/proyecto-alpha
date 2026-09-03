"""Script ejecutable para descargar y respaldar datos de mercado crudos.

Extrae precios actuales y la serie temporal de 30 días de Bitcoin,
guardando la respuesta original en data/raw/ para alimentar la Fase 3.
"""

from __future__ import annotations

import pprint
from typing import Any

from src.data.coingecko_client import CoinGeckoClient


def main() -> None:
    print("=" * 60)
    print("PROYECTO ALPHA: EXTRACCIÓN DE DATOS DE MERCADO")
    print("=" * 60)

    client = CoinGeckoClient()

    # 1. Comprobación de salud de la API
    if not client.ping():
        print("[ERROR] No se pudo establecer conexión con CoinGecko.")
        return
    print("[OK] Conexión establecida exitosamente.")

    # 2. Extracción de Precios Actuales
    print("\n--- 1. Consultando Precios en Tiempo Real ---")
    current_prices: dict[str, Any] = client.get_current_price(
        coin_ids=["bitcoin", "ethereum"],
        vs_currencies=["usd"],
    )
    pprint.pprint(current_prices)

    # 3. Extracción de Serie Temporal Histórica (30 días de Bitcoin)
    print("\n--- 2. Extrayendo Serie Histórica de 30 días (Bitcoin) ---")
    market_data: dict[str, Any] = client.get_market_chart(
        coin_id="bitcoin",
        vs_currency="usd",
        days=30,
    )

    total_puntos_precio: int = len(market_data.get("prices", []))
    print(f"[OK] Se recibieron {total_puntos_precio} puntos temporales de precios.")

    # 4. Guardado en Capa Raw (Materia Prima intacta)
    print("\n--- 3. Guardando Datos Crudos en data/raw/ ---")
    raw_path = client.save_raw_data(market_data, filename="bitcoin_30d")
    print(f"[OK] Archivo de respaldo creado en: {raw_path.name}")
    print("=" * 60)
    print("Extracción completada. Datos listos para la Fase 3 (pandas).")


if __name__ == "__main__":
    main()
