"""Aplicación interactiva de escritorio para Proyecto Alpha – El Pulso del Mercado.

Desarrollada con Streamlit y Plotly. Conecta las capas de datos, procesamiento
y visualización en un dashboard interactivo en tiempo real con caché inteligente.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from src.data.coingecko_client import CoinGeckoClient
from src.processing.market_transformer import MarketDataTransformer
from src.visualization.interactive_plotter import InteractivePlotter

# -------------------------------------------------------------
# 1. Configuración de la Página
# -------------------------------------------------------------
st.set_page_config(
    page_title="Proyecto Alpha – Terminal de Mercado",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------------------
# 2. Funciones de Carga con Caché Inteligente (Respetando Rate Limits)
# -------------------------------------------------------------
@st.cache_data(ttl=300, show_spinner=False)
def load_market_data(coin_id: str, days: int) -> tuple[dict[str, Any], pd.DataFrame]:
    """Descarga datos crudos y los transforma en DataFrame con caché de 5 minutos.

    Garantiza que la API de CoinGecko no se sobrecargue con peticiones repetidas.
    """
    client = CoinGeckoClient()

    # 1. Extraer datos crudos
    raw_data = client.get_market_chart(coin_id=coin_id, vs_currency="usd", days=days)
    client.save_raw_data(raw_data, filename=f"{coin_id}_{days}d")

    # 2. Transformar con pandas
    df = MarketDataTransformer.json_to_dataframe(raw_data)
    return raw_data, df


@st.cache_data(ttl=60, show_spinner=False)
def load_current_price(coin_id: str) -> dict[str, Any]:
    """Consulta el precio spot actual y variación en tiempo casi real."""
    client = CoinGeckoClient()
    return client.get_current_price(coin_ids=[coin_id], vs_currencies=["usd"])


# -------------------------------------------------------------
# 3. Barra Lateral (Controles Interactivos)
# -------------------------------------------------------------
st.sidebar.title("⚙️ Controles de Mercado")
st.sidebar.markdown("Personaliza los parámetros del análisis en tiempo real:")

# Catálogo de Activos
COINS_MAP: dict[str, str] = {
    "Bitcoin (BTC)": "bitcoin",
    "Ethereum (ETH)": "ethereum",
    "Solana (SOL)": "solana",
    "Binance Coin (BNB)": "binancecoin",
    "Cardano (ADA)": "cardano",
    "Ripple (XRP)": "ripple",
}

selected_coin_label: str = st.sidebar.selectbox(
    "Selecciona Criptoactivo:",
    options=list(COINS_MAP.keys()),
    index=0,
)
coin_id: str = COINS_MAP[selected_coin_label]

# Selector de Rango Temporal
timeframe_days: int = st.sidebar.select_slider(
    "Rango Temporal Histórico (Días):",
    options=[7, 14, 30, 90, 180, 365],
    value=30,
)

# Calibrador de Media Móvil (SMA)
sma_window: int = st.sidebar.slider(
    "Período de Media Móvil (Horas):",
    min_value=5,
    max_value=120,
    value=24,
    step=1,
    help="Define el suavizado de la tendencia. 24h = tendencia diaria; 72h = tendencia de 3 días.",
)

st.sidebar.markdown("---")
# Botón para forzar actualización inmediata
if st.sidebar.button("🔄 Refrescar Datos de API", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.caption("⚡ Proyecto Alpha v1.0 | Alimentado por CoinGecko REST API")


# -------------------------------------------------------------
# 4. Encabezado y Métricas Principales (KPI Cards)
# -------------------------------------------------------------
st.title("📈 Proyecto Alpha – El Pulso del Mercado")
st.markdown(f"Análisis cuantitativo de alta frecuencia para **{selected_coin_label}** en dólares estadounidenses.")

try:
    with st.spinner("Conectando con CoinGecko y procesando datos..."):
        spot_info = load_current_price(coin_id)
        _, df = load_market_data(coin_id=coin_id, days=timeframe_days)

    coin_spot = spot_info.get(coin_id, {})
    current_price: float = coin_spot.get("usd", df["price_usd"].iloc[-1])
    change_24h: float = coin_spot.get("usd_24h_change", 0.0)
    vol_24h: float = coin_spot.get("usd_24h_vol", df["volume_24h_usd"].iloc[-1])

    period_min: float = df["price_usd"].min()
    period_max: float = df["price_usd"].max()

    # Fila de métricas institucionales
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Precio Spot Actual",
            value=f"${current_price:,.2f}",
            delta=f"{change_24h:+.2f}% (24h)",
        )

    with col2:
        st.metric(
            label="Volumen 24 Horas",
            value=f"${vol_24h / 1e9:,.2f} B",
        )

    with col3:
        st.metric(
            label=f"Mínimo del Período ({timeframe_days}d)",
            value=f"${period_min:,.2f}",
        )

    with col4:
        st.metric(
            label=f"Máximo del Período ({timeframe_days}d)",
            value=f"${period_max:,.2f}",
        )

    st.markdown("---")

    # ---------------------------------------------------------
    # 5. Gráfico Financiero Interactivo de Doble Panel
    # ---------------------------------------------------------
    st.subheader("📊 Gráfico Interactivo de Precio y Liquidez")
    fig = InteractivePlotter.create_market_figure(
        df=df,
        asset_name=selected_coin_label,
        sma_period=sma_window,
    )
    st.plotly_chart(fig, use_container_width=True)

    # ---------------------------------------------------------
    # 6. Tabla de Datos Procesados y Descarga
    # ---------------------------------------------------------
    with st.expander("🔍 Explorar Datos Tabulares y Descargar CSV"):
        st.write("Últimas 20 observaciones procesadas:")
        st.dataframe(df.tail(20), use_container_width=True)

        csv_data = df.to_csv().encode("utf-8")
        st.download_button(
            label=f"📥 Descargar Dataset Procesado ({coin_id}_{timeframe_days}d.csv)",
            data=csv_data,
            file_name=f"{coin_id}_{timeframe_days}d_processed.csv",
            mime="text/csv",
            use_container_width=True,
        )

except Exception as err:
    st.error(f"Error al conectar con la API o procesar los datos: {err}")
    st.info("Espera unos segundos antes de reintentar si alcanzaste el límite de peticiones de CoinGecko.")
