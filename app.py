"""Aplicación interactiva de escritorio para Proyecto Alpha – El Pulso del Mercado.

Terminal analítica y de backtesting cuantitativo desarrollada con Streamlit y Plotly.
Integra:
- Ingestión de datos de CoinGecko con caché inteligente.
- Cálculo de indicadores técnicos multivariables (RSI, Bollinger, MACD).
- Generación algorítmica de señales de compra/venta.
- Motor de backtesting vectorizado con métricas de riesgo y curvas de balance.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from src.backtesting.engine import BacktestEngine, BacktestResult
from src.data.coingecko_client import CoinGeckoClient
from src.processing.market_transformer import MarketDataTransformer
from src.processing.technical_indicators import TechnicalIndicators
from src.strategies.signals import SignalGenerator
from src.visualization.interactive_plotter import InteractivePlotter

# -------------------------------------------------------------
# 1. Configuración de la Página
# -------------------------------------------------------------
st.set_page_config(
    page_title="Proyecto Alpha – Terminal Cuantitativa",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------------------
# 2. Funciones de Carga y Procesamiento con Caché
# -------------------------------------------------------------
@st.cache_data(ttl=300, show_spinner=False)
def get_base_market_data(coin_id: str, days: int) -> pd.DataFrame:
    """Descarga datos crudos y devuelve el DataFrame procesado básico con caché."""
    client = CoinGeckoClient()
    raw_data = client.get_market_chart(coin_id=coin_id, vs_currency="usd", days=days)
    client.save_raw_data(raw_data, filename=f"{coin_id}_{days}d")
    df = MarketDataTransformer.json_to_dataframe(raw_data)
    # Agregar todos los indicadores técnicos de base
    df = TechnicalIndicators.add_all_indicators(df)
    return df


@st.cache_data(ttl=60, show_spinner=False)
def get_spot_data(coin_id: str) -> dict[str, Any]:
    """Consulta rápida de precio spot actual."""
    client = CoinGeckoClient()
    return client.get_current_price(coin_ids=[coin_id], vs_currencies=["usd"])


# -------------------------------------------------------------
# 3. Barra Lateral (Controles de Mercado y Estrategia)
# -------------------------------------------------------------
st.sidebar.title("⚙️ Parámetros de Mercado")

COINS_MAP: dict[str, str] = {
    "Bitcoin (BTC)": "bitcoin",
    "Ethereum (ETH)": "ethereum",
    "Solana (SOL)": "solana",
    "Binance Coin (BNB)": "binancecoin",
    "Cardano (ADA)": "cardano",
    "Ripple (XRP)": "ripple",
}

selected_coin_label: str = st.sidebar.selectbox(
    "Criptoactivo:",
    options=list(COINS_MAP.keys()),
    index=0,
)
coin_id: str = COINS_MAP[selected_coin_label]

timeframe_days: int = st.sidebar.select_slider(
    "Historial (Días):",
    options=[7, 14, 30, 90, 180, 365],
    value=30,
)

st.sidebar.markdown("---")
st.sidebar.subheader("🤖 Configuración de Estrategia")

STRATEGIES = {
    "Cruce de Medias (SMA Crossover)": "sma_crossover",
    "Reversión a la Media (Bollinger + RSI)": "mean_reversion",
}
selected_strategy_label = st.sidebar.selectbox(
    "Estrategia Algorítmica:",
    options=list(STRATEGIES.keys()),
)
strategy_key = STRATEGIES[selected_strategy_label]

strategy_params: dict[str, Any] = {}

if strategy_key == "sma_crossover":
    c_fast, c_slow = st.sidebar.columns(2)
    with c_fast:
        strategy_params["fast_period"] = st.number_input("SMA Rápida (h)", min_value=3, max_value=50, value=12)
    with c_slow:
        strategy_params["slow_period"] = st.number_input("SMA Lenta (h)", min_value=10, max_value=120, value=24)

elif strategy_key == "mean_reversion":
    strategy_params["bb_period"] = st.sidebar.slider("Período Bollinger", min_value=10, max_value=50, value=20)
    strategy_params["rsi_period"] = 14
    strategy_params["rsi_oversold"] = st.sidebar.slider("Umbral Sobreventa RSI", min_value=15, max_value=45, value=35)
    strategy_params["rsi_overbought"] = st.sidebar.slider("Umbral Sobrecompra RSI", min_value=55, max_value=85, value=65)

st.sidebar.markdown("---")
st.sidebar.subheader("🛡️ Fricción y Gestión de Riesgo")
fee_rate_pct: float = st.sidebar.number_input(
    "Comisión de Exchange (%):",
    min_value=0.0,
    max_value=1.0,
    value=0.10,
    step=0.01,
    help="Comisión cobrada por orden en el exchange (ej. 0.10% en Binance).",
)
fee_rate: float = fee_rate_pct / 100.0

enable_sl: bool = st.sidebar.checkbox("Habilitar Stop-Loss", value=True)
sl_val: float | None = None
if enable_sl:
    sl_val = st.sidebar.slider("Stop-Loss (% Máx Caída):", min_value=0.5, max_value=10.0, value=2.0, step=0.5)

enable_tp: bool = st.sidebar.checkbox("Habilitar Take-Profit", value=True)
tp_val: float | None = None
if enable_tp:
    tp_val = st.sidebar.slider("Take-Profit (% Ganancia Objetivo):", min_value=1.0, max_value=25.0, value=5.0, step=0.5)

st.sidebar.markdown("---")
initial_capital: float = st.sidebar.number_input(
    "Capital Inicial Simulado ($ USD):",
    min_value=500.0,
    max_value=1000000.0,
    value=10000.0,
    step=1000.0,
)

if st.sidebar.button("🔄 Refrescar API y Recalcular", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("🔔 Notificaciones Telegram")
if st.sidebar.button("📲 Probar Alerta en Celular", use_container_width=True):
    from src.alerts.telegram_notifier import TelegramNotifier
    notifier = TelegramNotifier()
    if notifier.send_message("🔔 <b>¡Prueba desde tu Dashboard!</b>\nTu conexión entre la terminal y tu celular está 100% activa."):
        st.sidebar.success("¡Mensaje enviado a tu Telegram!")
    else:
        st.sidebar.error("No se pudo enviar. Revisa tus credenciales en .env.")

st.sidebar.caption("⚡ Proyecto Alpha v2.5 | Realismo Cuantitativo")


# -------------------------------------------------------------
# 4. Procesamiento de Datos y Ejecución de Backtest
# -------------------------------------------------------------
try:
    with st.spinner("Descargando mercado y ejecutando simulación..."):
        spot_info = get_spot_data(coin_id)
        df_base = get_base_market_data(coin_id=coin_id, days=timeframe_days)

        # Aplicar estrategia seleccionada
        df_with_signals = SignalGenerator.apply_strategy(
            df=df_base,
            strategy_name=strategy_key,
            params=strategy_params,
        )

        # Ejecutar simulación de backtesting con realismo financiero
        backtest_res: BacktestResult = BacktestEngine.run_backtest(
            df_with_signals=df_with_signals,
            initial_capital=initial_capital,
            fee_rate=fee_rate,
            stop_loss_pct=sl_val,
            take_profit_pct=tp_val,
        )

    # ---------------------------------------------------------
    # 5. Encabezado y Tarjetas KPI en Vivo
    # ---------------------------------------------------------
    st.title("⚡ Proyecto Alpha – Terminal Cuantitativa")
    st.markdown(f"Análisis y simulación algorítmica para **{selected_coin_label}** en dólares estadounidenses.")

    coin_spot = spot_info.get(coin_id, {})
    current_price: float = coin_spot.get("usd", df_base["price_usd"].iloc[-1])
    change_24h: float = coin_spot.get("usd_24h_change", 0.0)
    vol_24h: float = coin_spot.get("usd_24h_vol", df_base["volume_24h_usd"].iloc[-1])

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("Precio Spot Actual", f"${current_price:,.2f}", f"{change_24h:+.2f}% (24h)")
    with kpi2:
        st.metric("Volumen 24 Horas", f"${vol_24h / 1e9:,.2f} B")
    with kpi3:
        st.metric("Mínimo del Período", f"${df_base['price_usd'].min():,.2f}")
    with kpi4:
        st.metric("Máximo del Período", f"${df_base['price_usd'].max():,.2f}")

    st.markdown("---")

    # ---------------------------------------------------------
    # 6. Pestañas de la Aplicación
    # ---------------------------------------------------------
    tab_market, tab_oscillators, tab_backtest = st.tabs(
        ["📊 Análisis de Mercado & Señales", "🌊 Osciladores (RSI & MACD)", "🤖 Laboratorio de Backtesting"]
    )

    # PESTAÑA 1: Mercado y Señales
    with tab_market:
        col_t1, col_t2 = st.columns([1, 1])
        with col_t1:
            show_bb = st.checkbox("Mostrar Bandas de Bollinger", value=True)
        with col_t2:
            show_sigs = st.checkbox("Mostrar Señales de Compra/Venta en Gráfico", value=True)

        sma_ref = strategy_params.get("slow_period", 24)
        fig_market = InteractivePlotter.create_market_figure(
            df=df_with_signals,
            asset_name=selected_coin_label,
            sma_period=sma_ref,
            show_bollinger=show_bb,
            show_signals=show_sigs,
        )
        st.plotly_chart(fig_market, use_container_width=True)

    # PESTAÑA 2: Osciladores
    with tab_oscillators:
        st.info("💡 **RSI** indica Sobrecompra (>70) o Sobreventa (<30). **MACD** mide aceleración e inversión de tendencia.")
        fig_osc = InteractivePlotter.create_oscillators_figure(df=df_base)
        st.plotly_chart(fig_osc, use_container_width=True)

    # PESTAÑA 3: Backtesting Lab
    with tab_backtest:
        st.subheader(f"Resultados de Simulación: {selected_strategy_label}")

        # Métricas de Desempeño
        b_col1, b_col2, b_col3, b_col4, b_col5 = st.columns(5)
        strat_color = "normal" if backtest_res.total_return_pct >= 0 else "inverse"

        with b_col1:
            st.metric(
                label="Retorno Neto Estrategia",
                value=f"{backtest_res.total_return_pct:+.2f}%",
                delta=f"${backtest_res.final_capital - backtest_res.initial_capital:+,.2f}",
            )
        with b_col2:
            st.metric(
                label="Buy & Hold (Benchmark)",
                value=f"{backtest_res.benchmark_return_pct:+.2f}%",
            )
        with b_col3:
            st.metric(
                label="Win Rate (% Aciertos)",
                value=f"{backtest_res.win_rate_pct:.1f}%",
                help=f"{backtest_res.winning_trades} ganadores de {backtest_res.total_trades} trades.",
            )
        with b_col4:
            st.metric(
                label="Máximo Drawdown (Riesgo)",
                value=f"{backtest_res.max_drawdown_pct:.2f}%",
                help="La máxima caída registrada desde un pico de capital.",
            )
        with b_col5:
            st.metric(
                label="Profit Factor",
                value=f"{backtest_res.profit_factor:.2f}",
                help="Ganancias brutas divididas entre pérdidas brutas.",
            )

        # Fila 2: Desglose de Fricción y Riesgo
        r_col1, r_col2, r_col3, r_col4 = st.columns(4)
        with r_col1:
            st.metric("Comisiones Pagadas", f"${backtest_res.total_fees_paid:,.2f}", help=f"Tasa configurada: {fee_rate_pct:.2f}% por orden.")
        with r_col2:
            st.metric("Salidas por Stop-Loss", f"{backtest_res.stop_loss_count} trades", help="Trades cerrados por límite de pérdida de emergencia.")
        with r_col3:
            st.metric("Salidas por Take-Profit", f"{backtest_res.take_profit_count} trades", help="Trades cerrados por objetivo de ganancia.")
        with r_col4:
            st.metric("Salidas por Señal Técnica", f"{backtest_res.signal_exit_count} trades", help="Trades cerrados por cambio en el indicador.")

        # Gráfico de Curva de Capital
        fig_equity = InteractivePlotter.create_equity_curve_figure(
            equity_curve=backtest_res.equity_curve,
            benchmark_curve=backtest_res.benchmark_curve,
            drawdown_curve=backtest_res.drawdown_curve,
        )
        st.plotly_chart(fig_equity, use_container_width=True)

        # Registro de Trades
        st.subheader(f"📋 Historial de Operaciones Detallado ({backtest_res.total_trades} trades)")
        if backtest_res.trades:
            trades_df = pd.DataFrame(backtest_res.trades)
            reason_map = {
                "STOP_LOSS": "🛑 Stop-Loss",
                "TAKE_PROFIT": "🎯 Take-Profit",
                "SEÑAL_ESTRATEGIA": "🔄 Señal",
                "FIN_PERIODO": "⏳ Fin Período",
            }
            trades_df["exit_reason"] = trades_df["exit_reason"].map(lambda x: reason_map.get(x, x))
            trades_df["pnl_pct"] = trades_df["pnl_pct"].map(lambda x: f"{x:+.2f}%")
            trades_df["pnl_usd"] = trades_df["pnl_usd"].map(lambda x: f"${x:+,.2f}")
            trades_df["entry_price"] = trades_df["entry_price"].map(lambda x: f"${x:,.2f}")
            trades_df["exit_price"] = trades_df["exit_price"].map(lambda x: f"${x:,.2f}")
            trades_df.rename(
                columns={
                    "entry_date": "Fecha Entrada",
                    "exit_date": "Fecha Salida",
                    "entry_price": "Precio Entrada",
                    "exit_price": "Precio Salida",
                    "exit_reason": "Motivo Salida",
                    "pnl_pct": "Rendimiento Neto (%)",
                    "pnl_usd": "Ganancia/Pérdida ($)",
                    "won": "¿Ganador?",
                },
                inplace=True,
            )
            st.dataframe(trades_df, use_container_width=True)
        else:
            st.info("No se generaron trades con los parámetros actuales en este rango temporal.")

    # ---------------------------------------------------------
    # 7. Explorador y Descarga de Datos
    # ---------------------------------------------------------
    with st.expander("🔍 Explorar Datos Tabulares y Descargar Dataset Completo"):
        st.dataframe(df_with_signals.tail(30), use_container_width=True)
        csv_bytes = df_with_signals.to_csv().encode("utf-8")
        st.download_button(
            label=f"📥 Descargar Dataset Cuantitativo ({coin_id}_{timeframe_days}d_full.csv)",
            data=csv_bytes,
            file_name=f"{coin_id}_{timeframe_days}d_quant_dataset.csv",
            mime="text/csv",
            use_container_width=True,
        )

except Exception as err:
    st.error(f"Error durante la ejecución del sistema cuantitativo: {err}")
    st.info("Verifica tu conexión a internet o espera unos segundos antes de reintentar.")
