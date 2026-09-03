---
name: crypto-market-pipeline
description: Procedimientos para extracción, persistencia inmutable y transformación cuantitativa de datos de mercado con CoinGecko y pandas en Proyecto Alpha. Activar cuando se modifique o extienda la ingesta de criptomonedas, manejo de límites de tasa (429) o cálculo de indicadores técnicos.
---

# Crypto Market Pipeline (Proyecto Alpha)

Esta skill proporciona las directrices y procedimientos para operar el pipeline de datos de mercado en Proyecto Alpha.

## Componentes del Pipeline

1. **Cliente API (`src/data/coingecko_client.py`)**:
   - Conexión con CoinGecko REST API v3.
   - Autenticación segura mediante cabecera `x-cg-demo-api-key` (si existe) o modo público.
   - Manejo de límite de cuota (HTTP 429) con retroceso exponencial.
   - Endpoint spot: `/simple/price`.
   - Endpoint histórico: `/coins/{id}/market_chart`.

2. **Persistencia Cruda (`data/raw/`)**:
   - Método `save_raw_data(data, filename)`.
   - Formato inmutable: JSON indentado con timestamp UTC (`YYYYMMDD_HHMMSS`).
   - Los datos crudos jamás deben sobreescribirse ni alterarse.

3. **Transformador Cuantitativo (`src/processing/market_transformer.py`)**:
   - `json_to_dataframe(raw_data)`:
     - Convierte arrays de pares `[timestamp_ms, valor]` a DataFrame.
     - Aplica DatetimeIndex en UTC: `pd.to_datetime(ts, unit='ms', utc=True)`.
     - Normaliza columnas: `price_usd`, `market_cap_usd`, `volume_24h_usd`.
   - `calculate_returns(df)`:
     - Retornos porcentuales: `pct_change()`.
     - Retornos logarítmicos: `np.log(price / price.shift(1))`.

4. **Indicadores Técnicos (`src/processing/technical_indicators.py`)**:
   - SMA (Simple Moving Average) y EMA (Exponential Moving Average).
   - Bandas de Bollinger (`bb_upper`, `bb_middle`, `bb_lower`).
   - RSI (Relative Strength Index) con suavizado de Wilder o estándar de 14 períodos.
   - MACD (Moving Average Convergence Divergence) con línea de señal e histograma.

## Verificación Rápida de Ingesta

Para probar la conectividad y flujo de extracción sin levantar toda la suite:

```powershell
.\.venv\Scripts\python.exe -c "from src.data.coingecko_client import CoinGeckoClient; c = CoinGeckoClient(); print('Ping:', c.ping())"
```
