"""Módulo de generación de señales cuantitativas de trading.

Implementa estrategias algorítmicas basadas en reglas:
1. Cruce de Medias Móviles (SMA Fast vs SMA Slow).
2. Reversión a la Media con Bandas de Bollinger y RSI.

Devuelve columnas estandarizadas:
- 'position': 1 (Comprado / Long) o 0 (En liquidez / Flat).
- 'signal': +1 (Orden de Compra), -1 (Orden de Venta), 0 (Mantener).
"""

from __future__ import annotations

from typing import Any
import numpy as np
import pandas as pd

from src.processing.technical_indicators import TechnicalIndicators


class SignalGenerator:
    """Generador de señales algorítmicas y estados de posición."""

    @staticmethod
    def sma_crossover(
        df: pd.DataFrame,
        fast_period: int = 12,
        slow_period: int = 24,
        price_col: str = "price_usd",
    ) -> pd.DataFrame:
        """Estrategia de cruce de medias móviles.

        - Posición 1 cuando SMA(fast) > SMA(slow)
        - Posición 0 cuando SMA(fast) <= SMA(slow)
        """
        df_out = df.copy()
        df_out["sma_fast"] = df_out[price_col].rolling(window=fast_period).mean()
        df_out["sma_slow"] = df_out[price_col].rolling(window=slow_period).mean()

        # Condición de compra: Fast > Slow
        df_out["position"] = np.where(df_out["sma_fast"] > df_out["sma_slow"], 1, 0)

        # Señales de cambio de posición: +1 = Compra, -1 = Venta, 0 = Sin cambio
        df_out["signal"] = df_out["position"].diff().fillna(0).astype(int)
        return df_out

    @staticmethod
    def mean_reversion_bollinger_rsi(
        df: pd.DataFrame,
        bb_period: int = 20,
        rsi_period: int = 14,
        rsi_oversold: float = 35.0,
        rsi_overbought: float = 65.0,
        price_col: str = "price_usd",
    ) -> pd.DataFrame:
        """Estrategia de reversión a la media con Bandas de Bollinger y RSI.

        - Compra cuando el precio cae por debajo de la Banda Inferior y RSI < oversold.
        - Venta/Salida cuando el precio rebota por encima de la Banda Central o RSI > overbought.
        """
        df_out = TechnicalIndicators.add_bollinger_bands(df, price_col=price_col, period=bb_period)
        df_out = TechnicalIndicators.add_rsi(df_out, price_col=price_col, period=rsi_period)

        positions = np.zeros(len(df_out), dtype=int)
        current_pos = 0

        # Simulación de estados de posición
        prices = df_out[price_col].to_numpy()
        bb_lower = df_out["bb_lower"].to_numpy()
        bb_middle = df_out["bb_middle"].to_numpy()
        rsi = df_out["rsi"].to_numpy()

        for i in range(len(df_out)):
            # Esperar a que los indicadores tengan datos válidos
            if np.isnan(bb_lower[i]) or np.isnan(rsi[i]):
                positions[i] = 0
                continue

            # Condición de Entrada (Sobreventa extrema)
            if current_pos == 0 and (prices[i] <= bb_lower[i] and rsi[i] <= rsi_oversold):
                current_pos = 1
            # Condición de Salida (Reversión a la media lograda)
            elif current_pos == 1 and (prices[i] >= bb_middle[i] or rsi[i] >= rsi_overbought):
                current_pos = 0

            positions[i] = current_pos

        df_out["position"] = positions
        df_out["signal"] = df_out["position"].diff().fillna(0).astype(int)
        return df_out

    @classmethod
    def apply_strategy(
        cls,
        df: pd.DataFrame,
        strategy_name: str,
        params: dict[str, Any] | None = None,
    ) -> pd.DataFrame:
        """Aplica la estrategia seleccionada y devuelve el DataFrame enriquecido."""
        if params is None:
            params = {}

        if strategy_name == "sma_crossover":
            fast = params.get("fast_period", 12)
            slow = params.get("slow_period", 24)
            return cls.sma_crossover(df, fast_period=fast, slow_period=slow)

        if strategy_name == "mean_reversion":
            bb_p = params.get("bb_period", 20)
            rsi_p = params.get("rsi_period", 14)
            rsi_os = params.get("rsi_oversold", 35.0)
            rsi_ob = params.get("rsi_overbought", 65.0)
            return cls.mean_reversion_bollinger_rsi(
                df,
                bb_period=bb_p,
                rsi_period=rsi_p,
                rsi_oversold=rsi_os,
                rsi_overbought=rsi_ob,
            )

        raise ValueError(f"Estrategia desconocida: '{strategy_name}'")
