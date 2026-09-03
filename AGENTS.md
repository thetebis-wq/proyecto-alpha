# Directrices de Desarrollo para Proyecto Alpha – El Pulso del Mercado

Este documento define las reglas de arquitectura, estándares cuantitativos y restricciones operativas que deben regir todas las intervenciones de código en este repositorio.

---

## 🏛️ 1. Arquitectura y Separación de Responsabilidades

El proyecto desacopla estrictamente cada etapa del ciclo de vida de los datos:

1. **Ingestión / Extracción (`src/data/`)**:
   - Acceso exclusivo a APIs externas (CoinGecko REST API).
   - Manejo obligatorio de headers, timeouts y límites de cuota (HTTP 429).
   - Persistencia inmutable en `data/raw/` con marcas de tiempo UTC en formato JSON.
   - **Regla de Oro**: Jamás transformar ni modificar los archivos generados en `data/raw/`.

2. **Transformación y Análisis Cuantitativo (`src/processing/`)**:
   - Limpieza y conversión a DataFrames (`pandas`).
   - Normalización de marcas temporales a DatetimeIndex con zona horaria UTC.
   - Cálculo de métricas e indicadores técnicos (SMA, EMA, RSI, Bandas de Bollinger, MACD).
   - Persistencia de series procesadas en `data/processed/` en formato CSV.

3. **Estrategias Algorítmicas (`src/strategies/`)**:
   - Generación de señales discretas vectorizadas (`signal`: 1 = Compra, -1 = Venta/Cierre, 0 = Neutral).
   - Prohibido el *lookahead bias* (no utilizar información de velas futuras para señales pasadas).

4. **Motor de Backtesting (`src/backtesting/`)**:
   - Simulación de órdenes con fricción financiera realista: comisiones de exchange (`fee_rate`), slippage, stop-loss y take-profit.
   - Cálculo de métricas de desempeño: Sharpe Ratio, Sortino Ratio, Drawdown Máximo y Tasa de Aciertos (*Win Rate*).

5. **Visualización (`src/visualization/`)**:
   - Gráficos estáticos de alta definición para reportes institucionales (`matplotlib`).
   - Gráficos interactivos responsivos multieje para la terminal interactiva (`plotly`).

6. **Vigilante Autónomo y Alertas (`src/alerts/`)**:
   - Monitoreo desatendido 24/7 en segundo plano.
   - Despacho de notificaciones estructuradas con formato HTML a la API de Telegram Bot.
   - Memoria de estados anti-spam para evitar duplicación de alertas en la misma señal.

---

## 🛡️ 2. Seguridad y Gestión de Credenciales

- **Sin credenciales en código**: Jamás colocar tokens de Telegram o API Keys de CoinGecko directamente en el código fuente.
- **Acceso centralizado**: Toda variable de entorno debe leerse exclusivamente a través de `src/config.py`.
- **Protección Git**: Asegurar que `.env`, `.venv/` y los contenidos de `data/` permanezcan permanentemente ignorados en `.gitignore`.

---

## 💻 3. Estándares de Código Python

- **Tipado Estricto**: Todo nuevo módulo debe comenzar con `from __future__ import annotations` e incluir *type hints* en todas las funciones y clases.
- **Rutas Agnósticas al SO**: Usar siempre `pathlib.Path` referenciado a `src.config.BASE_DIR`. Evitar concatenación manual de cadenas para rutas.
- **Manejo de Excepciones**: No usar bloques `except Exception: pass`. Registrar siempre el error con el logger adecuado (`logging.getLogger(...)`).
- **Resiliencia de Red**: Toda petición HTTP (`requests`) debe especificar el parámetro `timeout=REQUEST_TIMEOUT` definido en `src/config.py`.
