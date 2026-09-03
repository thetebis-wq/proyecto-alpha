"""Motor de Backtesting Cuantitativo Vectorizado.

Simula el rendimiento histórico de una estrategia con prevención estricta de
sesgo de anticipación (Lookahead Bias), calculando curvas de capital (Equity Curves)
y métricas clave de desempeño institucional (Win Rate, Max Drawdown, Benchmark comparison).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class BacktestResult:
    """Contenedor de resultados del backtesting."""

    initial_capital: float
    final_capital: float
    total_return_pct: float
    benchmark_return_pct: float
    max_drawdown_pct: float
    win_rate_pct: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    equity_curve: pd.Series
    benchmark_curve: pd.Series
    drawdown_curve: pd.Series
    trades: list[dict[str, Any]] = field(default_factory=list)


class BacktestEngine:
    """Motor de simulación y evaluación de desempeño cuantitativo."""

    @staticmethod
    def run_backtest(
        df_with_signals: pd.DataFrame,
        initial_capital: float = 10000.0,
        price_col: str = "price_usd",
    ) -> BacktestResult:
        """Ejecuta el backtest vectorizado sobre un DataFrame con 'position' y 'signal'.

        Args:
            df_with_signals: DataFrame indexado por fecha con 'position' (0 o 1) y precio.
            initial_capital: Capital base en USD.
            price_col: Nombre de la columna de precio.

        Returns:
            BacktestResult con métricas y series temporales de capital.
        """
        df = df_with_signals.copy()

        # 1. Asegurar cálculo del retorno del activo en cada barra
        if "return_pct" not in df.columns:
            df["return_pct"] = df[price_col].pct_change().fillna(0.0)
        else:
            df["return_pct"] = df["return_pct"].fillna(0.0)

        # 2. Retorno de la estrategia (ANTI-LOOKAHEAD BIAS: posición tomada en t-1)
        # La posición decidida al cierre de la vela t-1 gana/pierde el retorno de la vela t
        df["strategy_return"] = df["position"].shift(1).fillna(0.0) * df["return_pct"]

        # 3. Curvas de Capital Acumulado
        df["benchmark_equity"] = initial_capital * (1.0 + df["return_pct"]).cumprod()
        df["strategy_equity"] = initial_capital * (1.0 + df["strategy_return"]).cumprod()

        # 4. Cálculo del Drawdown
        cum_max = df["strategy_equity"].cummax()
        df["drawdown"] = (df["strategy_equity"] - cum_max) / cum_max
        max_drawdown: float = float(df["drawdown"].min()) if not df["drawdown"].empty else 0.0

        # 5. Registro y Análisis Trade a Trade
        trades: list[dict[str, Any]] = []
        in_trade = False
        entry_idx = None
        entry_price = 0.0

        for idx, row in df.iterrows():
            sig = row.get("signal", 0)
            price = row[price_col]

            # Nueva entrada
            if sig == 1 and not in_trade:
                in_trade = True
                entry_idx = idx
                entry_price = price

            # Salida
            elif (sig == -1 or idx == df.index[-1]) and in_trade:
                in_trade = False
                exit_idx = idx
                exit_price = price
                pnl_pct = (exit_price - entry_price) / entry_price
                pnl_usd = (entry_price * (1 + pnl_pct)) - entry_price  # Nominal simple

                trades.append(
                    {
                        "entry_date": entry_idx,
                        "exit_date": exit_idx,
                        "entry_price": entry_price,
                        "exit_price": exit_price,
                        "pnl_pct": pnl_pct * 100.0,
                        "won": pnl_pct > 0,
                    }
                )

        # 6. Métricas de Resumen
        total_trades = len(trades)
        wins = [t for t in trades if t["won"]]
        losses = [t for t in trades if not t["won"]]

        winning_trades_count = len(wins)
        losing_trades_count = len(losses)

        win_rate = (winning_trades_count / total_trades * 100.0) if total_trades > 0 else 0.0

        total_gains = sum(t["pnl_pct"] for t in wins) if wins else 0.0
        total_losses = abs(sum(t["pnl_pct"] for t in losses)) if losses else 0.0

        profit_factor = (total_gains / total_losses) if total_losses > 0 else (99.9 if total_gains > 0 else 0.0)

        final_capital = float(df["strategy_equity"].iloc[-1])
        total_return_pct = ((final_capital - initial_capital) / initial_capital) * 100.0
        benchmark_final = float(df["benchmark_equity"].iloc[-1])
        benchmark_return_pct = ((benchmark_final - initial_capital) / initial_capital) * 100.0

        return BacktestResult(
            initial_capital=initial_capital,
            final_capital=final_capital,
            total_return_pct=total_return_pct,
            benchmark_return_pct=benchmark_return_pct,
            max_drawdown_pct=max_drawdown * 100.0,
            win_rate_pct=win_rate,
            profit_factor=profit_factor,
            total_trades=total_trades,
            winning_trades=winning_trades_count,
            losing_trades=losing_trades_count,
            equity_curve=df["strategy_equity"],
            benchmark_curve=df["benchmark_equity"],
            drawdown_curve=df["drawdown"] * 100.0,
            trades=trades,
        )
