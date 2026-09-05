# Proyecto Alpha – El Pulso del Mercado

Terminal web cuantitativa profesional para la extracción, procesamiento, modelado algorítmico y backtesting de activos financieros en tiempo real e históricos.

Migrado a un stack web nativo (React + Vite + TypeScript + Tailwind CSS + Express) optimizado para despliegue en la nube y ejecución en Google AI Studio.

---

## 🏛️ Arquitectura del Sistema

El proyecto implementa una separación cuantitativa completa:

```
proyecto-alpha/
├── src/
│   ├── components/
│   │   ├── Sidebar.tsx           <- Controles de mercado, hiperparámetros y riesgo
│   │   ├── KpiHeader.tsx         <- Tarjetas métricas spot, volumen y rango
│   │   ├── MarketTab.tsx         <- Gráficos de velas/precio con Bollinger y señales
│   │   ├── OscillatorsTab.tsx    <- Gráficos de RSI (14) y MACD (12,26,9) con histograma
│   │   ├── BacktestTab.tsx       <- Curva de capital, drawdown submarino y tabla de trades
│   │   └── DatasetExpander.tsx   <- Visor tabular y exportador CSV
│   ├── lib/
│   │   ├── technical_indicators.ts <- RSI, Bandas de Bollinger, MACD
│   │   ├── strategies.ts         <- Cruce SMA y Reversión a la Media
│   │   ├── backtest_engine.ts    <- Motor mark-to-market con comisiones y SL/TP
│   │   └── mock_data.ts          <- Generador realista de respaldo / fallback
│   ├── types.ts                  <- Tipos e interfaces TypeScript estrictas
│   ├── App.tsx                   <- Orquestador de estado y terminal
│   ├── main.tsx                  <- Punto de entrada React 18
│   └── index.css                 <- Estilos globales Tailwind CSS v4
│
├── server.ts                     <- Servidor backend Express con proxy a CoinGecko y Telegram
├── package.json                  <- Dependencias y scripts de compilación
├── tsconfig.json                 <- Configuración TypeScript estricta
└── .env.example                  <- Plantilla de variables de entorno (CoinGecko, Telegram)
```

---

## 🚀 Instalación y Uso

### 1. Variables de Entorno
Copia el archivo `.env.example` a `.env` si deseas configurar credenciales reales para CoinGecko y Telegram:
```env
COINGECKO_API_KEY=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

### 2. Modo Desarrollo
```bash
npm run dev
```
La aplicación inicia en `http://localhost:3000`.

### 3. Compilación de Producción
```bash
npm run build
npm start
```
