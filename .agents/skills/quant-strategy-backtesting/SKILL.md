---
name: quant-strategy-backtesting
description: Directrices y patrones de diseño para formulación de estrategias algorítmicas, generación de señales vectorizadas y simulación de backtesting con métricas de riesgo en Proyecto Alpha. Activar al diseñar nuevas estrategias, calibrar hiperparámetros o auditar el motor de simulación.
---

# Quantitative Strategy & Backtesting (Proyecto Alpha)

Esta skill define la metodología cuantitativa para desarrollar, evaluar y auditar estrategias de trading algorítmico en Proyecto Alpha.

## 1. Generación de Señales (`src/strategies/signals.py`)

Toda estrategia algorítmica debe implementarse de forma vectorizada o con iteradores sin sesgo:
- `signal = 1`: Señal de Compra / Entrada Larga.
- `signal = -1`: Señal de Venta / Cierre / Salida.
- `signal = 0`: Neutral / Mantener.

### Reglas Críticas Anti-Sesgo:
- **No Lookahead Bias**: No calcular medias o condiciones usando `.shift(-k)` o índices futuros. Toda decisión en el índice `t` solo puede depender de datos hasta `t`.
- **Estrategias Soportadas**:
  - `sma_crossover`: Cruce de media rápida y lenta (`fast_period`, `slow_period`).
  - `mean_reversion`: Reversión a la media con Bandas de Bollinger y confirmación por sobreventa/sobrecompra de RSI.

## 2. Motor de Backtesting Cuantitativo (`src/backtesting/engine.py`)

El motor simula la ejecución con condiciones de mercado realistas:

1. **Fricción Financiera**:
   - `fee_rate`: Comisión porcentual por transacción (compra y venta).
   - Deducción obligatoria del capital antes y después del trade.
2. **Gestión de Riesgo Dinámica**:
   - `stop_loss_pct`: Cierre forzoso de posición si la pérdida excede el umbral configurado.
   - `take_profit_pct`: Cierre de posición para asegurar ganancias en el objetivo.
3. **Métricas Clave de Rendimiento**:
   - **Retorno Total (%)**: Rendimiento neto comparado con el Buy & Hold.
   - **Tasa de Aciertos (Win Rate %)**: Ratio de trades ganadores sobre trades cerrados.
   - **Sharpe Ratio**: Retorno ajustado por volatilidad.
   - **Max Drawdown (%)**: Caída máxima desde el punto pico de balance (equity peak).
   - **Curva de Balance**: Serie temporal de valor de cartera vs tiempo.

## 3. Procedimiento de Validación

Al añadir una nueva estrategia o modificar parámetros:
1. Validar que no produzca valores `NaN` o infinitos en las señales.
2. Comprobar que el capital simulado final refleje las comisiones cobradas en cada operación.
3. Contrastar siempre el resultado con la métrica pasiva (*Buy & Hold Benchmark*).
