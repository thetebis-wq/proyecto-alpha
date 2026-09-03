"""Motor de Backtesting Cuantitativo Realista.

Simula el rendimiento de una estrategia incorporando fricción de mercado
real (comisiones de exchange), corte de pérdidas de emergencia (Stop-Loss),
toma de beneficios (Take-Profit) y contabilidad Mark-to-Market de capital.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class BacktestResult:
    """Contenedor detallado de resultados del backtesting realista."""

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
    total_fees_paid: float
    stop_loss_count: int
    take_profit_count: int
    signal_exit_count: int
    equity_curve: pd.Series
    benchmark_curve: pd.Series
    drawdown_curve: pd.Series
    trades: list[dict[str, Any]] = field(default_factory=list)


class BacktestEngine:
    """Motor de simulación financiera con contabilidad de fricción y riesgo."""

    @staticmethod
    def run_backtest(
        df_with_signals: pd.DataFrame,
        initial_capital: float = 10000.0,
        fee_rate: float = 0.001,  # 0.10% por defecto (estándar Binance/Coinbase)
        stop_loss_pct: float | None = 2.0,  # 2.0% de Stop-Loss
        take_profit_pct: float | None = 5.0,  # 5.0% de Take-Profit
        price_col: str = "price_usd",
    ) -> BacktestResult:
        """Ejecuta una simulación realista con comisiones, Stop-Loss y Take-Profit.

        Args:
            df_with_signals: DataFrame indexado por fecha con 'signal' y precios.
            initial_capital: Capital inicial en USD.
            fee_rate: Tasa de comisión decimal por operación (0.001 = 0.1%).
            stop_loss_pct: Porcentaje máximo de caída permitida antes de salir (o None).
            take_profit_pct: Porcentaje de ganancia para toma de beneficio anticipada (o None).
            price_col: Nombre de la columna del precio spot.

        Returns:
            BacktestResult con contabilidad neta y registro de operaciones.
        """
        df = df_with_signals.copy()

        # Variables de estado del portafolio
        capital: float = initial_capital
        position_units: float = 0.0
        in_trade: bool = False
        entry_price: float = 0.0
        entry_idx: Any = None
        trade_start_capital: float = 0.0
        total_fees_paid: float = 0.0

        stop_loss_count: int = 0
        take_profit_count: int = 0
        signal_exit_count: int = 0

        trades: list[dict[str, Any]] = []
        equity_series: list[float] = []

        timestamps = df.index
        prices = df[price_col].to_numpy()
        signals = df["signal"].to_numpy() if "signal" in df.columns else np.zeros(len(df))

        for i in range(len(df)):
            current_time = timestamps[i]
            current_price = prices[i]
            current_signal = signals[i]
            is_last_bar = i == (len(df) - 1)

            # ---------------------------------------------------------
            # 1. GESTIÓN DE SALIDAS (Si estamos comprados)
            # ---------------------------------------------------------
            if in_trade:
                pnl_unrealized_pct = ((current_price - entry_price) / entry_price) * 100.0
                exit_triggered = False
                exit_reason = ""

                # Condición 1: Stop-Loss alcanzado
                if stop_loss_pct is not None and pnl_unrealized_pct <= -abs(stop_loss_pct):
                    exit_triggered = True
                    exit_reason = "STOP_LOSS"
                    stop_loss_count += 1

                # Condición 2: Take-Profit alcanzado
                elif take_profit_pct is not None and pnl_unrealized_pct >= abs(take_profit_pct):
                    exit_triggered = True
                    exit_reason = "TAKE_PROFIT"
                    take_profit_count += 1

                # Condición 3: Señal de Venta de la Estrategia (-1)
                elif current_signal == -1:
                    exit_triggered = True
                    exit_reason = "SEÑAL_ESTRATEGIA"
                    signal_exit_count += 1

                # Condición 4: Cierre al final de los datos
                elif is_last_bar:
                    exit_triggered = True
                    exit_reason = "FIN_PERIODO"
                    signal_exit_count += 1

                # Ejecución del Cierre de Posición
                if exit_triggered:
                    gross_sale = position_units * current_price
                    exit_fee = gross_sale * fee_rate
                    capital = gross_sale - exit_fee
                    total_fees_paid += exit_fee

                    net_trade_pnl_pct = ((capital - trade_start_capital) / trade_start_capital) * 100.0
                    net_trade_pnl_usd = capital - trade_start_capital

                    trades.append(
                        {
                            "entry_date": entry_idx,
                            "exit_date": current_time,
                            "entry_price": entry_price,
                            "exit_price": current_price,
                            "exit_reason": exit_reason,
                            "pnl_pct": net_trade_pnl_pct,
                            "pnl_usd": net_trade_pnl_usd,
                            "won": net_trade_pnl_pct > 0,
                        }
                    )

                    in_trade = False
                    position_units = 0.0

            # ---------------------------------------------------------
            # 2. GESTIÓN DE ENTRADAS (Si estamos en liquidez)
            # ---------------------------------------------------------
            if not in_trade and current_signal == 1 and not is_last_bar:
                in_trade = True
                entry_idx = current_time
                entry_price = current_price
                trade_start_capital = capital

                entry_fee = capital * fee_rate
                total_fees_paid += entry_fee
                usable_capital = capital - entry_fee
                position_units = usable_capital / entry_price

            # ---------------------------------------------------------
            # 3. VALORACIÓN MARK-TO-MARKET DEL PORTAFOLIO
            # ---------------------------------------------------------
            if in_trade:
                # Valor de liquidación neta si cerráramos ahora mismo
                current_equity = (position_units * current_price) * (1.0 - fee_rate)
            else:
                current_equity = capital

            equity_series.append(current_equity)

        # -------------------------------------------------------------
        # 4. CÁLCULO DE CURVAS Y MÉTRICAS GLOBALES
        # -------------------------------------------------------------
        equity_curve = pd.Series(equity_series, index=df.index)

        # Benchmark (Buy & Hold) descontando comisiones de entrada y salida
        initial_price = prices[0]
        benchmark_units = (initial_capital * (1.0 - fee_rate)) / initial_price
        benchmark_curve = pd.Series((benchmark_units * prices) * (1.0 - fee_rate), index=df.index)

        # Drawdown
        cum_max = equity_curve.cummax()
        drawdown_curve = ((equity_curve - cum_max) / cum_max) * 100.0
        max_drawdown = float(drawdown_curve.min()) if not drawdown_curve.empty else 0.0

        # Estadísticas de Trades
        total_trades = len(trades)
        wins = [t for t in trades if t["won"]]
        losses = [t for t in trades if not t["won"]]

        winning_trades_count = len(wins)
        losing_trades_count = len(losses)

        win_rate = (winning_trades_count / total_trades * 100.0) if total_trades > 0 else 0.0

        total_gains = sum(t["pnl_usd"] for t in wins) if wins else 0.0
        total_losses = abs(sum(t["pnl_usd"] for t in losses)) if losses else 0.0
        profit_factor = (total_gains / total_losses) if total_losses > 0 else (99.9 if total_gains > 0 else 0.0)

        final_capital = float(equity_curve.iloc[-1])
        total_return_pct = ((final_capital - initial_capital) / initial_capital) * 100.0
        benchmark_final = float(benchmark_curve.iloc[-1])
        benchmark_return_pct = ((benchmark_final - initial_capital) / initial_capital) * 100.0

        return BacktestResult(
            initial_capital=initial_capital,
            final_capital=final_capital,
            total_return_pct=total_return_pct,
            benchmark_return_pct=benchmark_return_pct,
            max_drawdown_pct=max_drawdown,
            win_rate_pct=win_rate,
            profit_factor=profit_factor,
            total_trades=total_trades,
            winning_trades=winning_trades_count,
            losing_trades=losing_trades_count,
            total_fees_paid=total_fees_paid,
            stop_loss_count=stop_loss_count,
            take_profit_count=take_profit_count,
            signal_exit_count=signal_exit_count,
            equity_curve=equity_curve,
            benchmark_curve=benchmark_curve,
            drawdown_curve=drawdown_curve,
            trades=trades,
        )
