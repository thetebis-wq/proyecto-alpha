"""Módulo de visualización interactiva con Plotly.

Genera gráficos de calidad institucional:
1. Gráfico de Mercado con Bandas de Bollinger y Señales de Compra/Venta.
2. Gráfico de Osciladores (RSI y MACD).
3. Gráfico de Curva de Capital (Equity Curve vs Benchmark) y Drawdown.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class InteractivePlotter:
    """Generador de gráficos cuantitativos interactivos basados en Plotly."""

    @staticmethod
    def create_market_figure(
        df: pd.DataFrame,
        asset_name: str = "Bitcoin",
        sma_period: int = 24,
        show_bollinger: bool = True,
        show_signals: bool = True,
    ) -> go.Figure:
        """Crea el gráfico de mercado principal con precio, SMA, Bollinger y señales."""
        df_plot = df.copy()

        # Asegurar SMA personalizada si no existe
        if "sma_dynamic" not in df_plot.columns:
            df_plot["sma_dynamic"] = df_plot["price_usd"].rolling(window=sma_period).mean()

        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.04,
            row_heights=[0.75, 0.25],
            subplot_titles=(f"{asset_name} – Análisis de Precio y Estructura", "Volumen 24 Horas"),
        )

        # 1. Bandas de Bollinger (si están habilitadas)
        if show_bollinger and "bb_upper" in df_plot.columns and "bb_lower" in df_plot.columns:
            # Banda Superior (línea transparente que define el límite superior del relleno)
            fig.add_trace(
                go.Scatter(
                    x=df_plot.index,
                    y=df_plot["bb_upper"],
                    name="Bollinger Sup",
                    line=dict(color="rgba(173, 216, 230, 0.3)", width=1),
                    hoverinfo="skip",
                    showlegend=False,
                ),
                row=1,
                col=1,
            )
            # Banda Inferior (rellena hacia la superior)
            fig.add_trace(
                go.Scatter(
                    x=df_plot.index,
                    y=df_plot["bb_lower"],
                    name="Bandas Bollinger",
                    fill="tonexty",
                    fillcolor="rgba(30, 144, 255, 0.08)",
                    line=dict(color="rgba(173, 216, 230, 0.3)", width=1),
                    hoverinfo="skip",
                ),
                row=1,
                col=1,
            )

        # 2. Precio Spot
        fig.add_trace(
            go.Scatter(
                x=df_plot.index,
                y=df_plot["price_usd"],
                name="Precio Spot (USD)",
                mode="lines",
                line=dict(color="#00D4B2", width=2),
                hovertemplate="<b>Precio:</b> $%{y:,.2f}<extra></extra>",
            ),
            row=1,
            col=1,
        )

        # 3. Media Móvil (SMA)
        fig.add_trace(
            go.Scatter(
                x=df_plot.index,
                y=df_plot["sma_dynamic"],
                name=f"SMA ({sma_period}h)",
                mode="lines",
                line=dict(color="#FFA500", width=1.8, dash="dash"),
                hovertemplate=f"<b>SMA {sma_period}h:</b> $" + "%{y:,.2f}<extra></extra>",
            ),
            row=1,
            col=1,
        )

        # 4. Señales de Trading (▲ Compra y ▼ Venta)
        if show_signals and "signal" in df_plot.columns:
            buy_points = df_plot[df_plot["signal"] == 1]
            sell_points = df_plot[df_plot["signal"] == -1]

            if not buy_points.empty:
                fig.add_trace(
                    go.Scatter(
                        x=buy_points.index,
                        y=buy_points["price_usd"],
                        mode="markers",
                        name="Señal COMPRA",
                        marker=dict(
                            symbol="triangle-up",
                            size=12,
                            color="#00FF7F",
                            line=dict(width=1, color="#FFFFFF"),
                        ),
                        hovertemplate="<b>COMPRA:</b> $%{y:,.2f}<extra></extra>",
                    ),
                    row=1,
                    col=1,
                )

            if not sell_points.empty:
                fig.add_trace(
                    go.Scatter(
                        x=sell_points.index,
                        y=sell_points["price_usd"],
                        mode="markers",
                        name="Señal VENTA",
                        marker=dict(
                            symbol="triangle-down",
                            size=12,
                            color="#FF4500",
                            line=dict(width=1, color="#FFFFFF"),
                        ),
                        hovertemplate="<b>VENTA:</b> $%{y:,.2f}<extra></extra>",
                    ),
                    row=1,
                    col=1,
                )

        # 5. Panel Inferior: Volumen
        fig.add_trace(
            go.Bar(
                x=df_plot.index,
                y=df_plot["volume_24h_usd"] / 1e9,
                name="Volumen ($B)",
                marker=dict(color="#4A90E2", opacity=0.7),
                hovertemplate="<b>Volumen:</b> $%{y:,.2f}B<extra></extra>",
            ),
            row=2,
            col=1,
        )

        # Configuración de layout
        fig.update_layout(
            template="plotly_dark",
            height=650,
            margin=dict(l=50, r=40, t=50, b=40),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        fig.update_yaxes(title_text="Precio ($ USD)", tickprefix="$", tickformat=",.0f", row=1, col=1)
        fig.update_yaxes(title_text="Volumen ($B)", ticksuffix="B", tickformat=",.1f", row=2, col=1)
        fig.update_xaxes(showgrid=True, gridcolor="#2D3748", row=1, col=1)
        fig.update_xaxes(showgrid=True, gridcolor="#2D3748", row=2, col=1)
        return fig

    @staticmethod
    def create_oscillators_figure(df: pd.DataFrame) -> go.Figure:
        """Crea panel con los osciladores RSI y MACD sincronizados."""
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.08,
            subplot_titles=("Índice de Fuerza Relativa (RSI 14)", "MACD (12, 26, 9)"),
        )

        # 1. Gráfico RSI
        if "rsi" in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["rsi"],
                    name="RSI (14)",
                    line=dict(color="#B388FF", width=2),
                    hovertemplate="<b>RSI:</b> %{y:.1f}<extra></extra>",
                ),
                row=1,
                col=1,
            )
            # Líneas de sobrecompra (70) y sobreventa (30)
            fig.add_hline(y=70, line_dash="dot", line_color="#FF5252", annotation_text="Sobrecompra (70)", row=1, col=1)
            fig.add_hline(y=30, line_dash="dot", line_color="#69F0AE", annotation_text="Sobreventa (30)", row=1, col=1)

        # 2. Gráfico MACD
        if "macd_line" in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["macd_line"],
                    name="MACD",
                    line=dict(color="#29B6F6", width=1.5),
                ),
                row=2,
                col=1,
            )
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["macd_signal"],
                    name="Señal",
                    line=dict(color="#FFA726", width=1.5, dash="dot"),
                ),
                row=2,
                col=1,
            )
            # Histograma
            hist_colors = np.where(df["macd_hist"] >= 0, "rgba(76, 175, 80, 0.7)", "rgba(244, 67, 54, 0.7)")
            fig.add_trace(
                go.Bar(
                    x=df.index,
                    y=df["macd_hist"],
                    name="Histograma",
                    marker=dict(color=hist_colors),
                ),
                row=2,
                col=1,
            )

        fig.update_layout(
            template="plotly_dark",
            height=550,
            margin=dict(l=50, r=40, t=50, b=40),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        fig.update_yaxes(title_text="RSI", range=[0, 100], row=1, col=1)
        fig.update_yaxes(title_text="Momentum", row=2, col=1)
        fig.update_xaxes(showgrid=True, gridcolor="#2D3748", row=1, col=1)
        fig.update_xaxes(showgrid=True, gridcolor="#2D3748", row=2, col=1)
        return fig

    @staticmethod
    def create_equity_curve_figure(
        equity_curve: pd.Series,
        benchmark_curve: pd.Series,
        drawdown_curve: pd.Series,
    ) -> go.Figure:
        """Crea el gráfico de desempeño del backtest (Equity Curve y Drawdown)."""
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.06,
            row_heights=[0.75, 0.25],
            subplot_titles=("Curva de Capital (Estrategia vs Buy & Hold)", "Underwater Chart (Drawdown %)"),
        )

        # 1. Curva de Capital
        fig.add_trace(
            go.Scatter(
                x=equity_curve.index,
                y=equity_curve,
                name="Estrategia Algorítmica",
                line=dict(color="#00E676", width=2.2),
                hovertemplate="<b>Estrategia:</b> $%{y:,.2f}<extra></extra>",
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=benchmark_curve.index,
                y=benchmark_curve,
                name="Buy & Hold (Benchmark)",
                line=dict(color="#78909C", width=1.5, dash="dash"),
                hovertemplate="<b>Buy & Hold:</b> $%{y:,.2f}<extra></extra>",
            ),
            row=1,
            col=1,
        )

        # 2. Drawdown
        fig.add_trace(
            go.Scatter(
                x=drawdown_curve.index,
                y=drawdown_curve,
                name="Drawdown",
                fill="tozeroy",
                fillcolor="rgba(239, 83, 80, 0.3)",
                line=dict(color="#EF5350", width=1),
                hovertemplate="<b>Drawdown:</b> %{y:.2f}%<extra></extra>",
            ),
            row=2,
            col=1,
        )

        fig.update_layout(
            template="plotly_dark",
            height=580,
            margin=dict(l=50, r=40, t=50, b=40),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        fig.update_yaxes(title_text="Capital ($ USD)", tickprefix="$", tickformat=",.0f", row=1, col=1)
        fig.update_yaxes(title_text="Caída (%)", ticksuffix="%", tickformat=".1f", row=2, col=1)
        fig.update_xaxes(showgrid=True, gridcolor="#2D3748", row=1, col=1)
        fig.update_xaxes(showgrid=True, gridcolor="#2D3748", row=2, col=1)
        return fig
