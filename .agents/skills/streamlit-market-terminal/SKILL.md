---
name: streamlit-market-terminal
description: Procedimientos para desarrollo, optimización de caché, visualización con Plotly y diseño reactivo de la terminal de escritorio interactiva en Streamlit (app.py) para Proyecto Alpha. Activar al modificar componentes de UI, métricas KPI en tiempo real o gráficos interactivos.
---

# Streamlit Market Terminal (Proyecto Alpha - App 1)

Esta skill guía la construcción, depuración y optimización de la aplicación interactiva de escritorio (`app.py`).

## 1. Arquitectura de la Terminal (`app.py`)

La terminal sigue una estructura reactiva organizada en secciones:
1. **Configuración de Página y Tema**: Definido vía `.streamlit/config.toml` y `st.set_page_config(layout="wide")`.
2. **Caché Inteligente de Datos**:
   - `@st.cache_data(ttl=300)` para series temporales históricas (evita saturar CoinGecko).
   - `@st.cache_data(ttl=60)` para precios spot en tiempo real.
3. **Barra Lateral de Controles (`st.sidebar`)**:
   - Selector de activo cripto (BTC, ETH, SOL, BNB, ADA, XRP).
   - Deslizador de temporalidad (7, 14, 30, 90, 180, 365 días).
   - Selector dinámico de estrategia algorítmica e hiperparámetros.
   - Parámetros de gestión de riesgo (comisiones %, stop-loss %, take-profit %, capital inicial).
   - Botón manual de invalidación de caché (`st.cache_data.clear()`).
4. **Tarjetas KPI en Vivo**:
   - Precio spot, variación porcentual de 24 horas, volumen global y rango de precios.
5. **Pestañas Analíticas (`st.tabs`)**:
   - `📊 Análisis de Mercado & Señales`: Gráfico de velas/precio con Bandas de Bollinger y marcas visuales de compra/venta.
   - `🌊 Osciladores (RSI & MACD)`: Subgráficos independientes sincronizados temporalmente.
   - `🤖 Laboratorio de Backtesting`: Tarjetas de rendimiento, curva de equity y bitácora de trades.
6. **Explorador y Exportación**:
   - Visualización de datos tabulares y botón de descarga en formato CSV.

## 2. Buenas Prácticas de Rendimiento en Streamlit

- **Evitar recálculos pesados fuera de funciones cacheadas**: Todo cálculo sobre DataFrames debe desacoplarse o memorizarse.
- **Gráficos Plotly Reactivos**: Usar `st.plotly_chart(fig, use_container_width=True)` con fondo transparente o sincronizado con el tema oscuro institucional (`#0E1117`).
- **Manejo de Errores de Conexión**: Envolver las llamadas a la API en bloques `try...except` mostrando alertas legibles (`st.warning` o `st.error`) en lugar de trazas crudas de Python.

## 3. Ejecución Local

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```
O ejecutando el script optimizado `iniciar_dashboard.bat`.
