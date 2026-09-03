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

### 3. Ejecutar el Pipeline Completo
```powershell
python main.py
```

El pipeline ejecutará automáticamente:
1. Conexión a la API de CoinGecko y respaldo en `data/raw/`.
2. Normalización de timestamps a UTC y cálculo de indicadores (`return_pct`, `sma_24h`) en `data/processed/`.
3. Exportación de gráfico de doble panel (Precio/SMA arriba y Volumen abajo) en `reports/figures/`.

---

## 🛡️ Ciberseguridad y Buenas Prácticas
* **Sin secretos en código:** Todas las claves se manejan vía `.env` usando `python-dotenv`.
* **Protección Git:** `.gitignore` excluye `.env`, `.venv` y los archivos de datos para evitar fugas de datos y saturación del repositorio.
* **Trazabilidad Cuantitativa:** Los datos originales nunca se sobreescriben, garantizando reproducibilidad para futuro *backtesting*.
