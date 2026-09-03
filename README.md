# Proyecto Alpha – El Pulso del Mercado

Arquitectura profesional para la extracción, procesamiento y análisis visual de datos de mercados financieros en tiempo real y series temporales históricas.

---

## 🏛️ Arquitectura del Sistema

El proyecto sigue una estricta **separación de responsabilidades** desacoplando cada fase del ciclo de vida de los datos:

```
proyecto-alpha/
├── src/
│   ├── config.py                 <- Carga centralizada de .env y definición de rutas
│   ├── data/
│   │   ├── coingecko_client.py   <- Cliente HTTP para la API REST de CoinGecko
│   │   └── download_market_data.py
│   ├── processing/
│   │   └── market_transformer.py <- Limpieza y transformación a DataFrames (pandas)
│   └── visualization/
│       └── market_plotter.py     <- Generación de gráficos institucionales (matplotlib)
│
├── data/
│   ├── raw/                      <- Datos crudos originales (JSON) sin alterar
│   └── processed/                <- Datos limpios con indicadores financieros (CSV)
│
├── reports/
│   └── figures/                  <- Gráficos analíticos generados (PNG alta resolución)
│
├── .env                          <- Secretos y credenciales (IGNORADO por Git)
├── .env.example                  <- Plantilla pública de variables de entorno
├── .gitignore                    <- Protección contra fugas de credenciales y datos
├── requirements.txt              <- Dependencias del stack cuantitativo
└── main.py                       <- Orquestador del pipeline de datos
```

---

## 🚀 Instalación y Uso

### 1. Requisitos
* Python 3.10+ en Windows 10/11
* Entorno virtual aislado (`.venv`)

### 2. Activar entorno virtual
```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Ejecutar el Pipeline por Lotes (Batch)
```powershell
python main.py
```

### 4. Lanzar la Aplicación Interactiva de Escritorio (Dashboard)
```powershell
streamlit run app.py
```
Se abrirá automáticamente en tu navegador predeterminado en `http://localhost:8501`. Podrás:
* Seleccionar activos (Bitcoin, Ethereum, Solana, Cardano, etc.).
* Cambiar temporalidades de 7 a 365 días.
* Calibrar la media móvil (SMA) con un deslizador reactivo.
* Interactuar con el gráfico (zoom, paneo, inspección de precios y volúmenes).
* Descargar los datos procesados en CSV.

### 5. Lanzar el Vigilante Autónomo (Alertas Telegram 24/7)
Doble clic al archivo:
```powershell
iniciar_monitor_alertas.bat
```
El bot monitorea Bitcoin, Ethereum y Solana periódicamente y despacha notificaciones automáticas a tu Telegram con Stop-Loss sugerido cuando se disparan las señales cuantitativas.

---

## 🛡️ Ciberseguridad y Buenas Prácticas
* **Sin secretos en código:** Todas las claves se manejan vía `.env` usando `python-dotenv`.
* **Protección Git:** `.gitignore` excluye `.env`, `.venv` y los archivos de datos para evitar fugas de datos y saturación del repositorio.
* **Trazabilidad Cuantitativa:** Los datos originales nunca se sobreescriben, garantizando reproducibilidad para futuro *backtesting*.
