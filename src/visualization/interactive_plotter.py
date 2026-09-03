"""Módulo de visualización interactiva con Plotly.

Genera gráficos de doble panel reactivos con zoom, paneo y tooltips
optimizados para integración directa con dashboards en Streamlit.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class InteractivePlotter:
    """Generador de gráficos financieros interactivos basados en Plotly."""

    @staticmethod
    def create_market_figure(
        df: pd.DataFrame,
        asset_name: str = "Bitcoin",
        sma_period: int = 24,
    ) -> go.Figure:
        """Crea una figura interactiva de 2 paneles (Precio/SMA arriba y Volumen abajo).

        Args:
            df: DataFrame con DatetimeIndex y columnas 'price_usd', 'volume_24h_usd'.
            asset_name: Nombre legible del activo (ej. 'Bitcoin').
            sma_period: Período dinámico para la media móvil.

        Returns:
            go.Figure interactiva lista para renderizar en Streamlit.
        """
        # Calcular SMA dinámica en el DataFrame según la selección del usuario
        df_plot = df.copy()
        df_plot["sma_dynamic"] = df_plot["price_usd"].rolling(window=sma_period).mean()

        # Crear figura con 2 filas compartiendo el eje X
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.04,
            row_heights=[0.75, 0.25],
            subplot_titles=(f"{asset_name} – Precio Spot y Tendencia", "Volumen de Negociación (24h)"),
        )

        # ---------------------------------------------------------
        # PANEL 1 (Superior): Precio y Media Móvil
        # ---------------------------------------------------------
        # Traza de Precio Spot
        fig.add_trace(
            go.Scatter(
                x=df_plot.index,
                y=df_plot["price_usd"],
                name="Precio (USD)",
                mode="lines",
                line=dict(color="#00D4B2", width=2),
                hovertemplate="<b>Precio:</b> $%{y:,.2f}<extra></extra>",
            ),
            row=1,
            col=1,
        )

        # Traza de Media Móvil Dinámica (SMA)
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

        # ---------------------------------------------------------
        # PANEL 2 (Inferior): Volumen de 24 horas
        # ---------------------------------------------------------
        fig.add_trace(
            go.Bar(
                x=df_plot.index,
                y=df_plot["volume_24h_usd"] / 1e9,  # Miles de Millones ($B)
                name="Volumen ($B)",
                marker=dict(color="#4A90E2", opacity=0.7),
                hovertemplate="<b>Volumen:</b> $%{y:,.2f}B<extra></extra>",
            ),
            row=2,
            col=1,
        )

        # ---------------------------------------------------------
        # Configuración de Estilo y Herramientas Interactivas
        # ---------------------------------------------------------
        fig.update_layout(
            template="plotly_dark",
            height=680,
            margin=dict(l=50, r=40, t=50, b=40),
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
        )

        # Configuración de ejes Y
        fig.update_yaxes(
            title_text="Precio ($ USD)",
            tickprefix="$",
            tickformat=",.0f",
            row=1,
            col=1,
        )
        fig.update_yaxes(
            title_text="Volumen ($B)",
            ticksuffix="B",
            tickformat=",.1f",
            row=2,
            col=1,
        )

        # Configuración de eje X (fechas)
        fig.update_xaxes(
            rangeslider=dict(visible=False),
            showgrid=True,
            gridcolor="#2D3748",
            row=2,
            col=1,
        )
        fig.update_xaxes(showgrid=True, gridcolor="#2D3748", row=1, col=1)

        return fig
