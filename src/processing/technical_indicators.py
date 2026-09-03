"""Módulo de cálculo de indicadores técnicos cuantitativos.

Proporciona cálculos vectorizados de alto rendimiento con pandas para:
- RSI (Relative Strength Index) con suavizado exponencial tipo Wilder.
- Bandas de Bollinger (media móvil central +/- n desviaciones estándar).
- MACD (Moving Average Convergence Divergence) y su histograma.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


class TechnicalIndicators:
    """Calcula indicadores técnicos de momentum y volatilidad sobre series de precios."""

    @staticmethod
    def add_rsi(
        df: pd.DataFrame,
        price_col: str = "price_usd",
        period: int = 14,
    ) -> pd.DataFrame:
        """Calcula el Índice de Fuerza Relativa (RSI) y añade la columna 'rsi'.

        RSI = 100 - (100 / (1 + RS))
        Donde RS = Ganancia Promedio / Pérdida Promedio (usando suavizado Wilder / EWM).
        """
        df_out = df.copy()
        delta = df_out[price_col].diff()

        # Separar ganancias y pérdidas
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        # Suavizado exponencial estándar (Wilder: alpha = 1 / period)
        avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()

        # Evitar división por cero
        rs = avg_gain / avg_loss.replace(0, np.nan)
        df_out["rsi"] = 100.0 - (100.0 / (1.0 + rs))

        # En caso de que avg_loss sea 0, RSI es 100
        df_out.loc[avg_loss == 0, "rsi"] = 100.0
        return df_out

    @staticmethod
    def add_bollinger_bands(
        df: pd.DataFrame,
        price_col: str = "price_usd",
        period: int = 20,
        num_std: float = 2.0,
    ) -> pd.DataFrame:
        """Calcula las Bandas de Bollinger y añade 'bb_middle', 'bb_upper', 'bb_lower'.

        - Banda Central = SMA(period)
        - Banda Superior = Central + (num_std * Desviación Estándar)
        - Banda Inferior = Central - (num_std * Desviación Estándar)
        """
        df_out = df.copy()
        middle = df_out[price_col].rolling(window=period).mean()
        std = df_out[price_col].rolling(window=period).std()

        df_out["bb_middle"] = middle
        df_out["bb_upper"] = middle + (num_std * std)
        df_out["bb_lower"] = middle - (num_std * std)
        df_out["bb_bandwidth"] = (df_out["bb_upper"] - df_out["bb_lower"]) / middle
        return df_out

    @staticmethod
    def add_macd(
        df: pd.DataFrame,
        price_col: str = "price_usd",
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ) -> pd.DataFrame:
        """Calcula el MACD y añade 'macd_line', 'macd_signal', 'macd_hist'.

        - Línea MACD = EMA(fast) - EMA(slow)
        - Línea Señal = EMA(signal) de Línea MACD
        - Histograma = Línea MACD - Línea Señal
        """
        df_out = df.copy()
        ema_fast = df_out[price_col].ewm(span=fast_period, adjust=False).mean()
        ema_slow = df_out[price_col].ewm(span=slow_period, adjust=False).mean()

        macd_line = ema_fast - ema_slow
        macd_signal = macd_line.ewm(span=signal_period, adjust=False).mean()
        macd_hist = macd_line - macd_signal

        df_out["macd_line"] = macd_line
        df_out["macd_signal"] = macd_signal
        df_out["macd_hist"] = macd_hist
        return df_out

    @classmethod
    def add_all_indicators(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica todos los indicadores técnicos estándar al DataFrame."""
        df_out = cls.add_rsi(df)
        df_out = cls.add_bollinger_bands(df_out)
        df_out = cls.add_macd(df_out)
        return df_out
