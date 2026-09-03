"""Cliente para envío de notificaciones y alertas vía Telegram Bot API.

Maneja peticiones HTTP a la API oficial de Telegram, formateo HTML seguro,
gestión de timeouts y control de excepciones.
"""

from __future__ import annotations

import logging
from typing import Any
import requests

from src.config import REQUEST_TIMEOUT, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Cliente HTTP para interactuar con Telegram Bot API."""

    def __init__(
        self,
        bot_token: str | None = None,
        chat_id: str | None = None,
        timeout: int = REQUEST_TIMEOUT,
    ) -> None:
        """Inicializa el notificador con credenciales seguras."""
        self.bot_token: str = (bot_token or TELEGRAM_BOT_TOKEN).strip()
        self.chat_id: str = (chat_id or TELEGRAM_CHAT_ID).strip()
        self.timeout: int = timeout
        self.base_url: str = f"https://api.telegram.org/bot{self.bot_token}"

    def is_configured(self) -> bool:
        """Verifica si las credenciales de Telegram están presentes."""
        return bool(self.bot_token and self.chat_id)

    def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """Envía un mensaje de texto formateado a través de Telegram.

        Args:
            text: Contenido del mensaje (acepta etiquetas HTML como <b>, <i>, <code>).
            parse_mode: Modo de interpretación ('HTML' o 'MarkdownV2').

        Returns:
            True si el mensaje se entregó con éxito, False en caso de error.
        """
        if not self.is_configured():
            logger.warning("Telegram no está configurado (faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID).")
            return False

        url = f"{self.base_url}/sendMessage"
        payload: dict[str, Any] = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True,
        }

        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            if response.status_code == 200:
                logger.info("Notificación de Telegram enviada exitosamente.")
                return True

            logger.error(f"Error al enviar mensaje a Telegram (HTTP {response.status_code}): {response.text}")
            return False

        except requests.exceptions.RequestException as err:
            logger.error(f"Error de red al conectar con la API de Telegram: {err}")
            return False

    def send_trade_alert(
        self,
        coin_label: str,
        signal_type: str,
        price: float,
        rsi_val: float | None = None,
        strategy_name: str = "Alpha Engine",
        stop_loss_pct: float = 2.0,
    ) -> bool:
        """Construye y envía una alerta visual estructurada para una señal de trading."""
        is_buy = "COMPRA" in signal_type.upper() or "BUY" in signal_type.upper()
        emoji_action = "🟢 COMPRA DETECTADA" if is_buy else "🔴 VENTA / SALIDA"

        rsi_text = f"{rsi_val:.1f}" if rsi_val is not None else "N/A"
        stop_loss_price = price * (1.0 - (stop_loss_pct / 100.0)) if is_buy else price * (1.0 + (stop_loss_pct / 100.0))

        message = (
            f"🔔 <b>PROYECTO ALPHA – ALERTA CUANTITATIVA</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🪙 <b>Activo:</b> {coin_label}\n"
            f"🎯 <b>Señal:</b> <b>{emoji_action}</b>\n"
            f"💵 <b>Precio Spot:</b> ${price:,.2f} USD\n"
            f"📊 <b>RSI (14):</b> {rsi_text}\n"
            f"🤖 <b>Estrategia:</b> {strategy_name}\n"
            f"🛡️ <b>Stop-Loss sugerido (-{stop_loss_pct}%):</b> ${stop_loss_price:,.2f} USD\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⚡ <i>Alerta generada en tiempo real por tu terminal local.</i>"
        )
        return self.send_message(message)

    def test_connection(self) -> bool:
        """Envía un mensaje de prueba para validar la vinculación de Telegram."""
        test_msg = (
            "🚀 <b>¡Proyecto Alpha conectado exitosamente!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Tu bot de Telegram ha quedado vinculado con tu entorno local de Python.\n"
            "A partir de este momento, recibirás aquí las alertas automáticas de mercado cuando tus estrategias detecten oportunidades."
        )
        return self.send_message(test_msg)


if __name__ == "__main__":
    notifier = TelegramNotifier()
    if notifier.is_configured():
        print("Probando envío de mensaje a Telegram...")
        success = notifier.test_connection()
        print(f"Resultado: {'EXITOSO' if success else 'FALLIDO'}")
    else:
        print("Telegram no configurado. Revisa tu archivo .env.")
