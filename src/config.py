"""Módulo de configuración centralizada del Proyecto Alpha.

Carga de forma segura las variables de entorno y define constantes de
rutas para garantizar reproducibilidad en cualquier sistema operativo.
"""

from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

# 1. Definición de Rutas Base del Proyecto
# BASE_DIR apunta a la raíz del repositorio (dos niveles arriba de src/config.py)
BASE_DIR: Path = Path(__file__).resolve().parent.parent

DATA_DIR: Path = BASE_DIR / "data"
RAW_DATA_DIR: Path = DATA_DIR / "raw"
PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
REPORTS_DIR: Path = BASE_DIR / "reports"
FIGURES_DIR: Path = REPORTS_DIR / "figures"

# Asegurar que los directorios existan
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# 2. Carga de Variables de Entorno (.env)
ENV_PATH: Path = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# 3. Configuración de CoinGecko API
COINGECKO_API_KEY: str = os.getenv("COINGECKO_API_KEY", "").strip()
COINGECKO_BASE_URL: str = "https://api.coingecko.com/api/v3"
ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

# 4. Configuración de Telegram Bot API
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "").strip()

# Tiempo límite estándar para peticiones HTTP en segundos (buena práctica de ciberseguridad)
REQUEST_TIMEOUT: int = 10
