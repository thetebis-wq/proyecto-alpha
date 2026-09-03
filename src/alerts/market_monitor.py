"""Vigilante Autónomo de Mercado para Proyecto Alpha.

Ejecuta un bucle continuo de monitoreo multiactivo, calcula indicadores
técnicos en tiempo real y despacha alertas automáticas a Telegram cuando
detecta señales válidas de compra o venta (con filtro anti-spam).
"""

from __future__ import annotations

import argparse
import logging
import time
from datetime import datetime, timezone
from typing import Any

from src.alerts.telegram_notifier import TelegramNotifier
from src.data.coingecko_client import CoinGeckoClient
from src.processing.market_transformer import MarketDataTransformer
from src.processing.technical_indicators import TechnicalIndicators
from src.strategies.signals import SignalGenerator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("MarketMonitor")

# Catálogo de monedas a vigilar
MONITORED_ASSETS: dict[str, str] = {
    "Bitcoin (BTC)": "bitcoin",
    "Ethereum (ETH)": "ethereum",
    "Solana (SOL)": "solana",
}


class MarketMonitor:
    """Motor de vigilancia continua y despacho de alertas."""

    def __init__(self, check_interval_minutes: int = 15) -> None:
        self.interval_seconds = check_interval_minutes * 60
        self.notifier = TelegramNotifier()
        self.client = CoinGeckoClient()
        # Memoria de estados para evitar spam: {coin_id: {"last_signal": int, "last_alert_time": datetime}}
        self.alert_history: dict[str, dict[str, Any]] = {}

    def scan_asset(self, coin_label: str, coin_id: str) -> None:
        """Inspecciona un activo y despacha alertas si surge una señal fresca."""
        logger.info(f"Escaneando mercado para: {coin_label}...")

        try:
            # 1. Extraer datos históricos recientes (14 días bastan para indicadores rápidos)
            raw_data = self.client.get_market_chart(coin_id=coin_id, vs_currency="usd", days=14)
            df = MarketDataTransformer.json_to_dataframe(raw_data)
            df = TechnicalIndicators.add_all_indicators(df)

            # 2. Evaluar Estrategia de Reversión a la Media (Bollinger + RSI)
            df_signals = SignalGenerator.apply_strategy(
                df=df,
                strategy_name="mean_reversion",
                params={"bb_period": 20, "rsi_period": 14, "rsi_oversold": 35.0, "rsi_overbought": 65.0},
            )

            # 3. Analizar la última vela
            last_row = df_signals.iloc[-1]
            signal = int(last_row.get("signal", 0))
            current_price = float(last_row["price_usd"])
            current_rsi = float(last_row.get("rsi", 50.0))

            logger.info(f"[{coin_label}] Precio: ${current_price:,.2f} | RSI: {current_rsi:.1f} | Señal: {signal}")

            # 4. Lógica de Disparo y Anti-Spam
            if signal != 0:
                history = self.alert_history.get(coin_id, {})
                last_sig = history.get("last_signal")

                # Solo notificar si la señal cambió o no se había notificado antes
                if last_sig != signal:
                    signal_name = "COMPRA" if signal == 1 else "VENTA / SALIDA"
                    logger.info(f"🚨 ¡DISPARANDO ALERTA A TELEGRAM para {coin_label}! Señal: {signal_name}")

                    self.notifier.send_trade_alert(
                        coin_label=coin_label,
                        signal_type=signal_name,
                        price=current_price,
                        rsi_val=current_rsi,
                        strategy_name="Reversión a la Media (Bollinger + RSI)",
                    )

                    # Registrar en memoria
                    self.alert_history[coin_id] = {
                        "last_signal": signal,
                        "last_alert_time": datetime.now(timezone.utc),
                    }
            else:
                # Si volvió a neutral (0), actualizar memoria para permitir la próxima señal
                if coin_id in self.alert_history and self.alert_history[coin_id]["last_signal"] != 0:
                    self.alert_history[coin_id]["last_signal"] = 0

        except Exception as err:
            logger.error(f"Error al escanear {coin_label}: {err}")

    def run_once(self) -> None:
        """Ejecuta una sola ronda de escaneo sobre todos los activos."""
        logger.info("=== Iniciando ronda de escaneo de mercado ===")
        for label, cid in MONITORED_ASSETS.items():
            self.scan_asset(label, cid)
            time.sleep(2)  # Pausa de cortesía para respetar límites de API
        logger.info("=== Ronda completada exitosamente ===")

    def start_loop(self) -> None:
        """Inicia el bucle continuo de vigilancia en segundo plano."""
        print("\n" + "=" * 65)
        print("   PROYECTO ALPHA: VIGILANTE DE MERCADO ACTIVO (24/7)")
        print(f"   Intervalo de escaneo: Cada {self.interval_seconds // 60} minutos")
        print("   Presiona Ctrl + C para detener el monitor.")
        print("=" * 65 + "\n")

        # Notificar al usuario que el bot despertó
        self.notifier.send_message(
            "🛡️ <b>Vigilante de Mercado Iniciado</b>\n"
            "El sistema está monitoreando Bitcoin, Ethereum y Solana 24/7 en segundo plano. "
            "Te notificaré de inmediato cuando se detecten oportunidades."
        )

        try:
            while True:
                self.run_once()
                logger.info(f"Durmiendo por {self.interval_seconds // 60} minutos...")
                time.sleep(self.interval_seconds)
        except KeyboardInterrupt:
            logger.info("Monitor detenido por el usuario.")
            self.notifier.send_message("🛑 <b>Vigilante de Mercado Detenido</b>\nEl monitor se ha pausado.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor de mercado autónomo con alertas de Telegram.")
    parser.add_argument("--once", action="store_true", help="Ejecuta una sola verificación y termina.")
    parser.add_argument("--interval", type=int, default=15, help="Intervalo en minutos entre escaneos (default: 15).")
    args = parser.parse_args()

    monitor = MarketMonitor(check_interval_minutes=args.interval)

    if args.once:
        monitor.run_once()
    else:
        monitor.start_loop()
