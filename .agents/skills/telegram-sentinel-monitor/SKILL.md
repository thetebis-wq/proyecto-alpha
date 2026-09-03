---
name: telegram-sentinel-monitor
description: Procedimientos y normas para el mantenimiento, despliegue, tolerancia a fallos y formateo de alertas del Vigilante de Mercado 24/7 (src/alerts/market_monitor.py y telegram_notifier.py) en Proyecto Alpha. Activar al configurar el bot de Telegram, añadir nuevos activos a vigilar o ajustar frecuencias de escaneo.
---

# Telegram Sentinel Monitor (Proyecto Alpha - App 2)

Esta skill define la operativa, arquitectura y mantenimiento del servicio de vigilancia autónoma 24/7.

## 1. Arquitectura del Vigilante

El sistema opera de forma desacoplada y continua:
- **`src/alerts/telegram_notifier.py`**:
  - Encapsula la comunicación con la API oficial de Telegram (`https://api.telegram.org/bot<TOKEN>/sendMessage`).
  - Utiliza formateo `parse_mode="HTML"` para destacar visualmente activos, señales, precios y niveles de stop-loss sugeridos.
  - Método `send_trade_alert()`: Construye el mensaje con emojis institucionales (🟢 Compra / 🔴 Venta) y cálculos dinámicos de gestión de riesgo.
  - Método `test_connection()`: Verifica la entrega bidireccional.
- **`src/alerts/market_monitor.py`**:
  - Bucle continuo (`start_loop()`) con intervalo configurable (`--interval`).
  - Registro dual de eventos: pantalla (consola) y archivo persistente (`data/monitor.log`).
  - **Memoria de Estados Anti-Spam (`alert_history`)**:
    - Registra el último estado de señal emitido por activo.
    - Evita despachar múltiples alertas si el mercado continúa en la misma condición sin un cambio genuino.
  - **Tolerancia a Fallos**:
    - Captura caídas de red o respuestas HTTP 429 de CoinGecko con pausas de recuperación para evitar que el proceso finalice abruptamente.

## 2. Comandos de Operación

1. **Prueba Rápida de Diagnóstico (1 sola pasada)**:
   ```powershell
   .\.venv\Scripts\python.exe -m src.alerts.market_monitor --once
   ```
2. **Ejecución Continua con Intervalo Personalizado (ej. cada 10 minutos)**:
   ```powershell
   .\.venv\Scripts\python.exe -m src.alerts.market_monitor --interval 10
   ```
3. **Lanzamiento mediante Acceso Directo**:
   Doble clic al archivo optimizado `iniciar_monitor_alertas.bat`.
