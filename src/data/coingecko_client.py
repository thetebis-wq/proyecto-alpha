"""Cliente para la API REST de CoinGecko.

Maneja peticiones HTTP, autenticación mediante headers, control de errores
(incluyendo rate limiting 429) y persistencia de datos crudos (data/raw).
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from src.config import (
    COINGECKO_API_KEY,
    COINGECKO_BASE_URL,
    RAW_DATA_DIR,
    REQUEST_TIMEOUT,
)

# Configuración básica de logging para trazabilidad
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class CoinGeckoAPIError(Exception):
    """Excepción base para errores de la API de CoinGecko."""


class CoinGeckoRateLimitError(CoinGeckoAPIError):
    """Lanzada cuando se excede el límite de peticiones (HTTP 429)."""


class CoinGeckoClient:
    """Cliente HTTP desacoplado para interactuar con la API REST de CoinGecko."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = COINGECKO_BASE_URL,
        timeout: int = REQUEST_TIMEOUT,
    ) -> None:
        """Inicializa el cliente de CoinGecko con headers de seguridad opcionales."""
        self.base_url: str = base_url.rstrip("/")
        self.timeout: int = timeout
        self.session: requests.Session = requests.Session()

        # Configurar headers estándar
        self.session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": "ProyectoAlpha/1.0",
            }
        )

        # Autenticación vía Header según estándares CoinGecko Demo 2026
        # Si no hay clave, funciona en modo público sin fallar
        key_to_use: str = api_key if api_key is not None else COINGECKO_API_KEY
        if key_to_use:
            self.session.headers.update({"x-cg-demo-api-key": key_to_use})
            logger.info("Cliente CoinGecko inicializado con clave Demo en header.")
        else:
            logger.info("Cliente CoinGecko inicializado en modo público (sin clave).")

    def _request(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Ejecuta una petición GET controlada y valida códigos de estado HTTP."""
        url: str = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response: requests.Response = self.session.get(
                url=url,
                params=params,
                timeout=self.timeout,
            )

            # Manejo específico de códigos de estado críticos
            if response.status_code == 200:
                return response.json()

            if response.status_code == 429:
                logger.error("Límite de peticiones alcanzado (HTTP 429 - Rate Limit Exceeded).")
                raise CoinGeckoRateLimitError(
                    "Has superado el límite de peticiones por minuto de CoinGecko. "
                    "Espera unos segundos antes de reintentar."
                )

            if response.status_code in (401, 403):
                logger.error(f"Error de autenticación/autorización (HTTP {response.status_code}).")
                raise CoinGeckoAPIError(
                    f"Error de credenciales (HTTP {response.status_code}): "
                    "Verifica tu COINGECKO_API_KEY en el archivo .env."
                )

            # Para cualquier otro error (400, 500, etc.)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout as err:
            logger.error(f"Tiempo de espera agotado al conectar con {url}.")
            raise CoinGeckoAPIError(f"Timeout al conectar con CoinGecko: {err}") from err
        except requests.exceptions.ConnectionError as err:
            logger.error(f"Error de conexión de red al contactar {url}.")
            raise CoinGeckoAPIError(f"Error de red: {err}") from err

    def ping(self) -> bool:
        """Verifica la conectividad con el servidor de CoinGecko (/ping)."""
        logger.info("Verificando conectividad con CoinGecko (/ping)...")
        data: dict[str, Any] = self._request("ping")
        # La respuesta esperada es: {"gecko_says": "(V3) To the Moon!"}
        return "gecko_says" in data

    def get_current_price(
        self,
        coin_ids: list[str],
        vs_currencies: list[str] | None = None,
        include_24hr_change: bool = True,
        include_24hr_vol: bool = True,
    ) -> dict[str, Any]:
        """Obtiene el precio actual y métricas de 24h para uno o varios activos.

        Endpoint: GET /simple/price
        """
        if vs_currencies is None:
            vs_currencies = ["usd"]

        params: dict[str, Any] = {
            "ids": ",".join(coin_ids),
            "vs_currencies": ",".join(vs_currencies),
            "include_24hr_change": str(include_24hr_change).lower(),
            "include_24hr_vol": str(include_24hr_vol).lower(),
            "include_last_updated_at": "true",
        }

        logger.info(f"Consultando precios actuales para: {coin_ids} en {vs_currencies}")
        return self._request("simple/price", params=params)

    def get_market_chart(
        self,
        coin_id: str,
        vs_currency: str = "usd",
        days: int = 30,
        interval: str | None = None,
    ) -> dict[str, Any]:
        """Extrae serie temporal histórica (precios, market caps y volúmenes).

        Endpoint: GET /coins/{id}/market_chart
        """
        params: dict[str, Any] = {
            "vs_currency": vs_currency,
            "days": str(days),
        }
        if interval:
            params["interval"] = interval

        logger.info(f"Extrayendo datos históricos de '{coin_id}' ({days} días)...")
        return self._request(f"coins/{coin_id}/market_chart", params=params)

    def save_raw_data(self, data: dict[str, Any], filename: str) -> Path:
        """Persiste los datos crudos originales en data/raw/ sin modificarlos.

        Garantiza trazabilidad y reproducibilidad (principio cuantitativo).
        """
        timestamp_str: str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        clean_filename: str = f"{filename}_{timestamp_str}.json"
        target_path: Path = RAW_DATA_DIR / clean_filename

        with open(target_path, mode="w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Dato crudo guardado exitosamente en: {target_path}")
        return target_path


if __name__ == "__main__":
    # Prueba rápida de conectividad
    client = CoinGeckoClient()
    connected = client.ping()
    print(f"Estado de conexión con CoinGecko: {'EXITOSA' if connected else 'FALLIDA'}")
